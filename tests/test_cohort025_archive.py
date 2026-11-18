"""Regression checks for the retrospective archive screen's substantive claims."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_cohort025_archive import analyze, joint_mi


class Cohort025ArchiveTests(unittest.TestCase):
    def test_information_examples(self):
        self.assertEqual(joint_mi([("on", 0), ("on", 1)]), 0)
        self.assertAlmostEqual(joint_mi([("off", 0), ("on", 1)]), 1)

    def test_archived_screen_reproduces_reported_boundaries(self):
        result = analyze()
        saved = json.loads((ROOT / "experiments/cohort_025/archive_methods_screen.json").read_text(encoding="utf-8"))
        self.assertEqual(result, saved)
        self.assertEqual(len(result["source_cohorts"]), 24)
        self.assertEqual(sum(len(runs) for runs in result["inventory"].values()), 59)
        self.assertEqual(result["metamorphic_024"]["mistral7b_f16"]["answer_order|decision|semantic"]
                         ["prediction_transform_correct_on_valid_pairs"], 6)
        self.assertEqual(result["metamorphic_024"]["mistral7b_f16"]["answer_order|source_selection|semantic"]
                         ["prediction_transform_correct_on_valid_pairs"], 0)
        self.assertEqual(result["precision_transitions"]["024|qwen7b_q4_k_m"]["causal_semantic"]["p01_gain"], 6)
        self.assertEqual(result["precision_transitions"]["024|qwen7b_q4_k_m"]["causal_semantic"]["p10_loss"], 7)
        self.assertEqual(result["order_interactions"]["024|qwen7b_q4_k_m"]["other_minus_reference_order_gap_pp"], 0)
