import unittest
from fractions import Fraction

from causalfade.target_transport import DESIGN, enumerate_world, sample
from tools.cohort029_prepare import worked_cases


class SCMTests(unittest.TestCase):
    def test_worked_quartets(self):
        self.assertEqual(worked_cases(), 4)

    def test_known_slots_worlds_and_proposal_cap(self):
        worlds = list(sample())
        self.assertEqual(len(worlds), 128)
        self.assertEqual(max(w[4] for w in worlds), 909)
        for h in range(8):
            self.assertEqual(len({w[2] for w in worlds if w[1] == h}), 16)
        for slot, h, _, _, _, _, _, worlds in worlds:
            p, g, b = DESIGN[h]
            self.assertEqual(slot//16, h)
            for role, (surface, _, scores) in enumerate(worlds):
                self.assertTrue(all(0 < value < 1 for s in surface for u in s for value in u))
                for target, (off, on) in enumerate(scores):
                    self.assertGreaterEqual((on-off)*b*(-1)**(p*target+g*role), Fraction(1, 200))

    def test_impossible_surface(self):
        with self.assertRaises(ValueError):
            enumerate_world((((2, 110), (100, 98)), ((198, 95), (100, 110))), (55, 80), 0)
