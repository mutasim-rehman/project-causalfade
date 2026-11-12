"""Validate the paired framing and order structure for cohort 013."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--expanded", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base = json.loads((args.source / "manifest.json").read_text())
    expanded_manifest = json.loads((args.expanded / "manifest.json").read_text())
    for folder, manifest in ((args.source, base), (args.expanded, expanded_manifest)):
        for name, digest in manifest["file_sha256"].items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Hash mismatch: {folder / name}")
    tasks = read_jsonl(args.expanded / "public_tasks.jsonl")
    output_contract = expanded_manifest.get("output_contract", "legacy")
    strict_instruction = (
        'Return exactly one JSON object with one key, activate, whose value is 0 or 1. '
        'The entire response must be exactly one of: {"activate": 0} or {"activate": 1}. '
        'Do not include a Markdown fence, explanation, or any other text.'
    )
    truth = {r["task_id"]: r for r in read_jsonl(args.expanded / "oracle_truth.jsonl")}
    grouped = defaultdict(list)
    for task in tasks:
        grouped[(task["family_id"], task["prompt_variant"], task["base_task_id"])].append(task)
    if len(tasks) != 128 or len(truth) != 128 or len(grouped) != 64:
        raise ValueError("Unexpected task count for the eight-family crossover")
    families = sorted({task["family_id"] for task in tasks})
    if len(families) != 8:
        raise ValueError(f"Expected eight families, found {len(families)}")
    balanced = defaultdict(lambda: defaultdict(int))
    for (family, variant, base_id), twins in grouped.items():
        if len(twins) != 2 or {r["presentation_order"] for r in twins} != {
                "randomized_first", "historical_first"}:
            raise ValueError(f"Incomplete order pair: {family}/{variant}/{base_id}")
        first = twins[0]["randomized_in_family_first_order"]
        balanced[(family, variant)][first] += 1
    if any(counts != {"randomized_first": 2, "historical_first": 2}
           for counts in balanced.values()):
        raise ValueError("First-position assignment is not balanced within family and prompt variant")
    for base_id in {r["base_task_id"] for r in tasks}:
        for order in ("randomized_first", "historical_first"):
            variants = [r for r in tasks if r["base_task_id"] == base_id
                        and r["presentation_order"] == order]
            if {r["prompt_variant"] for r in variants} != {"minimal", "causal_context"}:
                raise ValueError(f"Missing paired prompt variant: {base_id}/{order}")
            numerical = []
            for row in variants:
                rate_lines = [line for line in row["prompt"].splitlines()
                              if line.startswith(("Random assignment", "Historical data"))]
                numerical.append(tuple(rate_lines))
            if numerical[0] != numerical[1]:
                raise ValueError(f"Source rates/order changed across prompt variants: {base_id}")
    if output_contract == "strict_json" and any(
            not row["prompt"].endswith(strict_instruction) for row in tasks):
        raise ValueError("The strict JSON response instruction differs across prompts")
    report = {
        "status": "validated", "families": len(families),
        "base_tasks": 32, "expanded_tasks": len(tasks),
        "matched_prompt_variant_order_pairs": len(grouped),
        "balanced_family_variant_blocks": len(balanced),
        "shared_rate_lines_across_variants": True,
        "output_contract": output_contract,
        "source_manifest_sha256": hashlib.sha256(
            (args.source / "manifest.json").read_bytes()).hexdigest(),
        "expanded_manifest_sha256": hashlib.sha256(
            (args.expanded / "manifest.json").read_bytes()).hexdigest(),
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
