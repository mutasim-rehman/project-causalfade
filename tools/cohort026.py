"""Build and validate cohort 026 graph-switch development fixtures."""
import argparse
import hashlib
import json
import random
from fractions import Fraction as F
from pathlib import Path
from causalfade.graph_switch import family, encode_family, intervention_effect

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/cohort_026/input'


def numeric_table(world):
    j = world['joint']
    def prob(condition, event):
        den = sum(p for (w, x, y), p in j.items() if condition(w, x, y))
        num = sum(p for (w, x, y), p in j.items() if condition(w, x, y) and event(w, x, y))
        return num / den
    lines = ['Full observational distribution, identical across paired questions:']
    for w in (0, 1):
        for x in (0, 1):
            for y in (0, 1):
                lines.append(f'P(W={w}, X={x}, Y={y}) = {float(j[w,x,y]):.6f}')
    lines.append('You may use the following values derived from that same joint table:')
    for w in (0, 1):
        lines.append(f'P(W={w}) = {float(prob(lambda a,b,c: True, lambda a,b,c: a == w)):.6f}')
    for x in (0, 1):
        for w in (0, 1):
            lines.append(f'P(W={w}|X={x}) = {float(prob(lambda a,b,c: b == x, lambda a,b,c: a == w)):.6f}')
            lines.append(f'P(Y=1|X={x},W={w}) = {float(prob(lambda a,b,c: b == x and a == w, lambda a,b,c: c == 1)):.6f}')
    return '\n'.join(lines)


def prompt(table, graph, form, kind, option_order):
    desc = {'confounder': 'W causes X and W causes Y; X causes Y. W is determined before treatment X.',
            'mediator': 'X causes W and X causes Y; W causes Y. W is determined after treatment X.',
            'confounder_z': 'W causes X and W causes Y; X causes Y. W also causes an unmeasured Z, which has no effect on X or Y.'}[graph]
    if form == 'direct':
        stem = f'Consider binary treatment X and desirable outcome Y. Causal structure: {desc}\n{table}'
    else:
        stem = f'Setting X is an intervention, not an observation. The supplied structure is: {desc}\n{table}'
    if kind == 'graph':
        stem += '\nIn this structure, is W upstream of X or downstream of X?'
        options = ['upstream', 'downstream']
    elif kind == 'arithmetic':
        stem += '\nFor X=1, is P(Y=1|X=1,W=0) greater than P(Y=1|X=1,W=1)?'
        options = ['yes', 'no']
    else:
        stem += ('\nShould we set X=1 rather than X=0 to increase P(Y=1) under intervention?'
                 if form == 'direct' else '\nWhich setting gives the higher P(Y=1 | do(X))?')
        options = ['X=1', 'X=0']
    if option_order:
        options.reverse()
    return stem + '\nAnswer with exactly one of: ' + ' or '.join(options) + '. No explanation.'


def build(n_dev=8, n_validation=8, n_confirm=32):
    tasks, truth, worlds = [], [], []
    splits = [('development', n_dev, 260000), ('validation', n_validation, 270000),
              ('confirmation', n_confirm, 280000)]
    for split, count, start in splits:
        for i in range(count):
            world = family(start + i, bool(i % 2))
            family_id = f'{split}_{i:03d}'
            worlds.append({'family_id': family_id, 'split': split, **encode_family(world)})
            table = numeric_table(world)
            for form in ('direct', 'decision'):
                for kind, graph in [('switch', 'confounder'), ('switch', 'mediator'),
                                    ('no_change', 'confounder'), ('no_change', 'confounder_z'),
                                    ('graph', 'confounder'), ('graph', 'mediator'),
                                    ('arithmetic', 'confounder')]:
                    ordinal = len(tasks)
                    option_order = (i + ordinal) % 2
                    task_id = f'{family_id}_{form}_{kind}_{graph}'
                    expected = ('upstream' if graph != 'mediator' else 'downstream') if kind == 'graph' else (
                        ('yes' if world['joint'][(0,1,1)] / sum(world['joint'][(0,1,y)] for y in (0,1)) >
                                  world['joint'][(1,1,1)] / sum(world['joint'][(1,1,y)] for y in (0,1)) else 'no')
                        if kind == 'arithmetic' else ('X=1' if intervention_effect(world['joint'], 'confounder' if graph == 'confounder_z' else graph) > 0 else 'X=0'))
                    tasks.append({'task_id': task_id, 'family_id': family_id, 'split': split,
                                  'form': form, 'kind': kind, 'graph': graph,
                                  'option_order_reversed': bool(option_order),
                                  'prompt': prompt(table, graph, form, kind, option_order)})
                    truth.append({'task_id': task_id, 'expected': expected,
                                  'effect': str(intervention_effect(world['joint'], 'confounder' if graph == 'confounder_z' else graph)) if kind in ('switch','no_change') else None})
    return worlds, tasks, truth


def write():
    OUT.mkdir(parents=True, exist_ok=True)
    data = build()
    names = ('worlds.jsonl', 'public_tasks.jsonl', 'oracle_truth.jsonl')
    for name, records in zip(names, data):
        (OUT / name).write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in records), encoding='utf-8')
    manifest = {'classification': 'development fixture plus sealed validation/confirmation inputs; no inference',
                'counts': dict(zip(names, map(len, data))),
                'sha256': {n: hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n',encoding='utf-8')
    return manifest


if __name__ == '__main__':
    print(json.dumps(write(), indent=2))
