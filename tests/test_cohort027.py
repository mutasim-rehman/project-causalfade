import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from causalfade.cohort027 import build,validate,decode,displayed_effect
from cohort027_analyze import score,ceil_fraction
from cohort027_run import recover_incomplete_tail

class Cohort027Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds,cls.tasks,cls.truth=build()
    def test_fixture_and_balance(self):
        audit=validate(self.worlds,self.tasks,self.truth)
        self.assertEqual(audit['split_counts'],{'development':8,'validation':16})
        self.assertEqual(audit['action_positions'],{'first':240,'second':240})
        for split,n in (('development',224),('validation',448)):
            self.assertEqual(sum(t['split']==split for t in self.tasks),n)
        y={r['task_id']:r['expected'] for r in self.truth}
        for fid in {t['family_id'] for t in self.tasks}:
            for form in ('direct','decision'):
                for order in ('forward','reverse'):
                    main=[t for t in self.tasks if t['family_id']==fid and t['form']==form and t['kind']=='main' and t['order']==order]
                    self.assertEqual(len(main),3)
                    self.assertNotEqual(y[next(t['task_id'] for t in main if t['graph']=='confounder')],y[next(t['task_id'] for t in main if t['graph']=='mediator')])
                    self.assertEqual(y[next(t['task_id'] for t in main if t['graph']=='confounder')],y[next(t['task_id'] for t in main if t['graph']=='confounder_z')])
    def test_decoder_strict_and_sensitivity(self):
        self.assertEqual(decode('  X=1\n','main','stop'),('X=1','X=1'))
        self.assertEqual(decode('X=1.','main','stop'),(None,'X=1'))
        for raw,finish in (('X=1 or X=0','stop'),('```X=1```','stop'),('X=1','length'),('', 'stop'),(None,'stop')):
            self.assertEqual(decode(raw,'main',finish)[0],None)
    def test_integer_gates_and_shortcuts(self):
        self.assertEqual((ceil_fraction(112,95),ceil_fraction(224,95)),(107,213))
        tasks=[x for x in self.tasks if x['split']=='development']
        truth=[x for x in self.truth if x['task_id'].startswith('development_')]
        oracle=[{'task_id':x['task_id'],'strict_answer':x['expected']} for x in truth]
        self.assertTrue(score(tasks,truth,oracle,'development')['qualified'])
        for answer in ('X=0','X=1'):
            constant=[{'task_id':x['task_id'],'strict_answer':answer if x['kind']!='graph' else 'upstream'} for x in tasks]
            result=score(tasks,truth,constant,'development')
            self.assertFalse(result['qualified'])
            self.assertEqual(result['forms']['direct']['cells']['paired_switch']['correct'],0)
    def test_torn_tail_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'results.jsonl'
            p.write_bytes(b'{"task_id":"a"}\n{"task_id":')
            recover_incomplete_tail(p)
            self.assertEqual(p.read_bytes(),b'{"task_id":"a"}\n')
            self.assertEqual(len(list(Path(d).glob('*.partial_tail.*'))),1)
