import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from causalfade.guidance import generate, score_records, validate
from causalfade.sensitivity import digest, read_jsonl
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tools import replication_pilot as pilot

class FakeProcess:
    def poll(self): return None
    def terminate(self): pass
    def wait(self,timeout=None): return 0

class ReplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.dataset=self.base/"input"
        generate(self.dataset,20261118)
        truth={r["task_id"]:r for r in read_jsonl(self.dataset/"oracle_truth.jsonl")}
        self.by_prompt={p["prompt"]:truth[p["task_id"]] for p in read_jsonl(self.dataset/"public_tasks.jsonl")}
        self.server=self.base/"server";self.server.write_bytes(b"server")
        self.qwen=self.base/"qwen";self.qwen.write_bytes(b"qwen")
        self.mistral=self.base/"mistral";self.mistral.write_bytes(b"mistral")

    def args(self,name,checkpoint,model,**changes):
        values=dict(dataset=self.dataset,out=self.base/name,server=self.server,model=model,
                    checkpoint=checkpoint,role="reference",threads=1,max_tokens=64,seed=20261118,
                    max_seconds=7200,request_timeout=180,resume=False)
        values.update(changes);return argparse.Namespace(**values)

    def request(self,port,path,body=None,timeout=2):
        if path=="/health":return {"status":"ok"}
        r=self.by_prompt[body["messages"][0]["content"]]
        if r["task_type"]=="source_selection":ans={"governing_study":r["randomized_name"]}
        elif r["task_type"]=="direct_identification":ans={"randomized_study":r["randomized_name"]}
        else:ans={"decision":"activate" if r["optimal_action"] else "leave_off"}
        return {"choices":[{"finish_reason":"stop","message":{"content":json.dumps(ans)}}]}

    def execute(self,args):
        with patch.object(pilot.subprocess,"Popen",return_value=FakeProcess()),\
             patch.object(pilot.subprocess,"check_output",return_value="revision\n"),\
             patch.object(pilot,"request",side_effect=self.request),\
             patch.dict(pilot.MODEL_SHA256,{"qwen_f16":digest(self.qwen),"mistral_q4":digest(self.mistral)}):
            return pilot.run(args)

    def test_fixture_pairing_and_model_hashes(self):
        self.assertEqual(validate(self.dataset)["tasks"],576)
        q=self.args("q", "qwen_f16",self.qwen)
        self.assertEqual(self.execute(q),0)
        m=self.args("m", "mistral_q4",self.mistral)
        self.assertEqual(self.execute(m),0)
        self.assertEqual(pilot.load(q.out/"schedule.json"),pilot.load(m.out/"schedule.json"))
        self.assertEqual(len(read_jsonl(m.out/"raw_responses.jsonl")),576)
        with self.assertRaisesRegex(ValueError,"Model hash"):
            self.execute(self.args("bad","mistral_q4",self.qwen))

    def test_resume_and_lock(self):
        q=self.args("q","qwen_f16",self.qwen,max_seconds=60)
        self.assertEqual(self.execute(q),2)
        q.resume,q.max_seconds=True,7200
        self.assertEqual(self.execute(q),0)
        q.max_tokens=128
        with self.assertRaisesRegex(ValueError,"Resume configuration"):self.execute(q)
        lock=self.base/"locked.lock";lock.write_text('{"pid":1}')
        with self.assertRaisesRegex(ValueError,"Exclusive run lock"):
            self.execute(self.args("locked","qwen_f16",self.qwen))
