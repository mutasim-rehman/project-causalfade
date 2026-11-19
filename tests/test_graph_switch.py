import unittest
from fractions import Fraction as F
from causalfade.graph_switch import observational_joint, intervention_effect, validate_pair


class GraphSwitchTests(unittest.TestCase):
    def test_document_example_and_reverse_polarity(self):
        for reverse, expected in ((False, (F(-1, 10), F(38, 100))),
                                  (True, (F(1, 10), F(-38, 100)))):
            pair = validate_pair(reverse)
            self.assertEqual((pair['confounder_effect'], pair['mediator_effect']), expected)
            self.assertEqual(sum(pair['joint'].values()), 1)
            for graph, effect in zip(('confounder', 'mediator'), expected):
                self.assertEqual(intervention_effect(observational_joint(reverse), graph), effect)

    def test_reject_unknown_graph(self):
        with self.assertRaises(ValueError):
            intervention_effect(observational_joint(), 'unknown')

class GeneratedFamilyTests(unittest.TestCase):
    def test_independent_family_generation(self):
        from causalfade.graph_switch import family, encode_family
        records = [family(260000 + i, bool(i % 2)) for i in range(24)]
        self.assertEqual(len({tuple(r['joint'].values()) for r in records}), 24)
        for r in records:
            self.assertEqual(sum(r['joint'].values()), 1)
            self.assertLess(r['confounder_effect'] * r['mediator_effect'], 0)
            self.assertEqual(F(encode_family(r)['confounder_effect']), r['confounder_effect'])
