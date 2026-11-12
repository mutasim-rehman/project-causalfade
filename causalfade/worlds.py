"""Binary confounded SCMs with an orthogonal 2 x 2 diagnostic design."""
from dataclasses import dataclass, asdict
import hashlib
import numpy as np


@dataclass(frozen=True)
class World:
    family_id: str
    causal_positive: int
    association_positive: int
    effect_size: float
    severity_gap: float
    assignment_strength: float

    def __post_init__(self):
        if self.causal_positive not in (0, 1) or self.association_positive not in (0, 1):
            raise ValueError('Condition indicators must be binary.')
        if not 0 < self.assignment_strength < 1:
            raise ValueError('Assignment must satisfy positivity.')
        if not 0 < self.effect_size < self.assignment_strength * self.severity_gap:
            raise ValueError('Association must dominate the effect in conflict cells.')
        if not 0 < self.severity_gap < 1 - self.effect_size:
            raise ValueError('Outcome probabilities must be strictly interior.')

    @property
    def tau(self):
        return (2 * self.causal_positive - 1) * self.effect_size

    @property
    def propensity(self):
        # k < 0 assigns X more often to healthy machines, producing positive association.
        k = -(2 * self.association_positive - 1) * self.assignment_strength
        return np.array([(1 - k) / 2, (1 + k) / 2])

    @property
    def outcome(self):
        # Rows: Z=0 (healthy), Z=1 (severe). Columns: X=0, X=1.
        mu = np.array([0.5 + self.severity_gap / 2, 0.5 - self.severity_gap / 2])
        return mu[:, None] + np.array([-0.5, 0.5])[None, :] * self.tau

    @property
    def do_means(self):
        return self.outcome.mean(axis=0)

    @property
    def observational_means(self):
        ex = self.propensity
        return np.array([np.dot(1 - ex, self.outcome[:, 0]),
                         np.dot(ex, self.outcome[:, 1])])

    @property
    def observational_difference(self):
        means = self.observational_means
        return float(means[1] - means[0])

    def sample_counts(self, n, rng):
        if n < 1:
            raise ValueError('Sample size must be positive.')
        z = rng.binomial(1, 0.5, n)
        x = rng.binomial(1, self.propensity[z])
        y = rng.binomial(1, self.outcome[z, x])
        return [dict(z=i, x=j, n=int(np.sum((z == i) & (x == j))),
                     successes=int(np.sum(y[(z == i) & (x == j)])))
                for i in (0, 1) for j in (0, 1)]

    def truth(self):
        return {**asdict(self), 'ate': self.tau,
                'observational_difference': self.observational_difference,
                'do_success_x0': float(self.do_means[0]),
                'do_success_x1': float(self.do_means[1]),
                'optimal_action': self.causal_positive,
                'conflict': self.causal_positive != self.association_positive}


def make_families(n, seed):
    if n < 1:
        raise ValueError('At least one world family is required.')
    rng = np.random.default_rng(seed)
    for family in range(n):
        params = dict(family_id=f'world-{family:04d}', effect_size=float(rng.uniform(.06, .12)),
                      severity_gap=float(rng.uniform(.50, .70)),
                      assignment_strength=float(rng.uniform(.65, .90)))
        for t, s in ((0, 0), (0, 1), (1, 0), (1, 1)):
            yield World(causal_positive=t, association_positive=s, **params)


def make_matched_signal_families(n, seed):
    """Generate 2x2 families with equal-magnitude observational contrasts.

    The causal effect and outcome severity gap are shared within each family.
    Assignment strength varies across cells so the observational contrast has
    magnitude ``target_observational_magnitude`` in all four cells.
    """
    if n < 1:
        raise ValueError('At least one world family is required.')
    rng = np.random.default_rng(seed)
    for family in range(n):
        effect_size = float(rng.uniform(.06, .12))
        severity_gap = float(rng.uniform(.68, .80))
        target = float(rng.uniform(.38, .46))
        family_id = f'world-{family:04d}'
        for causal_positive, association_positive in ((0, 0), (0, 1), (1, 0), (1, 1)):
            aligned = causal_positive == association_positive
            confounding_gap = target - effect_size if aligned else target + effect_size
            assignment_strength = confounding_gap / severity_gap
            yield World(family_id=family_id, causal_positive=causal_positive,
                        association_positive=association_positive,
                        effect_size=effect_size, severity_gap=severity_gap,
                        assignment_strength=assignment_strength)


def opaque_id(world, seed, mode):
    raw = f'{seed}:{world.family_id}:{world.causal_positive}:{world.association_positive}:{mode}'
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def prompt(world, evidence):
    # Ground truth and condition labels must never be passed to the agent.
    import json
    return (
        'A fictional machine has initial severity Z, setting X, and successful operation Y. '
        'All variables are binary. Z=1 means severe initial condition. X=1 activates the setting. '
        'Y=1 means success. The known causal graph is Z -> X, Z -> Y, X -> Y. '
        'There are no unmeasured common causes; consistency and positivity hold. '
        'The target population has P(Z=0)=P(Z=1)=0.5. '
        'Estimate the population average effect E[Y|do(X=1)]-E[Y|do(X=0)]. '
        'Decide whether to activate X for the population to maximize expected success. '
        'Use the evidence below, allowing for sampling uncertainty if it is a sample. '
        'Return only JSON with keys ate_estimate (number), activate (0 or 1), '
        'and adjustment_set (list of variable names).\nEvidence:\n' + json.dumps(evidence)
    )


def exact_evidence(world):
    return {'type': 'exact_population_probabilities', 'strata': [
        dict(z=z, x=x, success_probability=float(world.outcome[z, x]),
             population_cell_probability=float(.5 * (world.propensity[z] if x else 1-world.propensity[z])))
        for z in (0, 1) for x in (0, 1)]}


def backdoor_estimate(strata):
    if any(row['n'] == 0 for row in strata):
        return None  # Do not silently smooth or invent an empty stratum.
    rates = {(r['z'], r['x']): r['successes'] / r['n'] for r in strata}
    return .5 * sum(rates[z, 1] - rates[z, 0] for z in (0, 1))


def naive_estimate(strata):
    n = [sum(r['n'] for r in strata if r['x'] == x) for x in (0, 1)]
    if min(n) == 0:
        return None
    return sum(r['successes'] for r in strata if r['x'] == 1) / n[1] - sum(
        r['successes'] for r in strata if r['x'] == 0) / n[0]
