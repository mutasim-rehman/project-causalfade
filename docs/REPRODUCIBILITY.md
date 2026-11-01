# Reproducing the design-validation package

This package runs locally with Python 3.10+ and NumPy. The separate literature downloader also needs pypdf and network access. No model weights, API credentials or GPU are required for synthetic validation.

## Install and verify

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m causalfade.generate --families 24 --rows 2000 --seed 20261101 --out results/design_validation
python -m causalfade.validate --repetitions 200 --bootstrap 500 --seed 20261101 --out results/design_validation
```

The committed run uses NumPy 2.3.5; Python/NumPy versions appear in the reports. Matching versions is recommended for byte-for-byte regeneration. Checksums in the generated manifest cover the exported task/truth/baseline files; they are not promises of identical output across arbitrary future numerical-library versions.

The seed is fixed for reproducibility, not selected for statistical significance. The validation default date-based seed is 20261101. Re-running overwrites the chosen output files. Choose a different `--out` directory to preserve an earlier run.

## Files produced

- `public_tasks.jsonl`: 192 prompts = 24 families x 4 cells x 2 evidence layers. Only the prompt field is sent to a model.
- `oracle_truth.jsonl`: evaluator-only true effects, condition labels, expected outcomes and optimal actions.
- `baselines.jsonl`: backdoor, association and seeded-random reference decisions. No LLM answers.
- `manifest.json`: generator arguments, baseline summaries and file SHA-256 hashes.
- `parameter_recovery.json`: 18 scenario/sample-size combinations, diagnostics, illustrative bootstrap intervals and model checks.
- `recovery_replicates.csv`: all 3,600 synthetic fitted datasets, including nonconverged/undefined results.
- `VALIDATION_REPORT.md`: readable generated report.

The report gives bias/RMSE only for finite converged estimates and discloses excluded counts in JSON. Do not silently discard the corresponding failure records in the CSV or interpret retained averages as uniformly reliable boundary estimation.

## Scoring future outputs

One predictions file must correspond to one checkpoint/configuration/run. See the [data contract](DATA_CONTRACT.md). Write a provenance JSON with at least `checkpoint`, `precision`, `quantizer`, `seed` and `evidence_source`; retain the richer run information specified in the methodology.

```bash
python -m causalfade.score --truth results/design_validation/oracle_truth.jsonl --predictions path/to/predictions.jsonl --provenance path/to/provenance.json --out path/to/scored.jsonl
```

The `path/to` paths describe researcher-supplied run files, not bundled LLM results. Missing predictions are scored as incorrect actions; malformed JSONL must be repaired or represented explicitly as an invalid task response rather than skipped. Do not let a runner silently omit parsing failures from the denominator.

Compare two scored runs using complete matched families:

```bash
python -m causalfade.analyze --reference path/to/full_precision_scored.jsonl --comparison path/to/quantized_scored.jsonl --mode exact --bootstrap 2000 --out path/to/paired_contrast.json
```

This computes the probability-scale change in conflict penalty and a family-block percentile-bootstrap interval. It rejects mismatched task sets, duplicate IDs and incomplete four-cell families. It is a pilot nonparametric analysis, not the planned hierarchical GLMM, a power calculation or a calibrated confirmatory p-value.

## Validation sequence and interpretation

1. Verify analytic SCM signs, positivity and backdoor effects with tests.
2. Check reference baselines and export determinism.
3. Inspect recovery across sample sizes, including boundaries and convergence failures.
4. Inspect fit on tree-generated responses, observationally equivalent logistic responses, and an incompatible asymmetric logistic generator.
5. Compare held-out predictive log loss. A single split is a demonstration; future model selection must hold out whole world families.
6. Expand simulation to hierarchical dependence, interval coverage, test calibration and power before confirmatory collection.

These steps validate portions of the experiment and measurement implementation. They do not establish that real LLM responses follow the tree or that quantization causes any particular deficit.

## Test coverage

Tests exercise independent sign manipulation, valid probabilities, analytic adjustment, sampled estimation, deterministic export, withholding of oracle labels from prompts, empty strata, constrained-likelihood recovery, boundary identification, equivalent/violating rival generators, invalid-output scoring, and preservation of paired families in analysis. No test downloads a model or calls an API.
