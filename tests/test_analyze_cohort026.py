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

    def test_archived_gate_reproduction(self):
        import json
        for model in ('qwen7b_f16','llama8b_f16'):
            saved=json.loads((ROOT/'experiments/cohort_026/runs'/model/'development_analysis.json').read_text())
            self.assertEqual(analyze(model), saved)
            self.assertFalse(any(x['qualified'] for x in saved['forms'].values()))
