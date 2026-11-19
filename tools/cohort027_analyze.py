"""Integer gates and family-paired analysis for cohort 027."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from cohort027_prepare import BASE, jsonl, atomic_json, verify


def ceil_fraction(n,pct):
    return (n*pct+99)//100


def score(tasks,truth,records,split):
    by_id={r['task_id']:r for r in records}
    if len(by_id)!=len(records) or set(by_id)!={t['task_id'] for t in tasks}:
        raise ValueError('Incomplete or duplicate arm; analyze only complete scheduled arms')
    expected={r['task_id']:r['expected'] for r in truth}
    if set(expected)!=set(by_id):raise ValueError('Truth mismatch')
    n_families=8 if split=='development' else 16
    output={}
    for form in ('direct','decision'):
        group=[t for t in tasks if t['form']==form]
        def count(sub):
            return {'correct':sum(by_id[t['task_id']].get('strict_answer')==expected[t['task_id']] for t in sub),'scheduled':len(sub)}
        def check(sub,pct):
            c=count(sub);return c['correct']>=ceil_fraction(c['scheduled'],pct)
        main=lambda t:t['kind']=='main'
        graph=lambda t:t['kind']=='graph'
        arithmetic=lambda t:t['kind']=='arithmetic'
        z=lambda t:main(t) and t['graph']=='confounder_z'
        cells={
            'validity':{'correct':sum(by_id[t['task_id']].get('strict_answer') is not None for t in group),'scheduled':len(group)},
            'graph':count([t for t in group if graph(t)]),
            'arithmetic':count([t for t in group if arithmetic(t)]),
            'added_z':count([t for t in group if z(t)]),
        }
        for label in ('upstream','downstream'):
            cells['graph_'+label]=count([t for t in group if graph(t) and expected[t['task_id']]==label])
        for action in ('X=0','X=1'):
            cells['arithmetic_'+action]=count([t for t in group if arithmetic(t) and expected[t['task_id']]==action])
            cells['added_z_'+action]=count([t for t in group if z(t) and expected[t['task_id']]==action])
            for order in ('forward','reverse'):
                cells['switch_'+action+'_'+order]=count([t for t in group if main(t) and t['graph']!='confounder_z' and expected[t['task_id']]==action and t['order']==order])
        paired=[]
        for fid in sorted({t['family_id'] for t in group}):
            four=[t for t in group if t['family_id']==fid and main(t) and t['graph'] in ('confounder','mediator')]
            if len(four)!=4:raise ValueError('Missing switch quartet')
            paired.append(all(by_id[t['task_id']].get('strict_answer')==expected[t['task_id']] for t in four))
        cells['paired_switch']={'correct':sum(paired),'scheduled':len(paired)}
        gate={
            'validity':cells['validity']['correct']>=ceil_fraction(len(group),95),
            'graph_overall':check([t for t in group if graph(t)],80),
            'graph_each_label':all(check([t for t in group if graph(t) and expected[t['task_id']]==a],80) for a in ('upstream','downstream')),
            'arithmetic_overall':check([t for t in group if arithmetic(t)],80),
            'arithmetic_each_action':all(check([t for t in group if arithmetic(t) and expected[t['task_id']]==a],80) for a in ('X=0','X=1')),
            'switch_each_action_order':all(check([t for t in group if main(t) and t['graph']!='confounder_z' and expected[t['task_id']]==a and t['order']==o],75) for a in ('X=0','X=1') for o in ('forward','reverse')),
            'added_z_overall':check([t for t in group if z(t)],80),
            'added_z_each_action':all(check([t for t in group if z(t) and expected[t['task_id']]==a],75 if split=='validation' else 87) for a in ('X=0','X=1')),
            'paired_switch':sum(paired)>=ceil_fraction(n_families,75),
        }
        # Exact integer gate of 7/8 or 13/16 for added-Z per action.
        gate['added_z_each_action']=all(cells['added_z_'+a]['correct'] >= (7 if split=='development' else 13) for a in ('X=0','X=1'))
        output[form]={'cells':cells,'family_paired':dict(zip(sorted({t['family_id'] for t in group}),paired)),
                      'gates':gate,'qualified':all(gate.values())}
    return {'split':split,'forms':output,'qualified':all(x['qualified'] for x in output.values()),
            'scheduled':len(tasks),'raw_records':len(records),
            'infrastructure_failures':sum(bool(r.get('infrastructure_error')) for r in records)}


def analyze_arm(split,arm_id):
    verify()
    tasks=jsonl(BASE/split/'public_tasks.jsonl')
    truth=jsonl(BASE/split/'oracle_truth.jsonl')
    raw=jsonl(BASE/'runs'/split/arm_id/'results.jsonl')
    result=score(tasks,truth,raw,split)
    atomic_json(BASE/'runs'/split/arm_id/'analysis.json',result)
    return result


def shortcut_audit():
    tasks=jsonl(BASE/'development'/'public_tasks.jsonl')
    truth=jsonl(BASE/'development'/'oracle_truth.jsonl')
    outputs={}
    for strategy in ('always_first','always_last','constant_x0','constant_x1','graph_blind'):
        records=[]
        for t in tasks:
            if t['kind']=='graph':answer='upstream'
            elif strategy=='constant_x0':answer='X=0'
            elif strategy=='constant_x1':answer='X=1'
            elif strategy=='graph_blind':answer='X=1'
            else:
                first='upstream' if t['kind']=='graph' else 'X=1'
                second='downstream' if t['kind']=='graph' else 'X=0'
                answer=(first if strategy=='always_first' else second) if t['order']=='forward' else (second if strategy=='always_first' else first)
            records.append({'task_id':t['task_id'],'strict_answer':answer})
        result=score(tasks,truth,records,'development')
        outputs[strategy]={'qualified':result['qualified'],
                           'paired':{f:x['cells']['paired_switch']['correct'] for f,x in result['forms'].items()}}
        if result['qualified'] or any(outputs[strategy]['paired'].values()):
            raise ValueError('Shortcut strategy passed switch fidelity: '+strategy)
    return outputs

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('split',choices=('development','validation'));p.add_argument('arm_id');a=p.parse_args()
    print(json.dumps(analyze_arm(a.split,a.arm_id),indent=2))
