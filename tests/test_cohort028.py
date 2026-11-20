import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from causalfade.cohort028 import build,validate,calculate,parse_bare,parse_structured,replay
from cohort028_analyze import analyze
from cohort028_run import recover_tail
from cohort028_prepare import schedule

class Cohort028Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.worlds,cls.tasks,cls.truth=build();cls.y={x['task_id']:x for x in cls.truth}
    def test_factorial_and_balances(self):
        report=validate(self.worlds,self.tasks,self.truth)
        self.assertEqual((report['families'],report['tasks']),(48,3840))
        for split,count in (('development',1280),('validation',2560)):
            self.assertEqual(sum(t['split']==split for t in self.tasks),count)
        for fid in {t['family_id'] for t in self.tasks}:
            for form in ('direct','decision'):
                for condition in ('bare','structured'):
                    self.assertEqual(sum(t['family_id']==fid and t['form']==form and t['condition']==condition for t in self.tasks),20)
        for split in ('development','validation'):
            ordered=schedule(self.tasks,split)
            by_id={t['task_id']:t for t in self.tasks}
            first={'bare':0,'structured':0}
            for a,b in zip(ordered[::2],ordered[1::2]):
                self.assertEqual(by_id[a]['stem_id'],by_id[b]['stem_id'])
                self.assertNotEqual(by_id[a]['condition'],by_id[b]['condition'])
                first[by_id[a]['condition']]+=1
            self.assertEqual(first['bare'],first['structured'])
    def test_public_calculator_and_leakage(self):
        task=next(t for t in self.tasks if t['kind']=='causal' and t['graph']=='confounder' and t['representation']=='raw')
        payload=task['payload'];expected=self.y[task['task_id']]
        right=calculate(payload,expected['expected_rule'])
        wrong=calculate(payload,'conditional' if expected['expected_rule']=='marginal' else 'marginal')
        self.assertEqual(right['action'],expected['expected_action'])
        self.assertNotEqual(wrong['action'],right['action'])
        poisoned=copy.deepcopy(payload);poisoned['hidden_truth']='X=0';poisoned['graph']='mediator'
        self.assertEqual(calculate(poisoned,expected['expected_rule']),right)
        self.assertEqual(replay(payload,{'rule':expected['expected_rule']}),right)
        for bad in ('__import__("os").system("false")','marginal; rm -rf /'):
            with self.assertRaises(ValueError):calculate(payload,bad)
        tied=copy.deepcopy(payload);tied['outcomes']['1']=dict(tied['outcomes']['0'])
        with self.assertRaises(ValueError):calculate(tied,'marginal')
    def test_strict_schemas(self):
        self.assertEqual(parse_bare(' X=1\n','stop'),'X=1')
        for s in ('X=1.','X=1 or X=0','```X=1```'):
            self.assertIsNone(parse_bare(s,'stop'))
        good='{"rule":"marginal","score_x0":0.4,"score_x1":0.6,"action":"X=1"}'
        self.assertIsNotNone(parse_structured(good,'stop'))
        bad=(good+' extra',good.replace('0.4','NaN'),good.replace('"action"','"extra"'),
             good.replace('"score_x0":0.4,',''),good.replace('"rule":"marginal"','"rule":"__import__"'),
             good.replace('"action":"X=1"','"action":"X=1","action":"X=0"'))
        for s in bad:self.assertIsNone(parse_structured(s,'stop'))
        self.assertIsNone(parse_structured(good,'length'))
    def test_oracle_and_shortcut_gates(self):
        for split in ('development','validation'):
            tasks=[t for t in self.tasks if t['split']==split]
            truth=[self.y[t['task_id']] for t in tasks]
            records=[]
            for t in tasks:
                y=self.y[t['task_id']]
                raw=y['expected_action'] if t['condition']=='bare' else json.dumps({'rule':y['expected_rule'],'score_x0':float(y['score_x0']),
                     'score_x1':float(y['score_x1']),'action':y['expected_action']})
                records.append({'task_id':t['task_id'],'raw':raw,'finish_reason':'stop'})
            oracle_report=analyze(tasks,truth,records,split)
            self.assertTrue(oracle_report['qualified'])
            self.assertEqual(len(oracle_report['descriptive_cells']),80)
            for rule in ('marginal','conditional'):
                shortcut=[]
                for t in tasks:
                    v=calculate(t['payload'],rule)
                    raw=v['action'] if t['condition']=='bare' else json.dumps({'rule':rule,'score_x0':float(v['score_x0']),
                         'score_x1':float(v['score_x1']),'action':v['action']})
                    shortcut.append({'task_id':t['task_id'],'raw':raw,'finish_reason':'stop'})
                self.assertFalse(analyze(tasks,truth,shortcut,split)['qualified'])
    def test_torn_write_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'results.jsonl';p.write_bytes(b'{"task_id":"a"}\n{"task_id":')
            recover_tail(p);self.assertEqual(p.read_bytes(),b'{"task_id":"a"}\n')
            self.assertEqual(len(list(Path(d).glob('*.partial_tail.*'))),1)
