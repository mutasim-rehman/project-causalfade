"""Cohort 023 frozen-factor measurement audit (development only)."""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
from statistics import mean

import numpy as np
from .worlds import World
from .sensitivity import OBSERVATIONAL_STRENGTH, cluster_interval, digest, read_jsonl, write_json, write_jsonl

VERSION = 'measurement-audit-v1'
SEED = 20261119
FAMILIES = 8
STRENGTH = .12
KINDS = ('decision','source_selection','randomized_only','numerical_control','noncausal_control')
ORDERS = ('randomized_first','historical_first')
ANSWER_ORDERS = ('canonical','reversed')


def alternatives(row):
    kind=row['task_type']
    if kind=='source_selection':
        options=['{"governing_study":"A"}','{"governing_study":"B"}']
    elif kind=='numerical_control':
        options=['{"larger":"X=0"}','{"larger":"X=1"}']
    else:
        options=['{"decision":"activate"}','{"decision":"leave_off"}']
    if row['answer_order']=='reversed': options.reverse()
    return ' or '.join(options)


def blocks(row, causal=True):
    r0,r1=row['randomized_rates']; h0,h1=row['historical_rates']
    if causal:
        labels=('X was assigned randomly.','operators chose X.')
    else:
        labels=('PRIMARY scorecard.','secondary scorecard.')
    parts={'randomized':f'Study {row["randomized_name"]}\nAssignment method: {labels[0]}\nSuccess probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.',
           'historical':f'Study {row["historical_name"]}\nAssignment method: {labels[1]}\nSuccess probabilities: X=0 {h0:.6f}; X=1 {h1:.6f}.'}
    order=('randomized','historical') if row['presentation_order']=='randomized_first' else ('historical','randomized')
    return '\n\n'.join(f'{i}. {parts[k]}' for i,k in enumerate(order,1))


def render(row):
    kind=row['task_type']
    tail='Return exactly one JSON object: '+alternatives(row)+'. No other fields, fences, explanation, or text.'
    if kind=='numerical_control':
        r0,r1=row['randomized_rates']
        return f'Exact success probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.\n\nWhich rate is larger? '+tail
    if kind=='noncausal_control':
        pre=('Two machine scorecards contain exact numerical scores for leaving X off and activating X. '
             'Choose the action with the higher score on the PRIMARY scorecard; ignore the secondary scorecard.')
        return pre+'\n\n'+blocks(row,False)+'\n\n'+tail
    pre=('A machine setting X may affect success Y. Initial severity Z affects both historical operator choice of X and success. '
         'The studies refer to the same target population. There are no unmeasured common causes. '
         'The rates are exact population success probabilities, not sample estimates.')
    if kind=='randomized_only':
        r0,r1=row['randomized_rates']
        evidence=f'Study {row["randomized_name"]}\nAssignment method: X was assigned randomly.\nSuccess probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.'
    else: evidence=blocks(row)
    question=('Which study provides the appropriate evidence for estimating the effect of intervening on X in this target population? ' if kind=='source_selection' else
              'Does activating X improve success under intervention? ')
    return pre+'\n\n'+evidence+'\n\n'+question+tail


def add(public,truth,row,seed):
    task_id=hashlib.sha256(json.dumps([seed,VERSION,row],sort_keys=True).encode()).hexdigest()[:24]
    row={**row,'task_id':task_id}; truth.append(row)
    public.append({'task_id':task_id,'family_id':row['family_id'],'prompt':render(row)})


