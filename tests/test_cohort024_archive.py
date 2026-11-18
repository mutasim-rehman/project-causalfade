"""Reproducibility gate for the completed cohort 024 archive."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from analyze_cohort024_archive import analyze


class Cohort024ArchiveTests(unittest.TestCase):
    def test_completed_archive_rescores_and_binds_to_frozen_plan(self):
        base = Path(__file__).resolve().parents[1] / "experiments/cohort_024"
        output = analyze(base)
        self.assertEqual(output["audit"]["arms"], 21)
        self.assertEqual(output["audit"]["scheduled_responses"], 30912)
        self.assertEqual(output["audit"]["valid_responses"], 30281)
        self.assertEqual(output["arms"]["mistral7b_f16"]["cells"]["source_selection"]["first_option_valid"], 1)
        self.assertEqual(output["arms"]["llama8b_q4_k_m"]["invalid"]["finish_reason"]["length"], 448)
        self.assertEqual(output["arms"]["qwen7b_f16"]["signal_detection"]["decision|semantic"]["false_alarms"], 121)
        self.assertIsNone(output["arms"]["llama8b_q4_k_m"]["signal_detection"]["noncausal_control|semantic"]["d_prime"])
