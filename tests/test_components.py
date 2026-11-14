import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from causalfade import components
from causalfade.sensitivity import digest, read_jsonl, write_json, write_jsonl
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tools import component_pilot as pilot


class ComponentFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dataset = Path(self.temp.name) / "input"
        components.generate(self.dataset)

    def test_counts_pairs_scm_and_rendered_block_order(self):
        self.assertEqual(components.validate(self.dataset)["tasks"], 224)
        truth = read_jsonl(self.dataset / "oracle_truth.jsonl")
        public = {p["task_id"]: p["prompt"] for p in read_jsonl(self.dataset / "public_tasks.jsonl")}
        stems = {}
        for row in truth:
            if row["task_type"] != "source_identification":
                stems.setdefault(row["stem_id"], []).append(row)
            if row["task_type"] == "source_identification" or row["task_type"].startswith(("aligned", "conflict")):
                blocks = public[row["task_id"]].split("\n\n")
                if row["task_type"] == "source_identification":
                    first = blocks[0]
                else:
                    first = next(x for x in blocks if x.startswith("1. Study "))
                expected = row["randomized_name"] if row["presentation_order"] == "randomized_first" else row["historical_name"]
                self.assertTrue(first.startswith(f"1. Study {expected}\n"))
                self.assertIn("Assignment method:", first)
        self.assertEqual(len(stems), 32)
        for variants in stems.values():
            self.assertEqual({r["task_type"] for r in variants}, set(components.KINDS))
            self.assertEqual(len({tuple(r["randomized_rates"]) for r in variants}), 1)
            self.assertEqual(len({r["optimal_action"] for r in variants}), 1)

    def test_strict_decoding_and_missing_duplicate_records(self):
        good = (("number", '{"larger":"X=1"}', 1),
                ("randomized_only", '{"decision":"leave_off"}', 0),
                ("source_identification", '{"randomized_study":"B"}', "B"))
        for kind, value, expected in good:
            self.assertEqual(components.decode(value, kind), expected)
            for bad in (value+" prose", "```json\n"+value+"\n```", '{}',
                        '{"decision":"activate","extra":1}',
                        '{"larger":"X=0","larger":"X=1"}',
                        '{"randomized_study":"C"}'):
                self.assertIsNone(components.decode(bad, kind))
        truth = read_jsonl(self.dataset / "oracle_truth.jsonl")
        self.assertEqual(sum(r["completed"] for r in components.score_records(truth, [])), 0)
        with self.assertRaises(ValueError):
            components.score_records(truth, [{"task_id": truth[0]["task_id"]}] * 2)

    def test_tampered_oracle_rejected_even_with_new_checksum(self):
        truth = read_jsonl(self.dataset / "oracle_truth.jsonl")
        decision = next(r for r in truth if r["task_type"] == "randomized_only")
        decision["optimal_action"] ^= 1
        write_jsonl(self.dataset / "oracle_truth.jsonl", truth)
        m = json.loads((self.dataset / "manifest.json").read_text())
        m["file_sha256"]["oracle_truth.jsonl"] = digest(self.dataset / "oracle_truth.jsonl")
        write_json(self.dataset / "manifest.json", m)
        with self.assertRaises(ValueError):
            components.validate(self.dataset)

    def test_family_paired_contrast(self):
        truth = read_jsonl(self.dataset / "oracle_truth.jsonl")
        raw = []
        for row in truth:
            if row["task_type"] == "source_identification":
                answer = {"randomized_study": row["correct_study"]}
            else:
                action = row["optimal_action"]
                if row["task_type"] == "conflict_historical_first": action ^= 1
                answer = ({"larger": "X=1" if action else "X=0"} if row["task_type"] == "number" else
                          {"decision": "activate" if action else "leave_off"})
            raw.append({"task_id": row["task_id"], "response": {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(answer)}}]}})
        rows = components.score_records(truth, raw)
        effect = components.analyze_rows(rows)["paired_contrasts"]["conflict_historical_first_minus_conflict_randomized_first"]
        self.assertEqual((effect["families"], effect["estimate"]), (8, -1))
        self.assertEqual(effect["paired_answer_flips"]["0_to_1"] + effect["paired_answer_flips"]["1_to_0"], 32)


class FakeProcess:
    def poll(self): return None
    def terminate(self): pass
    def wait(self, timeout=None): return 0


class ComponentRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.dataset = self.base / "input"
        components.generate(self.dataset)
        truth = read_jsonl(self.dataset / "oracle_truth.jsonl")
        self.by_prompt = {p["prompt"]: next(r for r in truth if r["task_id"] == p["task_id"])
                          for p in read_jsonl(self.dataset / "public_tasks.jsonl")}
        self.server, self.model = self.base / "server", self.base / "model"
        self.server.write_bytes(b"mock-server")
        self.model.write_bytes(b"mock-f16")

    def args(self, name, **kwargs):
        values = dict(dataset=self.dataset, out=self.base/name, server=self.server, model=self.model,
                      role="reference", threads=1, max_tokens=64, seed=components.SEED,
                      max_seconds=7200, request_timeout=180, resume=False)
        values.update(kwargs)
        return argparse.Namespace(**values)

    def request(self, port, path, body=None, timeout=2):
        if path == "/health": return {"status":"ok"}
        row = self.by_prompt[body["messages"][0]["content"]]
        if row["task_type"] == "source_identification": ans={"randomized_study":row["correct_study"]}
        elif row["task_type"] == "number": ans={"larger":"X=1" if row["optimal_action"] else "X=0"}
        else: ans={"decision":"activate" if row["optimal_action"] else "leave_off"}
        return {"choices":[{"finish_reason":"stop","message":{"content":json.dumps(ans)}}]}

    def execute(self, args):
        with patch.object(pilot.subprocess,"Popen",return_value=FakeProcess()), \
             patch.object(pilot.subprocess,"check_output",return_value="test-revision\n"), \
             patch.object(pilot,"request",side_effect=self.request), \
             patch.object(pilot,"F16_SHA256",digest(self.model)):
            return pilot.run(args)

    def test_pause_resume_provenance_and_lock(self):
        args=self.args("reference",max_seconds=60)
        self.assertEqual(self.execute(args),2)
        self.assertEqual(pilot.load(args.out/"status.json")["status"],"paused_budget")
        args.resume,args.max_seconds=True,7200
        self.assertEqual(self.execute(args),0)
        before=(args.out/"raw_responses.jsonl").read_bytes()
        args.max_tokens=128
        with self.assertRaisesRegex(ValueError,"Resume configuration"):
            self.execute(args)
        self.assertEqual((args.out/"raw_responses.jsonl").read_bytes(),before)
        lock=(self.base/"other.lock")
        lock.write_text('{"pid":1}')
        with self.assertRaisesRegex(ValueError,"Exclusive run lock"):
            self.execute(self.args("other"))

    def test_no_q4_or_comparison_arm(self):
        with self.assertRaisesRegex(ValueError,"reference inference only"):
            self.execute(self.args("comparison",role="comparison"))
        self.assertFalse((self.base/"comparison").exists())
