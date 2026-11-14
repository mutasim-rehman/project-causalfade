import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from causalfade import guidance
from causalfade.sensitivity import digest, read_jsonl, write_json, write_jsonl
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from tools import guidance_pilot as pilot


class GuidanceFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dataset=Path(self.temp.name)/"input"
        guidance.generate(self.dataset)

    def test_complete_evidence_twins_and_actual_order(self):
        result=guidance.validate(self.dataset)
        self.assertEqual((result["tasks"],result["stems"]),(576,128))
        truth=read_jsonl(self.dataset/"oracle_truth.jsonl")
        public={p["task_id"]:p for p in read_jsonl(self.dataset/"public_tasks.jsonl")}
        stems=defaultdict(list);bases=defaultdict(list)
        for r in truth:
            prompt=public[r["task_id"]]["prompt"]
            self.assertNotIn('"optimal_action"',prompt)
            if r["task_type"]=="randomized_only":
                self.assertNotIn("operators chose X",prompt)
            elif r["task_type"]!="direct_identification":
                stems[r["stem_id"]].append(r)
                blocks=guidance.evidence(r).split("\n\n")
                first=next(x for x in blocks if x.startswith("1. Study "))
                second=next(x for x in blocks if x.startswith("2. Study "))
                expected_first=r["randomized_name"] if r["presentation_order"]=="randomized_first" else r["historical_name"]
                expected_second=r["historical_name"] if r["presentation_order"]=="randomized_first" else r["randomized_name"]
                self.assertTrue(first.startswith(f"1. Study {expected_first}\n"))
                self.assertTrue(second.startswith(f"2. Study {expected_second}\n"))
            if r["task_type"]!="direct_identification": bases[r["base_id"]].append(r)
        for variants in stems.values():
            self.assertEqual({r["task_type"] for r in variants},set(guidance.TASKS))
            self.assertEqual(len({guidance.evidence(r) for r in variants}),1)
            self.assertEqual(len({r["optimal_action"] for r in variants}),1)
        for variants in bases.values():
            self.assertEqual(len(variants),17)
            self.assertEqual(len({tuple(r["randomized_rates"]) for r in variants}),1)

    def test_strict_decoding_missing_duplicates_and_tampering(self):
        good=(("source_selection",'{"governing_study":"B"}',"B"),
              ("direct_identification",'{"randomized_study":"A"}',"A"),
              ("ordinary",'{"decision":"leave_off"}',0))
        for kind,value,answer in good:
            self.assertEqual(guidance.decode(value,kind),answer)
            for bad in (value+" prose","```json\n"+value+"\n```",'{}',
                        '{"decision":"activate","extra":1}',
                        '{"decision":"activate","decision":"leave_off"}',
                        '{"governing_study":"C"}'):
                self.assertIsNone(guidance.decode(bad,kind))
        truth=read_jsonl(self.dataset/"oracle_truth.jsonl")
        self.assertEqual(sum(r["completed"] for r in guidance.score_records(truth,[])),0)
        with self.assertRaises(ValueError):
            guidance.score_records(truth,[{"task_id":truth[0]["task_id"]}]*2)
        decision=next(r for r in truth if r["task_type"]=="ordinary")
        decision["optimal_action"]^=1
        write_jsonl(self.dataset/"oracle_truth.jsonl",truth)
        m=json.loads((self.dataset/"manifest.json").read_text())
        m["file_sha256"]["oracle_truth.jsonl"]=digest(self.dataset/"oracle_truth.jsonl")
        write_json(self.dataset/"manifest.json",m)
        with self.assertRaises(ValueError): guidance.validate(self.dataset)

    def test_paired_analysis_and_joint_counts(self):
        truth=read_jsonl(self.dataset/"oracle_truth.jsonl")
        raw=[]
        for r in truth:
            if r["task_type"]=="source_selection": answer={"governing_study":r["randomized_name"]}
            elif r["task_type"]=="direct_identification": answer={"randomized_study":r["randomized_name"]}
            else:
                action=r["optimal_action"]^(r["task_type"]=="ordinary")
                answer={"decision":"activate" if action else "leave_off"}
            raw.append({"task_id":r["task_id"],"response":{"choices":[{"finish_reason":"stop","message":{"content":json.dumps(answer)}}]}})
        rows=guidance.score_records(truth,raw)
        report=guidance.analyze_rows(rows)
        self.assertEqual(report["by_task_type"]["source_selection"]["correct"],128)
        self.assertEqual(report["by_task_type"]["ordinary"]["correct"],0)
        self.assertEqual(report["by_task_type"]["guided"]["correct"],128)
        contrast=report["paired_contrasts"]["aligned|randomized_first|guided_minus_ordinary"]
        self.assertEqual((contrast["families"],contrast["estimate"]),(8,1))
        joint=report["source_decision_joint_counts"]["ordinary|aligned|randomized_first"]
        self.assertEqual(joint["source_correct|decision_incorrect"],32)


class FakeProcess:
    def poll(self): return None
    def terminate(self): pass
    def wait(self,timeout=None): return 0


class GuidanceRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.dataset=self.base/"input"
        guidance.generate(self.dataset)
        truth={r["task_id"]:r for r in read_jsonl(self.dataset/"oracle_truth.jsonl")}
        self.by_prompt={p["prompt"]:truth[p["task_id"]] for p in read_jsonl(self.dataset/"public_tasks.jsonl")}
        self.server,self.model=self.base/"server",self.base/"model"
        self.server.write_bytes(b"mock-server")
        self.model.write_bytes(b"mock-f16")

    def args(self,name,**changes):
        v=dict(dataset=self.dataset,out=self.base/name,server=self.server,model=self.model,
               role="reference",threads=1,max_tokens=64,seed=guidance.SEED,
               max_seconds=7200,request_timeout=180,resume=False)
        v.update(changes)
        return argparse.Namespace(**v)

    def request(self,port,path,body=None,timeout=2):
        if path=="/health": return {"status":"ok"}
        r=self.by_prompt[body["messages"][0]["content"]]
        if r["task_type"]=="source_selection": answer={"governing_study":r["randomized_name"]}
        elif r["task_type"]=="direct_identification": answer={"randomized_study":r["randomized_name"]}
        else: answer={"decision":"activate" if r["optimal_action"] else "leave_off"}
        return {"choices":[{"finish_reason":"stop","message":{"content":json.dumps(answer)}}]}

    def execute(self,args):
        with patch.object(pilot.subprocess,"Popen",return_value=FakeProcess()), \
             patch.object(pilot.subprocess,"check_output",return_value="test-revision\n"), \
             patch.object(pilot,"request",side_effect=self.request), \
             patch.object(pilot,"F16_SHA256",digest(self.model)):
            return pilot.run(args)

    def test_pause_resume_provenance_lock_and_no_q4(self):
        args=self.args("reference",max_seconds=60)
        self.assertEqual(self.execute(args),2)
        self.assertEqual(pilot.load(args.out/"status.json")["status"],"paused_budget")
        args.resume,args.max_seconds=True,7200
        self.assertEqual(self.execute(args),0)
        before=(args.out/"raw_responses.jsonl").read_bytes()
        args.max_tokens=128
        with self.assertRaisesRegex(ValueError,"Resume configuration"): self.execute(args)
        self.assertEqual((args.out/"raw_responses.jsonl").read_bytes(),before)
        lock=self.base/"other.lock";lock.write_text('{"pid":1}')
        with self.assertRaisesRegex(ValueError,"Exclusive run lock"): self.execute(self.args("other"))
        with self.assertRaisesRegex(ValueError,"reference inference only"):
            self.execute(self.args("comparison",role="comparison"))
