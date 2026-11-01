"""Generate public prompts, separate oracle truth, and reference baselines."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from .worlds import make_families, exact_evidence, opaque_id, prompt, backdoor_estimate, naive_estimate


def generate(out, families=24, seed=20261101, rows=2000):
    if rows < 1:
        raise ValueError('rows must be positive')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed+1)
    tasks, truth, baselines = [], [], []
    for world in make_families(families, seed):
        for mode in ('exact', 'sampled'):
            task_id = opaque_id(world, seed, mode)
            counts = world.sample_counts(rows, rng) if mode == 'sampled' else None
            evidence = exact_evidence(world) if mode == 'exact' else {'type': 'observational_sample', 'strata': counts}
            tasks.append(dict(task_id=task_id, family_id=world.family_id, evidence_mode=mode,
                              prompt=prompt(world, evidence)))
            truth.append(dict(task_id=task_id, evidence_mode=mode, **world.truth()))
            estimates = {'backdoor': world.tau if counts is None else backdoor_estimate(counts),
                         'association': world.observational_difference if counts is None else naive_estimate(counts),
                         'random': None}
            for name, estimate in estimates.items():
                action = int(rng.integers(2)) if name == 'random' else (None if estimate is None else int(estimate > 0))
                baselines.append(dict(task_id=task_id, family_id=world.family_id, evidence_mode=mode,
                                      baseline=name, ate_estimate=estimate, activate=action,
                                      correct=None if action is None else action == world.causal_positive,
                                      regret=None if action is None else float(abs(world.tau)*(action != world.causal_positive)),
                                      missing_stratum=action is None))
    checksums = {}
    for name, records in [('public_tasks.jsonl', tasks), ('oracle_truth.jsonl', truth), ('baselines.jsonl', baselines)]:
        data = ''.join(json.dumps(r, sort_keys=True)+'\n' for r in records).encode()
        (out/name).write_bytes(data)
        checksums[name] = hashlib.sha256(data).hexdigest()
    metadata = dict(seed=seed, families=families, tasks=len(tasks), sampled_rows_per_task=rows,
                    evidence_modes=['exact', 'sampled'], status='synthetic_design_validation_not_LLM_results',
                    numpy_version=np.__version__, file_sha256=checksums,
                    baseline_summary={f'{mode}:{name}': {
                        'accuracy': float(np.mean([r['correct'] for r in baselines if r['evidence_mode']==mode and r['baseline']==name and r['correct'] is not None])),
                        'invalid_count': sum(r['activate'] is None for r in baselines if r['evidence_mode']==mode and r['baseline']==name)}
                        for mode in ('exact','sampled') for name in estimates})
    (out/'manifest.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='results/design_validation')
    parser.add_argument('--families', type=int, default=24)
    parser.add_argument('--seed', type=int, default=20261101)
    parser.add_argument('--rows', type=int, default=2000)
    args = parser.parse_args()
    print(json.dumps(generate(args.out, args.families, args.seed, args.rows), indent=2))
