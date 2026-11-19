"""Analyze frozen development rows with family-level paired switch fidelity."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from run_cohort026 import BASE, rows


def analyze(model_id):
    plan=json.loads((BASE/'frozen_development_plan.json').read_text())
    tasks=[t for t in rows(BASE/'input/public_tasks.jsonl') if t['split']=='development']
    truth={t['task_id']:t for t in rows(BASE/'input/oracle_truth.jsonl')}
    raw=rows(BASE/'runs'/model_id/'raw_responses.jsonl')
    predictions={r['task_id']:r for r in raw}
    if len(predictions)!=len(raw) or set(predictions)!=set(t['task_id'] for t in tasks):
        raise ValueError('Incomplete or duplicate development schedule')
    result={'model_id':model_id,'scheduled':len(tasks),'valid':sum(predictions[t['task_id']].get('answer') is not None for t in tasks),'forms':{}}
    for form in plan['forms']:
        group=[t for t in tasks if t['form']==form]
        cells=defaultdict(list)
        by_family=defaultdict(dict)
        for t in group:
            r=predictions[t['task_id']]
            expected=truth[t['task_id']]['expected']
            correct=r.get('answer')==expected
            cells[t['kind']].append(correct)
            if t['kind']=='switch':
                polarity=expected
                cells['switch_'+polarity].append(correct)
                by_family[t['family_id']][t['graph']]=correct
        paired=[len(v)==2 and all(v.values()) for v in by_family.values()]
        rates={k:sum(v)/len(v) for k,v in cells.items()}
        rates['paired_switch_fidelity']=sum(paired)/len(paired)
        rates['strict_validity']=sum(predictions[t['task_id']].get('answer') is not None for t in group)/len(group)
        gates=plan['gates']
        checks={'strict_validity':rates['strict_validity']>=gates['strict_validity'],
                'graph_accuracy':rates['graph']>=gates['graph_accuracy'],
                'arithmetic_accuracy':rates['arithmetic']>=gates['arithmetic_accuracy'],
                'switch_accuracy_each_polarity':all(rates['switch_'+p]>=gates['switch_accuracy_each_polarity'] for p in ('X=0','X=1')),
                'no_change_accuracy':rates['no_change']>=gates['no_change_accuracy'],
                'paired_switch_fidelity':rates['paired_switch_fidelity']>=gates['paired_switch_fidelity']}
        result['forms'][form]={'rates':rates,'counts':{k:{'correct':sum(v),'scheduled':len(v)} for k,v in cells.items()},
                               'paired':{'correct':sum(paired),'scheduled':len(paired)},'checks':checks,
                               'qualified':all(checks.values())}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model_id');a=p.parse_args()
    report=analyze(a.model_id)
    target=BASE/'runs'/a.model_id/'development_analysis.json'
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
