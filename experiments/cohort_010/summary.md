# Fresh-family interleaved order replication

Both formats completed 96 responses over 48 paired source-selection items from 12 independently generated families. The worlds used simulator seed 20261113. Each item appeared in both evidence orders, with balanced randomized first-order assignment within family and a shared shuffled execution schedule. Both runs used the same CPU server, inference settings and scoring analysis.

| Format | Condition | Randomized evidence first | Historical evidence first | Change |
| --- | --- | ---: | ---: | ---: |
| F16 | Aligned | 8/24 | 12/24 | +16.667 points (95% family interval +16.667 to +41.667) |
| F16 | Conflict | 6/24 | 3/24 | −25 points (−37.5 to −12.5) |
| Q4_K_M | Aligned | 6/24 | 8/24 | +12.5 points (−4.167 to +29.167) |
| Q4_K_M | Conflict | 6/24 | 6/24 | 0 points (0 to 0) |

The primary F16 conflict order effect again favored randomized evidence first. Its size was 25 points, close to cohort 009's 21.875 points on the reused families. The Q4_K_M conflict effect remained at zero, with the model getting one quarter of conflict decisions right in both orders. The secondary format interaction was +25 points in conflict accuracy change for Q4_K_M relative to F16 (family interval +12.5 to +37.5).

The direction replicated on a new draw of SCM families with both orders interleaved in one run per format. This increases confidence that the order result applies beyond the original worlds. Absolute task performance remains weak, especially on conflicts. The study still uses one 3B checkpoint family, one domain and task framing, and an exploratory cluster bootstrap selected after earlier findings. It does not support a general claim about model quantization or internal causal reasoning.

[Paired family analysis](source_order_analysis.json) · [Input fixture and generation manifests](input/) · [F16 run](run_001_f16/) · [Q4_K_M run](run_001_q4_k_m/)
