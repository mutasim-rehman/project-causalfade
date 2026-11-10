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
| cohort_004 / run_001_f16 | Screen 7B F16 direct-response reference competence | [Config](experiments/cohort_004/run_001_f16/config.json) | Running | [Run](experiments/cohort_004/run_001_f16/) |
