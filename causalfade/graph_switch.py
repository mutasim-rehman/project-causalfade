"""Exact-rational observationally equivalent causal-graph switch oracle."""
from fractions import Fraction as F
from itertools import product

W = (F(1, 2), F(1, 2))
X_GIVEN_W = (F(9, 10), F(1, 10))
Y_GIVEN_XW = ((F(85, 100), F(75, 100)), (F(25, 100), F(15, 100)))


def observational_joint(reverse_outcome=False):
    """Return P(W=w,X=x,Y=y), indexed by binary variable tuple."""
    out = {}
    for w, x, y in product((0, 1), repeat=3):
        px = X_GIVEN_W[w] if x else 1 - X_GIVEN_W[w]
        py = Y_GIVEN_XW[w][x]
        if reverse_outcome:
            py = 1 - py
        out[(w, x, y)] = W[w] * px * (py if y else 1 - py)
    assert sum(out.values()) == 1
    return out


def intervention_effect(joint, graph):
    """Graph A: W confounds X/Y. Graph B: X causes W, then Y."""
    if graph not in ('confounder', 'mediator'):
        raise ValueError(graph)
    def risk(x):
        p_x = sum(v for (w0, x0, y0), v in joint.items() if x0 == x)
        total = F(0)
        for w in (0, 1):
            p_w = sum(v for (w0, x0, y0), v in joint.items() if w0 == w)
            p_wx = sum(v for (w0, x0, y0), v in joint.items() if w0 == w and x0 == x)
            p_ywx = joint[(w, x, 1)] / p_wx
            weight = p_w if graph == 'confounder' else p_wx / p_x
            total += weight * p_ywx
        return total
    return risk(1) - risk(0)


def validate_pair(reverse_outcome=False):
    joint_a = observational_joint(reverse_outcome)
    joint_b = observational_joint(reverse_outcome)
    assert joint_a == joint_b
    a = intervention_effect(joint_a, 'confounder')
    b = intervention_effect(joint_b, 'mediator')
    if not a * b < 0:
        raise ValueError('No opposite intervention signs')
    return {'joint': joint_a, 'confounder_effect': a, 'mediator_effect': b}


def family(seed, reverse_outcome=False):
    """Deterministic, distinct exact-rational families; reject weak/non-switch worlds."""
    import random
    rng = random.Random(seed)
    for _ in range(10000):
        pw = F(rng.randint(4, 6), 10)
        px = (F(rng.randint(7, 9), 10), F(rng.randint(1, 3), 10))
        low = F(rng.randint(65, 85), 100)
        high = F(rng.randint(15, 35), 100)
        harm = F(rng.randint(5, 15), 100)
        if low <= high or low - harm <= 0 or high - harm <= 0:
            continue
        joint = {}
        for w, x, y in product((0, 1), repeat=3):
            p_w = pw if w else 1 - pw
            p_x = px[w] if x else 1 - px[w]
            p_y = (low if w == 0 else high) - x * harm
            if reverse_outcome:
                p_y = 1 - p_y
            joint[(w, x, y)] = p_w * p_x * (p_y if y else 1 - p_y)
        a = intervention_effect(joint, 'confounder')
        b = intervention_effect(joint, 'mediator')
        if a * b < 0 and abs(a) >= F(4, 100) and abs(b) >= F(15, 100):
            return {'seed': seed, 'reverse_outcome': reverse_outcome, 'joint': joint,
                    'confounder_effect': a, 'mediator_effect': b,
                    'parameters': {'p_w1': pw, 'p_x1_given_w': px,
                                   'p_y1_baselines': (low, high), 'harm': harm}}
    raise ValueError('Could not generate a sufficiently separated family')


def encode_family(record):
    """JSON-safe exact representation for manifests and independent checking."""
    return {'seed': record['seed'], 'reverse_outcome': record['reverse_outcome'],
            'joint': [{'w': w, 'x': x, 'y': y, 'p': str(p)}
                      for (w, x, y), p in sorted(record['joint'].items())],
            'confounder_effect': str(record['confounder_effect']),
            'mediator_effect': str(record['mediator_effect']),
            'parameters': {k: [str(v) for v in value] if isinstance(value, tuple) else str(value)
                           for k, value in record['parameters'].items()}}
