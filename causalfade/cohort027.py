"""Cohort 027 exact-rational fixture and strict scoring. No inference here."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from .graph_switch import family, intervention_effect

SEEDS = {'development': 27027000, 'validation': 27028000}
COUNTS = {'development': 8, 'validation': 16}
FORMS = ('direct', 'decision')
GRAPHS = ('confounder', 'mediator', 'confounder_z')


def joint_signature(j):
    return sha256('|'.join(str(j[k]) for k in sorted(j)).encode()).hexdigest()


def conditional(j, condition, event):
    den = sum(v for k, v in j.items() if condition(k))
    if den <= 0:
        raise ValueError('positivity failure')
    return sum(v for k, v in j.items() if condition(k) and event(k)) / den


def table(j):
    out = ['All rates below describe the same observational population.']
    for w in (0, 1):
        for x in (0, 1):
            for y in (0, 1):
                out.append(f'P(W={w},X={x},Y={y}) = {float(j[w,x,y]):.6f}')
    for w in (0, 1):
        out.append(f'P(W={w}) = {float(conditional(j, lambda k: True, lambda k: k[0]==w)):.6f}')
    for x in (0, 1):
        for w in (0, 1):
            out.append(f'P(W={w}|X={x}) = {float(conditional(j, lambda k: k[1]==x, lambda k: k[0]==w)):.6f}')
            out.append(f'P(Y=1|X={x},W={w}) = {float(conditional(j, lambda k: k[1]==x and k[0]==w, lambda k: k[2]==1)):.6f}')
    return '\n'.join(out)


def displayed_effect(j, rule):
    """Independent float oracle using exactly the six-decimal displayed rates."""
    p_w = {w: round(float(conditional(j, lambda k: True, lambda k: k[0]==w)),6) for w in (0,1)}
    p_wx = {(w,x): round(float(conditional(j, lambda k: k[1]==x, lambda k: k[0]==w)),6) for w in (0,1) for x in (0,1)}
    p_y = {(w,x): round(float(conditional(j, lambda k: k[1]==x and k[0]==w, lambda k: k[2]==1)),6) for w in (0,1) for x in (0,1)}
    risks = [sum((p_w[w] if rule=='marginal' else p_wx[w,x])*p_y[w,x] for w in (0,1)) for x in (0,1)]
    return risks[1]-risks[0]


def rounded_joint_effect(j, rule):
    """Second display oracle from the eight rounded joint cells alone."""
    q={k:round(float(v),6) for k,v in j.items()}
    risks=[]
    for x in (0,1):
        px=sum(v for (w0,x0,y0),v in q.items() if x0==x)
        risk=0.0
        for w in (0,1):
            pw=sum(v for (w0,x0,y0),v in q.items() if w0==w)
            pwx=sum(v for (w0,x0,y0),v in q.items() if w0==w and x0==x)
            py=q[w,x,1]/pwx
            weight=pw/sum(q.values()) if rule=='marginal' else pwx/px
            risk+=weight*py
        risks.append(risk)
    return risks[1]-risks[0]


def graph_text(graph):
    base = 'W occurs before X. W causes X and Y; X causes Y.'
    if graph == 'mediator':
        return 'X occurs before W. X causes W and Y; W causes Y.'
    if graph == 'confounder_z':
        return base + ' W also causes an unmeasured Z; Z has no path to X or Y.'
    return base


def answer_for(j, graph):
    return 'X=1' if intervention_effect(j, 'confounder' if graph == 'confounder_z' else graph) > 0 else 'X=0'


def render(j, form, kind, graph, order, rule=None):
    pre = ('Compare the two interventions for binary treatment X and desirable outcome Y.' if form == 'direct'
           else 'Choose the intervention setting that maximizes the chance of desirable outcome Y.')
    rates = table(j)
    if kind == 'graph':
        body = f'{pre}\nCausal structure: {graph_text(graph)}\n{rates}\nIs W upstream or downstream of X?'
        opts = ('upstream', 'downstream')
    elif kind == 'arithmetic':
        weight = 'P(W)' if rule == 'marginal' else 'P(W|X=x) separately for each x'
        body = f'{pre}\n{rates}\nArithmetic only: for each x, weight P(Y=1|X=x,W) using {weight}. Which X gives the larger weighted average?'
        opts = ('X=1', 'X=0')
    else:
        body = f'{pre}\nCausal structure: {graph_text(graph)}\n{rates}\nIf W is upstream of X, weight the outcome rates by P(W). If W is downstream of X, weight separately by P(W|X=x). Which intervention gives the larger P(Y=1)?'
        opts = ('X=1', 'X=0')
    if order == 'reverse':
        opts = opts[::-1]
    return body + '\nReturn exactly one bare answer: ' + ' or '.join(opts) + '. No punctuation or explanation.'


def build():
    worlds, tasks, truths = [], [], []
    for split, count in COUNTS.items():
        for i in range(count):
            rec = family(SEEDS[split]+i, bool(i % 2))
            j = rec['joint']
            fid = f'{split}_{i:03d}'
            worlds.append({'family_id':fid,'split':split,'seed':rec['seed'],'reverse_outcome':rec['reverse_outcome'],
                           'signature':joint_signature(j),'joint':[{'w':w,'x':x,'y':y,'p':str(p)} for (w,x,y),p in sorted(j.items())],
                           'effects':{g:str(intervention_effect(j,g)) for g in ('confounder','mediator')}})
            for form in FORMS:
                specs = [('main',g,None) for g in GRAPHS] + [('graph',g,None) for g in ('confounder','mediator')] + [('arithmetic',None,r) for r in ('marginal','conditional')]
                for kind, graph, rule in specs:
                    for order in ('forward','reverse'):
                        tid = f'{fid}_{form}_{kind}_{graph or rule}_{order}'
                        expected = ('upstream' if graph == 'confounder' else 'downstream') if kind == 'graph' else (answer_for(j,graph) if kind == 'main' else answer_for(j,'confounder' if rule == 'marginal' else 'mediator'))
                        tasks.append({'task_id':tid,'family_id':fid,'split':split,'form':form,'kind':kind,'graph':graph,'rule':rule,
                                      'order':order,'prompt':render(j,form,kind,graph,order,rule)})
                        truths.append({'task_id':tid,'expected':expected})
    return worlds,tasks,truths


def decode(raw, kind, finish):
    allowed = ('upstream','downstream') if kind == 'graph' else ('X=1','X=0')
    if not isinstance(raw,str) or finish != 'stop':
        return None,None
    stripped = raw.strip()
    strict = stripped if stripped in allowed else None
    sensitivity = strict or (stripped[:-1] if stripped.endswith('.') and stripped[:-1] in allowed else None)
    return strict,sensitivity


def validate(worlds,tasks,truths,prior_signatures=()):
    if len(worlds)!=24 or len(tasks)!=672 or len(truths)!=672:
        raise ValueError('fixture cardinality')
    if len({w['signature'] for w in worlds})!=24 or set(prior_signatures)&{w['signature'] for w in worlds}:
        raise ValueError('world reuse')
    lookup={t['task_id']:t for t in truths}
    if len(lookup)!=672 or set(lookup)!={t['task_id'] for t in tasks}:
        raise ValueError('task/truth mismatch')
    for w in worlds:
        j={(r['w'],r['x'],r['y']):F(r['p']) for r in w['joint']}
        if len(j)!=8 or sum(j.values())!=1 or any(v<=0 for v in j.values()):
            raise ValueError('invalid joint')
        if intervention_effect(j,'confounder')*intervention_effect(j,'mediator')>=0:
            raise ValueError('non-switch world')
        for (ww,xx,yy),p in j.items():
            pw=conditional(j,lambda k:True,lambda k:k[0]==ww)
            pxw=conditional(j,lambda k:k[0]==ww,lambda k:k[1]==xx)
            px=conditional(j,lambda k:True,lambda k:k[1]==xx)
            pwx=conditional(j,lambda k:k[1]==xx,lambda k:k[0]==ww)
            pyxw=conditional(j,lambda k:k[0]==ww and k[1]==xx,lambda k:k[2]==yy)
            if pw*pxw*pyxw!=p or px*pwx*pyxw!=p:
                raise ValueError('graph factorization mismatch')
        for rule,graph in (('marginal','confounder'),('conditional','mediator')):
            exact=intervention_effect(j,graph)
            shown=displayed_effect(j,rule)
            shown_joint=rounded_joint_effect(j,rule)
            if shown*float(exact)<=0 or shown_joint*float(exact)<=0 or min(abs(shown),abs(shown_joint))<0.01:
                raise ValueError('displayed-number contradiction or near tie')
        if w['signature']!=joint_signature(j):
            raise ValueError('signature mismatch')
    grouped=defaultdict(list)
    for t in tasks:
        grouped[(t['family_id'],t['form'])].append(t)
    if any(len(v)!=14 for v in grouped.values()):
        raise ValueError('form balance')
    for pair in grouped.values():
        for kind,graphs in (('main',GRAPHS),('graph',('confounder','mediator'))):
            for graph in graphs:
                sub=[t for t in pair if t['kind']==kind and t['graph']==graph]
                if {t['order'] for t in sub}!={'forward','reverse'}:
                    raise ValueError('order balance')
                if len({lookup[t['task_id']]['expected'] for t in sub})!=1:
                    raise ValueError('order changed oracle')
        for order in ('forward','reverse'):
            c=next(t for t in pair if t['kind']=='main' and t['graph']=='confounder' and t['order']==order)
            z=next(t for t in pair if t['kind']=='main' and t['graph']=='confounder_z' and t['order']==order)
            if lookup[c['task_id']]['expected']!=lookup[z['task_id']]['expected']:
                raise ValueError('added node changed answer')
            if c['prompt'].split('Causal structure: ')[1].split('\n')[0] not in z['prompt']:
                raise ValueError('added node changed base graph')
        for rule in ('marginal','conditional'):
            if {t['order'] for t in pair if t['kind']=='arithmetic' and t['rule']==rule}!={'forward','reverse'}:
                raise ValueError('arithmetic balance')
    return {'families':len(worlds),'tasks':len(tasks),'split_counts':dict(Counter(w['split'] for w in worlds)),
            'action_positions':dict(Counter(('first' if (lookup[t['task_id']]['expected']=='X=1')==(t['order']=='forward') else 'second') for t in tasks if t['kind']!='graph'))}
