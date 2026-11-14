# Cohort 018: development reference screen

## Completion and gate

On 14 November 2026, the prepared eight-family fixture validated at 288 tasks, all 37 tests passed, and the existing CPU llama.cpp b12176 server and 7B F16/Q4_K_M model hashes matched cohort 016. The F16 reference completed 288/288 requests in about 34 minutes (04:06–04:40 UTC), with 288 strict-valid outputs and no recorded infrastructure failures. Available memory was 25 GiB and disk space 101 GiB before the run. The reference used eight CPU threads, no GPU layers, F16 KV, greedy decoding, and the committed fixture. Raw records, schedule, configuration, server log, metrics and gate result are preserved in [run_001_7b_f16](run_001_7b_f16/).

The fixed operational gate **failed**. F16 scored 64/128 causal choices against the required 80/128. Conflict accuracy was 18/32 randomized-first (meeting its cutoff) and 14/32 historical-first (below 18/32). Validity was 288/288 (required 260) and mapping/source comprehension was 32/32 (required 28). Q4_K_M was therefore not run. This is a completed development screen, not a confirmatory precision comparison.

## Patterns and interpretation

Accuracy was 64/128 on causal decisions and 62/128 on matched-number noncausal controls. The controls show that the poor score is not confined to the causal instruction; they do not equate the two tasks' semantics. Activation occurred on 74/128 causal decisions and 62/128 controls. Both strengths yielded 32/64 causal correct. At strength 0.04, corrected SDT d-prime was 0.31 randomized-first and −0.30 historical-first; at 0.12 it was 0 in both orders. At 0.12 randomized-first, hits and false alarms were both 12/16, illustrating an activation shift without measured discrimination gain. Equal-variance SDT assumptions are unverified.

The causal historical-first minus randomized-first accuracy contrast was 0 points on aligned items (eight-family percentile interval −12.5 to +12.5) and −12.5 points on conflicts (−50 to +25). Matched controls showed −6.25 points on aligned items (−37.5 to +25) and −31.25 on conflicts (−40.625 to −25). Order thus matters on controls too; these small-family intervals and task differences do not identify a causal-specific presentation effect. The available strength grid does not support a full response curve, and stronger evidence did not improve aggregate causal accuracy in this screen.

Administration diagnostics show 50/64 causal correct under mapping 0 versus 14/64 under mapping 1; controls show 51/64 versus 11/64. Yet the 16 mapping checks and 16 source checks were all correct. This suggests that applying a reversed token mapping inside the longer decision task may be difficult despite isolated comprehension. Mappings and source names vary **between** families, so these are confounded with family and cannot identify within-world mapping or name effects. The fixed first-source strategy had the lowest descriptive action-prediction log loss (2.09) among the listed baselines, followed by always-activate (2.16); agreement is not a fitted or held-out mechanism test. Sensitivity, action bias, token mapping and presentation remain entangled.

## Research decision

Revise the task in a separately versioned development fixture. Cross output mappings **within each family** while retaining paired causal/control numbers, orders and strengths, and test a clearer decision response contract on new development families. Keep this fixture, gate and failed reference screen unchanged. Screen F16 again before any conditional precision comparison. The existing 34-minute F16 runtime makes a bounded revised pilot feasible on this PC; do not launch larger confirmation until the task demonstrates stable reference competence.

For a later frozen study, a candidate primary endpoint is the family-standardized Q4_K_M-minus-F16 difference in balanced causal accuracy at the two prespecified strengths, contrasted with the corresponding difference on matched numerical controls. This format-by-task contrast remains a **candidate**, contingent on reference competence, endpoint specification and new family-cluster power/coverage simulation. Cohort 016's power calculation does not apply. All cohort 018 findings are development-only.

See [development_analysis.json](development_analysis.json) and [development_analysis.md](development_analysis.md). No 14B inference was repeated.
