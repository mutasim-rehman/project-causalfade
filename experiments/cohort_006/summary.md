# Q8_0 formula-control follow-up results

The [3B Q8_0 arm](run_001_q8_0/) completed all 64 requests on the exact schedules used by the archived F16 and Q4_K_M formula controls. The model digest matched the preparation record. All outputs stopped normally and used a single JSON fence.

| Format | Correct estimate sign | Explicit action correct | Estimate sign disagrees with action |
| --- | ---: | ---: | ---: |
| F16 | 61/64 | 32/64 | 29/64 |
| Q8_0 | 61/64 | 32/64 | 29/64 |
| Q4_K_M | 45/64 | 35/64 | 48/64 |

Q8_0 and F16 had equal aggregate estimate-sign accuracy, with one task improving and one worsening. The paired overall difference was 0 points (16-family percentile interval −4.69 to +4.69). Relative to Q4_K_M, Q8_0 was 25 points higher (+12.50 to +35.94). Q8_0 scored 29/32 aligned and 32/32 conflicting on signs, equal to F16's aggregate cell rates. All 64 Q8_0 explicit actions were decline. The analytic formula scores 64/64, while always declining scores 32/64.

The result is consistent with stronger arithmetic execution at Q8_0 than Q4_K_M on this scaffold. It is an exploratory result on the reused development families, with no equivalence margin or claim about quantizer algorithms in general. The match concerns sign accuracy. Actual numeric estimates and exact responses can differ. Strict JSON scoring rejected every fenced response.

[F16 to Q8_0 sign comparison](run_001_f16_vs_q8_0_estimate_sign.json) · [Q4_K_M to Q8_0 sign comparison](run_002_q4_k_m_vs_q8_0_estimate_sign.json) · [Explicit action comparison](f16_vs_q8_0_explicit_action.json)
