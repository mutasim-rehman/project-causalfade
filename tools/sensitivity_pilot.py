"""Prepare, validate, run/resume and analyze the development sensitivity pilot."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from causalfade.sensitivity import (analyze_rows, cluster_interval, competence, describe,
                                   digest, generate, read_jsonl, score_records, validate,
                                   write_json)
from run_direct_pilot import request


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source_hashes():
    return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in (
        Path(__file__).resolve(), ROOT / "causalfade/sensitivity.py",
        ROOT / "causalfade/worlds.py", ROOT / "tools/run_direct_pilot.py")}


def load_run(directory, dataset, require_complete=True):
    directory, dataset = Path(directory), Path(dataset)
    if directory.with_name(directory.name + ".lock").exists():
        raise ValueError("Run is locked by a writer; wait for completion or inspect a stale lock")
    validate(dataset)
    config = load(directory / "config.json")
    if config["dataset_manifest_sha256"] != digest(dataset / "manifest.json"):
        raise ValueError("Run belongs to a different fixture")
    tasks = read_jsonl(dataset / "public_tasks.jsonl")
    if load(directory / "schedule.json") != tasks:
        raise ValueError("Run schedule differs from frozen public tasks")
    raw = read_jsonl(directory / "raw_responses.jsonl")
    rows = score_records(read_jsonl(dataset / "oracle_truth.jsonl"), raw)
    if require_complete and (load(directory / "status.json")["status"] != "success" or
                             not all(r["completed"] for r in rows)):
        raise ValueError(f"Run is not complete/successful: {directory}")
    if require_complete and config["source_sha256"] != source_hashes():
        raise ValueError("Run code differs from current analysis; preserve it and document an amendment")
    return config, rows


def check_reference(directory, dataset):
    config, rows = load_run(directory, dataset)
    if config["role"] != "reference":
        raise ValueError("Comparison gate requires a reference-role run")
    gate = competence(rows, load(Path(dataset) / "manifest.json")["gate"])
    if not gate["passed"]:
        raise ValueError("Reference competence gate failed; retain the screen and revise on new development data")
    return {"config_sha256": digest(Path(directory) / "config.json"),
            "raw_sha256": digest(Path(directory) / "raw_responses.jsonl"),
            "model_sha256": config["model_sha256"], "gate": gate}


def run(args):
    # A sibling lock also protects creation/resume checks before the run
    # directory exists. A crashed process leaves a visible lock for inspection.
    out = args.out.resolve()
    lock = out.with_name(out.name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError(f"Exclusive run lock exists: {lock}; inspect its process before removing a stale lock") from error
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"pid": os.getpid(), "created_utc": now()}, stream)
        return _run(args)
    finally:
        lock.unlink()


def _run(args):
    dataset, out = args.dataset.resolve(), args.out.resolve()
    validate(dataset)
    if args.threads < 1 or args.max_tokens < 1 or args.max_seconds <= 0 or args.request_timeout <= 0:
        raise ValueError("Threads, tokens and timing budgets must be positive")
    if not args.server.is_file() or not args.model.is_file():
        raise ValueError("Explicit existing llama-server and model paths are required")
    if args.role == "comparison" and not args.reference_run:
        raise ValueError("Comparison requires --reference-run; the competence gate cannot be bypassed")
    reference = check_reference(args.reference_run, dataset) if args.role == "comparison" else None
    if args.role == "reference" and args.reference_run:
        raise ValueError("A reference-role run cannot itself have a reference prerequisite")
    tasks = read_jsonl(dataset / "public_tasks.jsonl")
    truth = read_jsonl(dataset / "oracle_truth.jsonl")
    started = time.monotonic()
    deadline = started + args.max_seconds
    config = {"version": "sensitivity-run-v1", "classification": "development_only",
              "role": args.role, "dataset": str(dataset),
              "dataset_manifest_sha256": digest(dataset / "manifest.json"),
              "model": str(args.model.resolve()), "model_sha256": digest(args.model),
              "server": str(args.server.resolve()), "server_sha256": digest(args.server),
              "threads": args.threads, "max_tokens": args.max_tokens, "seed": args.seed,
              "request_timeout": args.request_timeout, "source_sha256": source_hashes(),
              "reference": reference,
              "decoding": {"temperature": 0, "cache_prompt": False, "stream": False},
              "context": 2048, "gpu_layers": 0, "kv_precision": "f16",
              "failure_policy": "one persisted attempt per task; infrastructure failures abort; resume never replaces an attempt"}
    if reference and config["model_sha256"] == reference["model_sha256"]:
        raise ValueError("Comparison requires different weights from its reference")
    if args.resume:
        if load(out / "config.json") != config or load(out / "schedule.json") != tasks:
            raise ValueError("Resume configuration/schedule mismatch")
        records = read_jsonl(out / "raw_responses.jsonl")
        score_records(truth, records)  # rejects duplicates/unknown IDs before a server starts
    else:
        out.mkdir(parents=True, exist_ok=False)
        write_json(out / "config.json", config)
        write_json(out / "schedule.json", tasks)
        write_json(out / "dataset_manifest.json", load(dataset / "manifest.json"))
        (out / "raw_responses.jsonl").touch(exist_ok=False)
        records = []
    attempts = {r["task_id"] for r in records}
    pending = [t for t in tasks if t["task_id"] not in attempts]
    server = None
    status = "running"
    reason = None
    command = []
    def stop(_signum, _frame):
        raise KeyboardInterrupt
    previous_handler = signal.signal(signal.SIGTERM, stop)
    write_json(out / "status.json", {"status": status, "updated_utc": now(), "completed": len(records)})
    try:
        if pending:
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            command = [str(args.server.resolve()), "-m", str(args.model.resolve()),
                       "--host", "127.0.0.1", "--port", str(port), "-ngl", "0", "-c", "2048",
                       "-np", "1", "-t", str(args.threads), "--cache-type-k", "f16", "--cache-type-v", "f16"]
            with (out / "stdout.log").open("a", encoding="utf-8") as stdout, (out / "stderr.log").open("a", encoding="utf-8") as stderr:
                server = subprocess.Popen(command, stdout=stdout, stderr=stderr)
                startup_deadline = min(deadline, time.monotonic() + 180)
                while True:
                    if time.monotonic() >= startup_deadline:
                        raise TimeoutError("Server startup exceeded available budget")
                    if server.poll() is not None:
                        raise RuntimeError(f"Server exited: {server.returncode}")
                    try:
                        request(port, "/health")
                        break
                    except OSError:
                        time.sleep(.5)
                with (out / "raw_responses.jsonl").open("a", encoding="utf-8", newline="\n") as raw:
                    for task in pending:
                        if deadline - time.monotonic() < args.request_timeout:
                            status = "paused_budget"
                            break
                        record = {"task_id": task["task_id"], "started_utc": now()}
                        request_start = time.monotonic()
                        try:
                            record["response"] = request(port, "/v1/chat/completions", {
                                **config["decoding"], "seed": args.seed, "max_tokens": args.max_tokens,
                                "messages": [{"role": "user", "content": task["prompt"]}],
                            }, timeout=args.request_timeout)
                        except (Exception, KeyboardInterrupt) as error:
                            record["execution_error"] = repr(error)
                            raise
                        finally:
                            record["duration_seconds"] = time.monotonic() - request_start
                            raw.write(json.dumps(record, allow_nan=False) + "\n")
                            raw.flush()
                            os.fsync(raw.fileno())
                            records.append(record)
                        write_json(out / "status.json", {"status": "running", "updated_utc": now(),
                                                         "completed": len(records), "scheduled": len(tasks)})
        if status == "running":
            status = "failed" if any(r.get("execution_error") for r in records) else "success"
            if status == "failed":
                reason = "Persisted infrastructure-failed attempts require an explicit new run/amendment"
    except KeyboardInterrupt:
        status, reason = "interrupted", "Signal received; attempts retained"
    except Exception as error:
        status, reason = "failed", repr(error)
    finally:
        signal.signal(signal.SIGTERM, previous_handler)
        if server is not None and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
        rows = score_records(truth, records)
        write_json(out / "results.json", rows)
        write_json(out / "metrics.json", describe(rows))
        write_json(out / "gate_analysis.json", competence(rows, load(dataset / "manifest.json")["gate"]))
        write_json(out / "status.json", {"status": status, "reason": reason, "updated_utc": now(),
                                         "completed": len(records), "scheduled": len(tasks)})
        with (out / "sessions.jsonl").open("a", encoding="utf-8", newline="\n") as history:
            history.write(json.dumps({"end_utc": now(), "python": platform.python_version(),
                                      "numpy": __import__("numpy").__version__, "platform": platform.platform(),
                                      "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                                      "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)),
                                      "command": command, "duration_seconds": time.monotonic() - started,
                                      "budget_seconds": args.max_seconds, "status": status}) + "\n")
    return 0 if status == "success" else 2


def analysis(dataset, reference, comparison, out):
    config, rows = load_run(reference, dataset)
    if config["role"] != "reference":
        raise ValueError("Expected reference-role run")
    output = {"classification": "development_only", "reference": analyze_rows(rows),
              "reference_gate": competence(rows, load(Path(dataset) / "manifest.json")["gate"]),
              "dataset_manifest_sha256": digest(Path(dataset) / "manifest.json"),
              "source_sha256": source_hashes()}
    if comparison:
        qconfig, qrows = load_run(comparison, dataset)
        ref = check_reference(reference, dataset)
        if qconfig["role"] != "comparison" or qconfig["reference"] != ref:
            raise ValueError("Comparison provenance does not match the supplied gated reference")
        if config["model_sha256"] == qconfig["model_sha256"]:
            raise ValueError("Reference and comparison use identical weights")
        output["comparison"] = analyze_rows(qrows)
        by_id = {r["task_id"]: r for r in rows}
        deltas = defaultdict(list)
        for r in qrows:
            if r["task_type"] in ("causal", "noncausal"):
                deltas[(r["task_type"], r["family_id"])].append(r["correct"] - by_id[r["task_id"]]["correct"])
        output["comparison_minus_reference_accuracy"] = {
            kind: cluster_interval([sum(v) / len(v) for (k, _), v in deltas.items() if k == kind])
            for kind in ("causal", "noncausal")}
        families = sorted({r["family_id"] for r in rows})
        output["causal_minus_noncausal_precision_accuracy_interaction"] = cluster_interval([
            sum(deltas[("causal", f)]) / len(deltas[("causal", f)]) -
            sum(deltas[("noncausal", f)]) / len(deltas[("noncausal", f)]) for f in families])
    out = Path(out)
    if out.exists() or out.with_suffix(".md").exists():
        raise FileExistsError("Choose a new analysis path; reports are not overwritten")
    write_json(out, output)
    lines = ["# Sensitivity development pilot", "", "Development-only; no confirmatory inference.", "",
             f'Reference operational competence gate: {output["reference_gate"]["passed"]}.', ""]
    for name in ("reference", "comparison"):
        if name in output:
            lines.append(f"## {name.capitalize()}")
            lines.append("")
            for kind, cell in output[name]["by_task_type"].items():
                lines.append(f'- {kind}: {cell["correct"]}/{cell["scheduled"]} correct; {cell["valid"]} valid.')
            lines.extend(["", "Order effects (historical-first minus randomized-first accuracy):", ""])
            for key, effect in output[name]["historical_minus_randomized_accuracy"].items():
                lines.append(f'- {key}: {effect["estimate"]:+.3f}; family percentile 95% interval {effect["family_percentile_95"]}.')
            lines.append("")
    lines.extend(["See the companion JSON for SDT strata, empirical curves, strategy scores and paired contrasts.", "",
                  "SDT assumptions are unverified. Response-mapping/source-name allocation may be between families; consult the fixture manifest.",
                  "Two strengths do not establish a full psychophysical curve. Fixed strategy scores describe action agreement, not held-out model superiority.",
                  "Matched controls differ in instruction semantics. No latent-route, neural-mechanism or general quantization claim follows."])
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--out", type=Path, required=True)
    prepare.add_argument("--families", type=int, default=8)
    prepare.add_argument("--seed", type=int, default=20261114)
    prepare.add_argument("--cross-mappings", action="store_true")
    valid = commands.add_parser("validate")
    valid.add_argument("--dataset", type=Path, required=True)
    execute = commands.add_parser("run")
    for field in ("server", "model", "dataset", "out"):
        execute.add_argument(f"--{field}", type=Path, required=True)
    execute.add_argument("--role", choices=("reference", "comparison"), required=True)
    execute.add_argument("--reference-run", type=Path)
    execute.add_argument("--resume", action="store_true")
    execute.add_argument("--threads", type=int, default=8)
    execute.add_argument("--max-tokens", type=int, default=64)
    execute.add_argument("--seed", type=int, default=20261114)
    execute.add_argument("--max-seconds", type=float, default=7200)
    execute.add_argument("--request-timeout", type=float, default=180)
    analyze = commands.add_parser("analyze")
    analyze.add_argument("--dataset", type=Path, required=True)
    analyze.add_argument("--reference", type=Path, required=True)
    analyze.add_argument("--comparison", type=Path)
    analyze.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = generate(args.out, args.families, args.seed, args.cross_mappings)
    elif args.command == "validate":
        result = validate(args.dataset)
    elif args.command == "run":
        sys.exit(run(args))
    else:
        analysis(args.dataset, args.reference, args.comparison, args.out)
        result = {"analysis": str(args.out), "report": str(args.out.with_suffix(".md"))}
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
