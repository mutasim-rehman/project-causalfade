"""Paired family-bootstrap accuracy contrasts for two scored configurations.

This is a nonparametric pilot analysis, not the planned hierarchical GLMM.
"""
import argparse
import json
from pathlib import Path
import numpy as np


def paired_contrast(reference, comparison, mode='exact', seed=20261101, bootstrap=2000):
    if bootstrap < 2:
        raise ValueError('Need at least two bootstrap replicates.')
    def index(rows):
        records=[r for r in rows if r['evidence_mode']==mode]
        indexed={r['task_id']:r for r in records}
        if len(indexed)!=len(records):
            raise ValueError('Duplicate task IDs; analyze one run/configuration at a time.')
        return indexed
    ref,comp=index(reference),index(comparison)
    if not ref or ref.keys()!=comp.keys():
        raise ValueError('Both configurations must contain the same nonempty task set.')
    families={}
    for key,r in ref.items():
        c=comp[key]
        for field in ('family_id','conflict','causal_positive','association_positive'):
            if r[field]!=c[field]:
                raise ValueError('Paired truth differs between configurations.')
        families.setdefault(r['family_id'],[]).append((r,c))
    if len(families)<2:
        raise ValueError('Need at least two independent families.')
    blocks=[]
    for records in families.values():
        if len(records)!=4 or {(r['causal_positive'],r['association_positive']) for r,c in records}!={(0,0),(0,1),(1,0),(1,1)}:
            raise ValueError('Each family must contain all four conditions exactly once.')
        blocks.append([np.mean([pair[j]['correct'] for pair in records if pair[j]['conflict']==conflict])
                       for j in (0,1) for conflict in (False,True)])
    blocks=np.asarray(blocks,float)  # ref aligned/conflict, comp aligned/conflict
    effect=(blocks[:,2]-blocks[:,3])-(blocks[:,0]-blocks[:,1])
    rng=np.random.default_rng(seed)
    draws=rng.integers(0,len(blocks),size=(bootstrap,len(blocks)))
    simulated=effect[draws].mean(axis=1)
    means=blocks.mean(axis=0)
    return dict(evidence_mode=mode,families=len(blocks),tasks_per_configuration=len(ref),
                reference_accuracy_aligned=float(means[0]),reference_accuracy_conflict=float(means[1]),
                comparison_accuracy_aligned=float(means[2]),comparison_accuracy_conflict=float(means[3]),
                delta_conflict_penalty=float(effect.mean()),
                paired_family_bootstrap_percentile_95_interval=np.quantile(simulated,[.025,.975]).tolist(),
                bootstrap_replicates=bootstrap,seed=seed,
                reference_invalid=sum(not r['valid_action'] for r in ref.values()),
                comparison_invalid=sum(not r['valid_action'] for r in comp.values()),
                inference_scope='pilot paired-family percentile bootstrap; no calibrated p-value or hierarchical GLMM')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True)
    parser.add_argument('--comparison',required=True)
    parser.add_argument('--mode',choices=['exact','sampled'],default='exact')
    parser.add_argument('--seed',type=int,default=20261101)
    parser.add_argument('--bootstrap',type=int,default=2000)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    read=lambda p:[json.loads(line) for line in Path(p).read_text(encoding='utf-8').splitlines() if line.strip()]
    result=paired_contrast(read(args.reference),read(args.comparison),args.mode,args.seed,args.bootstrap)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
