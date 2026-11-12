# Interleaved presentation-order crossover results

Both formats completed 128 responses. Each of 64 matched source-selection items appeared once in each evidence order, and the order assignment was balanced within each of 16 families. All model prompts ran in one session per format using the same frozen task schedule. The inputs, output hashes, model hashes, logs and analysis are archived in this cohort.

| Format | Condition | Randomized evidence first | Historical evidence first | Change |
| --- | --- | ---: | ---: | ---: |
| F16 | Aligned | 11/32 | 16/32 | +15.625 points (95% family interval +18.75 to +43.75) |
| F16 | Conflict | 8/32 | 4/32 | −21.875 points (−34.375 to −9.375) |
| Q4_K_M | Aligned | 10/32 | 8/32 | −9.375 points (−18.75 to 0) |
| Q4_K_M | Conflict | 8/32 | 8/32 | 0 points (0 to 0) |

F16's conflict accuracy fell when the historical rates appeared first, repeating the direction of the earlier reversal collected two days apart. In this simultaneous crossover, prompt order was randomized within family and execution order was shuffled across all 128 prompts. That removes collection date as the explanation for the order contrast on these items.

The order effect differed by format. Q4_K_M minus F16 was +21.875 points on conflict accuracy change (family interval +9.375 to +34.375) and −40.625 points on aligned accuracy change (−56.25 to −25). Q4_K_M showed no conflict order response because it made the same number of correct choices in both orders. Its result does not imply stronger causal evidence use. The Q4 format remained near chance in each conflict order.

The primary result supports sensitivity of F16 decisions to which evidence source appears first in this task. Both formats remain weak on the task, and F16 performs unusually poorly on conflict items. The experiment uses one checkpoint family, 16 reused world families, one prompt wording, one CPU runtime, and an exploratory family percentile bootstrap. It does not establish a general quantization effect or identify a cognitive route.

[Machine-readable paired analysis](source_order_analysis.json) · [F16 run](run_001_f16/) · [Q4_K_M run](run_001_q4_k_m/)
