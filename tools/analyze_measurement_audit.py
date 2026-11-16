"""Recompute cohort 023 development analysis solely from frozen truth and raw attempts."""
import argparse
from collections import Counter,defaultdict
import itertools
import json
from pathlib import Path
from statistics import mean

from causalfade.measurement_audit import validate,score_records
from causalfade.sensitivity import cluster_interval,digest,read_jsonl,write_json
from measurement_audit_pilot import load_run,source_hashes

DECISIONS=('decision','randomized_only','noncausal_control')

def cell(rows):
    valid=[r for r in rows if r['valid_answer']]
    return {'scheduled':len(rows),'completed':sum(r['completed'] for r in rows),'valid':len(valid),
            'correct':sum(r['correct'] for r in rows),'accuracy':mean(r['correct'] for r in rows) if rows else None,
            'activation_rate_valid':mean(r['answer']=='activate' for r in valid) if valid and rows[0]['task_type'] in DECISIONS else None,
            'finish_reasons':dict(Counter(r['finish_reason'] or 'none' for r in rows))}

def interval(rows):
    by=defaultdict(list)
    for r in rows:by[r['family_id']].append(r['correct'])
    return cluster_interval([mean(v) for v in by.values()])

def predictions(r):
    first_source=r['randomized_name'] if r['presentation_order']=='randomized_first' else r['historical_name']
    last_source=r['historical_name'] if r['presentation_order']=='randomized_first' else r['randomized_name']
    signs={'randomized_source':r['causal_positive'],'historical_source':r['association_positive'],
           'first_source':r['causal_positive'] if r['presentation_order']=='randomized_first' else r['association_positive'],
           'last_source':r['association_positive'] if r['presentation_order']=='randomized_first' else r['causal_positive'],
           'always_activate':1,'always_leave_off':0,
           'first_answer':1 if r['answer_order']=='canonical' else 0,
           'last_answer':0 if r['answer_order']=='canonical' else 1}
    if r['task_type']=='source_selection':
        return {'randomized_source':r['randomized_name'],'historical_source':r['historical_name'],
                'first_source':first_source,'last_source':last_source,'always_A':'A','always_B':'B',
                'first_answer':'A' if r['answer_order']=='canonical' else 'B',
                'last_answer':'B' if r['answer_order']=='canonical' else 'A'}
    return {k:'activate' if v else 'leave_off' for k,v in signs.items()}

