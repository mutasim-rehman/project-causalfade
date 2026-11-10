"""Derive exact-evidence development diagnostics from the same world families."""
import argparse
import hashlib
import json
from pathlib import Path

PROMPT = """Apply this numeric decision rule to a table indexed by binary z and x.
Let r[z,x] be success_probability for that row. The score is the average
of r[0,1] minus r[0,0] and r[1,1] minus r[1,0]:
0.5 * ((r[0,1] - r[0,0]) + (r[1,1] - r[1,0])).
Set activate to 1 if the score is positive and 0 otherwise. Return only
JSON with keys ate_estimate (the numeric score), activate (0 or 1), and
adjustment_set (the list of variable names used to group the rows).
Evidence:
"""


SOURCE_PROMPT = """A lab wants to choose whether to activate a setting on a new machine from the same population to maximize its chance of success. Two studies report success rates:
{first}
{second}
Return only a JSON object with activate equal to 1 if the lab should activate the setting, or 0 if it should leave it off.
"""


def source_selection_prompt(task, strata, reverse=False):
    """Render rounded success rates without revealing the evaluator's action."""
    cells = {(r["z"], r["x"]): r for r in strata}
    randomized = []
    observational = []
    for x in (0, 1):
        group = [cells[z, x] for z in (0, 1)]
        randomized.append(sum(r["success_probability"] for r in group) / 2)
        observational.append(
            sum(r["success_probability"] * r["population_cell_probability"] for r in group)
            / sum(r["population_cell_probability"] for r in group)
        )
    rates = [[round(rate * 100, 2) for rate in group]
             for group in (randomized, observational)]
    for exact, rounded in zip((randomized, observational), rates):
        if rounded[0] == rounded[1] or (exact[1] > exact[0]) != (rounded[1] > rounded[0]):
            raise ValueError(f"Rounding changes an evidence sign: {task['task_id']}")
    lines = [
        f"Random assignment by the lab: off {rates[0][0]:.2f}%, on {rates[0][1]:.2f}%.",
        f"Historical data where operators chose the setting: off {rates[1][0]:.2f}%, on {rates[1][1]:.2f}%.",
    ]
    historical_first = bool(hashlib.sha256(task["family_id"].encode()).digest()[0] % 2)
    if historical_first != reverse:
        lines.reverse()
    return SOURCE_PROMPT.format(first=lines[0], second=lines[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--variant", choices=("formula", "source-selection", "source-selection-reversed"),
                        default="formula")
    args = parser.parse_args()
    source = args.source
    manifest = json.loads((source / "manifest.json").read_text())
    data = {}
    for name, digest in manifest["file_sha256"].items():
        content = (source / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f"Source digest mismatch: {name}")
        records = (json.loads(line) for line in content.splitlines())
        data[name] = [row for row in records if row["evidence_mode"] == "exact"]
    for task in data["public_tasks.jsonl"]:
        _, separator, evidence = task["prompt"].partition("\nEvidence:\n")
        if not separator or json.loads(evidence)["type"] != "exact_population_probabilities":
            raise ValueError(f"Unexpected evidence format for {task['task_id']}")
        if args.variant == "formula":
            task["prompt"] = PROMPT + evidence
        else:
            task["prompt"] = source_selection_prompt(
                task, json.loads(evidence)["strata"], reverse=args.variant.endswith("-reversed"))

    args.out.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name, records in data.items():
        content = "".join(json.dumps(r, sort_keys=True) + "\n" for r in records).encode()
        (args.out / name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    manifest.update(evidence_modes=["exact"], tasks=len(data["public_tasks.jsonl"]),
                    file_sha256=hashes, source_file_sha256=manifest["file_sha256"],
                    status={"formula": "exploratory_formula_given_arithmetic_control",
                            "source-selection": "exploratory_evidence_source_selection",
                            "source-selection-reversed": "exploratory_evidence_source_reversal"}[args.variant],
                    baseline_summary={k: v for k, v in manifest["baseline_summary"].items()
                                      if k.startswith("exact:")})
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