def generate(directory,seed=SEED):
    directory=Path(directory)
    if directory.exists(): raise FileExistsError(directory)
    rng=random.Random(seed); public=[];truth=[]
    for f in range(FAMILIES):
        family=f'audit-{seed}-{f:04d}';gap=rng.uniform(.68,.78);offset=rng.uniform(-.04,.04)
        for t in (0,1):
            worlds={}
            for condition in ('aligned','conflict'):
                association=t if condition=='aligned' else 1-t
                assignment=(OBSERVATIONAL_STRENGTH-STRENGTH if association==t else OBSERVATIONAL_STRENGTH+STRENGTH)/gap
                worlds[condition]=World(family,t,association,STRENGTH,gap,assignment)
            for name,answer_order in itertools.product(('A','B'),ANSWER_ORDERS):
                base_id=hashlib.sha256(json.dumps([family,t,name,answer_order]).encode()).hexdigest()[:20]
                for kind in ('randomized_only','numerical_control'):
                    w=worlds['aligned'];row={**w.truth(),'family_id':family,'base_id':base_id,'task_type':kind,
                        'causal_positive':t,'condition':'randomized_only','presentation_order':'randomized_first',
                        'randomized_name':name,'historical_name':'B' if name=='A' else 'A','answer_order':answer_order,
                        'effect_size':STRENGTH,'severity_gap':gap,'rate_offset':offset,'optimal_action':t,
                        'randomized_rates':(w.do_means+offset).tolist(),
                        'historical_rates':(w.observational_means+offset).tolist(),
                        'do_success_x0':float(w.do_means[0]+offset),'do_success_x1':float(w.do_means[1]+offset)}
                    add(public,truth,row,seed)
                for condition,order in itertools.product(('aligned','conflict'),ORDERS):
                    w=worlds[condition]
                    common={**w.truth(),'family_id':family,'base_id':base_id,'causal_positive':t,'condition':condition,
                            'presentation_order':order,'randomized_name':name,'historical_name':'B' if name=='A' else 'A',
                            'answer_order':answer_order,'effect_size':STRENGTH,'severity_gap':gap,'rate_offset':offset,
                            'optimal_action':t,'randomized_rates':(w.do_means+offset).tolist(),
                            'historical_rates':(w.observational_means+offset).tolist(),
                            'do_success_x0':float(w.do_means[0]+offset),'do_success_x1':float(w.do_means[1]+offset)}
                    stem_id=hashlib.sha256(json.dumps([base_id,condition,order]).encode()).hexdigest()[:20]
                    for kind in ('decision','source_selection'):
                        add(public,truth,{**common,'stem_id':stem_id,'task_type':kind},seed)
                    # Matched noncausal control on the identical displayed rates and layout.
                    add(public,truth,{**common,'stem_id':stem_id,'task_type':'noncausal_control'},seed)
    rng.shuffle(public);directory.mkdir(parents=True)
    write_jsonl(directory/'public_tasks.jsonl',public);write_jsonl(directory/'oracle_truth.jsonl',truth)
    manifest={'version':VERSION,'classification':'development_only','seed':seed,'families':FAMILIES,'strength':STRENGTH,
              'tasks':len(public),'cells_per_family':len(public)//FAMILIES,'training_families':[f'audit-{seed}-{f:04d}' for f in range(4)],
              'heldout_families':[f'audit-{seed}-{f:04d}' for f in range(4,8)],
              'file_sha256':{n:digest(directory/n) for n in ('public_tasks.jsonl','oracle_truth.jsonl')}}
    write_json(directory/'manifest.json',manifest);validate(directory);return manifest


