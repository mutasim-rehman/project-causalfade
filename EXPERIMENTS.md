# Experiment index

Cohort 001 tests the provisional 3B quantization contrast on exact evidence from development families. See [cohort protocol](experiments/cohort_001/README.md).

| Run | Hypothesis | Config | Status | Artifacts |
| --- | --- | --- | --- | --- |
| cohort_001 / run_001_f16 | Establish reference accuracy and conflict penalty | [Config](experiments/cohort_001/run_001_f16/config.json) | Complete, 33/64 after fence handling | [Run](experiments/cohort_001/run_001_f16/) |
| cohort_001 / run_001_q2_k | Estimate change in conflict penalty | [Config](experiments/cohort_001/run_001_q2_k/config.json) | Complete, 0/64 valid; all token capped | [Run](experiments/cohort_001/run_001_q2_k/) |
| cohort_001 / run_001_q4_k_m | Exploratory intermediate-format comparison | [Config](experiments/cohort_001/run_001_q4_k_m/config.json) | Complete, 34/64 after fence handling | [Run](experiments/cohort_001/run_001_q4_k_m/) |
| cohort_003 / run_001_default | Reproduce Q2_K failure with default CPU repacking | [Config](experiments/cohort_003/run_001_default/config.json) | Complete, 0/16 valid, 16/16 capped | [Run](experiments/cohort_003/run_001_default/) |
| cohort_003 / run_002_no_repack | Test whether disabling repacking restores usable output | [Config](experiments/cohort_003/run_002_no_repack/config.json) | Complete, 0/16 valid, 16/16 capped | [Run](experiments/cohort_003/run_002_no_repack/) |
| cohort_002 / run_001_f16 | Test F16 on the same tables with formula given | [Config](experiments/cohort_002/run_001_f16/config.json) | Complete, 32/64 actions, 61/64 estimate signs after fence handling | [Run](experiments/cohort_002/run_001_f16/) |
| cohort_002 / run_002_q4_k_m | Test Q4_K_M on the same tables with formula given | [Config](experiments/cohort_002/run_002_q4_k_m/config.json) | Complete, 35/64 actions, 45/64 estimate signs after fence handling | [Run](experiments/cohort_002/run_002_q4_k_m/) |
| cohort_004 / run_001_f16 | Screen 7B F16 direct-response reference competence | [Config](experiments/cohort_004/run_001_f16/config.json) | Complete, 17/32 after fence handling; reference gate failed | [Run](experiments/cohort_004/run_001_f16/) |
| cohort_005 / run_001_f16 | Screen source selection when rates are supplied | [Config](experiments/cohort_005/run_001_f16/config.json) | Complete, 39/64 after fence handling | [Run](experiments/cohort_005/run_001_f16/) |
| cohort_005 / run_001_q4_k_m | Compare source-selection conflict penalty | [Config](experiments/cohort_005/run_001_q4_k_m/config.json) | Complete, 35/64 after fence handling | [Run](experiments/cohort_005/run_001_q4_k_m/) |
| cohort_006 / run_001_q8_0 | Compare estimate signs at moderate compression | [Config](experiments/cohort_006/run_001_q8_0/config.json) | Complete, 32/64 actions, 61/64 estimate signs after fence handling | [Run](experiments/cohort_006/run_001_q8_0/) |
| cohort_007 / run_001_f16 | Establish fresh-family estimate-sign reference | [Config](experiments/cohort_007/run_001_f16/config.json) | Complete, 24/48 actions, 46/48 estimate signs after fence handling | [Run](experiments/cohort_007/run_001_f16/) |
| cohort_007 / run_001_q4_k_m | Replicate the estimate-sign deficit on fresh families | [Config](experiments/cohort_007/run_001_q4_k_m/config.json) | Complete, 28/48 actions, 31/48 estimate signs after fence handling | [Run](experiments/cohort_007/run_001_q4_k_m/) |
| cohort_008 / run_001_f16 | Compare F16 evidence order within each item | [Config](experiments/cohort_008/run_001_f16/config.json) | Original attempt interrupted at 25/64; rerun complete 64/64 | [Run](experiments/cohort_008/run_001_f16/) |
| cohort_008 / run_002_f16 | Complete within-item reversal arm | [Config](experiments/cohort_008/run_002_f16/config.json) | Complete, 64/64 | [Run](experiments/cohort_008/run_002_f16/) |
| cohort_008 / run_002_q4_k_m | Complete within-item reversal arm | [Config](experiments/cohort_008/run_002_q4_k_m/config.json) | Complete, 64/64 | [Run](experiments/cohort_008/run_002_q4_k_m/) |
| cohort_009 / run_001_f16 | Interleaved randomized-first/historical-first crossover | [Config](experiments/cohort_009/run_001_f16/config.json) | Complete, 128/128 | [Run](experiments/cohort_009/run_001_f16/) |
| cohort_009 / run_001_q4_k_m | Interleaved randomized-first/historical-first crossover | [Config](experiments/cohort_009/run_001_q4_k_m/config.json) | Complete, 128/128 | [Run](experiments/cohort_009/run_001_q4_k_m/) |
| cohort_010 / run_001_f16 | Fresh-family interleaved source-order replication | [Config](experiments/cohort_010/run_001_f16/config.json) | Complete, 96/96 | [Run](experiments/cohort_010/run_001_f16/) |
| cohort_010 / run_001_q4_k_m | Fresh-family interleaved source-order replication | [Config](experiments/cohort_010/run_001_q4_k_m/config.json) | Complete, 96/96 | [Run](experiments/cohort_010/run_001_q4_k_m/) |
| cohort_011 / run_001_f16 | Matched observational-strength development pilot | [Config](experiments/cohort_011/run_001_f16/config.json) | Complete, 128/128 | [Run](experiments/cohort_011/run_001_f16/) |
| cohort_011 / run_001_q4_k_m | Matched observational-strength development pilot | [Config](experiments/cohort_011/run_001_q4_k_m/config.json) | Complete, 128/128 | [Run](experiments/cohort_011/run_001_q4_k_m/) |
| cohort_012 / run_001_7b_f16 | Matched-strength reference-competence feasibility screen | [Config](experiments/cohort_012/run_001_7b_f16/config.json) | Complete, 64/64; gate failed at 8/16 and 7/16 conflict accuracy by order | [Run](experiments/cohort_012/run_001_7b_f16/) |
| cohort_013 / run_001_7b_f16 | Minimal vs causal-context prompt-clarity crossover | [Config](experiments/cohort_013/run_001_7b_f16/config.json) | Complete, 128/128; minimal gate failed on conflict; causal-context invalid 64/64 | [Run](experiments/cohort_013/run_001_7b_f16/) |
| cohort_014 / run_001_7b_f16 | Strict-output minimal vs causal-context feasibility screen | [Config](experiments/cohort_014/run_001_7b_f16/config.json) | Complete, 128/128 strict-valid; both frames failed reference gate (minimal conflict; context overall by 2) | [Run](experiments/cohort_014/run_001_7b_f16/) |
| cohort_015 / run_001_7b_f16 | Fresh 16-family strict-output causal-context reference screen | [Plan](experiments/cohort_015/frozen_run_plan.json) | Frozen, not started; Q4_K_M arm conditional on all F16 gate criteria | [Cohort](experiments/cohort_015/) |

See the [cohort 011 summary](experiments/cohort_011/summary.md), [cohort 012 summary](experiments/cohort_012/summary.md), [cohort 013 summary](experiments/cohort_013/summary.md), and [cohort 014 summary](experiments/cohort_014/summary.md). Cohorts 011–015 are development work, not confirmatory evidence.
