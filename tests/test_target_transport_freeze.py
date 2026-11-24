import contextlib
import io
import platform
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from causalfade.target_transport import digest
from tools.cohort029_prepare import prepare, write
from tools.cohort029_runtime import load, sha
from tools.freeze_target_transport import BASE, frozen, verify
from tools import run_target_transport as runner


class FreezeTests(unittest.TestCase):
    def test_missing_manifest_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Missing frozen manifest"):
                verify(Path(tmp))

    @unittest.skipUnless(platform.python_version_tuple()[:2] == ("3", "13"), "formal freeze requires Python 3.13")
    def test_solo_freeze_replay_and_integrity(self):
        # Synthetic token counts isolate the freeze boundary; no model/server is used.
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temp)
            candidate, preflight, out = (root / name for name in ("candidate", "preflight", "freeze"))
            transfer = root / "transfer.json"
            write(transfer, {"context": "Test-only causal wording.", "arithmetic": "Test-only scorecard wording."})
            prepare(candidate, transfer, False)
            inv = dict(python=platform.python_version(), model_sha256="test-model", server_sha256="test-server")
            write(preflight / "inventory.json", inv)
            write(preflight / "token_budget.json", dict(
                template="test", template_sha256=digest(b"test"),
                counts={key: {"tokens": 100, "chat_sha256": digest(b"chat"),
                              "token_ids_sha256": digest(b"ids")} for key in load(candidate / "schedule.json")},
                tasks_sha256=sha(candidate / "tasks.jsonl"), context=2048, completion=48, **inv))
            args = (candidate, preflight, BASE / "CF-TP1-v1.0.md", out, "test-only", "unavailable")
            def seal():
                # Only the git lookup is stubbed; all scientific checks execute.
                with patch("tools.freeze_target_transport.subprocess.check_output", return_value="test-commit"):
                    frozen(*args)

            audit = candidate / "fixture_audit.json"
            saved = audit.read_bytes()
            audit.write_bytes(saved + b" ")
            with self.assertRaisesRegex(ValueError, "disagrees with deterministic validation"):
                seal()
            self.assertFalse(out.exists())
            audit.write_bytes(saved)
            seal()
            self.assertEqual(verify(out), sha(out / "manifest.json"))
            with patch("sys.argv", ["runner", "check-ready", "--freeze", str(out)]), \
                 patch.object(runner, "inventory", return_value=inv), \
                 patch.object(runner, "collect", side_effect=AssertionError("readiness dispatched inference")):
                runner.main()

            self.assertEqual(load(out / "evidence/provenance.json")["review"], "unavailable")
            with self.assertRaisesRegex(ValueError, "already exists"):
                seal()
            manifest = out / "manifest.json"
            contents = manifest.read_bytes()
            manifest.write_bytes(contents + b" ")
            with self.assertRaisesRegex(ValueError, "manifest checksum"):
                verify(out)
            manifest.write_bytes(contents)
            (out / "fixture/gold.jsonl").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Frozen artifact changed"):
                verify(out)
