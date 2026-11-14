import json
import argparse
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from causalfade import contracts
from causalfade.sensitivity import validate as validate_018, read_jsonl, write_json
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tools import contract_pilot as pilot


class ContractFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fixture"
        contracts.generate(self.path)

    def test_complete_crossing_oracles_and_public_twins(self):
        result = contracts.validate(self.path)
        self.assertEqual((result["tasks"], result["families"], result["decision_stems"]), (832, 8, 256))
        truth = read_jsonl(self.path / "oracle_truth.jsonl")
        public = {r["task_id"]: r for r in read_jsonl(self.path / "public_tasks.jsonl")}
        stems = {}
        for row in truth:
            if row["task_type"] in ("causal", "noncausal"):
                stems.setdefault(row["decision_stem_id"], []).append(row)
        for variants in stems.values():
            self.assertEqual({r["contract"] for r in variants}, set(contracts.CONTRACTS))
            self.assertEqual(len({r["optimal_action"] for r in variants}), 1)
            self.assertEqual(len({public[r["task_id"]]["prompt"].rsplit("\n", 1)[0] for r in variants}), 1)
        self.assertEqual(sum(r["task_type"] == "encoding_check" for r in truth), 48)
        self.assertEqual(sum(r["task_type"] == "source_check" for r in truth), 16)
        self.assertEqual(sum(r["contract"] == "semantic" for r in truth), 288)

    def test_strict_semantic_decoding(self):
        for contract, expected in (("semantic", '{"decision":"activate"}'),
                                   ("neutral_forward", '{"choice":"K"}'),
                                   ("neutral_reverse", '{"choice":"M"}')):
            self.assertEqual(contracts.decode(expected, contract), 1)
            for bad in ('```json\n'+expected+'\n```', expected+' prose',
                        '{"choice":"K","choice":"M"}',
                        '{"decision":"activate","extra":1}',
                        '{"choice":"X"}', '{"decision":1}'):
                self.assertIsNone(contracts.decode(bad, contract))
        self.assertEqual(contracts.decode('{"choice":"K"}', "neutral_reverse"), 0)

    def test_tampering_and_duplicate_records(self):
        truth = read_jsonl(self.path / "oracle_truth.jsonl")
        first = truth[0]
        with self.assertRaises(ValueError):
            contracts.score_records(truth, [{"task_id": first["task_id"]}] * 2)
        with self.assertRaises(ValueError):
            contracts.score_records(truth, [{"task_id": "unknown"}])
        rows = contracts.score_records(truth, [])
        self.assertEqual(sum(r["completed"] for r in rows), 0)
        self.assertFalse(contracts.competence(rows, contracts.GATE)["passed"])
        truth[0]["optimal_action"] ^= 1
        from causalfade.sensitivity import write_jsonl, digest
        write_jsonl(self.path / "oracle_truth.jsonl", truth)
        manifest = json.loads((self.path / "manifest.json").read_text())
        manifest["file_sha256"]["oracle_truth.jsonl"] = digest(self.path / "oracle_truth.jsonl")
        write_json(self.path / "manifest.json", manifest)
        with self.assertRaises(ValueError):
            contracts.validate(self.path)

    def test_family_paired_analysis_and_old_fixture(self):
        truth = read_jsonl(self.path / "oracle_truth.jsonl")
        raw = []
        for row in truth:
            action = row["optimal_action"]
            if row["contract"] == "neutral_reverse" and row["task_type"] in ("causal", "noncausal"):
                action ^= 1
            value = ({"decision": "activate" if action else "leave_off"} if row["contract"] == "semantic" else
                     {"choice": "K" if action == (row["contract"] == "neutral_forward") else "M"})
            raw.append({"task_id": row["task_id"], "response": {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(value)}}]}})
        rows = contracts.score_records(truth, raw)
        self.assertTrue(contracts.competence(rows, contracts.GATE)["passed"])
        report = contracts.analyze_rows(rows)
        effect = report["paired_contract_accuracy"]["causal|neutral_reverse_minus_neutral_forward"]
        self.assertEqual(effect["families"], 8)
        self.assertEqual(effect["estimate"], -1)
        self.assertEqual(effect["valid_paired_action_flips"]["0_to_1"] + effect["valid_paired_action_flips"]["1_to_0"], 128)
        validate_018(Path(__file__).resolve().parents[1] / "experiments/cohort_018/input")


