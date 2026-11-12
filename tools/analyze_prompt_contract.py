"""Analyze strict-JSON feasibility in the paired framing development screen."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_direct_pilot import arm


def summarize(rows, schedule):
    by_variant = defaultdict(list)
    for row in rows:
        task = schedule[row["task_id"]]
        by_variant[task["prompt_variant"]].append({**row, **task})
    output = {}
    for variant in ("minimal", "causal_context"):
        subset = by_variant[variant]
        cells = {}
        for name, conflict in (("aligned", False), ("conflict", True)):
            condition_rows = [row for row in subset if row["conflict"] == conflict]
            cells[name] = {
                "correct": sum(row["correct"] for row in condition_rows),
                "n": len(condition_rows),
                "valid_actions": sum(row["valid_action"] for row in condition_rows),
                "by_order": {
                    order: {
                        "correct": sum(row["correct"] for row in condition_rows
                                        if row["presentation_order"] == order),
                        "n": sum(row["presentation_order"] == order
                                 for row in condition_rows),
                        "valid_actions": sum(row["valid_action"] for row in condition_rows
                                             if row["presentation_order"] == order),
                    }
                    for order in ("randomized_first", "historical_first")
                },
            }
        output[variant] = {
            "correct": sum(row["correct"] for row in subset), "n": len(subset),
            "valid_actions": sum(row["valid_action"] for row in subset),
            "accuracy": float(np.mean([row["correct"] for row in subset])),
            "cells": cells,
        }
    return output, by_variant


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines()]
    plan = json.loads(args.plan.read_text())
    strict, fenced, diagnostics = arm(args.run, truth)
    schedule = {row["task_id"]: row for row in json.loads((args.run / "schedule.json").read_text())}
    if len(strict) != 128 or len(fenced) != 128 or len(schedule) != 128:
        raise ValueError("Expected complete 128-response schedule")
    strict_summary, _ = summarize(strict, schedule)
    fenced_summary, _ = summarize(fenced, schedule)
    gate = plan["gate_each_framing"]
    gates = {}
    for variant, metrics in strict_summary.items():
        conflict = metrics["cells"]["conflict"]
        checks = {
            "strict_valid_actions": metrics["valid_actions"] >= gate["valid_actions_min"],
            "overall_accuracy": metrics["correct"] >= gate["overall_correct_min"],
            "conflict_randomized_first": conflict["by_order"]["randomized_first"]["correct"]
                >= gate["conflict_correct_per_order_min"],
            "conflict_historical_first": conflict["by_order"]["historical_first"]["correct"]
                >= gate["conflict_correct_per_order_min"],
        }
        gates[variant] = {"passed": all(checks.values()), "checks": checks,
                          "failed_criteria": [key for key, value in checks.items() if not value]}

    variants = defaultdict(list)
    for row in strict:
        task = schedule[row["task_id"]]
        variants[task["prompt_variant"]].append({**row, **task})
    family_ids = sorted({row["family_id"] for row in strict})
    indices = np.random.default_rng(plan["analysis_seed"]).integers(
        len(family_ids), size=(10000, len(family_ids)))
    gains = {}
    for name, conflict in (("overall", None), ("aligned", False), ("conflict", True)):
        scores = {}
        for variant in ("minimal", "causal_context"):
            scores[variant] = np.array([
                np.mean([row["correct"] for row in variants[variant]
                         if row["family_id"] == family and
                         (conflict is None or row["conflict"] == conflict)])
                for family in family_ids
            ])
        delta = scores["causal_context"] - scores["minimal"]
        gains[name] = {
            "causal_context_minus_minimal": float(delta.mean()),
            "family_percentile_95_interval": np.quantile(
                delta[indices].mean(axis=1), [.025, .975]).tolist(),
        }
    result = {
        "families": len(family_ids), "responses": len(strict),
        "primary_scoring": "strict single JSON object; invalid outputs fail accuracy and validity",
        "strict_outcomes": strict_summary,
        "single_fence_sensitivity": fenced_summary,
        "reference_gates": gates,
        "paired_family_gains_strict": gains,
        "bootstrap_replicates": 10000,
        "bootstrap_seed": plan["analysis_seed"],
        "response_diagnostics": diagnostics,
        "limitations": [
            "Development cohort selected after prior prompt and output-format results.",
            "Eight fresh families, one model checkpoint, and one synthetic task domain.",
            "Causal-context frame provides mechanism information and is scaffolded.",
        ],
    }
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
