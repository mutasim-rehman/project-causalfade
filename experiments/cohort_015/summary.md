# Cohort 015: causal-context reference screen

## Design and execution

This exploratory cohort used 16 fresh matched-strength SCM families, one causal-context prompt frame, paired randomized-first and historical-first evidence order, and a strict one-key JSON response contract. The F16 arm had to pass the scaled reference gate before the predeclared Q4_K_M arm could run. Both arms completed all 128 responses, stopped normally, emitted valid strict JSON on every prompt, and used the identical frozen schedule. The model and schedule hashes match the plan.

## F16 reference gate

| Outcome | Result | Threshold | Status |
| --- | ---: | ---: | --- |
| Strict valid actions | 128/128 | ≥112 | Pass |
| Correct overall | 89/128 (69.5%) | ≥88 | Pass |
| Conflict, randomized first | 19/32 (59.4%) | ≥18 | Pass |
| Conflict, historical first | 22/32 (68.8%) | ≥18 | Pass |

F16 passed all frozen criteria, which triggered the Q4_K_M arm exactly as specified.

## Paired format results

| Format | Overall | Aligned | Conflict | Strict-valid |
| --- | ---: | ---: | ---: | ---: |
| 7B F16 | 89/128 (69.5%) | 48/64 (75.0%) | 41/64 (64.1%) | 128/128 |
| 7B Q4_K_M | 98/128 (76.6%) | 55/64 (85.9%) | 43/64 (67.2%) | 128/128 |

The family-paired Q4_K_M minus F16 accuracy change was +7.0 percentage points overall (16-family percentile interval +0.8 to +12.5), +10.9 points on aligned items (+4.7 to +17.2), and +3.1 points on conflict items (−9.4 to +15.6). The difference in aligned-minus-conflict penalties was +7.8 points (−7.8 to +23.4). These are exploratory intervals from 16 development families; they do not establish a general quantization benefit or selective causal degradation.

## Evidence-order diagnostic

Correct counts changed markedly with the order of the two studies:

| Format and condition | Randomized first | Historical first | Historical-first minus randomized-first |
| --- | ---: | ---: | ---: |
| F16 aligned | 32/32 | 16/32 | −50.0 pp (interval −50.0 to −50.0) |
| F16 conflict | 19/32 | 22/32 | +9.4 pp (0.0 to +18.8) |
| Q4_K_M aligned | 32/32 | 23/32 | −28.1 pp (−40.6 to −15.6) |
| Q4_K_M conflict | 11/32 | 32/32 | +65.6 pp (+56.3 to +78.1) |

The paired format difference in the conflict order effect was +56.3 points (family percentile interval +40.6 to +71.9). Order was counterbalanced within family, and each pair contains the same evidence rates with only line order reversed. The strong and partly unexpected order shifts—including changes on aligned items where both sources support the same action—need independent replication and an audit of task-order interpretation. Treat them as exploratory diagnostics, not a confirmatory interaction.

## Interpretation and next step

The strict response contract was workable, and the F16 reference gate passed. On this sample the quantized arm scored higher overall, while its conflict performance changed dramatically with source order. The 16-family, scaffolded, single-checkpoint result is too small and task-specific to support a broad format or reasoning claim. Preserve it as a development finding and replicate the evidence-order pattern on fresh families with the same paired task construction and both formats. Cohorts 011–015 remain development data.

Machine-readable results: [F16 gate](gate_analysis.json), [Q4 gate-style breakdown](q4_gate_analysis.json), [paired format analysis](format_analysis.json), and [order analysis](order_analysis.json).
