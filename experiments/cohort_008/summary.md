# Source-order reversal checkpoint

The session stopped at the user's request for PC shutdown. The F16 arm completed 25 of 64 scheduled requests and recorded the interrupted request as a separate raw record. The Q4_K_M arm had not started. The partial scores include unattempted items as failures and should not be used for an order contrast. The configuration, prompt schedule, raw responses, logs and interruption status are preserved.

To continue, rerun F16 and then Q4_K_M using the same reversed-order fixture and schedule. Use a new directory for the full F16 retry and retain this interrupted attempt. Run the paired order analysis only after both full arms complete.

## Completed continuation on 12 November 2026

After resuming, the reversed F16 and Q4_K_M arms were rerun with new run IDs and completed 64/64 tasks each. The earlier interrupted attempt remains archived separately. The analysis pairs each item with its complementary presentation order and resamples 16 family blocks.

| Format | Conflict accuracy, randomized first | Conflict accuracy, historical first | Historical first minus randomized first |
| --- | ---: | ---: | ---: |
| F16 | 16/32 | 7/32 | −28.125 points (95% paired family interval −40.625 to −15.625) |
| Q4_K_M | 16/32 | 16/32 | 0 points (0 to 0) |

F16's aligned accuracy moved in the other direction, from 26/32 randomized first to 32/32 historical first. Q4_K_M shifted from 20/32 to 16/32 aligned. In conflict cells, F16 activated on 32/32 randomized-first items and 23/32 historical-first items. Q4_K_M activated on all 64. The format difference in the order effect was +28.125 points in conflict accuracy for Q4_K_M relative to F16 (95% interval +15.625 to +40.625).

This strengthens evidence that evidence order changes F16 decisions on the tested source-selection task, especially in conflict trials. The Q4_K_M ceiling on activation hides any order response in its conflict cells. The reversed-order trials were collected two days after the first-order cohort, so repeated exposure and session timing remain entangled with line position. Each item used a fresh model context and prompt caching was disabled. Replicate with both orders randomized and interleaved within one collection session before treating presentation order as identified.

[Paired order analysis](source_order_analysis.json) · [Completed F16 rerun](run_002_f16/) · [Completed Q4_K_M rerun](run_002_q4_k_m/)
