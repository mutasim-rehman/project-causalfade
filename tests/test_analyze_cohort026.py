import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from analyze_cohort026 import analyze

class AnalysisTests(unittest.TestCase):
    def test_requires_complete_schedule(self):
        with self.assertRaises((ValueError,FileNotFoundError)):
            analyze('nonexistent_model')
