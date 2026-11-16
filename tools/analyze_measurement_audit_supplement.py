"""Post-inference supplement for predeclared cohort 023 aggregate/control contrasts omitted by frozen report."""
import argparse
from collections import Counter,defaultdict
import itertools
from pathlib import Path
from statistics import mean
from causalfade.measurement_audit import validate,score_records
from causalfade.sensitivity import cluster_interval,digest,read_jsonl,write_json


def summarize(rows):
    return {'scheduled':len(rows),'valid':sum(r['valid_answer'] for r in rows),'correct':sum(r['correct'] for r in rows),
            'accuracy':mean(r['correct'] for r in rows) if rows else None,'activation_rate':mean(r['answer']=='activate' for r in rows if r['valid_answer']) if rows and rows[0]['task_type'] in ('decision','randomized_only','noncausal_control') else None}

def analyze(dataset,run,out):
    validate(dataset);raw=read_jsonl(Path(run)/'raw_responses.jsonl')
    rows=score_records(read_jsonl(Path(dataset)/'oracle_truth.jsonl'),raw)
    if len(raw)!=896 or any(not r['completed'] for r in rows):raise ValueError('Incomplete raw run')
    baseline={(r['family_id'],r['base_id']):r for r in rows if r['task_type']=='randomized_only'}
    numeric={(r['family_id'],r['base_id']):r for r in rows if r['task_type']=='numerical_control'}
    controls={(r['family_id'],r['stem_id']):r for r in rows if r['task_type']=='noncausal_control'}
    decision=[r for r in rows if r['task_type']=='decision']
    def paired(subset,other):
        by=defaultdict(list);flips=Counter()
        for y in subset:
            x=other(y);by[y['family_id']].append(x['correct']-y['correct'])
            if x['valid_answer'] and y['valid_answer']:flips[x['answer']+'->'+y['answer']]+=1
        return {'other_minus_decision':cluster_interval([mean(v) for v in by.values()]),'action_flips_other_to_decision':dict(flips)}
    out_data={'classification':'post_inference_supplement_of_predeclared_outcomes',
              'raw_sha256':digest(Path(run)/'raw_responses.jsonl'),
              'source_reason':'Frozen analysis omitted aggregate paired and numeric-direction summaries; no scoring or fixture changes.',
              'overall_paired_randomized_only':paired(decision,lambda y:baseline[(y['family_id'],y['base_id'])]),
              'overall_paired_noncausal':paired(decision,lambda y:controls[(y['family_id'],y['stem_id'])]),
              'by_direction':{},'by_name':{},'by_answer_order':{},'by_physical_order':{},'by_condition':{}}
    for key,values in [('by_direction',(0,1)),('by_name',('A','B')),('by_answer_order',('canonical','reversed')),
                       ('by_physical_order',('randomized_first','historical_first')),('by_condition',('aligned','conflict'))]:
        attr={'by_direction':'causal_positive','by_name':'randomized_name','by_answer_order':'answer_order','by_physical_order':'presentation_order','by_condition':'condition'}[key]
        for val in values:
            subset=[r for r in decision if r[attr]==val]
            out_data[key][str(val)]={'decision':summarize(subset),
                'randomized_only_minus_decision':paired(subset,lambda y:baseline[(y['family_id'],y['base_id'])])}
    for kind in ('numerical_control','noncausal_control'):
        out_data[kind]={}
        for direction in (0,1):
            subset=[r for r in rows if r['task_type']==kind and r['causal_positive']==direction]
            by=defaultdict(list)
            for r in subset:by[r['family_id']].append(r['correct'])
            out_data[kind][str(direction)]={**summarize(subset),'family_interval':cluster_interval([mean(v) for v in by.values()])}
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    write_json(out,out_data);return out_data
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for x in ('dataset','run','out'):p.add_argument('--'+x,type=Path,required=True)
    a=p.parse_args();analyze(a.dataset,a.run,a.out)
