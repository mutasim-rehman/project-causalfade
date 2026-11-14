# Cohort 020 component diagnostic

Development-only; no precision comparison.

## Task results

- number: 28/32 correct; 32 valid.
- randomized_only: 29/32 correct; 32 valid. Activation among valid: 0.406.
- aligned_randomized_first: 31/32 correct; 32 valid. Activation among valid: 0.531.
- aligned_historical_first: 19/32 correct; 32 valid. Activation among valid: 0.094.
- conflict_randomized_first: 19/32 correct; 32 valid. Activation among valid: 0.656.
- conflict_historical_first: 16/32 correct; 32 valid. Activation among valid: 0.000.
- source_identification: 32/32 correct; 32 valid.

## Family-paired accuracy contrasts

- randomized_only_minus_number: +0.031; family percentile 95% interval [-0.15625, 0.25]; flips {'0_to_1': 0, '1_to_0': 7, '0_to_0': 12, '1_to_1': 13}.
- aligned_randomized_first_minus_randomized_only: +0.062; family percentile 95% interval [0.0, 0.15625]; flips {'0_to_1': 4, '1_to_0': 0, '0_to_0': 15, '1_to_1': 13}.
- aligned_historical_first_minus_randomized_only: -0.312; family percentile 95% interval [-0.4375, -0.125]; flips {'0_to_1': 0, '1_to_0': 10, '0_to_0': 19, '1_to_1': 3}.
- conflict_randomized_first_minus_randomized_only: -0.312; family percentile 95% interval [-0.5, -0.125]; flips {'0_to_1': 10, '1_to_0': 2, '0_to_0': 9, '1_to_1': 11}.
- conflict_historical_first_minus_randomized_only: -0.406; family percentile 95% interval [-0.46875, -0.3125]; flips {'0_to_1': 0, '1_to_0': 13, '0_to_0': 19, '1_to_1': 0}.
- aligned_historical_first_minus_aligned_randomized_first: -0.375; family percentile 95% interval [-0.46875, -0.25]; flips {'0_to_1': 0, '1_to_0': 14, '0_to_0': 15, '1_to_1': 3}.
- conflict_historical_first_minus_conflict_randomized_first: -0.094; family percentile 95% interval [-0.25, 0.0625]; flips {'0_to_1': 0, '1_to_0': 21, '0_to_0': 11, '1_to_1': 0}.

See JSON for direction, strength and randomized-study name/order breakdowns.
Eight families give coarse descriptive uncertainty; task contrasts do not identify internal stages.
