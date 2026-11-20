"""Cohort 028 strict scoring, assisted replay, integer gates and paired family summaries."""
from collections import Counter,defaultdict
from decimal import Decimal
import json
import math
import random
from pathlib import Path
from causalfade.cohort028 import parse_bare,parse_structured,calculate,replay,SCORE_TOLERANCE

BASE=Path(__file__).resolve().parents[1]/'experiments/cohort_028'

def rows(path):return [json.loads(s) for s in Path(path).read_text().splitlines() if s]
def ceil_pct(n,pct):return (n*pct+99)//100

def item_score(task,truth,record):
    raw=record.get('raw');finish=record.get('finish_reason')
    if task['condition']=='bare':
        a=parse_bare(raw,finish)
        return {'valid':a is not None,'action_a':a,'correct_a':a==truth['expected_action'],'infrastructure_error':bool(record.get('infrastructure_error'))}
    b=parse_structured(raw,finish)
    c=replay(task['payload'],b) if b is not None else None
    selected=calculate(task['payload'],b['rule']) if b is not None else None
    score_match=b is not None and all(abs(b[k]-selected[k])<=SCORE_TOLERANCE for k in ('score_x0','score_x1'))
    return {'valid':b is not None,'rule':b['rule'] if b else None,
            'rule_correct':b is not None and b['rule']==truth['expected_rule'],
            'score_match_selected':score_match,
            'action_score_agreement':b is not None and b['action']==('X=1' if b['score_x1']>b['score_x0'] else 'X=0') if b and b['score_x1']!=b['score_x0'] else False,
            'action_b':b['action'] if b else None,'action_c':c['action'] if c else None,
            'correct_b':b is not None and b['action']==truth['expected_action'],
            'correct_c':c is not None and c['action']==truth['expected_action'],
            'infrastructure_error':bool(record.get('infrastructure_error'))}

def bootstrap_mean(values,seed=28028,reps=2000):
    if not values:return None
    rng=random.Random(seed);n=len(values)
    samples=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(reps))
    return {'mean':sum(values)/n,'percentile_95':[samples[int(.025*reps)],samples[min(reps-1,int(.975*reps))]],'families':n}

def wilson(k,n):
    if n==0:return None
    z=1.95996398454;p=k/n;d=1+z*z/n
    center=(p+z*z/(2*n))/d
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,center-half),min(1,center+half)]

