# Cohort 014: strict-output prompt-clarity screen

## Design and execution

This exploratory screen compared the minimal and causal-context frames on eight fresh matched-strength families. Both frames used paired randomized-first and historical-first prompts, the same strict one-key JSON instruction, and the 7B F16 checkpoint. The frozen schedule contained 128 prompts. All 128 responses completed with a normal stop, produced a valid strict JSON action, and stayed within the 48-token limit. The recorded model hash and run schedule hash match the frozen plan.

## Primary results

| Frame | Strict valid | Overall correct | Aligned correct | Conflict correct, randomized first | Conflict correct, historical first | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Minimal | 64/64 | 48/64 (75.0%) | 32/32 | 8/16 | 8/16 | Fail: conflict thresholds |
| Causal context | 64/64 | 42/64 (65.6%) | 24/32 | 9/16 | 9/16 | Fail: overall threshold |

The causal-context frame met both conflict-by-order minima exactly, but missed the overall threshold of 44/64 by two responses. The minimal frame exceeded the overall threshold but reached only chance-level conflict accuracy in each order. Neither frame established reference competence under the frozen gate.

## Paired development contrast

The causal-context frame was 9.375 percentage points lower overall than minimal (8-family percentile interval −15.625 to −3.125), 25 points lower on aligned items (interval −25 to −25), and 6.25 points higher on conflict items (interval −6.25 to +18.75). These small-family intervals are descriptive and exploratory. Context was associated with fewer aligned decisions, while the conflict change remained uncertain.

All responses obeyed the stricter response contract, so the output-format issue seen in cohort 013 is resolved for these prompts. The cohort does not show that either frame is a competent reference, does not test quantization, and is not confirmatory evidence. The causal-context frame also supplies mechanism information and therefore should be treated as a scaffolded task condition.

## Gate decision and next step

The cohort-level reference gate failed for both frames. A fresh 16-family, causal-context-only development screen is planned to check whether the conflict behavior seen here holds while overall competence reaches the threshold. The subsequent Q4_K_M arm is conditional on the F16 arm passing every predeclared gate criterion; otherwise it will not run. All cohorts through 015 remain development data.

Machine-readable outcomes are in [analysis.json](analysis.json); the frozen plan, schedule, validation and full run artifacts are retained alongside this summary.
