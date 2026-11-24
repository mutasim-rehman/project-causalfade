import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from causalfade.target_forms import ARCHIVE, render
from causalfade.target_transport import sample
from tools.cohort029_prepare import prepare
from tools.cohort029_runtime import load
from tools.verify_target_transport import parse


class FormsTests(unittest.TestCase):
    def test_complete_mock_fixture_discloses_constant_rule_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "fixture"
            prepare(out, None, True)
            fixture = load(out / "fixture_audit.json")
            policy = load(out / "policy_audit.json")
            self.assertEqual((fixture["tasks"], fixture["oracle_mismatches"]), (4096, 0))
            self.assertEqual(load(out / "structural_diffs.json")["checks"]["role"], 2048)
            self.assertEqual(policy["ties"]["0"]["positive"]["correct"], 4096)
            self.assertEqual(len(policy["failures"]), 12)
            self.assertEqual(policy["ties"]["0"]["target_constant_0"]["disagreement_actions"], [1])

    def test_invalid_public_units_missing_rows_and_weights(self):
        _, _, bits, _, _, tables, weights, _ = next(sample())
        messages = render(ARCHIVE, 0, 0, 0, 0, tables, weights, bits)
        for old, new in (("Target mix:", "Target shares:"), ("%, on", ", on"),
                         ("historical study)", "randomized study)")):
            changed = deepcopy(messages)
            changed[1]["content"] = changed[1]["content"].replace(old, new)
            with self.assertRaises(ValueError):
                parse(changed)
