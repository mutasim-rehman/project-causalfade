"""Monte Carlo power for a family-blocked, paired evidence-order contrast."""
import argparse
import json
from pathlib import Path
from statistics import NormalDist

import numpy as np


def t_critical_975(df):
    # Cornish-Fisher expansion around the standard-normal 97.5th percentile.
    z = NormalDist().inv_cdf(0.975)
    return (z + (z**3 + z) / (4 * df)
            + (5 * z**5 + 16 * z**3 + 3 * z) / (96 * df**2)
            + (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * df**3))


def power(n_families, effect, discordance, within_family_correlation,
          replicates, rng):
    p_minus = (discordance - effect) / 2
    p_zero = 1 - discordance
    if min(p_minus, p_zero, (discordance + effect) / 2) < 0:
        raise ValueError("Effect and discordance imply invalid category probabilities")
    cuts = (NormalDist().inv_cdf(p_minus),
            NormalDist().inv_cdf(p_minus + p_zero))
    covariance = np.array([[1, within_family_correlation],
                           [within_family_correlation, 1]])
    reject = 0
    chunk_size = 5000
    critical = t_critical_975(n_families - 1)
    for start in range(0, replicates, chunk_size):
        count = min(chunk_size, replicates - start)
        latent = rng.multivariate_normal(
            [0, 0], covariance, size=(count, n_families))
        paired_differences = np.where(
            latent < cuts[0], -1,
            np.where(latent < cuts[1], 0, 1))
        family_means = paired_differences.mean(axis=2)
        means = family_means.mean(axis=1)
        standard_errors = family_means.std(axis=1, ddof=1) / np.sqrt(n_families)
        statistics = means / standard_errors
        reject += int(np.count_nonzero(np.abs(statistics) > critical))
    estimate = reject / replicates
    return {"power": estimate,
            "monte_carlo_standard_error": float(
                np.sqrt(estimate * (1 - estimate) / replicates)),
            "t_critical_approximation": critical}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261129)
    parser.add_argument("--replicates", type=int, default=100000)
    parser.add_argument("--effect", type=float, default=0.20)
    args = parser.parse_args()
    rng = np.random.default_rng(args.seed)
    scenarios = {}
    for discordance in (0.5, 0.7, 0.9):
        for correlation in (0.25, 0.5):
            key = f"discordance_{discordance:.1f}_within_family_r_{correlation:.2f}"
            scenarios[key] = {
                str(n): power(n, args.effect, discordance, correlation,
                              args.replicates, rng)
                for n in (48, 64, 80, 96, 112)
            }
    result = {
        "primary_effect": args.effect,
        "primary_test": "two-sided one-sample t test of 96 family-level mean paired differences, alpha 0.05",
        "outcome": "Q4_K_M conflict accuracy, historical-first minus randomized-first",
        "families_per_block": 2,
        "discordance_scenarios": [0.5, 0.7, 0.9],
        "within_family_gaussian_copula_correlations": [0.25, 0.5],
        "replicates_per_design_cell": args.replicates,
        "monte_carlo_seed": args.seed,
        "method": "Generate two paired binary-outcome differences per family from a bivariate Gaussian copula with probabilities P(D=-1)=(d-delta)/2, P(D=0)=1-d, P(D=1)=(d+delta)/2; test family means with a two-sided t statistic.",
        "power_by_scenario_and_family_count": scenarios,
        "limitations": [
            "Planning simulation, not evidence about model performance.",
            "The 20-point effect is the prespecified smallest effect of interest; discordance and within-family correlation are design assumptions.",
            "The independent sampling unit is the SCM family; two conflict task pairs are nested within each family.",
        ],
    }
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
