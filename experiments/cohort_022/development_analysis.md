# Cohort 022 independent checkpoint-family development replication

Both models use the identical fresh fixture; this is not confirmatory.

## qwen_f16

- source_selection: 128/128 correct; 128 valid.
- ordinary: 56/128 correct; 128 valid. Activation 0.734.
- guided: 60/128 correct; 128 valid. Activation 0.922.
- neutral_guidance: 55/128 correct; 128 valid. Activation 0.758.
- randomized_only: 31/32 correct; 32 valid. Activation 0.469.
- direct_identification: 32/32 correct; 32 valid.

## mistral_q4

- source_selection: 64/128 correct; 128 valid.
- ordinary: 64/128 correct; 128 valid. Activation 1.000.
- guided: 74/128 correct; 128 valid. Activation 0.922.
- neutral_guidance: 64/128 correct; 128 valid. Activation 1.000.
- randomized_only: 16/32 correct; 32 valid. Activation 1.000.
- direct_identification: 32/32 correct; 32 valid.

## Central randomized-only minus ordinary accuracy

- qwen_f16: +0.531; eight-family percentile interval [0.4609375, 0.578125].
- mistral_q4: +0.000; eight-family percentile interval [0.0, 0.0].
- mistral_minus_qwen: -0.531; eight-family percentile interval [-0.578125, -0.4609375].

See JSON for direction, order, guidance, joint-request and action-flip strata.
The independent reference is quantized; family and precision are bundled. No mechanistic or confirmatory claim follows.
