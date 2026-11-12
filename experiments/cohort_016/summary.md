# Cohort 016: fresh-family evidence-order replication

## Design and completion

This prospective replication used 96 newly generated matched-strength SCM families, a strict one-key JSON response contract and the causal-context prompt. Both 7B F16 and Q4_K_M received the same 768-task schedule. Every response was strict-valid, both runs completed normally, and model and schedule hashes matched the frozen plan. Cohort 015 was development evidence; its families were not reused here.

## Primary confirmatory result

The primary outcome was Q4_K_M conflict accuracy with historical evidence first minus accuracy with randomized evidence first, averaged within each family.

- Historical first: **175/192 (91.1%)**
- Randomized first: **55/192 (28.6%)**
- Mean family-level difference: **+62.5 percentage points**
- 95% family-level t interval: **+56.6 to +68.4 points**
- Two-sided one-sample t test: **t(95)=21.10, p=1.24×10⁻³⁷**
- 95% family-bootstrap interval: **+56.8 to +68.2 points**

The evidence-order effect from cohort 015 replicated on fresh families and was estimated precisely under the frozen analysis. This supports a strong order sensitivity for Q4_K_M on the tested conflict prompts; it does not establish broader model behavior beyond this checkpoint, prompt scaffold and synthetic task.

## Secondary format and aligned-item patterns

The Q4_K_M conflict order effect was 45.3 percentage points larger than the F16 effect (family-bootstrap interval +38.0 to +52.6). F16 conflict accuracy was 76/192 (39.6%) randomized-first and 109/192 (56.8%) historical-first, a +17.2-point change. This format interaction is secondary and descriptive; the primary test was the Q4_K_M order effect.

Both formats also showed a large accuracy and action-rate change on aligned prompts, where randomized and historical studies support the same action:

| Format | Randomized first | Historical first | Historical-first action rate |
| --- | ---: | ---: | ---: |
| F16 | 192/192 correct (100%) | 96/192 (50%) | 192/192 activate |
| Q4_K_M | 192/192 correct (100%) | 105/192 (54.7%) | 153/192 activate |

The aligned-item result means the prompt-order pattern cannot be summarized only as resistance to conflicting evidence. The shift in action rates points to a broader presentation-sensitive decision pattern; its mechanism remains unresolved. Treat secondary outcomes as descriptive.

## Interpretation and next step

The replication confirms a large Q4_K_M conflict-order effect in this task. It also reproduces a strong aligned-item shift that deserves a separate prompt-order audit. Do not label the result selective causal degradation or general quantization damage: order sensitivity is present in both formats, although the conflict-order shift is larger under Q4_K_M. A follow-up should separate line position, evidence source identity and action direction while preserving matched family-level pairs.

Machine-readable primary and secondary results are in [primary_analysis.json](primary_analysis.json). The frozen protocol and power plan are in [frozen_run_plan.json](frozen_run_plan.json) and [power_analysis.json](power_analysis.json).
