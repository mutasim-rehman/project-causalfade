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
