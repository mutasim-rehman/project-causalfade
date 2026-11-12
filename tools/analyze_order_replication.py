"""Confirmatory family-blocked analysis of paired evidence-order replication."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

import numpy as np

from analyze_direct_pilot import arm


def betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    tiny = 1e-300
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 301):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3e-14:
            return h
    raise ArithmeticError("Incomplete beta continued fraction did not converge")


def beta_regularized(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                     + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return front * betacf(a, b, x) / a
    return 1 - front * betacf(b, a, 1 - x) / b


def t_critical_975(df):
    z = 1.959963984540054
    return (z + (z**3 + z) / (4 * df)
            + (5 * z**5 + 16 * z**3 + 3 * z) / (96 * df**2)
            + (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * df**3))


def one_sample_t(values):
    values = np.asarray(values, dtype=float)
    n = len(values)
    mean = float(values.mean())
    sd = float(values.std(ddof=1))
    se = sd / math.sqrt(n)
    statistic = mean / se if se else (math.inf if mean else 0.0)
    df = n - 1
    p = beta_regularized(df / 2, 0.5, df / (df + statistic**2)) if math.isfinite(statistic) else 0.0
    critical = t_critical_975(df)
    return {
        "families": n, "mean_difference": mean,
        "family_level_sd": sd, "standard_error": se,
        "t_statistic": statistic, "degrees_of_freedom": df,
        "two_sided_p_value": p,
        "t_critical_975_approximation": critical,
        "t_interval_95": [mean - critical * se, mean + critical * se],
    }


def accuracy_by_order(rows, schedule, conflict_value, expected_per_family):
    cells = {}
    family_differences = {}
    for family in sorted({r["family_id"] for r in rows}):
        family_differences[family] = {}
    for order in ("randomized_first", "historical_first"):
        subset = [r for r in rows if r["conflict"] == conflict_value
                  and schedule[r["task_id"]]["presentation_order"] == order]
        cells[order] = {
            "correct": sum(r["correct"] for r in subset), "n": len(subset),
            "valid_actions": sum(r["valid_action"] for r in subset),
            "activate": sum(r["activate"] == 1 for r in subset),
        }
        by_family = defaultdict(list)
        for row in subset:
            by_family[row["family_id"]].append(row)
        if set(by_family) != set(family_differences) or any(
                len(outcomes) != expected_per_family for outcomes in by_family.values()):
            raise ValueError(f"Incomplete family/order cell for {order}")
        for family, outcomes in by_family.items():
            family_differences[family][order] = float(
                np.mean([row["correct"] for row in outcomes]))
    deltas = []
    for family, orders in family_differences.items():
        if set(orders) != {"randomized_first", "historical_first"}:
            raise ValueError(f"Incomplete family order block for {family}")
        deltas.append(orders["historical_first"] - orders["randomized_first"])
    return cells, np.asarray(deltas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f16", type=Path, required=True)
    parser.add_argument("--q4", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    truth = [json.loads(line) for line in args.truth.read_text().splitlines() if line]
    f_schedule = json.loads((args.f16 / "schedule.json").read_text())
    q_schedule = json.loads((args.q4 / "schedule.json").read_text())
    if f_schedule != q_schedule or len(f_schedule) != plan["responses_per_format"]:
        raise ValueError("Format arms do not share the complete frozen schedule")
    if hashlib_schedule(args.f16) != plan["schedule_sha256"]:
        raise ValueError("Run schedule differs from the frozen schedule hash")
    truth_ids = {r["task_id"] for r in truth}
    if truth_ids != {r["task_id"] for r in f_schedule}:
        raise ValueError("Schedule and evaluator truth task IDs differ")
    schedules = {row["task_id"]: row for row in f_schedule}
    arms = {"f16": arm(args.f16, truth), "q4_k_m": arm(args.q4, truth)}
    strict_rows = {name: value[0] for name, value in arms.items()}
    expected_families = plan["families"]
    if any(len({r["family_id"] for r in rows}) != expected_families
           for rows in strict_rows.values()):
        raise ValueError("Unexpected family count in a format arm")

    order_results, family_delta = {}, {}
    for name, rows in strict_rows.items():
        by_condition = {}
        for condition, conflict_value in (("aligned", False), ("conflict", True)):
            cells, deltas = accuracy_by_order(
                rows, schedules, conflict_value,
                plan["tasks_per_family_condition_per_order"])
            by_condition[condition] = {
                "by_order": cells,
                "historical_first_minus_randomized_first": float(deltas.mean()),
            }
            family_delta[(name, condition)] = deltas
        order_results[name] = by_condition

    primary = one_sample_t(family_delta[("q4_k_m", "conflict")])
    seed = plan["analysis_seed"]
    rng = np.random.default_rng(seed)
    n = expected_families
    indices = rng.integers(n, size=(10000, n))
    primary_delta = family_delta[("q4_k_m", "conflict")]
    bootstrap_primary = primary_delta[indices].mean(axis=1)
    primary["family_percentile_bootstrap_95_interval"] = np.quantile(
        bootstrap_primary, [.025, .975]).tolist()
    interaction = (family_delta[("q4_k_m", "conflict")]
                   - family_delta[("f16", "conflict")])
    bootstrap_interaction = interaction[indices].mean(axis=1)
    output = {
        "cohort": plan["cohort"], "classification": plan["classification"],
        "families": n, "responses_per_format": len(f_schedule),
        "strict_valid_actions": {
            name: sum(row["valid_action"] for row in rows)
            for name, rows in strict_rows.items()},
        "primary_hypothesis": plan["primary_hypothesis"],
        "primary_q4_conflict_order_effect": primary,
        "secondary_order_results": order_results,
        "secondary_format_by_conflict_order_interaction": {
            "estimate_q4_minus_f16": float(interaction.mean()),
            "family_percentile_bootstrap_95_interval": np.quantile(
                bootstrap_interaction, [.025, .975]).tolist(),
        },
        "bootstrap_replicates": 10000, "bootstrap_seed": seed,
        "scoring": "strict JSON accuracy; invalid output is incorrect",
        "limitations": [
            "The confirmatory claim is limited to these model checkpoints, prompt scaffold, synthetic generator and target rates.",
            "The replication was designed after cohort 015 exposed the order pattern; cohort 015 remains development evidence.",
            "Secondary format interactions and aligned-item order effects are descriptive.",
        ],
    }
    args.out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(json.dumps(output, indent=2, allow_nan=False))


def hashlib_schedule(run):
    import hashlib
    return hashlib.sha256((run / "schedule.json").read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
