"""Run, resume or stream the authorized CF-TP1 schedule."""

import argparse
import base64
import contextlib
import fcntl
import http.client
import itertools
import json
import os
import random
import signal
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

from causalfade.target_transport import TOTAL, digest, encode, task_id
from tools.cohort029_prepare import ROOT
from tools.cohort029_runtime import (
    SAMPLING, deployment_args, inventory, load, rows, serving, sha, template_identity,
)
from tools.freeze_target_transport import verify

BASE = ROOT / "experiments/cohort_029"
CHECKPOINT_REF = "refs/heads/codex/cohort-029-checkpoints"
JOURNAL = "events.jsonl"


def now():
    return datetime.now(UTC).isoformat()


def sync_dir(path):
    fd = os.open(path, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        name = tmp.name
        try:
            tmp.write(encode(data) + b"\n")
            tmp.flush()
            os.fsync(tmp.fileno())
            os.replace(name, path)
            sync_dir(path.parent)
        finally:
            Path(name).unlink(missing_ok=True)


def append(path, event):
    fresh = not path.exists()
    with path.open("ab") as out:
        out.write(encode(dict(utc=now(), **event)) + b"\n")
        out.flush()
        os.fsync(out.fileno())
    if fresh:
        sync_dir(path.parent)


def load_schedule(fixture):
    schedule = load(fixture / "schedule.json")
    prompts = rows(fixture / "tasks.jsonl")
    lookup = {row["task_id"]: row for row in prompts}
    expected = sorted(task_id((slot, *indices)) for slot in range(128)
                      for indices in itertools.product(range(2), repeat=5))
    random.Random(290432).shuffle(expected)
    if schedule != expected or len(prompts) != TOTAL or set(lookup) != set(expected):
        raise ValueError("Schedule IDs, order or response cap do not match CF-TP1")
    if any(digest(encode(row["messages"])) != row["request_sha256"] for row in prompts):
        raise ValueError("Request hash changed")
    return schedule, lookup


class Ledger:
    def __init__(self, path, schedule, tasks, binding):
        self.path, self.schedule, self.tasks, self.binding = path, schedule, tasks, binding
        self.done, self.open, self.failures, self.sequence = {}, None, 0, 0
        if path.exists():
            with path.open("rb") as src:
                for line in src:
                    if not line.endswith(b"\n"):
                        raise ValueError("Journal has torn bytes. Preserve it for reconciliation.")
                    self.apply(json.loads(line))

    def apply(self, event):
        if event["sequence"] != self.sequence or event["binding"] != self.binding:
            raise ValueError("Journal sequence or frozen run binding changed")
        self.sequence += 1
        if event["type"] == "start" and self.sequence == 1:
            return
        if self.sequence == 1 or len(self.done) >= len(self.schedule):
            raise ValueError("Event outside the frozen response cap")
        key = self.schedule[len(self.done)]
        if event["task_id"] != key or event["request_sha256"] != self.tasks[key]["request_sha256"]:
            raise ValueError("Duplicate, out-of-order or altered journal request")
        kind = event["type"]
        if kind == "intent" and self.open is None and event["attempt"] == self.sequence-1:
            self.open = (event["attempt"], "intent")
        elif self.open == (event["attempt"], "intent") and kind == "dispatch":
            self.open = (event["attempt"], "dispatch")
        elif self.open == (event["attempt"], "intent") and kind == "pre_dispatch_failure":
            self.open = None
            self.failures += 1
        elif self.open == (event["attempt"], "dispatch") and kind == "response":
            if event["http_status"] != 200:
                raise ValueError("Non-success response cannot close a task")
            raw = base64.b64decode(event["response_b64"], validate=True)
            if digest(raw) != event["response_sha256"]:
                raise ValueError("Stored response hash changed")
            self.done[key] = event
            self.open = None
        elif self.open == (event["attempt"], "dispatch") and kind == "ambiguous":
            self.open = (event["attempt"], "ambiguous")
        else:
            raise ValueError("Invalid journal transition or duplicate response")

    def event(self, kind, **details):
        record = dict(type=kind, sequence=self.sequence, binding=self.binding, **details)
        if kind != "start":
            key = self.schedule[len(self.done)]
            record.update(task_id=key, request_sha256=self.tasks[key]["request_sha256"],
                          attempt=self.open[0] if self.open else self.sequence)
        append(self.path, record)
        self.apply(record)

    def recover(self):
        if self.open and self.open[1] == "intent":
            self.event("pre_dispatch_failure", reason="recovered before dispatch marker")
        if self.open:
            raise RuntimeError("Uncertain in-flight request. Reconcile it before any further inference.")


def git(*args, env=None, timeout=30, check=True, data=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=data, capture_output=True,
                          text=True, timeout=timeout, check=check, env=env)


class Checkpoints:
    def __init__(self, run, remote, ref):
        self.paths = [str((run / name).relative_to(ROOT)) for name in (JOURNAL, "progress.json")]
        self.remote, self.ref = remote, ref
        git("check-ref-format", ref)
        if git("symbolic-ref", "-q", "HEAD", check=False).stdout.strip() == ref:
            raise ValueError("Check out a working branch before running checkpoints")
        if remote:
            if remote not in git("remote").stdout.splitlines():
                raise ValueError("Checkpoint remote is not configured")
        self.last = time.monotonic()
        self.pushed = True

    def verify_prior(self, journal):
        """Never advance a run whose saved checkpoint is ahead of its local journal."""
        branch = git("rev-parse", "--verify", self.ref, check=False)
        if self.remote:
            try:
                remote = git("ls-remote", "--refs", self.remote, self.ref,
                             env=dict(os.environ, GIT_TERMINAL_PROMPT="0",
                                      GIT_SSH_COMMAND="ssh -o BatchMode=yes"), timeout=25)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                if not journal.exists() and branch.returncode:
                    raise RuntimeError("Cannot check the checkpoint remote before starting a new journal")
                print("Checkpoint remote unavailable. Continuing with local journal and commits.", flush=True)
            else:
                if remote.stdout:
                    remote_head = remote.stdout.split()[0]
                    if branch.returncode or git("merge-base", "--is-ancestor", remote_head,
                                                self.ref, check=False).returncode:
                        raise RuntimeError("Checkpoint remote is ahead or diverged. Restore it before resuming.")
        if branch.returncode == 0:
            result = subprocess.run(["git", "show", f"{self.ref}:{self.paths[0]}"], cwd=ROOT,
                                    capture_output=True, timeout=30)
            if result.returncode == 0 and (not journal.exists() or
                                             not journal.read_bytes().startswith(result.stdout)):
                raise RuntimeError("Local journal is missing saved checkpoint data. Restore it before resuming.")

    def save(self, completed, force=False):
        if not force and time.monotonic()-self.last < 300:
            return
        self.last = time.monotonic()
        try:
            self.commit_and_push(completed, force)
        except (subprocess.SubprocessError, OSError) as error:
            if force:
                raise
            print(f"Checkpoint commit failed. Journal remains on disk. {error}", flush=True)

    def commit_and_push(self, completed, force):
        # Use an isolated index and branch, leaving the working branch and index alone.
        with tempfile.TemporaryDirectory() as scratch:
            env = dict(os.environ, GIT_INDEX_FILE=str(Path(scratch) / "index"))
            old = git("rev-parse", "--verify", self.ref, check=False).stdout.strip()
            parent = old or git("rev-parse", "HEAD").stdout.strip()
            git("read-tree", parent, env=env)
            git("add", "-f", "--", *self.paths, env=env)
            tree = git("write-tree", env=env).stdout.strip()
            commit = parent
            if tree != git("rev-parse", parent + "^{tree}").stdout.strip():
                commit = git("commit-tree", tree, "-p", parent,
                             data=f"Cohort 029 checkpoint {completed}/{TOTAL}\n").stdout.strip()
                git("update-ref", self.ref, commit, old or "0"*len(commit))
            print(f"Checkpoint {commit[:12]} ({completed}/{TOTAL})", flush=True)
        if self.remote:
            self.pushed = False
            for attempt in range(3 if force else 1):
                try:
                    git("push", "--porcelain", self.remote, f"{self.ref}:{self.ref}",
                        env=dict(os.environ, GIT_TERMINAL_PROMPT="0",
                                 GIT_SSH_COMMAND="ssh -o BatchMode=yes"), timeout=25)
                    self.pushed = True
                    print(f"Checkpoint pushed to {self.remote}/{self.ref.removeprefix('refs/heads/')}", flush=True)
                    return
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                    print(f"Checkpoint push failed ({type(exc).__name__}). Local commit is saved.", flush=True)
                    if force and attempt < 2:
                        time.sleep(2**attempt)


def progress(run, ledger, status, started, initial, detail=None):
    done = len(ledger.done)
    remaining = len(ledger.schedule)-done
    elapsed = time.monotonic()-started
    eta = round(elapsed*remaining/(done-initial)) if done > initial else None
    result = dict(status=status, completed=done, total=len(ledger.schedule),
                  percent=100*done/len(ledger.schedule), outstanding=remaining,
                  pre_dispatch_failures=ledger.failures,
                  ambiguous=int(bool(ledger.open and (ledger.open[1] == "ambiguous" or
                                    status == "blocked_ambiguous"))),
                  eta_seconds=eta, detail=detail, utc=now())
    atomic(run / "progress.json", result)
    output(result)


def output(result):
    eta = result["eta_seconds"]
    print(f"{result['utc']}  {result['completed']}/{result['total']} "
          f"({result['percent']:.2f}%)  {result['status']}  "
          f"remaining={result['outstanding']}  pre_dispatch_failures={result['pre_dispatch_failures']}  "
          f"ambiguous={result['ambiguous']}  ETA={str(eta)+'s' if eta is not None else '-'}"
          + (f"  {result['detail']}" if result.get("detail") else ""), flush=True)


def collect_one(ledger, row, port, token, on_dispatch):
    ledger.event("intent")
    started = time.monotonic()
    with contextlib.closing(http.client.HTTPConnection("127.0.0.1", port, timeout=900)) as conn:
        try:
            conn.connect()
        except OSError as exc:
            ledger.event("pre_dispatch_failure", reason=type(exc).__name__)
            return False
        on_dispatch()
        ledger.event("dispatch")
        try:
            conn.request("POST", "/v1/chat/completions", encode(
                dict(messages=row["messages"], **SAMPLING)),
                {"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
            reply = conn.getresponse()
            raw = reply.read()
        except (OSError, http.client.HTTPException) as exc:
            ledger.event("ambiguous", reason=type(exc).__name__)
            raise RuntimeError("HTTP response uncertain after dispatch") from exc
        data = dict(http_status=reply.status, response_b64=base64.b64encode(raw).decode(),
                    response_sha256=digest(raw), duration_seconds=time.monotonic()-started)
        if reply.status != 200:
            ledger.event("ambiguous", reason="HTTP failure after dispatch", **data)
            raise RuntimeError(f"HTTP {reply.status} after dispatch requires reconciliation")
        ledger.event("response", **data)
        return True


def collect_schedule(args, run, ledger, cp, started, initial, template):
    for restart in range(4):
        before = len(ledger.done)
        try:
            with serving(args.server, args.model, args.port,
                         run / "server.local.log") as (token, props):
                if template_identity(props) != template:
                    raise ValueError("Chat template changed")
                while len(ledger.done) < TOTAL:
                    key = ledger.schedule[len(ledger.done)]
                    def dispatch():
                        progress(run, ledger, "in_flight", started, initial)

                    for retry in range(4):
                        if collect_one(ledger, ledger.tasks[key], args.port, token, dispatch):
                            break
                        delay = 2**retry
                        progress(run, ledger, "retrying_connection", started, initial,
                                 f"safe pre-dispatch retry in {delay}s")
                        cp.save(len(ledger.done))
                        time.sleep(delay)
                    else:
                        raise ConnectionError("Connection retry budget exhausted")
                    progress(run, ledger, "running", started, initial)
                    cp.save(len(ledger.done))
                return
        except (ConnectionError, RuntimeError) as exc:
            # A failed startup or confirmed pre-dispatch socket failure is safe to restart.
            if ledger.open or restart == 3:
                raise
            delay = 5 * (2**restart)
            progress(run, ledger, "restarting_server", started, initial,
                     f"safe restart in {delay}s after {len(ledger.done)-before} responses: {exc}")
            cp.save(len(ledger.done))
            time.sleep(delay)


def collect(args):
    run = args.out.resolve()
    if not run.is_relative_to(BASE / "runs"):
        raise ValueError("Production run directory must be inside experiments/cohort_029/runs")
    run_path = str(run.relative_to(ROOT))
    binding = dict(manifest_sha256=verify(args.freeze, args.signatures, args.authorization,
                                         args.trust, run_path),
                   authorization_sha256=sha(args.authorization), run_path=run_path)
    manifest_inventory = load(args.freeze / "deployment/inventory.json")
    schedule, tasks = load_schedule(args.freeze / "fixture")
    run.mkdir(parents=True, exist_ok=True)
    with (run / "runner.local.lock").open("ab") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        closure = run / "terminal.json"
        if closure.exists() and not load(closure)["complete"]:
            raise ValueError("This campaign was closed as abandoned")
        if args.command == "resume" and not (run / JOURNAL).exists():
            raise ValueError("No local journal to resume")
        ledger = Ledger(run / JOURNAL, schedule, tasks, binding)
        cp = Checkpoints(run, args.remote, CHECKPOINT_REF)
        cp.verify_prior(run / JOURNAL)
        started, initial = time.monotonic(), len(ledger.done)
        status, detail = "failed", None
        if ledger.sequence == 0:
            ledger.event("start")
        try:
            ledger.recover()
            if len(ledger.done) < TOTAL:
                progress(run, ledger, "starting_server", started, initial)
                if inventory(args.server, args.model, run) != manifest_inventory:
                    raise ValueError("Local runtime inventory differs from the frozen inventory")
                template = load(args.freeze / "deployment/token_budget.json")["template_sha256"]
                collect_schedule(args, run, ledger, cp, started, initial, template)
            status = "complete"
        except (Exception, KeyboardInterrupt) as exc:
            status = "blocked_ambiguous" if ledger.open and ledger.open[1] != "intent" else "interrupted"
            detail = str(exc) or type(exc).__name__
            raise
        finally:
            progress(run, ledger, status, started, initial, detail)
            try:
                cp.save(len(ledger.done), force=True)
            except (subprocess.SubprocessError, OSError) as error:
                if status == "complete":
                    raise
                print(f"Final checkpoint failed. Journal remains on disk. {error}", flush=True)
        if not cp.pushed:
            progress(run, ledger, "complete_push_pending", started, initial,
                     "responses saved and committed locally")
            raise RuntimeError("Responses are complete and committed locally. Resume to retry the final push.")


def stream(run, follow):
    previous = None
    while True:
        path = run / "progress.json"
        if path.exists():
            saved = path.read_bytes()
            if saved != previous:
                result = json.loads(saved)
                output(result)
                previous = saved
        elif previous is None:
            print(f"Waiting for progress at {path}", flush=True)
            previous = b""
        if not follow:
            return
        time.sleep(1)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    for name in ("run", "resume"):
        run = commands.add_parser(name)
        for flag in ("freeze", "signatures", "authorization", "trust", "out"):
            run.add_argument("--" + flag, type=Path, required=True)
        run.add_argument("--remote", default="origin")
        deployment_args(run)
    view = commands.add_parser("stream")
    view.add_argument("--out", type=Path, required=True)
    view.add_argument("--once", action="store_true")
    args = cli.parse_args()
    if args.command == "stream":
        stream(args.out, not args.once)
    else:
        def interrupted(_signum, _frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, interrupted)
        collect(args)


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        print(f"Cohort 029 stopped: {error or type(error).__name__}", file=sys.stderr, flush=True)
        raise SystemExit(1) from error