def analyze(tasks,truth,records,split):
    lookup={t['task_id']:t for t in tasks};oracle={t['task_id']:t for t in truth};saved={r['task_id']:r for r in records}
    if len(lookup)!=len(tasks) or set(lookup)!=set(oracle) or len(saved)!=len(records) or set(saved)!=set(lookup):
        raise ValueError('Incomplete, duplicate or mismatched schedule')
    scored={tid:item_score(t,oracle[tid],saved[tid]) for tid,t in lookup.items()}
    n=16 if split=='development' else 32
    def select(**criteria):return [t for t in tasks if all(t[k]==v for k,v in criteria.items())]
    def metric(sub,key):return {'correct':sum(bool(scored[t['task_id']].get(key)) for t in sub),'scheduled':len(sub)}
    def pass_pct(sub,key,pct):
        x=metric(sub,key);return x['correct']>=ceil_pct(x['scheduled'],pct)
    forms={}
    for form in ('direct','decision'):
        structured=select(form=form,condition='structured')
        gates={'schema_validity':pass_pct(structured,'valid',95)}
        cells={'schema_validity':metric(structured,'valid')}
        for rep in ('raw','supplied'):
            for graph in ('confounder','mediator','confounder_z'):
                for action in ('X=0','X=1'):
                    for order in ('forward','reverse'):
                        sub=[t for t in structured if t['representation']==rep and t['kind']=='causal' and t['graph']==graph and t['order']==order and oracle[t['task_id']]['expected_action']==action]
                        key=f'{rep}_{graph}_{action}_{order}'
                        if len(sub)!=n//2:raise ValueError('Unbalanced causal stratum '+key)
                        cells[key]={'rule':metric(sub,'rule_correct'),'assisted':metric(sub,'correct_c')}
                        gates[key+'_rule']=pass_pct(sub,'rule_correct',80)
                        gates[key+'_assisted']=pass_pct(sub,'correct_c',80)
            for rule in ('marginal','conditional'):
                for action in ('X=0','X=1'):
                    sub=[t for t in structured if t['representation']==rep and t['kind']=='control' and t['specified_rule']==rule and oracle[t['task_id']]['expected_action']==action]
                    if len(sub)!=n:raise ValueError('Unbalanced control stratum')
                    key=f'{rep}_control_{rule}_{action}'
                    cells[key]={'assisted':metric(sub,'correct_c')}
                    gates[key+'_assisted']=pass_pct(sub,'correct_c',90)
                    if rep=='raw':
                        cells[key]['b_calculation']={'correct':sum(bool(scored[t['task_id']]['rule_correct'] and scored[t['task_id']]['score_match_selected']) for t in sub),'scheduled':len(sub)}
            paired=[];invariant=[]
            for fid in sorted({t['family_id'] for t in structured}):
                four=[t for t in structured if t['family_id']==fid and t['representation']==rep and t['kind']=='causal' and t['graph'] in ('confounder','mediator')]
                if len(four)!=4:raise ValueError('Missing switch quartet')
                paired.append(all(scored[t['task_id']]['correct_c'] for t in four))
                for order in ('forward','reverse'):
                    base=next(t for t in structured if t['family_id']==fid and t['representation']==rep and t['kind']=='causal' and t['graph']=='confounder' and t['order']==order)
                    add=next(t for t in structured if t['family_id']==fid and t['representation']==rep and t['kind']=='causal' and t['graph']=='confounder_z' and t['order']==order)
                    a=scored[base['task_id']]['action_c'];b=scored[add['task_id']]['action_c']
                    invariant.append(a is not None and a==b)
            cells[rep+'_paired_switch']={'correct':sum(paired),'scheduled':n,'wilson_95':wilson(sum(paired),n)}
            cells[rep+'_no_change_invariance']={'correct':sum(invariant),'scheduled':2*n}
            gates[rep+'_paired_switch']=sum(paired)>=ceil_pct(n,75)
            gates[rep+'_no_change_invariance']=sum(invariant)>=ceil_pct(2*n,90)
        forms[form]={'gates':gates,'cells':cells,'qualified':all(gates.values())}
    family=[]
    for fid in sorted({t['family_id'] for t in tasks}):
        row={'family_id':fid}
        for system in ('a','b','c'):
            condition='bare' if system=='a' else 'structured'
            for kind in ('causal','control'):
                sub=[t for t in tasks if t['family_id']==fid and t['condition']==condition and t['representation']=='raw' and t['kind']==kind and (kind=='control' or t['graph'] in ('confounder','mediator'))]
                if len(sub)!=8:raise ValueError('Family contrast denominator')
                row[f'{system}_{kind}_raw']=sum(scored[t['task_id']].get('correct_'+system,False) for t in sub)/8
        row['causal_gain']=row['c_causal_raw']-row['b_causal_raw']
        row['control_gain']=row['c_control_raw']-row['b_control_raw']
        row['specificity']=row['causal_gain']-row['control_gain']
        family.append(row)
    return {'split':split,'scheduled':len(tasks),'models_calls':len(records),'forms':forms,
            'qualified':all(x['qualified'] for x in forms.values()),'families':family,
            'primary_gain_pp':bootstrap_mean([100*r['causal_gain'] for r in family]),
            'specificity_pp':bootstrap_mean([100*r['specificity'] for r in family],seed=28029),
            'validity':{condition:metric(select(condition=condition),'valid') for condition in ('bare','structured')},
            'infrastructure_failures':sum(x['infrastructure_error'] for x in scored.values())}

def shortcut_audit(tasks,truth,split):
    oracle={x['task_id']:x for x in truth};out={}
    for strategy in ('constant_marginal','constant_conditional','first_candidate','last_candidate',
                     'graph_blind_observational','first_action','last_action','constant_x0','constant_x1'):
        records=[]
        for t in tasks:
            if strategy=='constant_marginal':rule='marginal'
            elif strategy in ('constant_conditional','graph_blind_observational'):rule='conditional'
            elif strategy=='first_candidate':rule=t['candidate_order'][0]
            elif strategy=='last_candidate':rule=t['candidate_order'][-1]
            else:rule='marginal'
            value=calculate(t['payload'],rule)
            if strategy=='first_action':action='X=0' if t['order']=='forward' else 'X=1'
            elif strategy=='last_action':action='X=1' if t['order']=='forward' else 'X=0'
            elif strategy=='constant_x0':action='X=0'
            elif strategy=='constant_x1':action='X=1'
            else:action=value['action']
            if t['condition']=='bare':
                raw=action
            else:raw=json.dumps({'rule':rule,'score_x0':float(value['score_x0']),
                                 'score_x1':float(value['score_x1']),'action':action})
            records.append({'task_id':t['task_id'],'raw':raw,'finish_reason':'stop'})
        result=analyze(tasks,truth,records,split)
        out[strategy]={'qualified':result['qualified'],
                       'raw_paired':{f:result['forms'][f]['cells']['raw_paired_switch']['correct'] for f in result['forms']}}
        if result['qualified'] or any(out[strategy]['raw_paired'].values()):
            raise ValueError('Shortcut qualified: '+strategy)
    return out
