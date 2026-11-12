"""Analyze same-session paired presentation orders by family."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from analyze_direct_pilot import arm


def analyze(run, truth, schedule, indices):
    _, scored, _ = arm(run, truth)
    metadata = {row["task_id"]: row for row in schedule}
    paired = defaultdict(dict)
    for row in scored:
        task = metadata[row["task_id"]]
        pair = paired[task["order_pair_id"]]
        order = task["presentation_order"]
        if order in pair:
            raise ValueError(f"Duplicate order for item {task['order_pair_id']}")
        pair[order] = row
    if len(paired) != len(schedule) // 2 or any(set(pair) != {"randomized_first", "historical_first"}
                                for pair in paired.values()):
        raise ValueError("Expected 64 complete prompt-order pairs")
    family_values = defaultdict(lambda: defaultdict(list))
    for pair_id, pair in paired.items():
        random_row, historical_row = pair["randomized_first"], pair["historical_first"]
        if (random_row["family_id"] != historical_row["family_id"]
                or random_row["conflict"] != historical_row["conflict"]):
            raise ValueError(f"Pair labels differ for {pair_id}")
        key = "conflict" if random_row["conflict"] else "aligned"
        family = random_row["family_id"]
        family_values[family][key].append(
            (random_row["correct"], historical_row["correct"],
             random_row["activate"] == 1, historical_row["activate"] == 1)
        )
    families = sorted(family_values)
    if len(families) != len({row["family_id"] for row in schedule}):
        raise ValueError("Some family blocks are incomplete")
    output = {}
    effects = {}
    for condition in ("aligned", "conflict"):
        per_family = np.array([
            [np.mean([row[index] for row in family_values[f][condition]])
             for index in range(4)]
            for f in families
        ])
        # Columns are random correct, historical correct, random yes, historical yes.
        draws = per_family[indices]
        values = {}
        for label, column in (("randomized_first", 0), ("historical_first", 1)):
            values[label] = {
                "correct": int(per_family[:, column].sum()),
                "n": int(len(families) * 2),
                "activate": int(per_family[:, column + 2].sum()),
            }
        delta = per_family[:, 1] - per_family[:, 0]
        boot_delta = draws[:, :, 1].mean(axis=1) - draws[:, :, 0].mean(axis=1)
        output[condition] = {
            **values,
            "historical_first_minus_randomized_first_accuracy": float(delta.mean()),
            "family_percentile_95_interval": np.quantile(boot_delta, [.025, .975]).tolist(),
        }
        effects[condition] = delta
    return output, effects


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f16", type=Path, required=True)
    parser.add_argument("--q4", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines()]
    schedules = [json.loads((run / "schedule.json").read_text()) for run in (args.f16, args.q4)]
    if schedules[0] != schedules[1]:
        raise ValueError("Format runs used different schedules")
    n = len({row["family_id"] for row in schedules[0]})
    indices = np.random.default_rng(20261112).integers(n, size=(10000, n))
    f16, f16_effects = analyze(args.f16, truth, schedules[0], indices)
    q4, q4_effects = analyze(args.q4, truth, schedules[0], indices)
    result = {
        "families": n, "paired_items_per_format": len(schedules[0]) // 2,
        "bootstrap_replicates": 10000, "bootstrap_seed": 20261112,
        "f16": f16, "q4_k_m": q4,
        "q4_k_m_minus_f16_order_interaction": {},
    }
    for condition in ("aligned", "conflict"):
        contrast = q4_effects[condition] - f16_effects[condition]
        boot = contrast[indices].mean(axis=1)
        result["q4_k_m_minus_f16_order_interaction"][condition] = {
            "historical_first_effect_difference": float(contrast.mean()),
            "family_percentile_95_interval": np.quantile(boot, [.025, .975]).tolist(),
        }
    with args.out.open("x") as out:
        json.dump(result, out, indent=2, allow_nan=False)
        out.write("\n")


if __name__ == "__main__":
    main()
