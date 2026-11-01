"""Constrained MLE for a proposed processing tree, plus a competing model.

Cells are ordered (T,S) = (0,0), (0,1), (1,0), (1,1).
Weights mix four policies: follow T, follow S, always yes, always no.
EM maximizes a concave binomial likelihood on the simplex. It does not fit
the planned hierarchical model or establish that these are neural routes.
"""
import numpy as np

POLICIES = np.array([[0., 0., 1., 0.], [0., 1., 1., 0.],
                     [1., 0., 1., 0.], [1., 1., 1., 0.]])


def probabilities(c, a, b):
    values = np.array([c, a, b], dtype=float)
    if np.any((values < 0) | (values > 1)) or not np.all(np.isfinite(values)):
        raise ValueError('Parameters must be finite probabilities.')
    return POLICIES @ np.array([c, (1-c)*a, (1-c)*(1-a)*b, (1-c)*(1-a)*(1-b)])


def fit_counts(successes, totals, tol=1e-9, max_iter=10000):
    if tol <= 0 or max_iter < 1:
        raise ValueError('Need a positive tolerance and iteration budget.')
    y = np.asarray(successes, dtype=float)
    if y.ndim == 1:
        y = y[None, :]
    n = np.broadcast_to(np.asarray(totals, dtype=float), y.shape)
    if y.ndim != 2 or y.shape[1] != 4 or not np.all(np.isfinite(y)) or not np.all(np.isfinite(n)):
        raise ValueError('Expected finite counts in four cells.')
    if np.any(n <= 0) or np.any(y < 0) or np.any(y > n):
        raise ValueError('Require 0 <= successes <= totals and positive cell totals.')
    weights = np.full((len(y), 4), .25)
    for iteration in range(max_iter):
        p = np.clip(weights @ POLICIES.T, 1e-14, 1-1e-14)
        update = weights * ((y/p) @ POLICIES + ((n-y)/(1-p)) @ (1-POLICIES)) / n.sum(axis=1)[:, None]
        change = np.max(np.abs(update - weights), axis=1)
        weights = update / update.sum(axis=1)[:, None]
        if np.max(change) < tol:
            break
    p = np.clip(weights @ POLICIES.T, 1e-14, 1-1e-14)
    c = weights[:, 0]
    a = np.divide(weights[:, 1], 1-c, out=np.full(len(y), np.nan), where=(1-c) > 1e-6)
    rem = weights[:, 2] + weights[:, 3]
    b = np.divide(weights[:, 2], rem, out=np.full(len(y), np.nan), where=rem > 1e-6)
    return dict(parameters=np.column_stack([c, a, b]), weights=weights, probabilities=p,
                converged=change < tol, iterations=iteration+1,
                log_likelihood=np.sum(y*np.log(p)+(n-y)*np.log1p(-p), axis=1))


def deviance(y, n, p):
    y, n, p = np.asarray(y, float), np.asarray(n, float), np.asarray(p, float)
    empirical = np.clip(y/n, 1e-14, 1-1e-14)
    p = np.clip(p, 1e-14, 1-1e-14)
    return 2*np.sum(y*np.log(empirical/p)+(n-y)*np.log((1-empirical)/(1-p)), axis=-1)


def bootstrap_fit_test(y, n, rng, replicates=500):
    if replicates < 1:
        raise ValueError('Need at least one bootstrap replicate.')
    fitted = fit_counts(y, n)
    p = fitted['probabilities'][0]
    boot = rng.binomial(n, p, size=(replicates, 4))
    fits = fit_counts(boot, n)
    observed = float(deviance(y, n, p))
    simulated = deviance(boot, n, fits['probabilities'])
    # Monte Carlo correction; no nominal chi-square assumption at boundaries.
    return dict(deviance=observed, bootstrap_p=float((1+np.sum(simulated >= observed))/(replicates+1)),
                bootstrap_replicates=replicates,
                nonconverged=int(np.sum(~fits['converged'])),
                observed_fit_converged=bool(fitted['converged'][0]))


def fit_logistic(y, n):
    """Additive logistic evidence integration, a competing behavioral model."""
    y, n = np.asarray(y, float), np.asarray(n, float)
    x = np.column_stack([np.ones(4), POLICIES[:, :2]])
    beta = np.zeros(3)
    for _ in range(100):
        p = 1/(1+np.exp(-np.clip(x @ beta, -30, 30)))
        h = x.T @ ((n*p*(1-p))[:, None]*x) + np.eye(3)*1e-8
        step = np.linalg.solve(h, x.T @ (y-n*p))
        beta += step
        if np.max(np.abs(step)) < 1e-9:
            break
    return {'coefficients': beta, 'probabilities': 1/(1+np.exp(-np.clip(x@beta, -30, 30))),
            'converged': bool(np.max(np.abs(step)) < 1e-9)}
