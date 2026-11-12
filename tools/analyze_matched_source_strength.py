"""Analyze format contrasts for matched-strength, order-twin source tasks."""
import argparse
from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from analyze_direct_pilot import arm


def describe(rows):
    result = {}
    for conflict, label in ((False, "aligned"), (True, "conflict")):
        subset = [row for row in rows if row["conflict"] == conflict]
        result[label] = {
            "correct": sum(row["correct"] for row in subset),
            "n": len(subset),
            "accuracy": float(np.mean([row["correct"] for row in subset])),
            "activate": sum(row["activate"] == 1 for row in subset),
            "invalid_action": sum(not row["valid_action"] for row in subset),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f16", type=Path, required=True)
    parser.add_argument("--q4", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261112)
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines()]
    arms = {"f16": arm(args.f16, truth), "q4_k_m": arm(args.q4, truth)}
    rows = {name: value[1] for name, value in arms.items()}
    if {row["task_id"] for row in rows["f16"]} != {
            row["task_id"] for row in rows["q4_k_m"]}:
        raise ValueError("Format arms do not have identical task sets")
    by_family = {name: defaultdict(list) for name in rows}
    for name, arm_rows in rows.items():
        for row in arm_rows:
            by_family[name][(row["family_id"], row["conflict"])].append(row)
    families = sorted({row["family_id"] for row in rows["f16"]})
    if len(families) != 16:
        raise ValueError(f"Expected 16 family blocks; found {len(families)}")
    for name in rows:
        if any(len(by_family[name][(family, conflict)]) != 4
               for family in families for conflict in (False, True)):
            raise ValueError(f"Incomplete family-condition block for {name}")

    indices = np.random.default_rng(args.seed).integers(
        len(families), size=(10000, len(families)))
    family_acc = {}
    for name in rows:
        condition_acc = {
            condition: np.array([
                np.mean([row["correct"] for row in
                         by_family[name][(family, condition)]])
                for family in families
            ])
            for condition in (False, True)
        }
        overall_acc = np.array([
            np.mean([row["correct"] for conflict in (False, True)
                     for row in by_family[name][(family, conflict)]])
            for family in families
        ])
        family_acc[name] = {**condition_acc, "overall": overall_acc}
    q4_penalty = family_acc["q4_k_m"][False] - family_acc["q4_k_m"][True]
    f16_penalty = family_acc["f16"][False] - family_acc["f16"][True]
    penalty_delta = q4_penalty - f16_penalty
    boot = penalty_delta[indices].mean(axis=1)
    output = {
        "families": len(families), "responses_per_format": len(rows["f16"]),
        "scoring": "runner-parsed JSON action; all observed outputs were bare JSON",
        "bootstrap_replicates": 10000, "bootstrap_seed": args.seed,
        "format_outcomes": {name: describe(arm_rows)
                            for name, arm_rows in rows.items()},
        "strict_valid_actions": {
            name: sum(row["valid_action"] for row in value[0])
            for name, value in arms.items()},
        "diagnostics": {name: value[2] for name, value in arms.items()},
        "q4_k_m_minus_f16_conflict_penalty": {
            "estimate": float(penalty_delta.mean()),
            "family_percentile_95_interval": np.quantile(boot, [.025, .975]).tolist(),
            "q4_k_m_conflict_penalty": float(q4_penalty.mean()),
            "f16_conflict_penalty": float(f16_penalty.mean()),
            "interpretation": "positive values indicate a larger aligned-minus-conflict accuracy penalty under Q4_K_M",
        },
        "paired_family_accuracy_change_q4_k_m_minus_f16": {
            condition: {
                "estimate": float((family_acc["q4_k_m"][condition] -
                                    family_acc["f16"][condition]).mean()),
                "family_percentile_95_interval": np.quantile(
                    (family_acc["q4_k_m"][condition] -
                     family_acc["f16"][condition])[indices].mean(axis=1),
                    [.025, .975]).tolist(),
            }
            for condition in ("overall", False, True)
        },
        "limitations": [
            "Exploratory development cohort selected after prior outcomes; it is not confirmatory.",
            "One 7B checkpoint family, one synthetic source-selection task and 16 SCM families.",
            "The causal-context prompt supplies mechanism information and is a scaffolded condition.",
            "The Q4_K_M conflict results differ sharply by evidence order; the aggregate format contrast alone hides this pattern.",
        ],
    }
    # JSON keys need condition labels rather than Python booleans.
    output["paired_family_accuracy_change_q4_k_m_minus_f16"] = {
        ("overall" if key == "overall" else
         "aligned" if key is False else "conflict"): value
        for key, value in output["paired_family_accuracy_change_q4_k_m_minus_f16"].items()
    }
    args.out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
