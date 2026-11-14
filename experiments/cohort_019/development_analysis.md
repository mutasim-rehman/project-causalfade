# Cohort 019 response-contract development analysis

Development-only; no confirmatory inference.

Reference semantic-subset gate: False.

## Reference

- semantic|causal: 73/128 correct; 128 valid.
- semantic|noncausal: 87/128 correct; 128 valid.
- semantic|encoding_check: 16/16 correct; 16 valid.
- semantic|source_check: 8/16 correct; 16 valid.
- neutral_forward|causal: 70/128 correct; 128 valid.
- neutral_forward|noncausal: 66/128 correct; 128 valid.
- neutral_forward|encoding_check: 16/16 correct; 16 valid.
- neutral_reverse|causal: 103/128 correct; 128 valid.
- neutral_reverse|noncausal: 113/128 correct; 128 valid.
- neutral_reverse|encoding_check: 16/16 correct; 16 valid.

Paired contract accuracy differences (second minus first):

- causal|neutral_forward_minus_semantic: -0.023; family percentile 95% interval [-0.046875, -0.0078125]; valid flips {'0_to_1': 87, '0_to_0': 18, '1_to_1': 23}.
- causal|neutral_reverse_minus_semantic: +0.234; family percentile 95% interval [0.171875, 0.2890625]; valid flips {'0_to_1': 39, '0_to_0': 66, '1_to_1': 20, '1_to_0': 3}.
- causal|neutral_reverse_minus_neutral_forward: +0.258; family percentile 95% interval [0.1796875, 0.3203125]; valid flips {'1_to_1': 59, '0_to_0': 18, '1_to_0': 51}.
- noncausal|neutral_forward_minus_semantic: -0.164; family percentile 95% interval [-0.2265625, -0.09375]; valid flips {'1_to_1': 41, '0_to_1': 41, '0_to_0': 46}.
- noncausal|neutral_reverse_minus_semantic: +0.203; family percentile 95% interval [0.1328125, 0.28125]; valid flips {'1_to_0': 9, '0_to_0': 70, '1_to_1': 32, '0_to_1': 17}.
- noncausal|neutral_reverse_minus_neutral_forward: +0.367; family percentile 95% interval [0.2421875, 0.46875]; valid flips {'1_to_0': 41, '0_to_0': 38, '1_to_1': 41, '0_to_1': 8}.

Order effects (historical-first minus randomized-first):

- semantic|causal|conflict=False: -0.500; family percentile 95% interval [-0.5, -0.5].
- semantic|causal|conflict=True: +0.031; family percentile 95% interval [-0.0625, 0.125].
- semantic|noncausal|conflict=False: -0.500; family percentile 95% interval [-0.59375, -0.40625].
- semantic|noncausal|conflict=True: -0.594; family percentile 95% interval [-0.6875, -0.53125].
- neutral_forward|causal|conflict=False: +0.312; family percentile 95% interval [0.1875, 0.4375].
- neutral_forward|causal|conflict=True: -0.125; family percentile 95% interval [-0.21875, -0.03125].
- neutral_forward|noncausal|conflict=False: -0.438; family percentile 95% interval [-0.5, -0.3125].
- neutral_forward|noncausal|conflict=True: -0.375; family percentile 95% interval [-0.625, -0.09375].
- neutral_reverse|causal|conflict=False: +0.062; family percentile 95% interval [0.0, 0.15625].
- neutral_reverse|causal|conflict=True: +0.281; family percentile 95% interval [0.03125, 0.53125].
- neutral_reverse|noncausal|conflict=False: -0.375; family percentile 95% interval [-0.46875, -0.28125].
- neutral_reverse|noncausal|conflict=True: -0.094; family percentile 95% interval [-0.21875, 0.0].

See JSON for contract-specific SDT denominators and precision contrasts.
SDT assumptions are unverified. Semantic-versus-neutral contrasts change multiple response properties.
Eight families are development-only; paired agreement does not identify an internal route.
