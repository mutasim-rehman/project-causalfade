# 7B prompt-clarity development crossover

The 7B F16 model completed all 128 prompts on the exact frozen schedule across eight fresh matched-strength families. The minimal and causal-context frames were paired on every base item and source order. Every minimal-frame response was a single fenced JSON object that stopped normally. Every causal-context response reached the 160-token limit; it began with a complete fenced action object and continued with prose.

## Prespecified scoring and reference gate

| Prompt frame | Valid actions | Correct overall | Aligned | Conflict, randomized first | Conflict, historical first | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Minimal | 64/64 after one fence | 48/64 | 32/32 | 8/16 | 8/16 | Fail: conflict in both orders |
| Causal context | 0/64 under the frozen parser | 0/64 primary score | 0/32 | 0/16 | 0/16 | Fail: validity and accuracy |

The minimal frame met the validity and overall-accuracy thresholds but repeated the always-activate policy in conflict cases, scoring exactly 50% in each order. It failed the 9/16 per-order conflict gate. The causal-context frame failed operational validity because trailing explanations followed the JSON object and generations hit the length cap. The quantized arm was not part of this cohort.

## Post hoc leading-object diagnostic

For diagnosis only, the analysis also extracted a complete JSON action at the beginning of a response and ignored any following prose. This does not change primary scoring or gate results: the contextual responses remain invalid under the frozen response contract. In this diagnostic, minimal wording scored 48/64 (75%). Causal-context wording scored 45/64 (70.3%): 16/16 aligned and 8/16 conflict with randomized evidence first; 5/16 aligned and 16/16 conflict with historical evidence first. The scaffold therefore did not improve overall performance, and its conflict behavior depended strongly on evidence order. This post hoc pattern is exploratory and needs independent replication.

The run data show a format-cost tradeoff: minimal framing yields compliant fenced objects but chance conflict accuracy; causal context changes action choices but triggers explanatory text and truncation. Both frames fail the reference gate. Do not use either as a confirmatory reference without further task and output-contract development.

The [frozen run plan](frozen_run_plan.json), [design audit](design_validation.json), [machine-readable analysis](analysis.json), [raw run](run_001_7b_f16/) and preserved pre-diagnostic analysis (`analysis_v1_before_prefix_diagnostic.json`) record the inputs and analysis versions. This is an exploratory development result on one 7B checkpoint and eight families.
