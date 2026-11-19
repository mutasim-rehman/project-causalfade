# Cohort 026 — observationally identical graph-switch assay

Status: prospective design checkpoint; no fixture or model run yet. Stop broad precision sweeps on the current assay. The purpose is to test whether supplied causal structure changes intervention decisions when the observational joint distribution is identical.

## Task and oracle

Use binary W, X and Y. Construct two valid SCMs with the same complete observational P(W,X,Y) and opposite signs of P(Y=1|do(X=1)) - P(Y=1|do(X=0)). Include the document's W→X, W→Y, X→Y versus X→W→Y construction as a validator seed, then generate fresh families. Verify equality of the full joint distribution at exact rational precision before display rounding. Reject ties, impossible probabilities and sign changes caused only by rounding. Keep variable names and every displayed observational number identical within a graph-switch pair. Change only supplied causal structure and its truthful semantics. Counterbalance positive/negative correct actions, graph order, answer option order and task form.

Add graph transformations that preserve the intervention answer. Include direct graph-reading and arithmetic probes with matched numbers. Predeclare two independently worded task forms before model calls; hold family splits disjoint.

## Bounded development screen

Use two fixed model lineages selected and hashed before the first request. Start with F16 references only. One initial form and at most one documented wording revision per form are allowed; log every failed form and model. Do not add checkpoints or prompts based on favorable effects. A lineage qualifies only if strict validity is at least 95%, graph reading and arithmetic are each at least 80%, both graph-switch polarities are at least 70% correct, no-change controls are at least 80% correct, and paired switch fidelity is at least 60% on development families. These provisional gates must be frozen with exact denominators and family counts before inference. If neither lineage qualifies within the revision cap, stop and report assay failure.

## Confirmation gate

Only after development qualification, choose one primary endpoint: paired graph-switch fidelity, where both decisions in a pair are correct. Define no-change accuracy and correctly directed switching as secondary checks. Freeze scorer, family split, invalid-response policy (invalid is wrong), model/runtime hashes, prompt forms, stopping rule and analysis before untouched-family inference. Simulate the actual family-clustered endpoint for power, interval coverage and false positives; choose family count from that study. A paired precision contrast is permitted only for a qualifying reference and controls, with a separately frozen quantized format and family-level paired estimator. Do not infer selective precision damage from overall accuracy alone.

## Progress checkpoints

1. Mathematical SCM generator, oracle and equality validators; unit tests; commit and push.
2. Two task forms, counterbalance manifest, strict scorer and control tasks; tests and fixture validation; commit and push.
3. Frozen development plan and independent family split; commit and push before model calls.
4. Development run and qualification report, including failures; commit and push.
5. Family-level simulation, frozen primary analysis and confirmation plan; commit and push before untouched runs.
6. Confirmation and conditional precision contrast; archive raw outputs, hashes and report; commit and push.

Choose the manuscript claim after results: selective precision effect if it survives qualified controls, evaluation methodology if measurement distortions transfer and the protocol resolves them, or a new assay/domain if neither transfers. No novelty claim is made for observational equivalence itself.

## First implementation checkpoint

`causalfade/graph_switch.py` now reproduces the investigation document's exact-rational seed: the same observational joint distribution yields effects −0.10 (W confounds X/Y) and +0.38 (W mediates X/Y). Complementing Y reverses both signs. Unit tests cover both polarities and normalization. This is an oracle seed, not yet an independent family generator or a development fixture. No model inference has begun.
