# Cohort 029 results from saved responses

These figures are recalculated from the 4,096 original response envelopes in
`runs/confirmatory/events.jsonl`. The prespecified primary unit is a target
pair: both target variants must be correct. All 4,096 responses had normal
termination and passed the strict one-key JSON parser. There were no missing
or ambiguous dispatches.

| Transfer-form primary endpoint | Causal | Arithmetic control |
| --- | ---: | ---: |
| Both target variants correct | 128/512 (25.00%) | 146/512 (28.515625%) |

The family-standardized causal-minus-control estimate is **−3.515625
percentage points**. Its approximate 95% t interval is **[−7.7713,
+0.7400] points** (SE 2.1324 points; Welch df 67.5285). The separately
reported conservative bounded interval is **[−27.5237, +20.4924] points**.
The approximate interval was the frozen coverage designation. It spans zero;
neither benefit nor equivalence is established.

## Prespecified paired diagnostics

Each target or source-role row below has 256 paired comparisons. `Both correct`
requires both responses to match their own oracle. `Same action` measures
behavioral invariance and is not by itself correctness. A reversal cell
requires the correct action to change; an invariant cell requires it to stay
the same. Physical-order rows have 512 comparisons each.

| Transfer form, pair | Causal both correct | Causal same action | Arithmetic both correct | Arithmetic same action |
| --- | ---: | ---: | ---: | ---: |
| Target invariant | 125/256 | 249/256 | 119/256 | 211/256 |
| Target reversal | 3/256 | 248/256 | 27/256 | 210/256 |
| Source-role invariant | 123/256 | 248/256 | 123/256 | 214/256 |
| Source-role reversal | 10/256 | 237/256 | 34/256 | 191/256 |
| Physical order | 241/512 | 483/512 | 187/512 | 339/512 |

Thus the causal transfer form changed action on 8/256 target-reversal pairs
and got both actions correct on 3/256. The arithmetic transfer form changed
action on 46/256 target-reversal pairs and on 45/256 target-invariant pairs.
The latter is an error of invariance, not evidence of correct sensitivity.

## Direction-specific and response diagnostics

| Transfer form | Gold action 0 correct | Gold action 1 correct | Activated |
| --- | ---: | ---: | ---: |
| Causal | 121/512 | 416/512 | 995/1,024 |
| Arithmetic | 124/512 | 397/512 | 785/1,024 |

The causal activation frequency is 995/1,024. These counts highlight a strong
action-direction bias. Full form, task, source-role, target and gold-action
cells are in `runs/confirmatory/analysis/secondary.json`; each strict row and
pair is in the adjacent JSONL outputs. The archived-form target-pair contrast
was zero; the transfer-minus-archive contrast was −3.515625 points.

## Fixture and shortcuts

The frozen fixture has 128 independent sampled numerical families and 4,096
scheduled tasks. `freeze/fixture/fixture_audit.json` records zero duplicate
prompts and zero public/private oracle mismatches. The frozen
`policy_audit.json` preserves **12 literal rival-policy failures** and shows
zero failures under the documented `constant-rivals-v1` clarification.
Forced source-role and target flips each fail 1,024 paired cells. These are
fixture discrimination checks, not outcomes observed from the model.

The dataset supports a deployment-specific conclusion about intervention
decision behavior and evaluation reliability. It does not establish a
selective quantization effect or identify an internal causal mechanism.
