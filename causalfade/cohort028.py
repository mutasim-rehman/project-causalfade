"""Cohort 028 public calculator, exact-rational worlds, tasks and strict scorers."""
from decimal import Decimal, InvalidOperation
from fractions import Fraction as F
from hashlib import sha256
import json
from collections import Counter,defaultdict
from .graph_switch import family, intervention_effect

SEEDS={'development':28028000,'validation':28029000}
COUNTS={'development':16,'validation':32}
FORMS=('direct','decision')
GRAPHS=('confounder','mediator','confounder_z')
RULES=('marginal','conditional')
SCORE_TOLERANCE=Decimal('0.0001')


def signature(j):
    return sha256('|'.join(str(j[k]) for k in sorted(j)).encode()).hexdigest()


def conditional(j, given, target):
    den=sum(v for k,v in j.items() if given(k))
    if den<=0:raise ValueError('positivity')
    return sum(v for k,v in j.items() if given(k) and target(k))/den


def public_payload(j,representation):
    weights={'marginal':{str(w):f'{float(conditional(j,lambda k:True,lambda k:k[0]==w)):.6f}' for w in (0,1)},
             'conditional':{str(x):{str(w):f'{float(conditional(j,lambda k:k[1]==x,lambda k:k[0]==w)):.6f}' for w in (0,1)} for x in (0,1)}}
    outcomes={str(x):{str(w):f'{float(conditional(j,lambda k:k[1]==x and k[0]==w,lambda k:k[2]==1)):.6f}' for w in (0,1)} for x in (0,1)}
    joint=[{'w':w,'x':x,'y':y,'p':f'{float(j[w,x,y]):.6f}'} for w in (0,1) for x in (0,1) for y in (0,1)]
    if representation=='raw':return {'representation':'raw','joint':joint,'weights':weights,'outcomes':outcomes}
    raw={'representation':'raw','joint':joint,'weights':weights,'outcomes':outcomes}
    scores={rule:calculate(raw,rule) for rule in RULES}
    return {'representation':'supplied','joint':joint,'weights':weights,'outcomes':outcomes,
            'scores':{rule:{k:format(v,'.6f') for k,v in score.items() if k.startswith('score_')} for rule,score in scores.items()}}


def decimal_number(v):
    if isinstance(v,bool) or isinstance(v,(dict,list)):
        raise ValueError('Non-numeric calculator input')
    try:d=Decimal(str(v))
    except (InvalidOperation,ValueError):raise ValueError('Non-numeric calculator input')
    if not d.is_finite() or not 0<=d<=1:raise ValueError('Probability outside [0,1]')
    return d


def calculate(payload,rule):
    """Only public numeric payload and an allowlisted selected rule enter this function."""
    if rule not in RULES:raise ValueError('Unknown rule')
    if payload.get('representation')=='supplied':
        pair=payload['scores'][rule]
        scores={x:decimal_number(pair['score_x'+str(x)]) for x in (0,1)}
    elif payload.get('representation')=='raw':
        scores={}
        for x in (0,1):
            score=Decimal(0)
            for w in (0,1):
                weight=payload['weights']['marginal'][str(w)] if rule=='marginal' else payload['weights']['conditional'][str(x)][str(w)]
                score+=decimal_number(weight)*decimal_number(payload['outcomes'][str(x)][str(w)])
            scores[x]=score
    else:raise ValueError('Unknown public representation')
    if scores[0]==scores[1]:raise ValueError('Tied intervention scores')
    return {'score_x0':scores[0],'score_x1':scores[1],'action':'X=1' if scores[1]>scores[0] else 'X=0'}


def graph_text(graph):
    base='W occurs before X. W causes X and Y; X causes Y.'
    if graph=='confounder':return base
    if graph=='confounder_z':return base+' W also causes an unmeasured Z; Z has no path to X or Y.'
    if graph=='mediator':return 'X occurs before W. X causes W and Y; W causes Y.'
    raise ValueError(graph)


def numeric_text(payload,rule_order):
    p=payload
    lines=['Observational joint distribution:']
    lines += [f"P(W={v['w']},X={v['x']},Y={v['y']}) = {v['p']}" for v in p['joint']]
    lines += [f"P(W={w}) = {p['weights']['marginal'][str(w)]}" for w in (0,1)]
    for x in (0,1):
        for w in (0,1):
            lines.append(f"P(W={w}|X={x}) = {p['weights']['conditional'][str(x)][str(w)]}")
            lines.append(f"P(Y=1|X={x},W={w}) = {p['outcomes'][str(x)][str(w)]}")
    if payload['representation']=='supplied':
        lines.append('Candidate final outcome scores computed from the displayed rates:')
        for rule in rule_order:
            pair=payload['scores'][rule]
            lines.append(f"{rule}: score for X=0 is {pair['score_x0']}; score for X=1 is {pair['score_x1']}")
    return '\n'.join(lines)


