# Experiment index

Cohort 001 tests the provisional 3B quantization contrast on exact evidence from development families. See [cohort protocol](experiments/cohort_001/README.md).

| Run | Hypothesis | Config | Status | Artifacts |
| --- | --- | --- | --- | --- |
| cohort_001 / run_001_f16 | Establish reference accuracy and conflict penalty | [Config](experiments/cohort_001/run_001_f16/config.json) | Complete, 33/64 after fence handling | [Run](experiments/cohort_001/run_001_f16/) |
| cohort_001 / run_001_q2_k | Estimate change in conflict penalty | [Config](experiments/cohort_001/run_001_q2_k/config.json) | Complete, 0/64 valid; all token capped | [Run](experiments/cohort_001/run_001_q2_k/) |
| cohort_001 / run_001_q4_k_m | Exploratory intermediate-format comparison | [Config](experiments/cohort_001/run_001_q4_k_m/config.json) | Complete, 34/64 after fence handling | [Run](experiments/cohort_001/run_001_q4_k_m/) |
