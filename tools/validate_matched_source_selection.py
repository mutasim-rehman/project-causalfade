"""Audit mathematical properties and matched-order joins of cohort 011."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--expanded", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_manifest = json.loads((args.base / "manifest.json").read_text())
    expanded_manifest = json.loads((args.expanded / "manifest.json").read_text())
    for folder, manifest in ((args.base, base_manifest), (args.expanded, expanded_manifest)):
        for name, expected in manifest["file_sha256"].items():
            actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f"Checksum mismatch: {folder / name}")

    base_tasks = read_jsonl(args.base / "public_tasks.jsonl")
    truths = {row["task_id"]: row for row in read_jsonl(args.base / "oracle_truth.jsonl")}
    evidence_rows = {row["task_id"]: row for row in read_jsonl(
        args.base / "evaluator_exact_evidence.jsonl")}
    pairs = defaultdict(list)
    bounds = {"min_outcome_probability": 1.0, "max_outcome_probability": 0.0,
              "min_treatment_probability": 1.0, "max_treatment_probability": 0.0,
              "max_randomized_difference_error": 0.0,
              "max_observational_difference_error": 0.0}
    parsed_rate_error = 0.0
    for task in base_tasks:
        truth = truths[task["task_id"]]
        evidence = evidence_rows[task["task_id"]]
        strata = evidence["strata"]
        cell = {(row["z"], row["x"]): row for row in strata}
        outcome = [[cell[z, x]["success_probability"] for x in (0, 1)] for z in (0, 1)]
        propensity = [2 * sum(cell[z, x]["population_cell_probability"] for x in (0, 1)
                             if x == 1) for z in (0, 1)]
        randomized = [sum(outcome[z][x] for z in (0, 1)) / 2 for x in (0, 1)]
        observed = [sum(cell[z, x]["success_probability"] *
                        cell[z, x]["population_cell_probability"] for z in (0, 1)) /
                    sum(cell[z, x]["population_cell_probability"] for z in (0, 1))
                    for x in (0, 1)]
        randomized_difference = randomized[1] - randomized[0]
        observational_difference = observed[1] - observed[0]
        bounds["max_randomized_difference_error"] = max(
            bounds["max_randomized_difference_error"],
            abs(randomized_difference - truth["ate"]))
        bounds["max_observational_difference_error"] = max(
            bounds["max_observational_difference_error"],
            abs(observational_difference - truth["observational_difference"]))
        if (randomized_difference > 0) != bool(truth["causal_positive"]):
            raise ValueError(f"Randomized evidence sign mismatch: {task['task_id']}")
        if (observational_difference > 0) != bool(truth["association_positive"]):
            raise ValueError(f"Observational evidence sign mismatch: {task['task_id']}")
        if not truth["conflict"] and truth["causal_positive"] != truth["association_positive"]:
            raise ValueError("Aligned labels disagree")
        if truth["conflict"] and truth["causal_positive"] == truth["association_positive"]:
            raise ValueError("Conflict labels agree")
        outcome_probabilities = [v for row in outcome for v in row]
        treatment_probabilities = [*propensity, *(1 - value for value in propensity)]
        bounds["min_outcome_probability"] = min(bounds["min_outcome_probability"],
                                                *outcome_probabilities)
        bounds["max_outcome_probability"] = max(bounds["max_outcome_probability"],
                                                *outcome_probabilities)
        bounds["min_treatment_probability"] = min(bounds["min_treatment_probability"],
                                                   *treatment_probabilities)
        bounds["max_treatment_probability"] = max(bounds["max_treatment_probability"],
                                                   *treatment_probabilities)
        rendered = re.findall(r"(Random assignment|Historical data).*?(\d+\.\d+)%.*?(\d+\.\d+)%",
                             task["prompt"])
        if len(rendered) != 2:
            raise ValueError(f"Could not parse rendered rates: {task['task_id']}")
        for source, off, on in rendered:
            expected = (randomized_difference if source.startswith("Random assignment")
                        else observational_difference)
            rendered_difference = (float(on) - float(off)) / 100
            error = abs(rendered_difference - expected)
            parsed_rate_error = max(parsed_rate_error, error)
            if error > .00011:
                raise ValueError(f"Rendered rate mismatch: {task['task_id']} {source}")
        pairs[truth["family_id"]].append(truth)

    for family, rows in pairs.items():
        if len(rows) != 4:
            raise ValueError(f"Expected four cells for {family}")
        aligned = [abs(row["observational_difference"]) for row in rows if not row["conflict"]]
        conflict = [abs(row["observational_difference"]) for row in rows if row["conflict"]]
        if max(aligned + conflict) - min(aligned + conflict) > 1e-10:
            raise ValueError(f"Observational magnitude not matched in {family}")
    expanded = read_jsonl(args.expanded / "public_tasks.jsonl")
    prompt_variants = tuple(json.loads((args.expanded / "manifest.json").read_text())
                            .get("prompt_variants", [None]))
    twins = defaultdict(list)
    for task in expanded:
        twins[task["order_pair_id"]].append(task)
    if len(expanded) != 2 * len(base_tasks) * len(prompt_variants) or any(
            len(group) != 2 or {row["presentation_order"] for row in group} !=
            {"randomized_first", "historical_first"} for group in twins.values()):
        raise ValueError("Expanded paired orders are incomplete")
    first_counts = defaultdict(lambda: defaultdict(int))
    for task in base_tasks:
        for variant in prompt_variants:
            pair_id = f"{task['task_id']}:{variant}" if variant else task["task_id"]
            twin = twins[pair_id]
            if len(twin) != 2:
                raise ValueError(f"Missing order twins: {pair_id}")
            assigned = twin[0]["randomized_in_family_first_order"]
            first_counts[(task["family_id"], variant)][assigned] += 1
    if any(counts != {"randomized_first": 2, "historical_first": 2}
           for counts in first_counts.values()):
        raise ValueError("First-position assignment is not balanced within family")

    report = {
        "status": "validated",
        "families": len(pairs), "base_tasks": len(base_tasks),
        "expanded_tasks": len(expanded), "complete_order_twins": len(twins),
        "balanced_families": len(first_counts),
        "bounds_and_formula_errors": bounds,
        "max_rendered_rate_difference_error": parsed_rate_error,
        "base_manifest_sha256": hashlib.sha256(
            (args.base / "manifest.json").read_bytes()).hexdigest(),
        "expanded_manifest_sha256": hashlib.sha256(
            (args.expanded / "manifest.json").read_bytes()).hexdigest(),
    }
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
