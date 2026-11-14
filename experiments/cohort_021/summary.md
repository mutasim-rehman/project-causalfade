# Cohort 021: source selection and guidance diagnostic

## Completion and validity

The 576-prompt, eight-family development fixture was frozen before inference at commit `52ffe3d` on 14 November 2026. Seed 20261117 supplied 32 randomized-only base stems and 128 two-source evidence stems; each two-source stem had independent source-selection, ordinary-decision, source-guided-decision and neutral-guided-decision requests. Thirty-two direct identification checks completed the design. The 7B F16 reference completed 576/576 requests with 576 strict-valid answers and no infrastructure failures in 4,327 seconds (72.1 minutes). The verified b12176 CPU server used eight threads, F16 KV, no GPU layers, temperature zero, fresh contexts and a 64-token cap. Raw attempts, schedule, configuration, hashes, logs and session provenance are in [run_001_7b_f16](run_001_7b_f16/). All 53 repository tests and the fixture validator passed. No Q4, new checkpoint or confirmatory collection was run.

## Source selection versus action choice

Directly identifying the randomized study was 32/32 correct, including 8/8 in each randomized-name × physical-order cell. Selecting the **governing study for estimating the intervention effect** was 128/128 correct, including 32/32 in each agreement × order cell and 32/32 for each randomized-name × order cell. Randomized-only intervention decisions were 30/32 correct: 16/16 for harmful interventions and 14/16 for beneficial ones.

Two-source action accuracy was much lower despite correct governing-source selection:

| Condition | Ordinary | Source guided | Neutral guided |
| --- | ---: | ---: | ---: |
| Aligned, randomized first | 16/32 | 16/32 | 16/32 |
| Aligned, historical first | 17/32 | 14/32 | 16/32 |
| Conflict, randomized first | 16/32 | 16/32 | 16/32 |
| Conflict, historical first | 9/32 | 12/32 | 8/32 |
| **All two-source decisions** | **58/128** | **58/128** | **56/128** |

Every randomized-first two-source decision activated X under all three contracts, so each scored 16/32 on direction-balanced stems. Historical-first conflict accuracy was 9/32 ordinary, 12/32 guided and 8/32 neutral guided. Relative to paired randomized-only decisions, ordinary accuracy fell by 43.75 points in either randomized-first condition (eight-family percentile interval −50 to −34.375) and by 65.625 points in historical-first conflict (−71.875 to −56.25). The ordinary conflict historical-first minus randomized-first order effect was −21.875 points (−25 to −15.625), with 25/32 actions flipping activate→leave-off and none the other way. The guided conflict order effect was −12.5 points (−28.125 to +3.125), with 10/32 such flips; order sensitivity remains.

## Guidance and joint patterns

Specific guidance did not improve aggregate two-source accuracy: 58/128 guided versus 58/128 ordinary, while neutral guidance was 56/128. In historical-first conflict, guided minus ordinary accuracy was +9.375 points (family interval −3.125 to +25) and guided minus neutral was +12.5 points (−3.125 to +28.125). In historical-first aligned cells, guided minus ordinary was −9.375 points (−18.75 to −3.125) and guided minus neutral was −6.25 points (−15.625 to 0). These opposite changes cancel in the aggregate. Specific guidance shifted 15 historical-first conflict actions and seven historical-first aligned actions from leave-off to activate, with no reverse flips in those paired cells. Activation rose from 94/128 ordinary and 96/128 neutral guided to 116/128 source guided. Guided accuracy was 55/64 for beneficial interventions but only 3/64 for harmful ones; ordinary was 44/64 and 14/64. This is a large action-propensity change, not a stable gain in discrimination.

Across independent fresh-context requests on the same evidence stems, governing-source selection was always correct. The four descriptive source-selection × decision-correctness cells therefore total 58 correct-source/correct-decision and 70 correct-source/incorrect-decision for ordinary actions; 58/70 for guided; and 56/72 for neutral guided. Both incorrect-source cells are zero. These joint patterns do not show the model's internal sequence or establish mediation. Guidance changes the task and cannot be labeled preserved unassisted causal reasoning. The source-selection prompt itself explicitly asks for an intervention-evidence criterion; success on it need not imply spontaneous use of that criterion during an action choice.

## Decision

The 7B F16 two-source task is **not ready for a precision comparison**. The main observed difficulty is translating a correctly identified governing source into a balanced intervention choice when both sources are displayed. The result is compatible with position-driven action bias, response habit, evidence integration failure or several interacting causes; it does not identify a psychological route. Eight families provide coarse development uncertainty, and saturated randomized-first activation limits what accuracy alone reveals.

Stop further broad prompt expansion on this checkpoint. The next experiment should be a separately planned diagnostic with an independent checkpoint family on fresh, matched worlds using the same source-selection and action conditions, to test whether this failure is specific to the 7B Qwen task/checkpoint. No checkpoint download or additional inference is part of cohort 021. If the pattern persists, narrow the research target to presentation-linked action behavior before considering any confirmatory protocol. A later precision study would require a newly declared competence gate and family-cluster power/coverage simulation; cohort 016's calculation does not apply.

All cohort 021 results are development-only. See [development_analysis.json](development_analysis.json), [development_analysis.md](development_analysis.md), and [frozen_run_plan.json](frozen_run_plan.json) for full direction, order, family-interval and decision-flip records.
