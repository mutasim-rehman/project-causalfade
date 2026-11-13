"""Checks for scientific counterbalancing, semantic scoring and durable execution."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from causalfade.sensitivity import (analyze_rows, competence, decode, digest, generate,
                                   read_jsonl, score_records, sdt, validate, write_json)
import sensitivity_pilot as pilot
from analyze_14b_followup import describe_difference


class FixtureTests(unittest.TestCase):
    def test_grid_oracle_and_counterbalancing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input"
            manifest = generate(path, 8, 11)
            self.assertEqual(manifest["tasks"], 288)
            self.assertTrue(validate(path)["valid"])
            rows = read_jsonl(path / "oracle_truth.jsonl")
            self.assertEqual(len({r["rate_offset"] for r in rows}), 8)
            self.assertEqual(Counter(r["task_type"] for r in rows),
                             {"causal": 128, "noncausal": 128, "mapping_check": 16, "source_check": 16})
            # Each order twin has exactly the same evidence and semantic answer.
            paired = {}
            for r in rows:
                if r["task_type"] not in ("causal", "noncausal"):
                    continue
                key = (r["family_id"], r["task_type"], r["effect_size"],
                       r["causal_positive"], r["association_positive"], r["mapping"])
                paired.setdefault(key, []).append(r)
            for pair in paired.values():
                self.assertEqual(len(pair), 2)
                self.assertEqual(pair[0]["randomized_rates"], pair[1]["randomized_rates"])
                self.assertEqual(pair[0]["historical_rates"], pair[1]["historical_rates"])
                self.assertEqual(pair[0]["optimal_action"], pair[1]["optimal_action"])

    def test_reproducible_crossed_fixture_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a", Path(tmp) / "b"
            generate(a, 4, 12, True)
            generate(b, 4, 12, True)
            for name in ("manifest.json", "public_tasks.jsonl", "oracle_truth.jsonl"):
                self.assertEqual((a / name).read_bytes(), (b / name).read_bytes())
                self.assertNotIn(b"\r\n", (a / name).read_bytes())
            self.assertEqual(validate(a)["tasks"], 288)
            with self.assertRaises(FileExistsError):
                generate(a, 4, 12)
            with self.assertRaises(ValueError):
                generate(Path(tmp) / "bad", 3, 12)

    def test_validator_rejects_truth_tampering_even_with_updated_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input"
            generate(path, 4, 4)
            rows = read_jsonl(path / "oracle_truth.jsonl")
            rows[0]["optimal_action"] ^= 1
            from causalfade.sensitivity import write_jsonl
            write_jsonl(path / "oracle_truth.jsonl", rows)
            manifest = pilot.load(path / "manifest.json")
            manifest["file_sha256"]["oracle_truth.jsonl"] = digest(path / "oracle_truth.jsonl")
            write_json(path / "manifest.json", manifest)
            with self.assertRaisesRegex(ValueError, "Oracle mismatch"):
                validate(path)


class ScoringTests(unittest.TestCase):
    def test_strict_decoder_and_semantic_inversion(self):
        self.assertEqual(decode('{"activate":1}', 0), 1)
        self.assertEqual(decode('{"activate":1}', 1), 0)
        for text in ('{"activate":true}', '{"activate":1.0}', '{"activate":"1"}',
                     '{"activate":0,"activate":1}', '{"activate":0,"other":1}',
                     '```json\n{"activate":1}\n```', '[]', '{"activate":1} explanation'):
            self.assertIsNone(decode(text, 0), text)

    def test_sdt_separates_constant_action_from_discrimination(self):
        rows = [{"optimal_action": action, "activate": 1, "valid_action": True,
                 "completed": True, "correct": action} for action in (0, 1) for _ in range(8)]
        constant = sdt(rows)
        self.assertAlmostEqual(constant["d_prime"], 0)
        self.assertLess(constant["criterion"], 0)
        for r in rows:
            r["activate"] = r["optimal_action"]
            r["correct"] = 1
        perfect = sdt(rows)
        self.assertGreater(perfect["d_prime"], 0)
        self.assertAlmostEqual(perfect["criterion"], 0)
        self.assertIsNone(sdt(rows, False)["d_prime"])

    def test_missing_duplicate_unknown_and_length_capped_outputs(self):
        truth = [{"task_id": "a", "mapping": 1, "optimal_action": 0}]
        record = {"task_id": "a", "response": {"choices": [{"finish_reason": "stop",
                  "message": {"content": '{"activate":1}'}}]}}
        self.assertEqual(score_records(truth, [record])[0]["correct"], 1)
        self.assertEqual(score_records(truth, [])[0]["correct"], 0)
        record["response"]["choices"][0]["finish_reason"] = "length"
        self.assertFalse(score_records(truth, [record])[0]["valid_action"])
        with self.assertRaises(ValueError):
            score_records(truth, [record, record])
        with self.assertRaises(ValueError):
            score_records(truth, [{"task_id": "unknown"}])

    def test_zero_variance_14b_inference_is_json_safe(self):
        result = describe_difference(np.full(96, -0.5))
        self.assertEqual(result["mean_difference"], -.5)
        self.assertIsNone(result["two_sided_p_value"])
        json.dumps(result, allow_nan=False)


class FakeProcess:
    def poll(self):
        return None
    def terminate(self):
        pass
    def wait(self, timeout=None):
        return 0


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.dataset = self.base / "input"
        generate(self.dataset, 4, 34)
        self.truth = read_jsonl(self.dataset / "oracle_truth.jsonl")
        self.tasks = read_jsonl(self.dataset / "public_tasks.jsonl")
        self.server, self.model = self.base / "server", self.base / "model"
        self.server.write_bytes(b"mock-server")
        self.model.write_bytes(b"GGUF-reference")
        answers = {r["task_id"]: r["optimal_action"] ^ r["mapping"] for r in self.truth}
        self.answers = {t["prompt"]: answers[t["task_id"]] for t in self.tasks}

    def args(self, name, **kwargs):
        values = dict(dataset=self.dataset, out=self.base / name, server=self.server, model=self.model,
                      threads=1, max_tokens=64, max_seconds=7200, request_timeout=180,
                      seed=34, resume=False, role="reference", reference_run=None)
        values.update(kwargs)
        return argparse.Namespace(**values)

    def request(self, port, path, body=None, timeout=2):
        if path == "/health":
            return {"status": "ok"}
        token = self.answers[body["messages"][0]["content"]]
        return {"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps({"activate": token})}}]}

    def execute(self, args, callback=None):
        with patch.object(pilot.subprocess, "Popen", return_value=FakeProcess()), \
                patch.object(pilot.subprocess, "check_output", return_value="test-revision\n"), \
                patch.object(pilot, "request", side_effect=callback or self.request):
            return pilot.run(args)

    def test_budget_pause_resume_gate_and_paired_analysis(self):
        args = self.args("reference", max_seconds=60)
        self.assertEqual(self.execute(args), 2)
        self.assertEqual(pilot.load(args.out / "status.json")["status"], "paused_budget")
        self.assertEqual(read_jsonl(args.out / "raw_responses.jsonl"), [])
        args.resume, args.max_seconds = True, 7200
        self.assertEqual(self.execute(args), 0)
        raw_bytes = (args.out / "raw_responses.jsonl").read_bytes()
        config, rows = pilot.load_run(args.out, self.dataset)
        self.assertTrue(competence(rows, pilot.load(self.dataset / "manifest.json")["gate"])["passed"])
        self.assertEqual(self.execute(args), 0)
        self.assertEqual((args.out / "raw_responses.jsonl").read_bytes(), raw_bytes)
        # A different weight file is required even when requests are mocked.
        qmodel = self.base / "q4"
        qmodel.write_bytes(b"GGUF-q4")
        comparison = self.args("comparison", model=qmodel, role="comparison", reference_run=args.out)
        self.assertEqual(self.execute(comparison), 0)
        output = pilot.analysis(self.dataset, args.out, comparison.out, self.base / "analysis.json")
        self.assertEqual(output["comparison_minus_reference_accuracy"]["causal"]["estimate"], 0)
        self.assertTrue((self.base / "analysis.md").exists())
        json.dumps(output, allow_nan=False)

    def test_failed_gate_blocks_comparison_and_preserves_outputs(self):
        def invalid(port, path, body=None, timeout=2):
            return {"choices": [{"finish_reason": "stop", "message": {"content": "invalid"}}]}
        args = self.args("reference")
        self.assertEqual(self.execute(args, invalid), 0)
        qmodel = self.base / "q4"
        qmodel.write_bytes(b"GGUF-q4")
        with self.assertRaisesRegex(ValueError, "gate failed"):
            self.execute(self.args("comparison", model=qmodel, role="comparison", reference_run=args.out))
        self.assertFalse((self.base / "comparison").exists())

    def test_resume_refuses_changed_settings_and_keeps_failed_attempt(self):
        args = self.args("reference")
        def failed(*_args, **_kwargs):
            if _args[1] == "/health":
                return {}
            raise OSError("simulated connection failure")
        self.assertEqual(self.execute(args, failed), 2)
        records = read_jsonl(args.out / "raw_responses.jsonl")
        self.assertEqual(len(records), 1)
        self.assertIn("execution_error", records[0])
        args.resume, args.max_tokens = True, 128
        with self.assertRaisesRegex(ValueError, "Resume configuration"):
            self.execute(args)
        args.max_tokens = 64
        self.assertEqual(self.execute(args), 2)  # failed attempt is never replaced
        self.assertEqual(len(read_jsonl(args.out / "raw_responses.jsonl")), len(self.tasks))
        failed_row = next(r for r in pilot.load(args.out / "results.json")
                          if r["task_id"] == records[0]["task_id"])
        self.assertFalse(failed_row["valid_action"])

    def test_exclusive_lock_blocks_second_writer(self):
        args = self.args("reference")
        lock = args.out.with_name(args.out.name + ".lock")
        lock.write_text('{"pid":12345}')
        with self.assertRaisesRegex(ValueError, "Exclusive run lock"):
            self.execute(args)
        self.assertFalse(args.out.exists())
        self.assertTrue(lock.exists())


if __name__ == "__main__":
    unittest.main()
