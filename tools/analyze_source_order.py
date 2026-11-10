"""Compare randomized-first and historical-first outcomes on matched items."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean

import numpy as np
from analyze_direct_pilot import arm


def load(path):
    return json.loads(path.read_text())


def paired_orders(original, reversed_order, truth):
    initial = load(original / "schedule.json")
    changed = load(reversed_order / "schedule.json")
    if [r["task_id"] for r in initial] != [r["task_id"] for r in changed]:
        raise ValueError("Task order differs")
    historical_first = {}
    for before, after in zip(initial, changed):
        lines = before["prompt"].splitlines()
        if after["prompt"].splitlines() != [lines[0], lines[2], lines[1], *lines[3:]]:
            raise ValueError(f"Prompt change extends beyond source order: {before['task_id']}")
        historical_first[before["task_id"]] = lines[1].startswith("Historical data")
    before = {r["task_id"]: r for r in arm(original, truth)[1]}
    after = {r["task_id"]: r for r in arm(reversed_order, truth)[1]}
    if before.keys() != after.keys() or before.keys() != historical_first.keys():
        raise ValueError("Scored task set differs from the schedules")
    return [(before[k], after[k]) if hist else (after[k], before[k])
            for k, hist in historical_first.items()]


def summarize(pairs, indices, conflict):
    families = defaultdict(list)
    counts = {"historical_first": {"correct": 0, "valid": 0, "activate": 0},
              "randomized_first": {"correct": 0, "valid": 0, "activate": 0}}
    for historical, randomized in pairs:
        if historical["conflict"] != conflict:
            continue
        families[historical["family_id"]].append(historical["correct"] - randomized["correct"])
        for name, record in (("historical_first", historical), ("randomized_first", randomized)):
            counts[name]["correct"] += record["correct"]
            counts[name]["valid"] += record["valid_action"]
            counts[name]["activate"] += record["activate"] == 1
    if any(len(rows) != 2 for rows in families.values()):
        raise ValueError("Each family must contribute both items per conflict condition")
    effects = np.array([mean(families[key]) for key in sorted(families)])
    return {**counts, "tasks_per_order": len(effects) * 2, **estimate(effects, indices)}, effects


def estimate(effects, indices):
    boot = effects[indices].mean(axis=1)
    return {"change_in_accuracy": float(effects.mean()),
            "family_percentile_95_interval": np.quantile(boot, [.025, .975]).tolist()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("original", "reversed", "truth", "out"):
        parser.add_argument(f"--{key}", type=Path, required=True)
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines()]
    pairs = {fmt: paired_orders(args.original / f"run_001_{fmt}",
                               args.reversed / f"run_001_{fmt}", truth)
             for fmt in ("f16", "q4_k_m")}
    ids = {key: {row["task_id"] for row, _ in values} for key, values in pairs.items()}
    if ids["f16"] != ids["q4_k_m"]:
        raise ValueError("Both formats must have the same tasks")
    n = len({row["family_id"] for row, _ in pairs["f16"]})
    indices = np.random.default_rng(20261101).integers(n, size=(10000, n))
    summary = {"contrast": "historical-first minus randomized-first, single-fence action accuracy",
               "families": n, "bootstrap_replicates": 10000, "bootstrap_seed": 20261101}
    for condition, conflict in (("aligned", False), ("conflict", True)):
        f16, f16_effects = summarize(pairs["f16"], indices, conflict)
        q4, q4_effects = summarize(pairs["q4_k_m"], indices, conflict)
        summary[condition] = {"f16": f16, "q4_k_m": q4,
                              "q4_k_m_minus_f16_order_effect": estimate(q4_effects - f16_effects, indices)}
    with args.out.open("x") as handle:
        json.dump(summary, handle, indent=2, allow_nan=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
