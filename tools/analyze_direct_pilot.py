"""Compare completed pilot arms and quantify sensitivity to Markdown fences."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
from statistics import mean, median
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from causalfade.analyze import paired_contrast
from causalfade.score import score

FENCE = re.compile(r"\s*```(?:json)?[ \t]*\r?\n(.*?)\r?\n[ \t]*```\s*", re.I | re.S)


def load(path):
    return json.loads(path.read_text())


def arm(directory, truth):
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
    return strict, relaxed, diagnostics


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("reference", "comparison", "truth", "out"):
        parser.add_argument(f"--{key}", type=Path, required=True)
    args = parser.parse_args()
    truth = [json.loads(line) for line in args.truth.read_text().splitlines()]
    f16 = arm(args.reference, truth)
    quant = arm(args.comparison, truth)
    evidence = f16[0][0]["evidence_mode"]
    output = {"reference": str(args.reference), "comparison": str(args.comparison),
              "diagnostics": {"reference": f16[2], "comparison": quant[2]}}
    for index, name in enumerate(("strict", "exploratory_fence_sensitivity")):
        output[name] = {"contrast": paired_contrast(f16[index], quant[index], mode=evidence,
                                                  bootstrap=10000),
                        "reference_cells": describe(f16[index]), "comparison_cells": describe(quant[index])}
    with args.out.open("x") as file:
        json.dump(output, file, indent=2, allow_nan=False)
        file.write("\n")


if __name__ == "__main__":
    main()
