"""Analyze framing-specific competence and paired gains in cohort 013."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from analyze_direct_pilot import arm

LEADING_FENCE = re.compile(r"^\s*```(?:json)?\s*\r?\n(.*?)\r?\n\s*```", re.I | re.S)


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
    schedule = {r["task_id"]: r for r in json.loads((args.run / "schedule.json").read_text())}
    if len(relaxed) != len(schedule) or len(relaxed) != 128:
        raise ValueError("Scored responses do not cover the frozen 128-task schedule")
    family_ids = sorted({r["family_id"] for r in relaxed})
    records = defaultdict(list)
    for row in relaxed:
        task = schedule[row["task_id"]]
        records[task["prompt_variant"]].append({**row, **task})
    outcomes, gate_checks, family_scores = {}, {}, {}
    raw_by_id = {row["task_id"]: row for row in (
        json.loads(line) for line in
        (args.run / "raw_responses.jsonl").read_text().splitlines())}
    leading = defaultdict(list)
    prefix_syntax = defaultdict(lambda: defaultdict(int))
    truth_by_id = {row["task_id"]: row for row in truth}
    for task_id, task in schedule.items():
        record = raw_by_id[task_id]
        content = record["response"]["choices"][0]["message"].get("content", "")
        match = LEADING_FENCE.match(content)
        action = None
        if match:
            try:
                value = json.loads(match.group(1))
                if isinstance(value, dict) and type(value.get("activate")) is int \
                        and value["activate"] in (0, 1):
                    action = value["activate"]
                    suffix = content[match.end():].strip()
                    prefix_syntax[task["prompt_variant"]][
                        "leading_fenced_action_with_trailing_prose" if suffix
                        else "single_leading_fence_only"] += 1
            except (TypeError, ValueError):
                pass
        if action is None:
            prefix_syntax[task["prompt_variant"]]["no_recoverable_leading_action"] += 1
        leading[task["prompt_variant"]].append({
            "task_id": task_id, "family_id": task["family_id"],
            "conflict": truth_by_id[task_id]["conflict"],
            "presentation_order": task["presentation_order"],
            "action": action,
            "correct": (action == truth_by_id[task_id]["optimal_action"])
                       if action is not None else False,
        })
    thresholds = plan["gate_each_framing"]
    for variant in ("minimal", "causal_context"):
        rows = records[variant]
        cell = {}
        for condition, conflict in (("aligned", False), ("conflict", True)):
            subset = [r for r in rows if r["conflict"] == conflict]
            by_order = {}
            for order in ("randomized_first", "historical_first"):
                order_rows = [r for r in subset if r["presentation_order"] == order]
                by_order[order] = {
                    "correct": sum(r["correct"] for r in order_rows),
                    "n": len(order_rows),
                    "activate": sum(r["activate"] == 1 for r in order_rows),
                }
            cell[condition] = {
                "correct": sum(r["correct"] for r in subset), "n": len(subset),
                "accuracy": float(np.mean([r["correct"] for r in subset])),
                "activate": sum(r["activate"] == 1 for r in subset),
                "by_order": by_order,
            }
        valid = sum(r["valid_action"] for r in rows)
        correct = sum(r["correct"] for r in rows)
        conflict_randomized = cell["conflict"]["by_order"]["randomized_first"]
        conflict_historical = cell["conflict"]["by_order"]["historical_first"]
        checks = {
            "valid_actions": valid >= thresholds["valid_actions_min"],
            "overall_accuracy": correct >= thresholds["overall_correct_min"],
            "conflict_randomized_first": conflict_randomized["correct"] >=
                thresholds["conflict_correct_per_order_min"],
            "conflict_historical_first": conflict_historical["correct"] >=
                thresholds["conflict_correct_per_order_min"],
        }
        outcomes[variant] = {
            "valid_actions": valid, "strict_valid_actions": sum(
                r["valid_action"] for r in strict
                if schedule[r["task_id"]]["prompt_variant"] == variant),
            "correct_overall": correct, "n": len(rows),
            "accuracy": float(np.mean([r["correct"] for r in rows])),
            "cells": cell,
        }
        gate_checks[variant] = {
            "passed": all(checks.values()), "checks": checks,
            "failed_criteria": [k for k, value in checks.items() if not value],
        }
        family_scores[variant] = {
            condition: np.array([
                np.mean([r["correct"] for r in rows if r["family_id"] == family
                         and (conflict is None or r["conflict"] == conflict)])
                for family in family_ids
            ])
            for condition, conflict in (("overall", None), ("aligned", False), ("conflict", True))
        }
    paired = defaultdict(dict)
    for variant in ("minimal", "causal_context"):
        for row in records[variant]:
            paired[(row["base_task_id"], row["presentation_order"])][variant] = row
    if any(set(pair) != {"minimal", "causal_context"} for pair in paired.values()):
        raise ValueError("Prompt variants are not paired on base item and evidence order")
    transitions = defaultdict(int)
    for pair in paired.values():
        a, b = pair["minimal"], pair["causal_context"]
        if (a["family_id"], a["conflict"], a["presentation_order"]) != \
                (b["family_id"], b["conflict"], b["presentation_order"]):
            raise ValueError("Prompt variant changed evaluator labels or order")
        transitions[f"{int(a['correct'])}_to_{int(b['correct'])}"] += 1

    seed = plan["analysis_seed"]
    rng = np.random.default_rng(seed)
    indices = rng.integers(len(family_ids), size=(10000, len(family_ids)))
    gains = {}
    for condition in ("overall", "aligned", "conflict"):
        delta = family_scores["causal_context"][condition] - family_scores["minimal"][condition]
        boot = delta[indices].mean(axis=1)
        gains[condition] = {
            "causal_context_minus_minimal": float(delta.mean()),
            "family_percentile_95_interval": np.quantile(boot, [.025, .975]).tolist(),
        }
    result = {
        "families": len(family_ids), "responses": len(relaxed),
        "single_fence_scoring": True,
        "bootstrap_replicates": 10000, "bootstrap_seed": seed,
        "outcomes": outcomes, "gates": gate_checks,
        "posthoc_leading_json_fence_diagnostic": {
            "policy": "extract only a complete leading fenced JSON action and ignore trailing prose; malformed response remains invalid for all primary metrics and gates",
            "syntax_by_variant": {k: dict(v) for k, v in prefix_syntax.items()},
            "actions_by_variant": {
                variant: {
                    "recoverable_actions": sum(row["action"] is not None for row in variant_rows),
                    "correct_overall": sum(row["correct"] for row in variant_rows),
                    "accuracy_if_leading_action_recovered": (
                        float(np.mean([row["correct"] for row in variant_rows
                                       if row["action"] is not None]))
                        if any(row["action"] is not None for row in variant_rows) else None),
                    "by_cell_and_order": {
                        f"{condition}_{order}": {
                            "correct": sum(row["correct"] for row in variant_rows
                                           if row["conflict"] == conflict and
                                           row["presentation_order"] == order),
                            "n": sum(row["action"] is not None for row in variant_rows
                                     if row["conflict"] == conflict and
                                     row["presentation_order"] == order),
                            "actions": sum(row["action"] == 1 for row in variant_rows
                                           if row["conflict"] == conflict and
                                           row["presentation_order"] == order),
                        }
                        for condition, conflict in (("aligned", False), ("conflict", True))
                        for order in ("randomized_first", "historical_first")
                    },
                }
                for variant, variant_rows in leading.items()
            },
        },
        "paired_prompt_variant_transitions": dict(transitions),
        "family_blocked_prompt_variant_gains": gains,
        "diagnostics": diagnostics,
        "interpretation": "development-only prompt clarity control; the causal_context variant supplies mechanism information and is not equivalent to the minimal reasoning task",
    }
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
