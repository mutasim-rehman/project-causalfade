"""Generate exact source-selection tasks with matched observational effects."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from causalfade.worlds import (exact_evidence, make_matched_signal_families,
                               opaque_id)
from make_arithmetic_control import source_selection_prompt


def write_jsonl(path, rows):
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode()
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def generate(out, families, seed):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    tasks, truths, baselines, evaluator_evidence = [], [], [], []
    for world in make_matched_signal_families(families, seed):
        task_id = opaque_id(world, seed, "exact")
        evidence = exact_evidence(world)
        evaluator_evidence.append({"task_id": task_id, **evidence})
        tasks.append({"task_id": task_id, "family_id": world.family_id,
                      "evidence_mode": "exact",
                      "prompt": source_selection_prompt(
                          {"task_id": task_id, "family_id": world.family_id},
                          evidence["strata"])})
        truth = {"task_id": task_id, "evidence_mode": "exact", **world.truth()}
        truths.append(truth)
        backdoor_action = world.causal_positive
        association_action = int(world.observational_difference > 0)
        for baseline, action in (("backdoor", backdoor_action),
                                 ("association", association_action)):
            baselines.append({"task_id": task_id, "family_id": world.family_id,
                              "evidence_mode": "exact", "baseline": baseline,
                              "ate_estimate": (world.tau if baseline == "backdoor"
                                               else world.observational_difference),
                              "activate": action,
                              "correct": action == world.causal_positive,
                              "regret": float(abs(world.tau) *
                                              (action != world.causal_positive)),
                              "missing_stratum": False})

    hashes = {
        "public_tasks.jsonl": write_jsonl(out / "public_tasks.jsonl", tasks),
        "oracle_truth.jsonl": write_jsonl(out / "oracle_truth.jsonl", truths),
        "baselines.jsonl": write_jsonl(out / "baselines.jsonl", baselines),
        "evaluator_exact_evidence.jsonl": write_jsonl(
            out / "evaluator_exact_evidence.jsonl", evaluator_evidence),
    }
    target_magnitudes = [abs(row["observational_difference"]) for row in truths]
    randomized_magnitudes = [abs(row["ate"]) for row in truths]
    manifest = {
        "seed": seed, "families": families, "tasks": len(tasks),
        "evidence_modes": ["exact"],
        "design": "matched_observational_magnitude_source_selection",
        "design_parameters": {
            "effect_size_uniform": [0.06, 0.12],
            "severity_gap_uniform": [0.68, 0.80],
            "target_observational_magnitude_uniform": [0.38, 0.46],
            "assignment_strength_formula": "(target magnitude - effect_size if aligned, + effect_size if conflict) / severity_gap",
        },
        "source_strength_summary": {
            "randomized_absolute_difference_min": min(randomized_magnitudes),
            "randomized_absolute_difference_max": max(randomized_magnitudes),
            "observational_absolute_difference_min": min(target_magnitudes),
            "observational_absolute_difference_max": max(target_magnitudes),
            "backdoor_accuracy": float(np.mean([r["correct"] for r in baselines
                                                 if r["baseline"] == "backdoor"])),
            "association_accuracy": float(np.mean([r["correct"] for r in baselines
                                                    if r["baseline"] == "association"])),
        },
        "numpy_version": np.__version__, "file_sha256": hashes,
        "status": "development_fixture_frozen_before_model_inference",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--families", type=int, default=16)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.out, args.families, args.seed), indent=2))


if __name__ == "__main__":
    main()
