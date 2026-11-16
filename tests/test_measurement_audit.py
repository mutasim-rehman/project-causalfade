import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from causalfade.measurement_audit import generate,validate,score_records,decode,render
from causalfade.sensitivity import digest,read_jsonl,write_jsonl
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from tools import measurement_audit_pilot as pilot
from tools.analyze_measurement_audit import analyze

class FakeProcess:
    def poll(self):return None
    def terminate(self):pass
    def wait(self,timeout=None):return 0

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.dataset=self.base/'input';generate(self.dataset)
        truth={r['task_id']:r for r in read_jsonl(self.dataset/'oracle_truth.jsonl')}
        self.by_prompt={p['prompt']:truth[p['task_id']] for p in read_jsonl(self.dataset/'public_tasks.jsonl')}
        self.server=self.base/'server';self.server.write_bytes(b'server')
        self.model=self.base/'model';self.model.write_bytes(b'qwen')
    def args(self,**changes):
        d=dict(dataset=self.dataset,out=self.base/'run',server=self.server,model=self.model,checkpoint='qwen_f16',role='reference',threads=1,max_tokens=64,seed=20261119,max_seconds=7200,request_timeout=180,resume=False)
        d.update(changes);return argparse.Namespace(**d)
    def request(self,port,path,body=None,timeout=2):
        if path=='/health':return {'status':'ok'}
        r=self.by_prompt[body['messages'][0]['content']];kind=r['task_type']
        ans={'governing_study':r['randomized_name']} if kind=='source_selection' else {'larger':'X=1' if r['causal_positive'] else 'X=0'} if kind=='numerical_control' else {'decision':'activate' if r['optimal_action'] else 'leave_off'}
        return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(ans)}}]}
    def execute(self,args):
        with patch.object(pilot.subprocess,'Popen',return_value=FakeProcess()),patch.object(pilot.subprocess,'check_output',return_value='revision\n'),patch.object(pilot,'request',side_effect=self.request),patch.dict(pilot.MODEL_SHA256,{'qwen_f16':digest(self.model)}):
            return pilot.run(args)
    def test_balance_render_oracle_and_strict_decoding(self):
        self.assertEqual(validate(self.dataset)['tasks'],896)
        truth=read_jsonl(self.dataset/'oracle_truth.jsonl')
        self.assertEqual(len({r['task_id'] for r in truth}),896)
        self.assertEqual(decode('{"decision":"activate","decision":"leave_off"}','decision'),None)
        self.assertEqual(decode('```json\n{"decision":"activate"}\n```','decision'),None)
        self.assertEqual(decode('{"decision":"activate"}','decision'),'activate')
        by={(r['family_id'],r['base_id'],r['condition'],r['presentation_order'],r['task_type']):r for r in truth if r['task_type']=='decision'}
        self.assertEqual(len(by),256)
        for r in truth:
            if r['answer_order']=='reversed' and r['task_type']=='decision':self.assertLess(render(r).index('{"decision":"leave_off"}'),render(r).index('{"decision":"activate"}'))
        bad=[dict(r) for r in truth];bad[0]['optimal_action']=1-bad[0]['optimal_action'];write_jsonl(self.dataset/'oracle_truth.jsonl',bad)
        from causalfade.sensitivity import write_json
        m=json.loads((self.dataset/'manifest.json').read_text());m['file_sha256']['oracle_truth.jsonl']=digest(self.dataset/'oracle_truth.jsonl');write_json(self.dataset/'manifest.json',m)
        with self.assertRaises(ValueError):validate(self.dataset)
    def test_runner_hash_resume_lock_and_full_schedule(self):
        with self.assertRaisesRegex(ValueError,'Model hash'):
            self.execute(self.args(model=self.server))
        a=self.args(max_seconds=60);self.assertEqual(self.execute(a),2)
        a.resume=True;a.max_seconds=7200;self.assertEqual(self.execute(a),0)
        raw=read_jsonl(a.out/'raw_responses.jsonl');self.assertEqual(len(raw),896)
        self.assertEqual(sum(r['correct'] for r in score_records(read_jsonl(self.dataset/'oracle_truth.jsonl'),raw)),896)
        report=analyze(self.dataset,a.out,self.base/'analysis.json')
        self.assertEqual(report['overall']['correct'],896)
        self.assertTrue(report['qualification']['passed'])
        a.max_tokens=128
        with self.assertRaisesRegex(ValueError,'Resume configuration'):self.execute(a)
        (self.base/'locked.lock').write_text('{"pid":1}')
        with self.assertRaisesRegex(ValueError,'Exclusive run lock'):self.execute(self.args(out=self.base/'locked'))
