"""Exploratory paired 14B Q8_0/Q4_K_M analysis on the cohort 016 tasks."""
import argparse
import json
from pathlib import Path

import numpy as np

from analyze_direct_pilot import arm
from analyze_order_replication import accuracy_by_order, one_sample_t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q8", type=Path, required=True)
    parser.add_argument("--q4", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    schedules = [json.loads((p / "schedule.json").read_text()) for p in (args.q8, args.q4)]
    if schedules[0] != schedules[1] or len(schedules[0]) != 768:
        raise ValueError("Both complete 768-task schedules must match")
    schedule = {r["task_id"]: r for r in schedules[0]}
    truth = [json.loads(s) for s in args.truth.read_text().splitlines()]
    if set(schedule) != {r["task_id"] for r in truth}:
        raise ValueError("Schedule and truth IDs differ")
    results = {}
    differences = {}
    for name, directory in (("q8_0", args.q8), ("q4_k_m", args.q4)):
        strict, _, diagnostics = arm(directory, truth)
        results[name] = {"n": len(strict), "correct": sum(r["correct"] for r in strict),
                         "valid_actions": sum(r["valid_action"] for r in strict),
                         "diagnostics": diagnostics}
        for condition, flag in (("conflict", True), ("aligned", False)):
            cells, delta = accuracy_by_order(strict, schedule, flag, 2)
            results[name][condition] = {"order_cells": cells,
                                        "historical_first_minus_randomized_first": one_sample_t(delta)}
            differences[(name, condition)] = delta
    rng = np.random.default_rng(20261113)
    idx = rng.integers(96, size=(10000, 96))
    interaction = differences[("q4_k_m", "conflict")] - differences[("q8_0", "conflict")]
    output = {"classification": "exploratory 14B matched-quantization follow-up on reused cohort 016 families",
              "families": 96, "results": results,
              "q4_minus_q8_conflict_order_interaction": {
                  "estimate": float(interaction.mean()),
                  "family_bootstrap_95": np.quantile(interaction[idx].mean(axis=1), [.025, .975]).tolist()},
              "limitations": ["Cohort 016 families were previously used and are not fresh confirmation.",
                              "Q8_0 is a quantized reference, not full precision.",
                              "This tests prompt-conditioned actions, not autonomous causal discovery."]}
    args.out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
