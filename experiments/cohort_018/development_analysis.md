# Sensitivity development pilot

Development-only; no confirmatory inference.

Reference operational competence gate: False.

## Reference

- causal: 64/128 correct; 128 valid.
- mapping_check: 16/16 correct; 16 valid.
- noncausal: 62/128 correct; 128 valid.
- source_check: 16/16 correct; 16 valid.

Order effects (historical-first minus randomized-first accuracy):

- causal|conflict=False: +0.000; family percentile 95% interval [-0.125, 0.125].
- causal|conflict=True: -0.125; family percentile 95% interval [-0.5, 0.25].
- noncausal|conflict=False: -0.062; family percentile 95% interval [-0.375, 0.25].
- noncausal|conflict=True: -0.312; family percentile 95% interval [-0.40625, -0.25].

See the companion JSON for SDT strata, empirical curves, strategy scores and paired contrasts.

SDT assumptions are unverified. Response-mapping/source-name allocation may be between families; consult the fixture manifest.
Two strengths do not establish a full psychophysical curve. Fixed strategy scores describe action agreement, not held-out model superiority.
Matched controls differ in instruction semantics. No latent-route, neural-mechanism or general quantization claim follows.
