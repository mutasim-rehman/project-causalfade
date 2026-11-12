"""Expand matched source tasks by evidence order and causal-context framing."""
import argparse
import hashlib
import json
import random
from pathlib import Path


FRAMES = ("minimal", "causal_context")
CONTEXT = (
    "A setting X may affect success Y. Initial severity Z affects both whether "
    "operators selected X in older records and whether the machine succeeds. "
    "The target population is the same as in the lab study. The lab assigned X "
    "at random; in the historical records, operators chose whether to use X. "
    "Because severity influenced historical choice and success, historical rate "
    "differences may reflect severity mix as well as the effect of X. Decide "
    "whether activating X would improve success under intervention in this "
    "target population."
)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def write_jsonl(path, rows):
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode()
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def expand(source, schedule_path, out, seed):
    source = Path(source)
    manifest = json.loads((source / "manifest.json").read_text())
    for name, expected in manifest["file_sha256"].items():
        actual = hashlib.sha256((source / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Source checksum mismatch: {name}")
    selected = [row["task_id"] for row in json.loads(Path(schedule_path).read_text())]
    public = {row["task_id"]: row for row in read_jsonl(source / "public_tasks.jsonl")}
    truths = {row["task_id"]: row for row in read_jsonl(source / "oracle_truth.jsonl")}
    # Read the small baseline table once, retaining all baseline records by task.
    baseline_rows = {}
    for row in read_jsonl(source / "baselines.jsonl"):
        baseline_rows.setdefault(row["task_id"], []).append(row)
    if len(selected) != len(set(selected)) or any(t not in public for t in selected):
        raise ValueError("Base schedule contains missing or duplicate task IDs")
    by_family = {}
    for task_id in selected:
        by_family.setdefault(public[task_id]["family_id"], []).append(public[task_id])
    if any(len(rows) != 4 for rows in by_family.values()):
        raise ValueError("Each selected family must have exactly four causal/association cells")

    rng = random.Random(seed)
    first_order = {}
    for frame in FRAMES:
        for family, tasks in sorted(by_family.items()):
            assignment = [True, True, False, False]
            rng.shuffle(assignment)
            first_order.update({(frame, task["task_id"]):
                                ("randomized_first" if random_first else "historical_first")
                                for task, random_first in zip(tasks, assignment)})

    expanded, expanded_truth, expanded_baselines = [], [], []
    for task_id in selected:
        task, truth = public[task_id], truths[task_id]
        baselines_for_task = baseline_rows[task_id]
        lines = task["prompt"].splitlines()
        randomized_line = next(line for line in lines if line.startswith("Random assignment"))
        historical_line = next(line for line in lines if line.startswith("Historical data"))
        for frame in FRAMES:
            prefix = ("A lab wants to choose whether to activate a setting on a new machine "
                      "from the same population to maximize its chance of success. "
                      "Two studies report success rates:")
            if frame == "causal_context":
                prefix = CONTEXT + " The two studies report these success rates:"
            for order, source_lines in (
                    ("randomized_first", [randomized_line, historical_line]),
                    ("historical_first", [historical_line, randomized_line])):
                expanded_id = hashlib.sha256(
                    f"{task_id}:{frame}:{order}".encode()).hexdigest()[:20]
                pair_id = f"{task_id}:{frame}"
                expanded.append({
                    "task_id": expanded_id, "family_id": task["family_id"],
                    "evidence_mode": "exact", "base_task_id": task_id,
                    "order_pair_id": pair_id, "presentation_order": order,
                    "prompt_variant": frame,
                    "randomized_in_family_first_order": first_order[(frame, task_id)],
                    "prompt": "\n".join([
                        prefix, *source_lines,
                        "Return only a JSON object with activate equal to 1 if the lab should activate the setting, or 0 if it should leave it off.",
                    ]),
                })
                expanded_truth.append({
                    **truth, "task_id": expanded_id, "base_task_id": task_id,
                    "order_pair_id": pair_id, "presentation_order": order,
                    "prompt_variant": frame,
                })
                expanded_baselines.extend({
                    **baseline, "task_id": expanded_id, "base_task_id": task_id,
                    "order_pair_id": pair_id, "presentation_order": order,
                    "prompt_variant": frame,
                } for baseline in baselines_for_task)

    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    hashes = {
        "public_tasks.jsonl": write_jsonl(out / "public_tasks.jsonl", expanded),
        "oracle_truth.jsonl": write_jsonl(out / "oracle_truth.jsonl", expanded_truth),
        "baselines.jsonl": write_jsonl(out / "baselines.jsonl", expanded_baselines),
    }
    manifest.update({
        "tasks": len(expanded), "prompt_variants": list(FRAMES),
        "source_manifest_sha256": hashlib.sha256(
            (source / "manifest.json").read_bytes()).hexdigest(),
        "source_schedule_sha256": hashlib.sha256(Path(schedule_path).read_bytes()).hexdigest(),
        "order_and_prompt_assignment_seed": seed,
        "status": "paired_prompt_clarity_development_crossover",
        "file_sha256": hashes,
    })
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {"families": len(by_family), "base_tasks": len(selected),
            "prompt_variants": list(FRAMES), "expanded_tasks": len(expanded),
            "order_pairs": len(expanded) // 2, "seed": seed, "sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(expand(args.source, args.schedule, args.out, args.seed), indent=2))


if __name__ == "__main__":
    main()
