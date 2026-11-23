"""Operational checkpoint cadence tests; no model or Git calls."""
import sys
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import cohort028_run_hourly as hourly


class HourlyCheckpointTests(TestCase):
    def test_due_at_hour_or_model_completion(self):
        self.assertFalse(hourly.due(3599, 0, False))
        self.assertTrue(hourly.due(3600, 0, False))
        self.assertTrue(hourly.due(1, 0, True))

    def test_no_commit_before_hour_or_on_early_interruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with patch.object(hourly, '_last_commit_mono', 100), \
                 patch.object(hourly.time, 'monotonic', return_value=200), \
                 patch.object(hourly, 'commit_snapshot') as commit:
                hourly.checkpoint(out, 'llama8b', 'development', 1030, 1280, True)
                self.assertEqual(__import__('json').loads((out/'progress.json').read_text())['completed'], 1030)
                commit.assert_not_called()

    def test_single_final_commit_after_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with patch.object(hourly, '_last_commit_mono', 100), \
                 patch.object(hourly.time, 'monotonic', return_value=200), \
                 patch.object(hourly, 'commit_snapshot') as commit:
                hourly.checkpoint(out, 'llama8b', 'development', 1280, 1280, True)
                commit.assert_not_called()
                (out/'analysis.json').write_text('{}')
                hourly.checkpoint(out, 'llama8b', 'development', 1280, 1280, True)
                commit.assert_called_once()

    def test_hourly_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with patch.object(hourly, '_last_commit_mono', 100), \
                 patch.object(hourly.time, 'monotonic', return_value=3700), \
                 patch.object(hourly, 'commit_snapshot') as commit:
                hourly.checkpoint(out, 'llama8b', 'development', 1100, 1280, True)
                commit.assert_called_once()
