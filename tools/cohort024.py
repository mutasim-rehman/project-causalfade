"""Cohort 024: fixture, fail-closed model inventory, resumable matrix, analysis."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from causalfade.matrix024 import prepare, validate, score
from causalfade.sensitivity import cluster_interval, digest, read_jsonl, write_json
from run_direct_pilot import request

SOURCE_FILES = ("causalfade/matrix024.py", "causalfade/measurement_audit.py", "causalfade/worlds.py",
                "causalfade/sensitivity.py", "tools/cohort024.py", "tools/run_direct_pilot.py")
PRECISIONS = ("F16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q3_K_M", "Q2_K")


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def source_hashes():
    return {name: digest(ROOT / name) for name in SOURCE_FILES}


def model_inventory(path):
    spec = load(path)
    if not isinstance(spec, list) or not spec:
        raise ValueError("Model specification must be a nonempty JSON array")
    seen = set()
    inventory = []
    for entry in spec:
        model_id = entry["id"]
        lineage, precision = entry["lineage"], entry["precision"]
        if not model_id.replace("_", "").isalnum() or model_id in seen or precision not in PRECISIONS:
            raise ValueError("Invalid/duplicate ID or unsupported precision: " + model_id)
        seen.add(model_id)
        model = Path(entry["path"]).expanduser().resolve()
        if not model.is_file() or not entry.get("source_revision"):
            raise ValueError("Missing model file or source_revision: " + model_id)
        actual = digest(model)
        if entry.get("sha256") and entry["sha256"] != actual:
            raise ValueError("Model hash mismatch: " + model_id)
        inventory.append({"id": model_id, "lineage": lineage, "precision": precision,
                          "source_revision": entry["source_revision"], "path": str(model),
                          "sha256": actual, "bytes": model.stat().st_size})
    by_lineage = defaultdict(list)
    for entry in inventory:
        by_lineage[entry["lineage"]].append(entry)
    for lineage, entries in by_lineage.items():
        if len({e["precision"] for e in entries}) != len(entries):
            raise ValueError("Duplicate precision within lineage: " + lineage)
        if len({e["source_revision"] for e in entries}) != 1:
            raise ValueError("Precision variants need one source revision: " + lineage)
        if "F16" not in {e["precision"] for e in entries}:
            raise ValueError("Each lineage requires an F16 reference: " + lineage)
    return inventory


def build_models(args):
    """Convert pinned F16 GGUF sources; never silently adopt an unrelated quant."""
    sources = load(args.sources)
    if not isinstance(sources, list) or not sources:
        raise ValueError("Sources must be a nonempty JSON array")
    levels = [x.strip() for x in args.levels.split(",")]
    if not levels or len(set(levels)) != len(levels) or any(x == "F16" or x not in PRECISIONS for x in levels):
        raise ValueError("Invalid quantization levels")
    quantizer = Path(args.quantizer).resolve()
    if not quantizer.is_file():
        raise ValueError("Quantizer binary missing")
    quant_hash = digest(quantizer)
    output_root = Path(args.out).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    inventory = []
    seen = set()
    for src in sources:
        lineage = src["lineage"]
        if not lineage.replace("_", "").isalnum() or lineage in seen or not src.get("source_revision"):
            raise ValueError("Invalid/duplicate lineage or missing source revision")
        seen.add(lineage)
        f16 = Path(src["path"]).expanduser().resolve()
        if not f16.is_file() or f16.suffix.lower() != ".gguf":
            raise ValueError("Source must be an existing F16 GGUF: " + lineage)
        with f16.open("rb") as stream:
            if stream.read(4) != b"GGUF":
                raise ValueError("Source is not a GGUF file: " + lineage)
        base_hash = digest(f16)
        if src.get("sha256") and src["sha256"] != base_hash:
            raise ValueError("Source hash mismatch: " + lineage)
        inventory.append({"id": lineage + "_f16", "lineage": lineage, "precision": "F16",
                          "path": str(f16), "source_revision": src["source_revision"], "sha256": base_hash})
        for precision in levels:
            target = output_root / f"{lineage}_{precision}.gguf"
            sidecar = output_root / f"{lineage}_{precision}.provenance.json"
            provenance = {"source_sha256": base_hash, "source_revision": src["source_revision"],
                          "quantizer_sha256": quant_hash, "precision": precision}
            if target.exists() or sidecar.exists():
                if not target.is_file() or not sidecar.is_file() or load(sidecar) != {**provenance, "output_sha256": digest(target)}:
                    raise ValueError(f"Existing quant lacks matching provenance: {target}")
                print(f"REUSE {target}", flush=True)
            else:
                if shutil.disk_usage(output_root).free < f16.stat().st_size * 1.5:
                    raise OSError(f"Insufficient free disk for safe conversion: {precision} {lineage}")
                print(f"QUANTIZE {lineage} {precision} -> {target}", flush=True)
                with (output_root / f"{lineage}_{precision}.quantize.log").open("w", encoding="utf-8") as log:
                    completed = subprocess.run([str(quantizer), str(f16), str(target), precision],
                                               stdout=log, stderr=subprocess.STDOUT, check=False)
                if completed.returncode != 0 or not target.is_file():
                    raise RuntimeError(f"Quantization failed ({completed.returncode}); inspect log and partial target: {target}")
                write_json(sidecar, {**provenance, "output_sha256": digest(target)})
            inventory.append({"id": f"{lineage}_{precision.lower()}", "lineage": lineage, "precision": precision,
                              "path": str(target), "source_revision": src["source_revision"], "sha256": digest(target)})
    if args.models_out.exists():
        raise FileExistsError(args.models_out)
    write_json(args.models_out, inventory)
    print(f"INVENTORY {len(inventory)} arms -> {args.models_out}", flush=True)


def freeze(args):
    dataset = Path(args.dataset).resolve()
    validate(dataset)
    inventory = model_inventory(args.models)
    server = Path(args.server).resolve()
    if not server.is_file():
        raise ValueError("Server binary missing")
    plan = {"classification": "development_only_measurement_screen", "created_utc": now(),
            "dataset": str(dataset), "dataset_hashes": {name: digest(dataset / name) for name in ("manifest.json", "public_tasks.jsonl", "oracle_truth.jsonl")},
            "source_hashes": source_hashes(), "server": str(server), "server_sha256": digest(server),
            "models": inventory, "runtime": {"threads": args.threads, "context": 2048, "gpu_layers": 0,
            "kv_precision": "f16", "max_tokens": 64, "temperature": 0, "seed": 20261120, "request_timeout": 180},
            "analysis_policy": "All scheduled tasks count; separate source/decision; family intervals; no model selection by outcome. F16 references before quantized arms; qualification is descriptive development screen.",
            "stopping_policy": "Run every listed arm; preserve failures; do not replace attempts or alter frozen plan."}
    out = Path(args.plan)
    if out.exists():
        raise FileExistsError(out)
    write_json(out, plan)
    print(f"FROZEN {out} | {len(inventory)} arms | {len(read_jsonl(dataset/'public_tasks.jsonl'))} tasks/arm", flush=True)


def check_plan(plan):
    dataset = Path(plan["dataset"])
    validate(dataset)
    for name, expected in plan["dataset_hashes"].items():
        if digest(dataset / name) != expected:
            raise ValueError("Dataset changed after freeze: " + name)
    if source_hashes() != plan["source_hashes"]:
        raise ValueError("Source changed after freeze; preserve plan and amend separately")
    if digest(plan["server"]) != plan["server_sha256"]:
        raise ValueError("Server hash changed")
    for model in plan["models"]:
        if digest(model["path"]) != model["sha256"]:
            raise ValueError("Model hash changed: " + model["id"])
    return dataset


def arm_order(models):
    # All references first, then other precisions, stable inside each group.
    return sorted(models, key=lambda m: (m["precision"] != "F16", m["lineage"], PRECISIONS.index(m["precision"])))


def run_arm(plan, model, out, budget, progress_every):
    dataset = Path(plan["dataset"])
    tasks = read_jsonl(dataset / "public_tasks.jsonl")
    truth = read_jsonl(dataset / "oracle_truth.jsonl")
    out = Path(out)
    lock = out.with_name(out.name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"Writer lock exists: {lock}; inspect process before removing a stale lock") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "created_utc": now()}, f)
        config = {"model": model, "dataset_hash": plan["dataset_hashes"]["manifest.json"],
                  "server_sha256": plan["server_sha256"], "source_hashes": plan["source_hashes"],
                  "runtime": plan["runtime"]}
        if out.exists():
            if load(out / "config.json") != config or load(out / "schedule.json") != tasks:
                raise ValueError("Resume configuration/schedule mismatch: " + model["id"])
            previous = load(out / "status.json")["status"]
            if previous == "success":
                existing = read_jsonl(out / "raw_responses.jsonl")
                if len(existing) != len(tasks) or score(truth, existing) != load(out / "results.json"):
                    raise ValueError("Completed arm failed raw-result audit: " + model["id"])
                return "success"
            if previous not in ("paused_budget", "interrupted"):
                raise ValueError("Prior run requires inspection/amendment: " + previous)
            records = read_jsonl(out / "raw_responses.jsonl")
            score(truth, records)
            if any("execution_error" in r for r in records):
                raise ValueError("Persisted failed attempt cannot be retried")
        else:
            out.mkdir()
            write_json(out / "config.json", config)
            write_json(out / "schedule.json", tasks)
            (out / "raw_responses.jsonl").touch(exist_ok=False)
            records = []
        attempted = {r["task_id"] for r in records}
        pending = [t for t in tasks if t["task_id"] not in attempted]
        started = time.monotonic()
        status, reason, server = "running", None, None
        command = []
        write_json(out / "status.json", {"status": status, "completed": len(records), "scheduled": len(tasks)})
        def stop(_signum, _frame):
            raise KeyboardInterrupt
        old_handler = signal.signal(signal.SIGTERM, stop)
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
            command = [plan["server"], "-m", model["path"], "--host", "127.0.0.1", "--port", str(port),
                       "-ngl", "0", "-c", "2048", "-np", "1", "-t", str(plan["runtime"]["threads"]),
                       "--cache-type-k", "f16", "--cache-type-v", "f16"]
            with (out / "stdout.log").open("a", encoding="utf-8") as stdout, (out / "stderr.log").open("a", encoding="utf-8") as stderr:
                server = subprocess.Popen(command, stdout=stdout, stderr=stderr)
                while True:
                    if server.poll() is not None: raise RuntimeError(f"Server exited: {server.returncode}")
                    if time.monotonic() - started > 180: raise TimeoutError("Server startup timeout")
                    try:
                        request(port, "/health"); break
                    except OSError:
                        time.sleep(.5)
                props = request(port, "/props", timeout=10)
                if not isinstance(props, dict) or not props:
                    raise ValueError("Server did not provide model properties")
                write_json(out / "server_props.json", props)
                with (out / "raw_responses.jsonl").open("a", encoding="utf-8", newline="\n") as raw:
                    for task in pending:
                        if budget - (time.monotonic() - started) < plan["runtime"]["request_timeout"]:
                            status = "paused_budget"; break
                        record = {"task_id": task["task_id"], "started_utc": now()}
                        tick = time.monotonic()
                        try:
                            record["response"] = request(port, "/v1/chat/completions", {
                                "temperature": 0, "cache_prompt": False, "stream": False,
                                "seed": plan["runtime"]["seed"], "max_tokens": plan["runtime"]["max_tokens"],
                                "messages": [{"role": "user", "content": task["prompt"]}]},
                                timeout=plan["runtime"]["request_timeout"])
                        except BaseException as exc:
                            record["execution_error"] = repr(exc)
                            raise
                        finally:
                            record["duration_seconds"] = time.monotonic() - tick
                            raw.write(json.dumps(record, allow_nan=False) + "\n"); raw.flush(); os.fsync(raw.fileno())
                            records.append(record)
                        n = len(records)
                        write_json(out / "status.json", {"status": "running", "completed": n, "scheduled": len(tasks), "updated_utc": now()})
                        if n % progress_every == 0 or n == len(tasks):
                            print(f"LIVE {model['id']} {n}/{len(tasks)} ({n/len(tasks):.1%}) last={record['duration_seconds']:.1f}s", flush=True)
            if status == "running": status = "success"
        except KeyboardInterrupt:
            status, reason = "interrupted", "Signal received; attempts retained"
        except Exception as exc:
            status, reason = "failed", repr(exc)
        finally:
            signal.signal(signal.SIGTERM, old_handler)
            if server is not None and server.poll() is None:
                server.terminate()
                try: server.wait(timeout=10)
                except subprocess.TimeoutExpired: server.kill(); server.wait()
            rows = score(truth, records)
            write_json(out / "results.json", rows)
            write_json(out / "metrics.json", {"scheduled": len(rows), "completed": sum(r["completed"] for r in rows),
                       "valid": sum(r["valid_answer"] for r in rows), "correct": sum(r["correct"] for r in rows)})
            write_json(out / "status.json", {"status": status, "reason": reason, "completed": len(records),
                       "scheduled": len(tasks), "updated_utc": now()})
            with (out / "sessions.jsonl").open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps({"end_utc": now(), "python": platform.python_version(), "platform": platform.platform(),
                                    "command": command, "duration_seconds": time.monotonic()-started, "status": status}) + "\n")
        print(f"END {model['id']} {status} {len(records)}/{len(tasks)} {reason or ''}", flush=True)
        return status
    finally:
        lock.unlink()


def run_all(args):
    plan = load(args.plan)
    check_plan(plan)
    if args.max_seconds <= 180 or args.progress_every < 1:
        raise ValueError("Budget must exceed request timeout; progress interval must be positive")
    for model in arm_order(plan["models"]):
        if args.arm and model["id"] != args.arm: continue
        status = run_arm(plan, model, Path(args.out) / model["id"], args.max_seconds, args.progress_every)
        if status != "success": return 2
    return 0


def analysis(args):
    plan = load(args.plan); dataset = check_plan(plan)
    truth = read_jsonl(dataset / "oracle_truth.jsonl")
    output = {"classification": "development_only", "plan_sha256": digest(args.plan), "arms": {}, "paired_precision": {}}
    rows_by_id = {}
    for model in arm_order(plan["models"]):
        out = Path(args.runs) / model["id"]
        if out.with_name(out.name+".lock").exists() or load(out / "status.json")["status"] != "success":
            raise ValueError("Incomplete or locked arm: " + model["id"])
        expected_config = {"model": model, "dataset_hash": plan["dataset_hashes"]["manifest.json"],
                           "server_sha256": plan["server_sha256"], "source_hashes": plan["source_hashes"],
                           "runtime": plan["runtime"]}
        if load(out / "config.json") != expected_config or load(out / "schedule.json") != read_jsonl(dataset / "public_tasks.jsonl"):
            raise ValueError("Model configuration mismatch: " + model["id"])
        rows = score(truth, read_jsonl(out / "raw_responses.jsonl"))
        if any(not r["completed"] for r in rows) or rows != load(out / "results.json"):
            raise ValueError("Raw/result mismatch: " + model["id"])
        rows_by_id[model["id"]] = {r["task_id"]: r for r in rows}
        cells = defaultdict(list)
        strata = defaultdict(list)
        for r in rows:
            cells["|".join((r["task_type"], r["contract"], "beneficial" if r["causal_positive"] else "harmful", r["answer_order"]))].append(r)
            if r["task_type"] in ("decision", "noncausal_control", "source_selection"):
                for factor in ("presentation_order", "randomized_name", "condition"):
                    strata["|".join((r["task_type"], r["contract"], factor, str(r[factor]), "beneficial" if r["causal_positive"] else "harmful"))].append(r)
        def summarize(group):
            valid = [r for r in group if r["valid_answer"]]
            families = defaultdict(list)
            for r in group: families[r["family_id"]].append(r["correct"])
            return {"correct": sum(r["correct"] for r in group), "n": len(group), "valid": len(valid),
                    "family_accuracy_interval": cluster_interval([mean(v) for v in families.values()]),
                    "activation": sum(r["answer"] in ("activate", "X=1") for r in valid) / len(valid)
                    if group[0]["task_type"] in ("decision", "noncausal_control", "randomized_only") and valid else None}
        baseline = {(r["family_id"], r["base_id"], r["contract"]): r for r in rows if r["task_type"] == "randomized_only"}
        paired_gap = {}
        for contract in ("semantic", "neutral"):
            for direction in (0, 1):
                by_family = defaultdict(list)
                for r in rows:
                    if r["task_type"] == "decision" and r["contract"] == contract and r["causal_positive"] == direction:
                        by_family[r["family_id"]].append(baseline[(r["family_id"], r["base_id"], contract)]["correct"] - r["correct"])
                paired_gap[f"{contract}|{direction}"] = cluster_interval([mean(v) for v in by_family.values()])
        output["arms"][model["id"]] = {"lineage": model["lineage"], "precision": model["precision"],
            "valid": sum(r["valid_answer"] for r in rows), "scheduled": len(rows),
            "cells": {key: summarize(group) for key, group in sorted(cells.items())},
            "strata": {key: summarize(group) for key, group in sorted(strata.items())},
            "randomized_only_minus_two_source": paired_gap}
    refs = {m["lineage"]: m for m in plan["models"] if m["precision"] == "F16"}
    for model in plan["models"]:
        if model["precision"] == "F16": continue
        ref = rows_by_id[refs[model["lineage"]]["id"]]; other = rows_by_id[model["id"]]
        by = defaultdict(list)
        for task_id, r in other.items():
            if r["task_type"] in ("decision", "noncausal_control"):
                by[(r["task_type"], r["contract"], r["causal_positive"], r["family_id"])].append(r["correct"]-ref[task_id]["correct"])
        estimates = {}
        for kind in ("decision", "noncausal_control"):
            for contract in ("semantic", "neutral"):
                for direction in (0, 1):
                    vals = [mean(by[(kind, contract, direction, f)]) for f in sorted({r["family_id"] for r in truth})]
                    estimates[f"{kind}|{contract}|{direction}"] = cluster_interval(vals)
        output["paired_precision"][model["id"]] = {"reference": refs[model["lineage"]]["id"], "effects": estimates}
    target = Path(args.out)
    if target.exists(): raise FileExistsError(target)
    write_json(target, output)
    print(f"ANALYZED {len(output['arms'])} arms -> {target}", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("prepare"); a.add_argument("--dataset", type=Path, required=True); a.add_argument("--seed", type=int, default=20261120)
    a = sub.add_parser("validate"); a.add_argument("--dataset", type=Path, required=True)
    a = sub.add_parser("freeze"); a.add_argument("--dataset", type=Path, required=True); a.add_argument("--models", type=Path, required=True); a.add_argument("--server", type=Path, required=True); a.add_argument("--plan", type=Path, required=True); a.add_argument("--threads", type=int, default=8)
    a = sub.add_parser("build-models"); a.add_argument("--sources", type=Path, required=True); a.add_argument("--quantizer", type=Path, required=True); a.add_argument("--out", type=Path, required=True); a.add_argument("--models-out", type=Path, required=True); a.add_argument("--levels", default="Q8_0,Q6_K,Q5_K_M,Q4_K_M,Q3_K_M,Q2_K")
    a = sub.add_parser("run-all"); a.add_argument("--plan", type=Path, required=True); a.add_argument("--out", type=Path, required=True); a.add_argument("--arm"); a.add_argument("--max-seconds", type=float, default=7200); a.add_argument("--progress-every", type=int, default=20)
    a = sub.add_parser("analyze"); a.add_argument("--plan", type=Path, required=True); a.add_argument("--runs", type=Path, required=True); a.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("status"); a.add_argument("--plan", type=Path, required=True); a.add_argument("--runs", type=Path, required=True)
    args = p.parse_args()
    if args.command == "prepare": print(json.dumps(prepare(args.dataset, args.seed), indent=2))
    elif args.command == "validate": print(json.dumps(validate(args.dataset), indent=2))
    elif args.command == "freeze": freeze(args)
    elif args.command == "build-models": build_models(args)
    elif args.command == "run-all": sys.exit(run_all(args))
    elif args.command == "analyze": analysis(args)
    else:
        plan = load(args.plan)
        for m in arm_order(plan["models"]):
            path = args.runs / m["id"] / "status.json"
            print(m["id"], load(path) if path.exists() else "not started", flush=True)


if __name__ == "__main__": main()
