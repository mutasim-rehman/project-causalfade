"""Score structured agent outputs without dropping invalid or missing decisions.

Predictions JSONL: task_id, activate, ate_estimate, adjustment_set.
One invocation scores one checkpoint/configuration/run; provenance is required.
"""
import argparse
import json
import math
from pathlib import Path


def score(truth_records, predictions):
    truth={r['task_id']:r for r in truth_records}
    if len(truth)!=len(truth_records):
        raise ValueError('Duplicate oracle task IDs.')
    seen={}
    for record in predictions:
        key=record['task_id']
        if key not in truth:
            raise ValueError(f'Unknown task ID: {key}')
        if key in seen:
            raise ValueError(f'Duplicate prediction for task: {key}')
        seen[key]=record
    rows=[]
    for key,t in truth.items():
        p=seen.get(key,{})
        action=p.get('activate')
        valid=type(action) is int and action in (0,1)
        estimate=p.get('ate_estimate')
        numeric=type(estimate) in (int,float) and math.isfinite(estimate)
        adjustment=p.get('adjustment_set')
        adjustment_valid=isinstance(adjustment,list) and len(adjustment)==1 and adjustment[0]=='Z'
        rows.append(dict(task_id=key,family_id=t['family_id'],evidence_mode=t['evidence_mode'],
                         causal_positive=t['causal_positive'],association_positive=t['association_positive'],
                         conflict=t['conflict'],missing_prediction=key not in seen,valid_action=valid,
                         # Intention-to-evaluate accuracy: missing/invalid actions count as failures.
                         correct=int(valid and action==t['optimal_action']),
                         activate=action if valid else None,
                         regret=abs(t['ate'])*(action!=t['optimal_action']) if valid else None,
                         ate_error=estimate-t['ate'] if numeric else None,
                         numeric_estimate_valid=numeric,adjustment_valid=adjustment_valid))
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--truth',required=True)
    parser.add_argument('--predictions',required=True)
    parser.add_argument('--provenance',required=True,help='JSON file: checkpoint, precision, quantizer, seed, evidence_source')
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    provenance=json.loads(Path(args.provenance).read_text(encoding='utf-8'))
    required={'checkpoint','precision','quantizer','seed','evidence_source'}
    if not required<=provenance.keys():
        raise ValueError(f'Missing provenance fields: {required-provenance.keys()}')
    read=lambda file:[json.loads(line) for line in Path(file).read_text(encoding='utf-8').splitlines() if line.strip()]
    rows=score(read(args.truth),read(args.predictions))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(''.join(json.dumps({**r,'provenance':provenance},allow_nan=False)+'\n' for r in rows),encoding='utf-8')
    print(json.dumps({'tasks':len(rows),'invalid_actions':sum(not r['valid_action'] for r in rows),
                      'accuracy':sum(r['correct'] for r in rows)/len(rows) if rows else None}))
