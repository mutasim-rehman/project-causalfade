# Cohort 026 — completed bounded development screen

**Status:** stopped after the predeclared two-lineage, two-form development screen and its single permitted wording revision. No form met all qualification gates. No validation or confirmation family was queried, no precision contrast was run, and no causal-specific quantization claim is made.

## Design and provenance

The exact-rational generator produced 48 disjoint SCM families: eight development, eight validation and 32 reserved confirmation. Within each family the confounder and mediator graphs share the full observational P(W,X,Y), while their intervention-effect signs differ. Both answer polarities are balanced. A graph with an additional W→Z child and no path from Z to X or Y supplies an unchanged-answer control. Two task forms, graph-reading and arithmetic controls, option-order reversals and strict one-token scoring are included. Display rounding was independently checked to preserve intervention signs. The [fixture manifest](input/manifest.json), [frozen development plan](frozen_development_plan.json), runner and analysis code determine the schedule and gates.

The first Qwen F16 pilot was invalidated because its arithmetic oracle incorrectly assumed the same answer after complementing Y, and its control prompt contained an extra intervention question. Its complete output is preserved separately. The repaired v2 screen was run for fixed Qwen2.5-7B-Instruct F16 and Llama-3.1-8B-Instruct F16, 112 scheduled prompts each. A single final wording revision (v3) explicitly supplied the graph-dependent weighting rule and asked for a bare answer token; it was frozen before rerunning both models on the same development families. All fixed thresholds, family IDs, scoring and answer policies remained unchanged. This was a development revision, so comparisons across v2 and v3 are descriptive.

## Frozen qualification results

| Model and form | Strict valid | Graph reading | Arithmetic | Switch correct | Paired switch fidelity | No-change correct | Qualified |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen v2 direct | 56/56 | 16/16 | 8/8 | 8/16 | 0/8 | 8/16 | No |
| Qwen v2 decision | 56/56 | 13/16 | 4/8 | 8/16 | 0/8 | 8/16 | No |
| Llama v2 direct | 24/56 | 16/16 | 4/8 | 0/16 | 0/8 | 0/16 | No |
| Llama v2 decision | 24/56 | 16/16 | 8/8 | 0/16 | 0/8 | 0/16 | No |
| Qwen v3 direct | 56/56 | 16/16 | 6/8 | 8/16 | 0/8 | 8/16 | No |
| Qwen v3 decision | 56/56 | 16/16 | 4/8 | 8/16 | 0/8 | 8/16 | No |
| Llama v3 direct | 56/56 | 16/16 | 4/8 | 0/16 | 0/8 | 7/16 | No |
| Llama v3 decision | 56/56 | 16/16 | 8/8 | 14/16 | 6/8 | 8/16 | No |

Each form has eight switch pairs and 56 scheduled prompts. The frozen gate required at least 95% strict validity, 80% graph and arithmetic controls, 70% switch accuracy in **each** answer polarity, 80% no-change accuracy and 60% paired switch fidelity. Invalid outputs count as wrong. Full per-form gate decisions are in each arm's `development_analysis.json`.

The final Qwen screen returned `X=1` on all switch and no-change action prompts in both forms. Its 8/16 switch accuracy is an action bias, not graph use. Llama v2 returned `X=1.` on all 64 action prompts, violating the exact-output contract. The final instruction repaired strict validity to 112/112. In Llama v3's decision form, the model got all eight confounder switch items and six of eight mediator switch items correct, but on the no-change pair it got all eight base confounder items and **zero of eight** W→Z variants correct. Thus its 6/8 paired switch fidelity alone does not establish principled graph use. Its direct form had 0/16 switch accuracy despite the same worlds, showing strong form dependence.

## Decision

The bounded development screen failed its predeclared qualification rule. Stop this graph-switch assay at development. Do not use the reserved validation or confirmation families, run a paired quantized arm, claim a selective precision effect, or promote the favorable Llama decision-form switch rate alone. The observed answer bias, punctuation-sensitive validity, and unchanged-answer graph sensitivity are useful measurement findings on these eight development families; they do not show transfer. A later study would require a separately versioned assay with a stronger no-change control and new development families, followed by fresh power and confirmation work only if its reference qualifies.