def render(payload,form,kind,graph,specified_rule,rule_order,option_order,condition):
    intro=('Compare interventions X=0 and X=1 for desirable outcome Y.' if form=='direct' else
           'Choose the intervention setting with the larger probability of desirable outcome Y.')
    definitions={'marginal':'marginal: for each X, average P(Y=1|X,W) using P(W).',
                 'conditional':'conditional: for each X, average P(Y=1|X,W) using P(W|X) separately.'}
    lines=[intro]
    if kind=='causal':lines.append('Causal structure: '+graph_text(graph))
    else:lines.append('Use the specified procedure: '+specified_rule+'. No causal graph selection is needed.')
    lines += ['Candidate procedures:',definitions[rule_order[0]],definitions[rule_order[1]],numeric_text(payload,rule_order),
              'Which intervention has the larger outcome probability?']
    choices=('X=0','X=1') if option_order=='forward' else ('X=1','X=0')
    lines.append('Displayed action alternatives: '+choices[0]+' or '+choices[1]+'.')
    if condition=='bare':lines.append('Return exactly X=0 or X=1, with no punctuation or explanation.')
    else:lines.append('Return one JSON object only, with exactly keys rule, score_x0, score_x1, action. Rule is marginal or conditional; scores are numbers in [0,1]; action is X=0 or X=1. No other fields, prose or fences.')
    return '\n'.join(lines)