def validate(directory):
    directory=Path(directory);m=json.loads((directory/'manifest.json').read_text())
    if (m['version'],m['classification'],m['families'],m['strength'],m['tasks'],m['cells_per_family'])!=(VERSION,'development_only',8,.12,896,112):
        raise ValueError('Manifest mismatch')
    for n in ('public_tasks.jsonl','oracle_truth.jsonl'):
        if digest(directory/n)!=m['file_sha256'][n]:raise ValueError('Fixture hash mismatch')
    public=read_jsonl(directory/'public_tasks.jsonl');truth=read_jsonl(directory/'oracle_truth.jsonl')
    pids={p['task_id'] for p in public};tids={r['task_id'] for r in truth}
    if len(public)!=896 or len(truth)!=896 or len(pids)!=896 or len(tids)!=896 or pids!=tids:raise ValueError('Task IDs')
    by_id={p['task_id']:p for p in public};cells=defaultdict(set);paired=defaultdict(list)
    for r in truth:
        p=by_id[r['task_id']]
        if p!={'task_id':r['task_id'],'family_id':r['family_id'],'prompt':render(r)}:raise ValueError('Rendered prompt mismatch')
        kind=r['task_type'];t=r['causal_positive'];name=r['randomized_name'];ao=r['answer_order']
        if kind not in KINDS or t not in (0,1) or name not in ('A','B') or ao not in ANSWER_ORDERS:raise ValueError('Invalid cell')
        w=World(r['family_id'],t,r['association_positive'],STRENGTH,r['severity_gap'],r['assignment_strength']);offset=r['rate_offset']
        expected=w.truth();expected['do_success_x0']+=offset;expected['do_success_x1']+=offset
        for k,v in expected.items():
            if not (math.isclose(r[k],v,abs_tol=1e-12,rel_tol=0) if isinstance(v,float) else r[k]==v):raise ValueError('SCM oracle')
        if not np.allclose(r['randomized_rates'],w.do_means+offset,rtol=0,atol=1e-12) or not np.allclose(r['historical_rates'],w.observational_means+offset,rtol=0,atol=1e-12):raise ValueError('Rate oracle')
        if r['optimal_action']!=t or int(float(f'{r["randomized_rates"][1]:.6f}')>float(f'{r["randomized_rates"][0]:.6f}'))!=t:raise ValueError('Action oracle')
        if kind in ('randomized_only','numerical_control'):
            if r['condition']!='randomized_only':raise ValueError('Baseline cell')
            cell=(t,name,ao,kind)
        else:
            cond=r['condition'];order=r['presentation_order']
            if cond not in ('aligned','conflict') or order not in ORDERS or r['association_positive']!=(t if cond=='aligned' else 1-t):raise ValueError('Two-source cell')
            first=name if order=='randomized_first' else r['historical_name']
            if not blocks(r,kind!='noncausal_control').startswith('1. Study '+first+'\n'):raise ValueError('Physical order')
            if r['historical_name']==name or alternatives(r) not in p['prompt']:raise ValueError('Presentation balance')
            cell=(t,name,ao,cond,order,kind);paired[(r['family_id'],r['stem_id'])].append(r)
        if cell in cells[r['family_id']]:raise ValueError('Duplicate cell')
        cells[r['family_id']].add(cell)
    expected={(t,n,a,k) for t,n,a,k in itertools.product((0,1),('A','B'),ANSWER_ORDERS,('randomized_only','numerical_control'))}
    expected|={(t,n,a,c,o,k) for t,n,a,c,o,k in itertools.product((0,1),('A','B'),ANSWER_ORDERS,('aligned','conflict'),ORDERS,('decision','source_selection','noncausal_control'))}
    if len(cells)!=8 or any(c!=expected for c in cells.values()) or len(paired)!=256:raise ValueError('Unbalanced cells')
    for rows in paired.values():
        if {r['task_type'] for r in rows}!={'decision','source_selection','noncausal_control'} or len({tuple(r['randomized_rates']) for r in rows})!=1 or len({tuple(r['historical_rates']) for r in rows})!=1 or len({r['optimal_action'] for r in rows})!=1:raise ValueError('Unpaired evidence')
    return {'valid':True,'tasks':896,'families':8,'two_source_stems':256,'manifest_sha256':digest(directory/'manifest.json')}


def decode(content,kind):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('Duplicate key')
            d[k]=v
        return d
    try:
        obj=json.loads(content,object_pairs_hook=unique)
        if not isinstance(obj,dict):return None
        key='governing_study' if kind=='source_selection' else 'larger' if kind=='numerical_control' else 'decision'
        allowed=('A','B') if kind=='source_selection' else ('X=0','X=1') if kind=='numerical_control' else ('activate','leave_off')
        return obj[key] if set(obj)=={key} and type(obj[key]) is str and obj[key] in allowed else None
    except (ValueError,TypeError,KeyError):return None


def score_records(truth,raw):
    ids={r['task_id'] for r in truth};records={}
    for record in raw:
        if record['task_id'] not in ids or record['task_id'] in records:raise ValueError('Unknown or duplicate raw task ID')
        records[record['task_id']]=record
    rows=[]
    for t in truth:
        record=records.get(t['task_id']);answer=None;finish=None
        if record and not record.get('execution_error'):
            try:
                choice=record['response']['choices'][0];finish=choice.get('finish_reason')
                if finish=='stop':answer=decode(choice['message']['content'],t['task_type'])
            except (KeyError,IndexError,TypeError):pass
        target=t['randomized_name'] if t['task_type']=='source_selection' else ('X=1' if t['causal_positive'] else 'X=0') if t['task_type']=='numerical_control' else ('activate' if t['optimal_action'] else 'leave_off')
        rows.append({**t,'completed':record is not None,'finish_reason':finish,'valid_answer':answer is not None,'answer':answer,'correct':int(answer==target)})
    return rows
