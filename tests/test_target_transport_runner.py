import base64
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from causalfade.target_transport import digest, encode
from tools.run_target_transport import Checkpoints, Ledger, JOURNAL


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / JOURNAL
        self.tasks = {"a": {"request_sha256": "m"}}
        self.binding = {"manifest_sha256": "test"}

    def ledger(self):
        return Ledger(self.path, ["a"], self.tasks, self.binding)

    def test_restart_before_and_after_dispatch(self):
        ledger = self.ledger()
        ledger.event("start")
        ledger.event("intent")
        ledger = self.ledger()
        ledger.recover()
        self.assertEqual(ledger.failures, 1)
        ledger.event("intent")
        ledger.event("dispatch")
        with self.assertRaisesRegex(RuntimeError, "Uncertain"):
            self.ledger().recover()

    def test_replay_checks_raw_hash_and_duplicate_reply(self):
        ledger = self.ledger()
        ledger.event("start")
        ledger.event("intent")
        ledger.event("dispatch")
        ledger.event("response", http_status=200, response_b64=base64.b64encode(b"abc").decode(),
                     response_sha256=digest(b"abc"))
        self.assertEqual(len(self.ledger().done), 1)
        extra = dict(self.ledger().done["a"], sequence=4)
        with self.path.open("ab") as f:
            f.write(encode(extra)+b"\n")
        with self.assertRaisesRegex(ValueError, "cap"):
            self.ledger()
        original = self.path.read_bytes().splitlines(keepends=True)[:4]
        original[-1] = original[-1].replace(b"YWJj", b"YWJk")
        self.path.write_bytes(b"".join(original))
        with self.assertRaisesRegex(ValueError, "response hash"):
            self.ledger()

    def test_checkpoint_push_isolated_from_working_index(self):
        root = Path(self.temp.name) / "repo"
        root.mkdir()
        remote = root.parent / "remote"
        run = root / "run"
        run.mkdir()
        def git(*args, cwd=root):
            return subprocess.check_output(["git", *args], cwd=cwd, stderr=subprocess.DEVNULL, text=True)
        git("init", "-q")
        git("init", "--bare", "-q", str(remote))
        git("config", "user.name", "Mock")
        git("config", "user.email", "mock@example.invalid")
        git("commit", "-qm", "base", "--allow-empty")
        head = git("rev-parse", "HEAD")
        git("remote", "add", "origin", str(remote))
        (run / JOURNAL).write_text("saved\n")
        (run / "progress.json").write_text("{}\n")
        (root / "unrelated").write_text("staged")
        git("add", "unrelated")
        ref = "refs/heads/codex/test-checkpoint"
        with patch("tools.run_target_transport.ROOT", root):
            checkpoint = Checkpoints(run, "origin", ref)
            checkpoint.save(1, force=True)
        self.assertTrue(checkpoint.pushed)
        self.assertEqual(git("show", f"{ref}:run/{JOURNAL}", cwd=remote), "saved\n")
        self.assertEqual(git("rev-parse", "HEAD"), head)
        self.assertEqual(git("diff", "--cached", "--name-only"), "unrelated\n")
        offline = remote.with_name("offline")
        remote.rename(offline)
        (run / JOURNAL).write_text("saved\nmore\n")
        with patch("tools.run_target_transport.ROOT", root), patch("tools.run_target_transport.time.sleep"):
            checkpoint.save(2, force=True)
            self.assertFalse(checkpoint.pushed)
            self.assertEqual(git("show", f"{ref}:run/{JOURNAL}"), "saved\nmore\n")
            offline.rename(remote)
            checkpoint.verify_prior(run / JOURNAL)
            checkpoint.save(2, force=True)
        self.assertTrue(checkpoint.pushed)
        self.assertEqual(git("show", f"{ref}:run/{JOURNAL}", cwd=remote), "saved\nmore\n")