def build():
    worlds,tasks,truth=[],[],[]
    for split,n in COUNTS.items():
        for i in range(n):
            rec=family(SEEDS[split]+i,bool(i%2));j=rec['joint'];fid=f'{split}_{i:03d}'
            worlds.append({'family_id':fid,'split':split,'signature':signature(j),'seed':rec['seed'],'polarity':int(i%2),
                           'joint':[{'w':w,'x':x,'y':y,'p':str(p)} for (w,x,y),p in sorted(j.items())],
                           'effects':{g:str(intervention_effect(j,g)) for g in ('confounder','mediator')}})
            rule_order=RULES if (i//2)%2==0 else RULES[::-1]
            for form in FORMS:
                for order in ('forward','reverse'):
                    for representation in ('raw','supplied'):
                        payload=public_payload(j,representation)
                        specs=[('causal',g,None) for g in GRAPHS]+[('control',None,r) for r in RULES]
                        for kind,graph,specified in specs:
                            oracle_rule=specified if kind=='control' else ('conditional' if graph=='mediator' else 'marginal')
                            calc=calculate(payload,oracle_rule)
                            stem=f'{fid}_{form}_{order}_{representation}_{kind}_{graph or specified}'
                            for condition in ('bare','structured'):
                                tid=stem+'_'+condition
                                tasks.append({'task_id':tid,'stem_id':stem,'family_id':fid,'split':split,'form':form,'order':order,
                                              'representation':representation,'kind':kind,'graph':graph,'specified_rule':specified,
                                              'candidate_order':list(rule_order),'condition':condition,'payload':payload,
                                              'prompt':render(payload,form,kind,graph,specified,rule_order,order,condition)})
                                truth.append({'task_id':tid,'expected_rule':oracle_rule,'expected_action':calc['action'],
                                              'score_x0':str(calc['score_x0']),'score_x1':str(calc['score_x1'])})
    return worlds,tasks,truth


def parse_bare(raw,finish):
    if finish!='stop' or not isinstance(raw,str):return None
    x=raw.strip()
    return x if x in ('X=0','X=1') else None


def parse_structured(raw,finish):
    if finish!='stop' or not isinstance(raw,str):return None
    def unique_pairs(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('duplicate JSON key')
            out[key]=value
        return out
    try:o=json.loads(raw.strip(),object_pairs_hook=unique_pairs)
    except (json.JSONDecodeError,TypeError,ValueError):return None
    if not isinstance(o,dict) or set(o)!={'rule','score_x0','score_x1','action'}:return None
    if o['rule'] not in RULES or o['action'] not in ('X=0','X=1'):return None
    if any(isinstance(o[k],bool) or not isinstance(o[k],(int,float)) for k in ('score_x0','score_x1')):return None
    try:s0=decimal_number(o['score_x0']);s1=decimal_number(o['score_x1'])
    except ValueError:return None
    return {'rule':o['rule'],'score_x0':s0,'score_x1':s1,'action':o['action']}


def replay(payload,structured):
    """Invalid full schema fails; no hidden metadata or oracle may enter."""
    if structured is None:return None
    return calculate(payload,structured['rule'])


def validate(worlds,tasks,truth,prior_signatures=()):
    if len(worlds)!=48 or len(tasks)!=3840 or len(truth)!=3840:raise ValueError('Fixture cardinality')
    sig={w['signature'] for w in worlds}
    if len(sig)!=48 or sig.intersection(prior_signatures):raise ValueError('World reuse')
    if Counter(w['split'] for w in worlds)!=COUNTS:raise ValueError('Split balance')
    y={x['task_id']:x for x in truth}
    if len(y)!=len(truth) or set(y)!={x['task_id'] for x in tasks}:raise ValueError('Truth mismatch')
    for w in worlds:
        j={(r['w'],r['x'],r['y']):F(r['p']) for r in w['joint']}
        if len(j)!=8 or sum(j.values())!=1 or any(p<=0 for p in j.values()):raise ValueError('Invalid joint')
        if signature(j)!=w['signature'] or intervention_effect(j,'confounder')*intervention_effect(j,'mediator')>=0:raise ValueError('Invalid graph switch')
        for (ww,xx,yy),p in j.items():
            pw=conditional(j,lambda k:True,lambda k:k[0]==ww)
            pxw=conditional(j,lambda k:k[0]==ww,lambda k:k[1]==xx)
            px=conditional(j,lambda k:True,lambda k:k[1]==xx)
            pwx=conditional(j,lambda k:k[1]==xx,lambda k:k[0]==ww)
            pyxw=conditional(j,lambda k:k[0]==ww and k[1]==xx,lambda k:k[2]==yy)
            if pw*pxw*pyxw!=p or px*pwx*pyxw!=p:raise ValueError('SCM factorization mismatch')
        raw=public_payload(j,'raw');supplied=public_payload(j,'supplied')
        displayed={(r['w'],r['x'],r['y']):F(r['p']) for r in raw['joint']}
        for rule,g in (('marginal','confounder'),('conditional','mediator')):
            r=calculate(raw,rule);s=calculate(supplied,rule)
            if r['action']!=s['action'] or abs(r['score_x1']-r['score_x0'])<Decimal('0.01'):
                raise ValueError('Display mismatch or near tie')
            if (r['score_x1']>r['score_x0'])!=(intervention_effect(j,g)>0):raise ValueError('Oracle sign mismatch')
            # Independent check from the rounded full joint, not the derived
            # public weights/outcome table consumed by the calculator.
            def risk(x):
                total=F(0)
                px=sum(v for (w0,x0,y0),v in displayed.items() if x0==x)
                for ww in (0,1):
                    pw=sum(v for (w0,x0,y0),v in displayed.items() if w0==ww)
                    pwx=sum(v for (w0,x0,y0),v in displayed.items() if w0==ww and x0==x)
                    weight=pw/sum(displayed.values()) if rule=='marginal' else pwx/px
                    total+=weight*displayed[ww,x,1]/pwx
                return total
            if (risk(1)>risk(0))!=(r['action']=='X=1'):raise ValueError('Rounded joint oracle mismatch')
    groups=defaultdict(list)
    for t in tasks:groups[(t['family_id'],t['form'],t['condition'])].append(t)
    if any(len(v)!=20 for v in groups.values()):raise ValueError('Per-family factorial mismatch')
    for rows in groups.values():
        if Counter((t['order'],t['representation'],t['kind']) for t in rows)!=Counter({(o,r,'causal'):3 for o in ('forward','reverse') for r in ('raw','supplied')})+Counter({(o,r,'control'):2 for o in ('forward','reverse') for r in ('raw','supplied')}):
            raise ValueError('Cell balance')
        if len({tuple(t['candidate_order']) for t in rows})!=1:raise ValueError('Candidate order leaked')
        for form_order in ('forward','reverse'):
            for representation in ('raw','supplied'):
                subset=[t for t in rows if t['order']==form_order and t['representation']==representation and t['kind']=='causal']
                if len(subset)!=3 or len({json.dumps(t['payload'],sort_keys=True) for t in subset})!=1:raise ValueError('Unmatched graph contrast')
                c=next(t for t in subset if t['graph']=='confounder');z=next(t for t in subset if t['graph']=='confounder_z')
                if y[c['task_id']]['expected_action']!=y[z['task_id']]['expected_action']:raise ValueError('No-change oracle')
                if graph_text('confounder') not in z['prompt']:raise ValueError('Base graph changed')
    return {'families':48,'tasks':3840,'development_calls_per_model':1280,'validation_calls_per_model':2560,
            'split_families':dict(Counter(w['split'] for w in worlds)),
            'conditions':dict(Counter(t['condition'] for t in tasks))}
