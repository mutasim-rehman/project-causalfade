# 3B direct-response pilot results

All three arms returned 64/64 responses on identical schedules of 16 balanced exact-evidence families. Local model hashes match the F16 conversion and quantization manifests. The first comparison was F16 versus Q2_K. Q4_K_M was added as an exploratory intermediate configuration after initial Q2_K failures. All used the [same CPU runtime](../environment_20261110.json) and output budget.

| Arm | Strict correct | Fence-only correct | Fence-only aligned | Fence-only conflict | Valid after fence handling | Length caps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [F16](run_001_f16/) | 0/64 | 33/64 | 16/32 | 17/32 | 64/64 | 0/64 |
| [Q2_K](run_001_q2_k/) | 0/64 | 0/64 | 0/32 | 0/32 | 0/64 | 64/64 |
| [Q4_K_M](run_001_q4_k_m/) | 0/64 | 34/64 | 16/32 | 18/32 | 64/64 | 0/64 |

The analytic backdoor baseline solves all 64 tasks. A policy that follows only the observational association scores 32/32 aligned and 0/32 conflicting. Always activating scores 16/32 in each condition. After unwrapping a single JSON fence, F16 chose activation on 63/64 and Q4_K_M on 62/64. Neither arm selected the correct adjustment set on any task. Both estimated the effect much less accurately on negative-effect tasks. The cell counts therefore indicate a strong activation preference and weak causal-task competence.

Q2_K produced repetitive or malformed output through the full token budget in every request. Both other configurations stopped normally and wrapped every response in a single Markdown fence. Median wall times per response were 9.40 s for F16, 7.24 s for Q2_K and 4.37 s for Q4_K_M, with mean output lengths of 42.4, 160 and 42.5 tokens respectively. These are descriptive runtime measurements under different realized generation lengths.

The strict conflict penalty is zero for all arms because all scores are at the floor. Under the post hoc fence sensitivity, Q2_K minus F16 changes the penalty by +3.125 percentage points (paired family bootstrap 0 to +9.375). That value comes from Q2_K failing in both conditions and F16 getting one more conflict item correct. Q4_K_M minus F16 changes the penalty by −3.125 points (−9.375 to 0). These descriptive bootstrap intervals do not constitute a confirmatory test, and the floor and near-constant activation rates limit the contrast. The evidence supports a configuration-specific output failure for Q2_K and reference-competence problems in the direct task. It leaves selective causal degradation unresolved.

See [Q2_K comparison](f16_vs_q2_k.json) and [Q4_K_M comparison](f16_vs_q4_k_m.json) for machine-readable cell counts, accuracy, effect errors and diagnostics. The 16 development families are the independent blocks. Future work includes a formula-given control, a CPU repacking diagnostic and a larger-reference screen.
