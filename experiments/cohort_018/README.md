# Cohort 018: prepared sensitivity/bias development pilot

**Prepared 13 November 2026; no model inference performed.** This is development data, not a registered or power-justified confirmatory study. Its prompts and operational gate are fixed in the hashed input manifest before inference. Do not silently regenerate this directory or alter thresholds after inspecting outcomes.

## Design and cost

The committed fixture contains eight independent families and **288 prompts per format**:

- 128 causal intervention choices.
- 128 matched-number noncausal primary-scorecard comparisons.
- 16 response-mapping and 16 source-comprehension checks.

Within each family, decision tasks cross two causal magnitudes (0.04 and 0.12), both causal directions, both observational directions, both source orders and both task types. Absolute observational differences are matched at 0.36. SCM severity gaps vary between families, and a family-specific outcome baseline offset in [−0.04, +0.04] changes the displayed rates while preserving both effects. Without this offset, fixed marginal strengths would produce repeated numerical prompts despite different hidden severity gaps. All rates are exact population quantities rendered to six decimals.

Response mappings and neutral source identifiers are balanced between families in a 2×2 allocation, not crossed within each family. Their effects are exploratory between-family diagnostics; do not present them as within-world causal effects or formal measurement invariance. A fully crossed response-mapping fixture can be generated separately with `--cross-mappings`; it doubles the request count and is a different fixture. Two strengths and one observational magnitude do not identify a complete psychophysical curve or a separate observational-strength slope.

Only `prompt` is sent into a fresh model context. The JSON key `activate` transports a binary output token; some prompts reverse its semantic mapping. Always use the new scorer. The old direct-pilot scorer would misinterpret reversed tokens. Public metadata contains no evaluator conditions.

## Operational reference gate

The proposed 7B F16 reference must complete the entire fixture successfully and meet all manifest cutoffs:

- At least 90% strict-valid responses overall (260/288).
- At least 62.5% causal accuracy (80/128).
- At least 55% conflict accuracy separately in each order (18/32 per order).
- At least 87.5% comprehension accuracy (28/32 across both checks).

These are operational development cutoffs, not calibrated confidence tests of competence. Missing/invalid outputs count as wrong. Gate failure stops the conditional Q4 run; preserve the failure and revise using a new development fixture/version. Never select individual tasks by reference correctness.

## Run and analyze

Use the [lab runbook](../../docs/LAB_FOLLOWUP_RUNBOOK.md). The new CLI supplies preparation/validation, CPU inference with append-only records and resumable budgets, strict semantic scoring, a reference-gated comparison and JSON/Markdown analysis.

The shipped fixture uses seed 20261114. Regenerate only to a new directory using the same seed/configuration to check reproducibility:

```bash
python tools/sensitivity_pilot.py prepare --out /tmp/causalfade-reproduction-input --families 8 --seed 20261114
python tools/sensitivity_pilot.py validate --dataset experiments/cohort_018/input
```

The analysis reports task-type accuracy, validity, activation, SDT summaries by strength/order, empirical response curves, administration breakdowns, family-cluster order effects, fixed-strategy action-prediction scores, paired precision accuracy differences and a causal-minus-control precision interaction. Strategy probabilities are fixed at 0.99/0.01 without fitting: they are descriptive baselines, not a held-out model-selection experiment. Hierarchical curve fitting, a full C/A/B-versus-integration comparison, new power simulations and independent model-family confirmation remain later work.
