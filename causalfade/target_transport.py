"""CF-TP1 private sampler and exact intervention/observation oracle."""

import hashlib
import itertools
import json
import random
from fractions import Fraction as Q

VERSION = "CF-TP1"
BITS = tuple(itertools.product(range(2), repeat=4))
DESIGN = tuple(itertools.product(range(2), range(2), (-1, 1)))
TOTAL = 4096


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def seed(*parts):
    return int(digest("|".join(map(str, (VERSION, *parts))).encode()), 16)


def task_id(indices):
    return format(seed("task", *indices), "064x")


def rational(value):
    value = Q(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def construct(trial, historical):
    """Stratum order is S=1, S=0. Surface axes are S, U, A."""
    return tuple(((2*h[0]-r[0], 3*r[1]-2*h[1]),
                  (3*r[0]-2*h[0], 2*h[1]-r[1]))
                 for r, h in zip(trial, historical))


def enumerate_world(tables, weights, role):
    trial, historical = (tuple(tuple(Q(cell, 200) for cell in row) for row in tables[i])
                         for i in (role, 1-role))
    surface = construct(trial, historical)
    if any(not 0 < q < 1 for stratum in surface for cells in stratum for q in cells):
        raise ValueError("Role world has a non-interior outcome probability")
    trial_check = tuple(tuple(sum(row[u][a]*Q(1, 2) for u in range(2))
                              for a in range(2)) for row in surface)
    joint_a = ((Q(3, 8), Q(1, 8)), (Q(1, 8), Q(3, 8)))
    historical_check = tuple(tuple(
        sum(row[u][a]*joint_a[u][a] for u in range(2)) /
        sum(joint_a[u][a] for u in range(2)) for a in range(2)) for row in surface)
    if (trial_check, historical_check) != (trial, historical):
        raise ValueError("Study margins do not reconstruct")
    scores = tuple(tuple(sum(Q(w, 100)*surface[s][u][a]*Q(1, 2)
                             for s, w in enumerate((weight, 100-weight)) for u in range(2))
                         for a in range(2)) for weight in weights)
    return surface, (trial_check, historical_check), scores


def sample():
    for h, (p, g, b) in enumerate(DESIGN):
        nuisance = list(BITS)
        random.Random(seed("nuisance", h)).shuffle(nuisance)
        for replicate, bits in enumerate(nuisance):
            slot = 16*h + replicate
            stream = seed(290431, slot)
            rng = random.Random(stream)
            for proposal in range(1, 100001):
                weights = rng.randint(54, 62), rng.randint(76, 84)
                untreated, effects = [], []
                for _ in range(2):
                    untreated.append((rng.randint(92, 108), rng.randint(92, 108)))
                    sign = rng.choice([-1, 1])
                    effects.append((sign*rng.randint(4, 16), -sign*rng.randint(4, 16)))
                if tuple(map(abs, effects[0])) == tuple(map(abs, effects[1])):
                    continue
                if any(b*(-1)**(g*r+p*k) * (w*d1+(100-w)*d0) < 100
                       for r, (d1, d0) in enumerate(effects) for k, w in enumerate(weights)):
                    continue
                tables = tuple(tuple((x, x+d) for x, d in zip(base, effect))
                               for base, effect in zip(untreated, effects))
                try:
                    worlds = tuple(enumerate_world(tables, weights, r) for r in range(2))
                except ValueError:
                    continue
                yield slot, h, bits, stream, proposal, tables, weights, worlds
                break
            else:
                raise ValueError(f"Proposal cap exhausted at slot {slot}")


def aliases(tables, weights):
    """Numerical signature vectors in percentage points."""
    for source, target, strata, treat, complement in itertools.product(range(2), repeat=5):
        yield tuple(100-w if strata else w for w in weights[::1-2*target]) + tuple(
            Q(200-v if complement else v, 2)
            for table in tables[::1-2*source] for row in table[::1-2*strata]
            for v in row[::1-2*treat])
