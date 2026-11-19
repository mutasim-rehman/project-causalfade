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
