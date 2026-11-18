"""Analyze the archived cohort 024 matrix without requiring lab-local model weights.

Post-inference descriptive analysis. The frozen runner, fixture, plan, and scores
are not changed. Every scheduled response remains in the denominator.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from statistics import NormalDist, mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from causalfade.matrix024 import score, validate
from causalfade.sensitivity import cluster_interval, digest, read_jsonl, write_json

SOURCE_FILES = ("causalfade/matrix024.py", "causalfade/measurement_audit.py",
                "causalfade/worlds.py", "causalfade/sensitivity.py",
                "tools/cohort024.py", "tools/run_direct_pilot.py")
DECISION_KINDS = ("decision", "noncausal_control", "randomized_only")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def first_option(row):
    if row["task_type"] == "source_selection":
        canonical = "A"
        reverse = "B"
    elif row["task_type"] == "numerical_control":
        canonical, reverse = "X=0", "X=1"
    elif row["contract"] == "neutral":
        canonical, reverse = "X=1", "X=0"
    else:
        canonical, reverse = "activate", "leave_off"
    return canonical if row["answer_order"] == "canonical" else reverse


def summary(rows):
    valid = [r for r in rows if r["valid_answer"]]
    result = {"scheduled": len(rows), "completed": sum(r["completed"] for r in rows),
              "valid": len(valid), "correct": sum(r["correct"] for r in rows),
              "accuracy": sum(r["correct"] for r in rows) / len(rows) if rows else None,
              "validity": len(valid) / len(rows) if rows else None}
    if rows and rows[0]["task_type"] in DECISION_KINDS:
        result["activation_valid"] = sum(r["answer"] in ("activate", "X=1") for r in valid) / len(valid) if valid else None
    if rows:
        result["first_option_valid"] = sum(r["answer"] == first_option(r) for r in valid) / len(valid) if valid else None
        by_family = defaultdict(list)
        for row in rows:
            by_family[row["family_id"]].append(row["correct"])
        result["family_accuracy_interval"] = cluster_interval([mean(x) for _, x in sorted(by_family.items())])
    return result


def family_effect(pairs):
    by_family = defaultdict(list)
    for family, value in pairs:
        by_family[family].append(value)
    return cluster_interval([mean(x) for _, x in sorted(by_family.items())])


def signal_detection(rows):
    """Descriptive binary-choice coordinates; invalid outputs are not recoded as no."""
    valid = [r for r in rows if r["valid_answer"]]
    signal = [r for r in valid if r["causal_positive"]]
    noise = [r for r in valid if not r["causal_positive"]]
    hits = sum(r["answer"] in ("activate", "X=1") for r in signal)
    false_alarms = sum(r["answer"] in ("activate", "X=1") for r in noise)
    out = {"scheduled": len(rows), "valid": len(valid), "signal_valid": len(signal),
           "noise_valid": len(noise), "hits": hits, "false_alarms": false_alarms,
           "boundary_correction": "(count+0.5)/(valid_direction_n+1)",
           "d_prime": None, "criterion": None}
    if signal and noise:
        zh = NormalDist().inv_cdf((hits + .5) / (len(signal) + 1))
        zf = NormalDist().inv_cdf((false_alarms + .5) / (len(noise) + 1))
        out["d_prime"] = zh - zf
        out["criterion"] = -.5 * (zh + zf)
    return out


def analyze(base):
    base = Path(base)
    plan_path = base / "frozen_lab_plan.json"
    plan = load(plan_path)
    dataset = base / "input"
    validate(dataset)
    for name, expected in plan["dataset_hashes"].items():
        if digest(dataset / name) != expected:
            raise ValueError("Frozen fixture hash mismatch: " + name)
    for name in SOURCE_FILES:
        if digest(ROOT / name) != plan["source_hashes"][name]:
            raise ValueError("Frozen source hash mismatch: " + name)
    public = read_jsonl(dataset / "public_tasks.jsonl")
    truth = read_jsonl(dataset / "oracle_truth.jsonl")
    model_ids = [m["id"] for m in plan["models"]]
    if len(model_ids) != 21 or len(set(model_ids)) != 21:
        raise ValueError("Expected complete 21-arm matrix")
    output = {"classification": "post_inference_archived_development_analysis",
              "plan_sha256": digest(plan_path), "fixture_manifest_sha256": digest(dataset / "manifest.json"),
              "source_hashes_match_frozen": True,
              "limitations": ["Lab-local model and server bytes are unavailable here; this verifies recorded hashes and archived outputs, not the underlying weight files.",
                              "Eight SCM families and three fixed checkpoints; family bootstrap intervals are descriptive and multiple contrasts are exploratory.",
                              "Threshold checks below reuse cohort 023 diagnostic criteria after collection; they are not a cohort 024 preregistered gate.",
                              "Invalid outputs count wrong in scheduled accuracy; activation and first-option rates condition on valid responses."],
              "audit": {}, "arms": {}, "paired_precision": {}}
    all_rows = {}
    all_raw_hashes = {}
    session_status = Counter()
    for model in plan["models"]:
        model_id = model["id"]
        path = base / "runs" / model_id
        if path.with_name(path.name + ".lock").exists():
            raise ValueError("Active/stale writer lock: " + model_id)
        status = load(path / "status.json")
        if status["status"] != "success" or status["completed"] != len(truth):
            raise ValueError("Incomplete arm: " + model_id)
        config = load(path / "config.json")
        expected = {"model": model, "dataset_hash": plan["dataset_hashes"]["manifest.json"],
                    "server_sha256": plan["server_sha256"], "source_hashes": plan["source_hashes"],
                    "runtime": plan["runtime"]}
        if config != expected or load(path / "schedule.json") != public:
            raise ValueError("Config/schedule mismatch: " + model_id)
        if not load(path / "server_props.json"):
            raise ValueError("Missing server properties: " + model_id)
        raw_path = path / "raw_responses.jsonl"
        all_raw_hashes[model_id] = digest(raw_path)
        raw = read_jsonl(raw_path)
        rows = score(truth, raw)
        if len(raw) != len(truth) or any(not r["completed"] for r in rows) or rows != load(path / "results.json"):
            raise ValueError("Raw/stored scoring mismatch: " + model_id)
        metrics = load(path / "metrics.json")
        if metrics != {"scheduled": len(rows), "completed": len(rows),
                       "valid": sum(r["valid_answer"] for r in rows), "correct": sum(r["correct"] for r in rows)}:
            raise ValueError("Stored metric mismatch: " + model_id)
        all_rows[model_id] = rows
        for session in read_jsonl(path / "sessions.jsonl"):
            session_status[session["status"]] += 1
        groups = defaultdict(list)
        for row in rows:
            keys = ["all", row["task_type"], f'{row["task_type"]}|{row["contract"]}',
                    f'{row["task_type"]}|{row["contract"]}|direction={row["causal_positive"]}',
                    f'{row["task_type"]}|{row["contract"]}|answer_order={row["answer_order"]}']
            if row["task_type"] in ("decision", "noncausal_control", "source_selection"):
                keys += [f'{row["task_type"]}|{row["contract"]}|evidence_order={row["presentation_order"]}',
                         f'{row["task_type"]}|{row["contract"]}|agreement={row["condition"]}',
                         f'{row["task_type"]}|{row["contract"]}|randomized_name={row["randomized_name"]}']
            for key in keys:
                groups[key].append(row)
        cells = {key: summary(group) for key, group in sorted(groups.items())}
        invalid = [r for r in rows if not r["valid_answer"]]
        invalid_by = {"task_contract": dict(sorted(Counter(f'{r["task_type"]}|{r["contract"]}' for r in invalid).items())),
                      "finish_reason": dict(sorted(Counter(str(r["finish_reason"]) for r in invalid).items()))}
        # This is a post-collection diagnostic using the earlier cohort 023 thresholds.
        checks = {"validity_at_least_95pct": cells["all"]["validity"] >= .95,
                  "source_A_at_least_75pct": cells["source_selection|semantic|randomized_name=A"]["accuracy"] >= .75,
                  "source_B_at_least_75pct": cells["source_selection|semantic|randomized_name=B"]["accuracy"] >= .75}
        for direction in (0, 1):
            checks[f"randomized_only_semantic_direction_{direction}_at_least_75pct"] = cells[f"randomized_only|semantic|direction={direction}"]["accuracy"] >= .75
            checks[f"numeric_direction_{direction}_at_least_75pct"] = cells[f"numerical_control|semantic|direction={direction}"]["accuracy"] >= .75
            for contract in ("semantic", "neutral"):
                checks[f"noncausal_{contract}_direction_{direction}_at_least_75pct"] = cells[f"noncausal_control|{contract}|direction={direction}"]["accuracy"] >= .75
        baseline = {(r["family_id"], r["base_id"], r["contract"]): r for r in rows if r["task_type"] == "randomized_only"}
        matched = {(r["family_id"], r["stem_id"], r["contract"]): r for r in rows if r["task_type"] == "noncausal_control"}
        contrasts = {}
        for contract in ("semantic", "neutral"):
            for direction in (0, 1):
                decisions = [r for r in rows if r["task_type"] == "decision" and r["contract"] == contract and r["causal_positive"] == direction]
                contrasts[f"randomized_only_minus_two_source|{contract}|{direction}"] = family_effect([
                    (r["family_id"], baseline[(r["family_id"], r["base_id"], contract)]["correct"] - r["correct"]) for r in decisions])
                contrasts[f"noncausal_minus_causal|{contract}|{direction}"] = family_effect([
                    (r["family_id"], matched[(r["family_id"], r["stem_id"], contract)]["correct"] - r["correct"]) for r in decisions])
        detection = {}
        for kind in DECISION_KINDS:
            for contract in ("semantic", "neutral"):
                detection[f"{kind}|{contract}"] = signal_detection([
                    r for r in rows if r["task_type"] == kind and r["contract"] == contract])
        output["arms"][model_id] = {"lineage": model["lineage"], "precision": model["precision"],
                                    "raw_sha256": all_raw_hashes[model_id], "cells": cells,
                                    "invalid": invalid_by, "diagnostic_checks": checks,
                                    "all_diagnostic_checks_pass": all(checks.values()),
                                    "paired_within_arm": contrasts, "signal_detection": detection}
    refs = {m["lineage"]: m["id"] for m in plan["models"] if m["precision"] == "F16"}
    for model in plan["models"]:
        if model["precision"] == "F16":
            continue
        model_id = model["id"]
        reference_id = refs[model["lineage"]]
        ref = {r["task_id"]: r for r in all_rows[reference_id]}
        rows = all_rows[model_id]
        qcontrols = {(r["family_id"], r["stem_id"], r["contract"]): r for r in rows if r["task_type"] == "noncausal_control"}
        fcontrols = {(r["family_id"], r["stem_id"], r["contract"]): r for r in all_rows[reference_id] if r["task_type"] == "noncausal_control"}
        effects = {}
        for kind in ("decision", "noncausal_control", "source_selection", "randomized_only", "numerical_control"):
            for contract in (("semantic", "neutral") if kind in ("decision", "noncausal_control", "randomized_only") else ("semantic",)):
                for direction in (0, 1):
                    subset = [r for r in rows if r["task_type"] == kind and r["contract"] == contract and r["causal_positive"] == direction]
                    effects[f"{kind}|{contract}|direction={direction}"] = family_effect([
                        (r["family_id"], r["correct"] - ref[r["task_id"]]["correct"]) for r in subset])
        for contract in ("semantic", "neutral"):
            for direction in (0, 1):
                subset = [r for r in rows if r["task_type"] == "decision" and r["contract"] == contract and r["causal_positive"] == direction]
                controlled = []
                for row in subset:
                    key = (row["family_id"], row["stem_id"], contract)
                    qcontrol, fcontrol = qcontrols[key], fcontrols[key]
                    controlled.append((row["family_id"], (row["correct"] - qcontrol["correct"]) - (ref[row["task_id"]]["correct"] - fcontrol["correct"])))
                effects[f"causal_minus_noncausal_precision_interaction|{contract}|direction={direction}"] = family_effect(controlled)
        output["paired_precision"][model_id] = {"reference": reference_id, "effects": effects}
    output["audit"] = {"arms": len(all_rows), "scheduled_responses": len(truth) * len(all_rows),
                       "valid_responses": sum(output["arms"][k]["cells"]["all"]["valid"] for k in all_rows),
                       "raw_sha256": all_raw_hashes, "session_status_counts": dict(session_status)}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=ROOT / "experiments/cohort_024")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result = analyze(args.base)
    write_json(args.out, result)
    print(f"Archived cohort 024 analysis: {result['audit']['arms']} arms, {result['audit']['scheduled_responses']} responses -> {args.out}")


if __name__ == "__main__":
    main()