class FakeProcess:
    def poll(self):
        return None
    def terminate(self):
        pass
    def wait(self, timeout=None):
        return 0


class ContractRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.fixture = self.base / "input"
        contracts.generate(self.fixture)
        self.truth = read_jsonl(self.fixture / "oracle_truth.jsonl")
        self.public = read_jsonl(self.fixture / "public_tasks.jsonl")
        self.by_prompt = {p["prompt"]: next(r for r in self.truth if r["task_id"] == p["task_id"])
                          for p in self.public}
        self.server = self.base / "server"
        self.model = self.base / "model"
        self.server.write_bytes(b"mock-server")
        self.model.write_bytes(b"mock-f16")

    def args(self, name, **changes):
        values = dict(dataset=self.fixture, out=self.base / name, server=self.server,
                      model=self.model, threads=1, max_tokens=64, max_seconds=7200,
                      request_timeout=180, seed=20261115, resume=False, role="reference",
                      reference_run=None)
        values.update(changes)
        return argparse.Namespace(**values)

    def request(self, port, path, body=None, timeout=2):
        if path == "/health":
            return {"status": "ok"}
        row = self.by_prompt[body["messages"][0]["content"]]
        action = row["optimal_action"]
        value = ({"decision": "activate" if action else "leave_off"} if row["contract"] == "semantic" else
                 {"choice": "K" if row["token_to_action"]["K"] == action else "M"})
        return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(value)}}]}

    def execute(self, args, callback=None):
        with patch.object(pilot.subprocess, "Popen", return_value=FakeProcess()), \
                patch.object(pilot.subprocess, "check_output", return_value="test-revision\n"), \
                patch.object(pilot, "request", side_effect=callback or self.request):
            return pilot.run(args)

    def test_resume_provenance_and_conditional_comparison(self):
        args = self.args("reference", max_seconds=60)
        self.assertEqual(self.execute(args), 2)
        self.assertEqual(pilot.load(args.out / "status.json")["status"], "paused_budget")
        args.resume, args.max_seconds = True, 7200
        self.assertEqual(self.execute(args), 0)
        self.assertTrue(pilot.check_reference(args.out, self.fixture)["gate"]["passed"])
        before = (args.out / "raw_responses.jsonl").read_bytes()
        args.max_tokens = 128
        with self.assertRaisesRegex(ValueError, "Resume configuration"):
            self.execute(args)
        self.assertEqual((args.out / "raw_responses.jsonl").read_bytes(), before)
        qmodel = self.base / "q4"
        qmodel.write_bytes(b"mock-q4")
        qargs = self.args("comparison", model=qmodel, role="comparison", reference_run=args.out)
        self.assertEqual(self.execute(qargs), 0)
        report = pilot.analysis(self.fixture, args.out, qargs.out, self.base / "analysis.json")
        self.assertEqual(report["comparison_minus_reference_accuracy"]["semantic|causal"]["estimate"], 0)

    def test_failed_semantic_gate_blocks_q4(self):
        def wrong(port, path, body=None, timeout=2):
            if path == "/health":
                return {}
            return {"choices": [{"finish_reason": "stop", "message": {"content": "invalid"}}]}
        args = self.args("reference")
        self.assertEqual(self.execute(args, wrong), 0)
        qmodel = self.base / "q4"
        qmodel.write_bytes(b"mock-q4")
        with self.assertRaisesRegex(ValueError, "gate failed"):
            self.execute(self.args("comparison", model=qmodel, role="comparison", reference_run=args.out))
        self.assertFalse((self.base / "comparison").exists())


if __name__ == "__main__":
    unittest.main()
