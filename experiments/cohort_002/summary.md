# Formula-given control results

F16 and Q4_K_M completed all 64 prompts on the identical 16-family schedule. They used the same model digests, table values, generation settings and task IDs as cohort 001. The prompt replaced the causal scenario with an explicit arithmetic formula and preserved the response fields. All responses stopped normally and contained a single fenced JSON object. Strict accuracy remained 0/64 per arm.

| Arm | Explicit action correct | Activate | Numeric sign correct | Action disagrees with estimate sign |
| --- | ---: | ---: | ---: | ---: |
| [F16](run_001_f16/) | 32/64 | 0/64 | 61/64 | 29/64 |
| [Q4_K_M](run_002_q4_k_m/) | 35/64 | 3/64 | 45/64 | 48/64 |

The analytic rule scores 64/64, and always declining scores 32/64. F16 went from recommending activation on 63/64 original prompts to 0/64 formula prompts. Q4_K_M went from 62/64 to 3/64. Neither format gained materially in explicit action accuracy. The formula helped numeric estimates: correct signs rose from 34 to 61 for F16 and from 35 to 45 for Q4_K_M. Mean absolute effect error fell from 0.246 to 0.062 for F16 and from 0.222 to 0.081 for Q4_K_M. The sign calculation is a post hoc diagnostic on the saved estimates and leaves the action score intact.

In the formula control, Q4_K_M's estimate signs were 7 fewer correct on aligned items and 9 fewer on conflicting items than F16. That difference suggests a broader execution issue under this scaffold. The model's explicit action and numeric estimate frequently disagree, so a deterministic sign-to-action policy would define a different interface. The wording change also removed the causal graph and changed prompt length, which limits attribution of the improvement to the formula alone.

The explicit action conflict penalty was 0 points for F16 and −9.375 points for Q4_K_M under fence handling. The latter reflects three correct activations in one conflict cell amid a strong decline bias. These are exploratory repeated-family results. We did not fit the processing tree given near-constant decisions and differences in output behavior.

[Between-format comparison](f16_vs_q4_k_m_formula.json) · [F16 original vs. formula](f16_matched_prompt_contrast.json) · [Q4_K_M original vs. formula](q4_k_m_matched_prompt_contrast.json)

The [post hoc sign-derived policy](estimate_sign_policy_sensitivity.json) turns each saved numeric estimate into an action using its sign. This reduces accuracy by 25 points under Q4_K_M relative to F16 (paired 16-family percentile interval −37.5 to −10.94). The change in conflict penalty is +6.25 points (−9.38 to +21.88). The larger overall change and wide conflict interval make this a candidate arithmetic execution effect for a later protocol, with no basis here for a selective conflict claim. These values come from rescoring existing responses.
