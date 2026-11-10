"""Build an exact-evidence arithmetic control using the same four-cell inputs."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
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
        task["prompt"] = PROMPT + evidence

    args.out.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name, records in data.items():
        content = "".join(json.dumps(r, sort_keys=True) + "\n" for r in records).encode()
        (args.out / name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    manifest.update(evidence_modes=["exact"], tasks=len(data["public_tasks.jsonl"]),
                    file_sha256=hashes, source_file_sha256=manifest["file_sha256"],
                    status="exploratory_formula_given_arithmetic_control",
                    baseline_summary={k: v for k, v in manifest["baseline_summary"].items()
                                      if k.startswith("exact:")})
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
