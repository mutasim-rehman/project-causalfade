"""Compare completed pilot arms and quantify sensitivity to Markdown fences."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
from statistics import mean, median
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from causalfade.analyze import paired_contrast
from causalfade.score import score

FENCE = re.compile(r"\s*```(?:json)?[ \t]*\r?\n(.*?)\r?\n[ \t]*```\s*", re.I | re.S)


def load(path):
    return json.loads(path.read_text())


def arm(directory, truth, estimate_sign_policy=False):
    if load(directory / "status.json")["status"] != "success":
        raise ValueError(f"Cannot compare incomplete run {directory}")
    strict = load(directory / "results.json")
    raw = [json.loads(line) for line in (directory / "raw_responses.jsonl").read_text().splitlines()]
    if len(raw) != len(strict) or {r["task_id"] for r in raw} != {r["task_id"] for r in strict}:
        raise ValueError(f"Response coverage mismatch in {directory}")
    predictions = []
    syntax = Counter()
    finishes = Counter()
    durations = []
    completion_tokens = []
    for record in raw:
        choice = record["response"]["choices"][0]
        finishes[choice["finish_reason"]] += 1
        durations.append(record["duration_seconds"])
        completion_tokens.append(record["response"]["usage"]["completion_tokens"])
        match = FENCE.fullmatch(choice["message"]["content"] or "")
        prediction = record["prediction"]
        if match:
            try:
                obj = json.loads(match[1])
                if isinstance(obj, dict):
                    prediction = {**obj, "task_id": record["task_id"]}
                    syntax["single_fenced_object"] += 1
                    predictions.append(prediction)
                    continue
            except ValueError:
                pass
        syntax[record["parse_status"]] += 1
        predictions.append(prediction)
    ids = {r["task_id"] for r in strict}
    relaxed = score([r for r in truth if r["task_id"] in ids], predictions)
    diagnostics = {"syntax": syntax, "finish_reasons": finishes,
                   "median_seconds_per_response": median(durations),
                   "mean_completion_tokens": mean(completion_tokens)}
    oracle = {r["task_id"]: r["optimal_action"] for r in truth}
    estimates = {
        "strict": {row["task_id"]: row["prediction"].get("ate_estimate") for row in raw},
        "single_fence": {row["task_id"]: row.get("ate_estimate") for row in predictions},
    }
    for label, scored in (("strict", strict), ("single_fence", relaxed)):
        comparable = [r for r in scored if r["valid_action"] and r["numeric_estimate_valid"]]
        diagnostics[f"{label}_sign_comparable"] = len(comparable)
        diagnostics[f"{label}_action_estimate_sign_disagreements"] = sum(
            r["activate"] != int(estimates[label][r["task_id"]] > 0)
            for r in comparable
        )
        diagnostics[f"{label}_estimate_sign_by_condition"] = {
            name: {
                "n": sum(r["numeric_estimate_valid"] and r["conflict"] == conflict for r in scored),
                "correct": sum(
                    r["numeric_estimate_valid"] and r["conflict"] == conflict
                    and int(estimates[label][r["task_id"]] > 0) == oracle[r["task_id"]]
                    for r in scored
                ),
            }
            for name, conflict in (("aligned", False), ("conflict", True))
        }
    if estimate_sign_policy:
        chosen_truth = [r for r in truth if r["task_id"] in ids]
        strict = sign_policy_rows(chosen_truth, [r["prediction"] for r in raw])
        relaxed = sign_policy_rows(chosen_truth, predictions)
    return strict, relaxed, diagnostics


def sign_policy_rows(truth, predictions):
    projected = []
    for row in predictions:
        estimate = row.get("ate_estimate")
        valid = type(estimate) in (int, float) and math.isfinite(estimate)
        projected.append({**row, "activate": int(estimate > 0) if valid else None})
    return score(truth, projected)


def describe(rows):
    cells = {}
    for t in (0, 1):
        for s in (0, 1):
            cell = [r for r in rows if (r["causal_positive"], r["association_positive"]) == (t, s)]
            errors = [r["ate_error"] for r in cell if r["numeric_estimate_valid"]]
            cells[f"{t}{s}"] = {
                "n": len(cell), "correct": sum(r["correct"] for r in cell),
                "activate": sum(r["activate"] == 1 for r in cell),
                "invalid_action": sum(not r["valid_action"] for r in cell),
                "valid_adjustment": sum(r["adjustment_valid"] for r in cell),
                "numeric_estimates": len(errors),
                "ate_mae": mean(map(abs, errors)) if errors else None,
                "ate_rmse": math.sqrt(mean(e**2 for e in errors)) if errors else None,
            }
    return cells


def accuracy_change(reference, comparison):
    by_id = {r["task_id"]: r for r in reference}
    changes = defaultdict(list)
    transitions = Counter()
    for row in comparison:
        original = by_id[row["task_id"]]
        changes[row["family_id"]].append(row["correct"] - original["correct"])
        transitions[f'{original["correct"]}_to_{row["correct"]}'] += 1
    family_deltas = np.array([mean(changes[key]) for key in sorted(changes)])
    rng = np.random.default_rng(20261101)
    indices = rng.integers(len(family_deltas), size=(10000, len(family_deltas)))
    boot = family_deltas[indices].mean(axis=1)
    return {"accuracy_change": float(family_deltas.mean()),
            "paired_family_bootstrap_percentile_95_interval": np.quantile(boot, [.025, .975]).tolist(),
            "item_correctness_transitions": dict(transitions)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("reference", "comparison", "truth", "out"):
        parser.add_argument(f"--{key}", type=Path, required=True)
    parser.add_argument("--estimate-sign-policy", action="store_true")
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines()]
    f16 = arm(args.reference, truth, args.estimate_sign_policy)
    quant = arm(args.comparison, truth, args.estimate_sign_policy)
    evidence = f16[0][0]["evidence_mode"]
    output = {"reference": str(args.reference), "comparison": str(args.comparison),
              "decision_policy": "estimate_sign" if args.estimate_sign_policy else "explicit_action",
              "diagnostics": {"reference": f16[2], "comparison": quant[2]}}
    for index, name in enumerate(("strict", "exploratory_fence_sensitivity")):
        output[name] = {"contrast": paired_contrast(f16[index], quant[index], mode=evidence,
                                                  bootstrap=10000),
                        "overall": accuracy_change(f16[index], quant[index]),
                        "reference_cells": describe(f16[index]), "comparison_cells": describe(quant[index])}
    with args.out.open("x") as file:
        json.dump(output, file, indent=2, allow_nan=False)
        file.write("\n")


if __name__ == "__main__":
    main()
