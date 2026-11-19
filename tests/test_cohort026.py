import json
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from cohort026 import build, numeric_table
from causalfade.graph_switch import family


class Cohort026FixtureTests(unittest.TestCase):
    def test_fixture_balance_and_pair_truth(self):
        worlds, tasks, truth = build()
        self.assertEqual((len(worlds), len(tasks), len(truth)), (48, 672, 672))
        by_id = {t['task_id']: t for t in truth}
        self.assertEqual(len(by_id), len(tasks))
        self.assertEqual(Counter(w['split'] for w in worlds), {'development':8,'validation':8,'confirmation':32})
        for w in worlds:
            self.assertEqual(sum(F(j['p']) for j in w['joint']), 1)
            self.assertLess(F(w['confounder_effect'])*F(w['mediator_effect']), 0)
            matched = [t for t in tasks if t['family_id']==w['family_id']]
            self.assertEqual(len(matched),14)
            for form in ('direct','decision'):
                switches = [t for t in matched if t['form']==form and t['kind']=='switch']
                no_changes = [t for t in matched if t['form']==form and t['kind']=='no_change']
                self.assertEqual(len(switches),2)
                self.assertNotEqual(by_id[switches[0]['task_id']]['expected'],by_id[switches[1]['task_id']]['expected'])
                self.assertEqual(len(no_changes),2)
                self.assertEqual(by_id[no_changes[0]['task_id']]['expected'],by_id[no_changes[1]['task_id']]['expected'])
                self.assertEqual(switches[0]['prompt'].split('Full observational distribution')[1].split('You may use')[0],
                                 switches[1]['prompt'].split('Full observational distribution')[1].split('You may use')[0])

    def test_displayed_joint_precision_preserves_sign(self):
        for i in range(48):
            split_seed = (260000+i if i<8 else 270000+i-8 if i<16 else 280000+i-16)
            w=family(split_seed,bool((i if i<8 else i-8 if i<16 else i-16)%2))
            text=numeric_table(w)
            rounded=[]
            for line in text.splitlines():
                if line.startswith('P(W=') and ', X=' in line:
                    rounded.append(F(line.split(' = ')[1]))
            self.assertEqual(len(rounded),8)
            self.assertLess(abs(sum(rounded)-1),F(1,100000))
