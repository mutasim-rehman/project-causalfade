# Cohort 020: staged component diagnostic

## Completion and validity

The 224-prompt development fixture was frozen before model calls at commit `2c48637` on 14 November 2026. It contains eight fresh families (seed 20261116), 32 matched randomized-rate stems, 160 intervention decisions across five evidence conditions, 32 single-pair number comparisons and 32 genuinely ordered direct source-identification checks. The existing 7B F16 checkpoint ran on the verified b12176 CPU server with eight threads, F16 KV, no GPU layers, greedy decoding and a constant 64-token cap. It completed 224/224 requests in 1,449 seconds (24.1 minutes), with 224 strict-valid answers and no infrastructure failures. Raw attempts, schedule, configuration, hashes, logs and session provenance are preserved in [run_001_7b_f16](run_001_7b_f16/). All 49 repository tests and the fixture validator passed. No Q4 or 14B inference was run.

## Component results

| Task | Correct / scheduled | Activation among valid decisions |
| --- | ---: | ---: |
| Compare randomized rates only | 28/32 | — |
| Randomized evidence alone | 29/32 | 13/32 |
| Aligned, randomized block first | 31/32 | 17/32 |
| Aligned, historical block first | 19/32 | 3/32 |
| Conflict, randomized block first | 19/32 | 21/32 |
| Conflict, historical block first | 16/32 | 0/32 |
| Directly identify randomized study | 32/32 | — |

All cells were complete and strict-valid. Number comparison was 16/16 when X=1 was larger and 12/16 when X=0 was larger. Randomized-only decisions were 16/16 for harmful interventions and 13/16 for beneficial interventions. Direct source identification was 8/8 in each randomized-name × actual-order cell, showing that the clear numbered-block check is usable under both names and positions. This does not prove that source information is applied correctly inside a full intervention decision.

The family-paired randomized-only minus number-comparison accuracy difference was +3.1 percentage points (eight-family percentile interval −15.6 to +25.0); seven matched answers flipped from X=1/activate to X=0/leave-off and none in the other direction. These tasks differ in wording and demands, so this contrast is diagnostic rather than a decomposition of processing stages.

Relative to randomized-only decisions on the same stems, aligned evidence changed accuracy by +6.25 points when the randomized block was first (family interval 0 to +15.6) and −31.25 points when historical was first (−43.75 to −12.5). Conflict evidence changed accuracy by −31.25 points randomized-first (−50 to −12.5) and −40.625 points historical-first (−46.875 to −31.25). Physical order reversal changed aligned accuracy by −37.5 points historical-first minus randomized-first (−46.875 to −25); 14 decisions flipped activate→leave-off and none the other way. The conflict order accuracy difference was −9.375 points (−25 to +6.25), but 21/32 decisions flipped activate→leave-off and none reversed. Accuracy masks that large action shift because effects were balanced in direction.

Direction-specific behavior makes the presentation pattern clearer. Historical-first conflict decisions were leave-off on all 32 stems: 16/16 correct for harmful interventions and 0/16 for beneficial ones. Historical-first aligned decisions also favored leave-off: 16/16 harmful correct and 3/16 beneficial correct. Randomized-first conflict decisions activated on 21/32, scoring 12/16 on beneficial and 7/16 on harmful interventions. The stronger 0.12 effect rescued randomized-only beneficial decisions (8/8 versus 5/8 at 0.04), but did not rescue historical-first beneficial conflict decisions (0/8 at either strength). The source blocks were physically ordered as recorded; the older cohort 019 source-check position ambiguity was removed in this fixture.

## Interpretation and next experiment

The main failure point in this 7B F16 task is **combining and presenting two sources**, especially the action shift when historical evidence is shown first. Single-pair numerical comparison, randomized-only intervention decisions and direct study identification were comparatively strong. The randomized-only preface still mentions historical operator choice as background, although it displays only randomized evidence; this limits how purely that condition isolates one source. The direct identification checks also use simpler evidence than the full decisions. The pattern remains compatible with source weighting, position bias, action bias, instruction interaction or combinations of them. The separate component scores do not uniquely identify an internal processing route, and eight families give coarse uncertainty. The 7B reference is suitable for further *component development* but not yet for a two-source causal-sensitivity precision comparison.

The next experiment should be one newly planned development fixture that keeps matched worlds and semantic responses but adds an explicit **which study should govern the intervention decision?** task alongside a separate fresh-context intervention choice, with physical block order crossed. That would test whether the model selects the randomized source yet changes its action when both rates are present. Freeze its prompts, scoring and gate on fresh families before running it. Do not launch Q4 or confirmation from the current diagnostic. All cohort 020 results are development-only; there is no quantization effect, formal mediation or identified psychological mechanism here.

See [development_analysis.json](development_analysis.json), [development_analysis.md](development_analysis.md), and [frozen_run_plan.json](frozen_run_plan.json) for all strata, paired flips, family intervals and provenance.
