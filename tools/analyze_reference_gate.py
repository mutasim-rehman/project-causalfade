"""Score a strict-action reference gate by prompt variant and evidence order."""
import argparse
import json
from pathlib import Path

from analyze_direct_pilot import arm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines() if line]
    plan = json.loads(args.plan.read_text())
    strict, _, diagnostics = arm(args.run, truth)
    schedule = {row["task_id"]: row for row in
                json.loads((args.run / "schedule.json").read_text())}
    if len(strict) != plan["responses"] or len(schedule) != plan["responses"]:
        raise ValueError("Run does not cover the frozen response count")
    if {row["task_id"] for row in strict} != set(schedule):
        raise ValueError("Scored outputs differ from the frozen schedule")

    gates = plan["gate"]
    outcomes, gate_results = {}, {}
    variants = sorted({row["prompt_variant"] for row in schedule.values()})
    for variant in variants:
        rows = [row for row in strict if schedule[row["task_id"]]["prompt_variant"] == variant]
        by_id = {row["task_id"]: row for row in rows}
        valid = sum(row["valid_action"] for row in rows)
        correct = sum(row["correct"] for row in rows)
        cells = {}
        for label, is_conflict in (("aligned", False), ("conflict", True)):
            subset = [row for row in rows if row["conflict"] == is_conflict]
            by_order = {}
            for order in ("randomized_first", "historical_first"):
                ordered = [row for row in subset
                           if schedule[row["task_id"]]["presentation_order"] == order]
                by_order[order] = {
                    "correct": sum(row["correct"] for row in ordered),
                    "valid_actions": sum(row["valid_action"] for row in ordered),
                    "n": len(ordered),
                }
            cells[label] = {
                "correct": sum(row["correct"] for row in subset),
                "valid_actions": sum(row["valid_action"] for row in subset),
                "n": len(subset), "by_order": by_order,
            }
        conflict = cells["conflict"]["by_order"]
        checks = {
            "strict_valid_actions": valid >= gates["strict_valid_actions_min"],
            "overall_accuracy": correct >= gates["overall_correct_min"],
            "conflict_randomized_first": conflict["randomized_first"]["correct"]
                >= gates["conflict_correct_per_order_min"],
            "conflict_historical_first": conflict["historical_first"]["correct"]
                >= gates["conflict_correct_per_order_min"],
        }
        outcomes[variant] = {
            "strict_valid_actions": valid, "n": len(rows),
            "correct_overall": correct,
            "accuracy": correct / len(rows) if rows else None,
            "cells": cells,
        }
        gate_results[variant] = {
            "passed": all(checks.values()), "checks": checks,
            "failed_criteria": [name for name, passed in checks.items() if not passed],
        }
    output = {
        "cohort": plan["cohort"], "families": len({r["family_id"] for r in schedule.values()}),
        "responses": len(strict), "scoring": "strict JSON action; invalid output incorrect",
        "outcomes": outcomes, "gates": gate_results,
        "response_diagnostics": diagnostics,
    }
    args.out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
