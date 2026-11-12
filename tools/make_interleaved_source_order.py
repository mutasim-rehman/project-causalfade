"""Create matched prompt-order twins for a same-session order experiment."""
import argparse
import hashlib
import json
import random
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def write_jsonl(path, rows):
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode()
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261112)
    args = parser.parse_args()
    manifest = json.loads((args.source / "manifest.json").read_text())
    for name, digest in manifest["file_sha256"].items():
        actual = hashlib.sha256((args.source / name).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"Source digest mismatch for {name}")
    selected = {row["task_id"] for row in json.loads(args.schedule.read_text())}
    tasks = [row for row in read_jsonl(args.source / "public_tasks.jsonl")
             if row["task_id"] in selected]
    truths = {row["task_id"]: row for row in read_jsonl(args.source / "oracle_truth.jsonl")}
    baselines = {row["task_id"]: row for row in read_jsonl(args.source / "baselines.jsonl")}
    if len(tasks) != len(selected) or any(task_id not in truths for task_id in selected):
        raise ValueError("Schedule and source task sets do not match")

    by_family = {}
    for task in tasks:
        by_family.setdefault(task["family_id"], []).append(task)
    rng = random.Random(args.seed)
    historical_first_ids = set()
    for family, family_tasks in sorted(by_family.items()):
        if len(family_tasks) != 4:
            raise ValueError(f"Family {family} does not contain four cells")
        randomized_assignment = [True, True, False, False]
        rng.shuffle(randomized_assignment)
        historical_first_ids.update(
            task["task_id"] for task, randomized_first in zip(family_tasks, randomized_assignment)
            if not randomized_first
        )

    expanded_tasks, expanded_truth, expanded_baselines = [], [], []
    for task in tasks:
        truth = truths[task["task_id"]]
        baseline = baselines[task["task_id"]]
        lines = task["prompt"].splitlines()
        randomized_line = next(line for line in lines if line.startswith("Random assignment"))
        historical_line = next(line for line in lines if line.startswith("Historical data"))
        order_prompts = {
            "randomized_first": "\n".join([
                "A lab wants to choose whether to activate a setting on a new machine from the same population to maximize its chance of success. Two studies report success rates:",
                randomized_line, historical_line,
                "Return only a JSON object with activate equal to 1 if the lab should activate the setting, or 0 if it should leave it off.",
            ]),
            "historical_first": "\n".join([
                "A lab wants to choose whether to activate a setting on a new machine from the same population to maximize its chance of success. Two studies report success rates:",
                historical_line, randomized_line,
                "Return only a JSON object with activate equal to 1 if the lab should activate the setting, or 0 if it should leave it off.",
            ]),
        }
        assigned = "historical_first" if task["task_id"] in historical_first_ids else "randomized_first"
        for order in ("randomized_first", "historical_first"):
            task_id = hashlib.sha256(f"{task['task_id']}:{order}".encode()).hexdigest()[:20]
            expanded_tasks.append({
                "task_id": task_id, "family_id": task["family_id"],
                "evidence_mode": "exact", "order_pair_id": task["task_id"],
                "presentation_order": order,
                "randomized_in_family_first_order": assigned,
                "prompt": order_prompts[order],
            })
            expanded_truth.append({**truth, "task_id": task_id, "order_pair_id": task["task_id"],
                                   "presentation_order": order})
            expanded_baselines.append({**baseline, "task_id": task_id,
                                       "order_pair_id": task["task_id"],
                                       "presentation_order": order})

    args.out.mkdir(parents=True, exist_ok=False)
    hashes = {
        "public_tasks.jsonl": write_jsonl(args.out / "public_tasks.jsonl", expanded_tasks),
        "oracle_truth.jsonl": write_jsonl(args.out / "oracle_truth.jsonl", expanded_truth),
        "baselines.jsonl": write_jsonl(args.out / "baselines.jsonl", expanded_baselines),
    }
    manifest.update(
        tasks=len(expanded_tasks), evidence_modes=["exact"],
        source_manifest_sha256=hashlib.sha256((args.source / "manifest.json").read_bytes()).hexdigest(),
        source_schedule_sha256=hashlib.sha256(args.schedule.read_bytes()).hexdigest(),
        order_assignment_seed=args.seed,
        status="interleaved_within_family_order_assignment", file_sha256=hashes,
    )
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"families": len(by_family), "base_tasks": len(tasks),
                      "expanded_tasks": len(expanded_tasks), "seed": args.seed,
                      "sha256": hashes}, indent=2))


if __name__ == "__main__":
    main()
