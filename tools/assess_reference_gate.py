"""Score a predeclared action-competence gate on a frozen source schedule."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_direct_pilot import arm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines()]
    plan = json.loads(args.plan.read_text())
    strict, relaxed, diagnostics = arm(args.run, truth)
    schedule = {row["task_id"]: row for row in json.loads(
        (args.run / "schedule.json").read_text())}
    if len(relaxed) != len(schedule):
        raise ValueError("Scored rows do not match the complete frozen schedule")
    n = len(relaxed)
    conflict = [row for row in relaxed if row["conflict"]]
    by_order = {
        order: [row for row in conflict
                if schedule[row["task_id"]]["presentation_order"] == order]
        for order in ("randomized_first", "historical_first")
    }
    gate = plan["gate"]
    observed = {
        "responses": n,
        "single_fence_valid_actions": sum(row["valid_action"] for row in relaxed),
        "single_fence_correct_overall": sum(row["correct"] for row in relaxed),
        "conflict_by_order": {
            order: {"correct": sum(row["correct"] for row in rows), "n": len(rows)}
            for order, rows in by_order.items()
        },
        "strict_valid_actions": sum(row["valid_action"] for row in strict),
    }
    checks = {
        "valid_actions": observed["single_fence_valid_actions"] >=
                         gate["single_fence_valid_actions_min"],
        "overall_accuracy": observed["single_fence_correct_overall"] >=
                            gate["single_fence_overall_accuracy_min"],
        "conflict_randomized_first": by_order["randomized_first"] and
            sum(row["correct"] for row in by_order["randomized_first"]) >=
            gate["single_fence_conflict_randomized_first_correct_min"],
        "conflict_historical_first": by_order["historical_first"] and
            sum(row["correct"] for row in by_order["historical_first"]) >=
            gate["single_fence_conflict_historical_first_correct_min"],
    }
    result = {
        "status": "pass" if all(checks.values()) else "fail",
        "observed": observed, "thresholds": gate, "checks": checks,
        "single_fence_diagnostics": diagnostics,
        "strict_is_primary": False,
        "classification": "exploratory feasibility screen; not confirmatory",
    }
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