def analyze(dataset,run,out):
    config,rows=load_run(run,dataset)
    if config['checkpoint']!='qwen_f16':raise ValueError('Checkpoint mismatch')
    grouped=defaultdict(list)
    for r in rows:
        grouped[r['task_type']].append(r)
        if r['task_type']=='decision':
            key='|'.join(str(r[k]) for k in ('causal_positive','condition','presentation_order','randomized_name','answer_order'))
            grouped['decision|'+key].append(r)
        if r['task_type']=='source_selection':grouped['selection|'+r['randomized_name']].append(r)
        if r['task_type'] in DECISIONS:grouped[r['task_type']+'|beneficial' if r['causal_positive'] else r['task_type']+'|harmful'].append(r)
    cells={k:{**cell(v),'family_interval':interval(v)} for k,v in sorted(grouped.items())}
    base=defaultdict(dict);variants=defaultdict(dict)
    for r in rows:
        if r['task_type']=='randomized_only':base[(r['family_id'],r['base_id'])]=r
        if r['task_type'] in ('decision','noncausal_control','source_selection'):variants[(r['family_id'],r['stem_id'])][r['task_type']]=r
    contrasts={}
    for condition,order,name,ao in itertools.product(('aligned','conflict'),('randomized_first','historical_first'),('A','B'),('canonical','reversed')):
        by=defaultdict(list);flips=Counter();control=defaultdict(list);control_flips=Counter()
        for (family,_),v in variants.items():
            y=v['decision']
            if (y['condition'],y['presentation_order'],y['randomized_name'],y['answer_order'])!=(condition,order,name,ao):continue
            x=base[(family,y['base_id'])];z=v['noncausal_control']
            by[family].append(y['correct']-x['correct']);control[family].append(y['correct']-z['correct'])
            if x['valid_answer'] and y['valid_answer']:flips[x['answer']+'->'+y['answer']]+=1
            if z['valid_answer'] and y['valid_answer']:control_flips[z['answer']+'->'+y['answer']]+=1
        key='|'.join((condition,order,name,ao))
        contrasts[key]={'two_source_minus_randomized_only':cluster_interval([mean(v) for v in by.values()]),
                        'decision_minus_noncausal_control':cluster_interval([mean(v) for v in control.values()]),
                        'baseline_to_two_source_action_flips':dict(flips),'control_to_decision_action_flips':dict(control_flips)}
    policy={};identical={}
    for kind in ('decision','source_selection'):
        test=grouped[kind];by_policy=defaultdict(list);same=Counter();names=tuple(predictions(test[0]))
        for r in test:
            p=predictions(r)
            for k,v in p.items():by_policy[k].append((r,v))
            for a,b in itertools.combinations(names,2):
                if p[a]==p[b]:same[a+'|'+b]+=1
        policy[kind]={k:{'agreement_with_model':sum(r['valid_answer'] and r['answer']==v for r,v in pairs),
                         'accuracy_against_oracle':sum(v==(r['randomized_name'] if kind=='source_selection' else ('activate' if r['optimal_action'] else 'leave_off')) for r,v in pairs),
                         'scheduled':len(pairs)} for k,pairs in by_policy.items()}
        identical[kind]={'scheduled':len(test),'equal_prediction_counts':dict(same)}
    # Fit only the simplest action-bias policy on first four families; evaluate on held-out four.
    train=set(json.loads((Path(dataset)/'manifest.json').read_text())['training_families'])
    options=('always_activate','always_leave_off','first_answer','last_answer')
    training=[r for r in grouped['decision'] if r['family_id'] in train]
    chosen=max(options,key=lambda k:(sum(r['answer']==predictions(r)[k] for r in training if r['valid_answer']),-options.index(k)))
    held=[r for r in grouped['decision'] if r['family_id'] not in train]
    fitted={'training_families':sorted(train),'heldout_families':sorted({r['family_id'] for r in held}),
            'selected_policy':chosen,'training_agreement':sum(r['valid_answer'] and r['answer']==predictions(r)[chosen] for r in training),
            'heldout_agreement':sum(r['valid_answer'] and r['answer']==predictions(r)[chosen] for r in held),
            'training_n':len(training),'heldout_n':len(held)}
    output={'classification':'development_only','manifest_sha256':digest(Path(dataset)/'manifest.json'),
            'run_config_sha256':digest(Path(run)/'config.json'),'source_sha256':source_hashes(),
            'overall':cell(rows),'cells':cells,'paired_contrasts':contrasts,'fixed_policies':policy,
            'policy_prediction_overlap':identical,'fitted_action_bias_holdout':fitted,
            'qualification':{'valid_rate_min':.95,'source_selection_each_name_min':.75,'randomized_only_each_direction_min':.75,
                             'passed':(cell(rows)['valid']/len(rows)>=.95 and all(cells['selection|'+n]['accuracy']>=.75 for n in ('A','B')) and all(cells['randomized_only|'+d]['accuracy']>=.75 for d in ('beneficial','harmful')))},
            'limitations':['Eight development families; percentile intervals are coarse.','Constant-policy zero-width intervals are not equivalence evidence.',
                           'Separate source and decision requests are not a mediation chain.','Policy response agreement is descriptive, not a psychological latent-route identification.']}
    out=Path(out)
    if out.exists() or out.with_suffix('.md').exists():raise FileExistsError(out)
    write_json(out,output)
    lines=['# Cohort 023 measurement audit','', 'Development-only. Full cell-level results and policy overlaps are in JSON.','']
    for k in ('decision','source_selection','randomized_only','numerical_control','noncausal_control'):
        c=cells[k];lines.append(f'- {k}: {c["correct"]}/{c["scheduled"]} correct; {c["valid"]} valid; activation {c["activation_rate_valid"]}.')
    lines+=['',f'Qualification passed: {output["qualification"]["passed"]}.',f'Fitted action-bias policy: {chosen}; held-out agreement {fitted["heldout_agreement"]}/{fitted["heldout_n"]}.','']
    out.with_suffix('.md').write_text('\n'.join(lines),encoding='utf-8')
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for x in ('dataset','run','out'):p.add_argument('--'+x,type=Path,required=True)
    a=p.parse_args();analyze(a.dataset,a.run,a.out)
