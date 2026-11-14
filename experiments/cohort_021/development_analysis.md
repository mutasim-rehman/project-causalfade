# Cohort 021 source-selection and guidance diagnostic

Development-only; no precision comparison.

## Task results

- source_selection: 128/128 correct; 128 valid.
- ordinary: 58/128 correct; 128 valid. Activation among valid: 0.734.
- guided: 58/128 correct; 128 valid. Activation among valid: 0.906.
- neutral_guidance: 56/128 correct; 128 valid. Activation among valid: 0.750.
- randomized_only: 30/32 correct; 32 valid. Activation among valid: 0.438.
- direct_identification: 32/32 correct; 32 valid.

## Two-source conditions

- source_selection|aligned|randomized_first: 32/32 correct; 32 valid.
- source_selection|aligned|historical_first: 32/32 correct; 32 valid.
- source_selection|conflict|randomized_first: 32/32 correct; 32 valid.
- source_selection|conflict|historical_first: 32/32 correct; 32 valid.
- ordinary|aligned|randomized_first: 16/32 correct; 32 valid. Activation: 1.000.
- ordinary|aligned|historical_first: 17/32 correct; 32 valid. Activation: 0.719.
- ordinary|conflict|randomized_first: 16/32 correct; 32 valid. Activation: 1.000.
- ordinary|conflict|historical_first: 9/32 correct; 32 valid. Activation: 0.219.
- guided|aligned|randomized_first: 16/32 correct; 32 valid. Activation: 1.000.
- guided|aligned|historical_first: 14/32 correct; 32 valid. Activation: 0.938.
- guided|conflict|randomized_first: 16/32 correct; 32 valid. Activation: 1.000.
- guided|conflict|historical_first: 12/32 correct; 32 valid. Activation: 0.688.
- neutral_guidance|aligned|randomized_first: 16/32 correct; 32 valid. Activation: 1.000.
- neutral_guidance|aligned|historical_first: 16/32 correct; 32 valid. Activation: 0.688.
- neutral_guidance|conflict|randomized_first: 16/32 correct; 32 valid. Activation: 1.000.
- neutral_guidance|conflict|historical_first: 8/32 correct; 32 valid. Activation: 0.312.

## Family-paired accuracy contrasts

- aligned|randomized_first|guided_minus_ordinary: +0.000; family percentile 95% interval [0.0, 0.0]; flips {'0_to_1': 0, '1_to_0': 0, '0_to_0': 0, '1_to_1': 32}.
- aligned|randomized_first|neutral_guidance_minus_ordinary: +0.000; family percentile 95% interval [0.0, 0.0]; flips {'0_to_1': 0, '1_to_0': 0, '0_to_0': 0, '1_to_1': 32}.
- aligned|randomized_first|guided_minus_neutral_guidance: +0.000; family percentile 95% interval [0.0, 0.0]; flips {'0_to_1': 0, '1_to_0': 0, '0_to_0': 0, '1_to_1': 32}.
- aligned|historical_first|guided_minus_ordinary: -0.094; family percentile 95% interval [-0.1875, -0.03125]; flips {'0_to_1': 7, '1_to_0': 0, '0_to_0': 2, '1_to_1': 23}.
- aligned|historical_first|neutral_guidance_minus_ordinary: -0.031; family percentile 95% interval [-0.09375, 0.0]; flips {'0_to_1': 0, '1_to_0': 1, '0_to_0': 9, '1_to_1': 22}.
- aligned|historical_first|guided_minus_neutral_guidance: -0.062; family percentile 95% interval [-0.15625, 0.0]; flips {'0_to_1': 8, '1_to_0': 0, '0_to_0': 2, '1_to_1': 22}.
- conflict|randomized_first|guided_minus_ordinary: +0.000; family percentile 95% interval [0.0, 0.0]; flips {'0_to_1': 0, '1_to_0': 0, '0_to_0': 0, '1_to_1': 32}.
- conflict|randomized_first|neutral_guidance_minus_ordinary: +0.000; family percentile 95% interval [0.0, 0.0]; flips {'0_to_1': 0, '1_to_0': 0, '0_to_0': 0, '1_to_1': 32}.
- conflict|randomized_first|guided_minus_neutral_guidance: +0.000; family percentile 95% interval [0.0, 0.0]; flips {'0_to_1': 0, '1_to_0': 0, '0_to_0': 0, '1_to_1': 32}.
- conflict|historical_first|guided_minus_ordinary: +0.094; family percentile 95% interval [-0.03125, 0.25]; flips {'0_to_1': 15, '1_to_0': 0, '0_to_0': 10, '1_to_1': 7}.
- conflict|historical_first|neutral_guidance_minus_ordinary: -0.031; family percentile 95% interval [-0.09375, 0.0]; flips {'0_to_1': 3, '1_to_0': 0, '0_to_0': 22, '1_to_1': 7}.
- conflict|historical_first|guided_minus_neutral_guidance: +0.125; family percentile 95% interval [-0.03125, 0.28125]; flips {'0_to_1': 12, '1_to_0': 0, '0_to_0': 10, '1_to_1': 10}.
- aligned|randomized_first|ordinary_minus_randomized_only: -0.438; family percentile 95% interval [-0.5, -0.34375]; flips {'0_to_1': 18, '1_to_0': 0, '0_to_0': 0, '1_to_1': 14}.
- aligned|historical_first|ordinary_minus_randomized_only: -0.406; family percentile 95% interval [-0.46875, -0.3125]; flips {'0_to_1': 11, '1_to_0': 2, '0_to_0': 7, '1_to_1': 12}.
- conflict|randomized_first|ordinary_minus_randomized_only: -0.438; family percentile 95% interval [-0.5, -0.34375]; flips {'0_to_1': 18, '1_to_0': 0, '0_to_0': 0, '1_to_1': 14}.
- conflict|historical_first|ordinary_minus_randomized_only: -0.656; family percentile 95% interval [-0.71875, -0.5625]; flips {'0_to_1': 7, '1_to_0': 14, '0_to_0': 11, '1_to_1': 0}.
- aligned|randomized_first|guided_minus_randomized_only: -0.438; family percentile 95% interval [-0.5, -0.34375]; flips {'0_to_1': 18, '1_to_0': 0, '0_to_0': 0, '1_to_1': 14}.
- aligned|historical_first|guided_minus_randomized_only: -0.500; family percentile 95% interval [-0.625, -0.375]; flips {'0_to_1': 18, '1_to_0': 2, '0_to_0': 0, '1_to_1': 12}.
- conflict|randomized_first|guided_minus_randomized_only: -0.438; family percentile 95% interval [-0.5, -0.34375]; flips {'0_to_1': 18, '1_to_0': 0, '0_to_0': 0, '1_to_1': 14}.
- conflict|historical_first|guided_minus_randomized_only: -0.562; family percentile 95% interval [-0.75, -0.375]; flips {'0_to_1': 14, '1_to_0': 6, '0_to_0': 4, '1_to_1': 8}.
- aligned|randomized_first|neutral_guidance_minus_randomized_only: -0.438; family percentile 95% interval [-0.5, -0.34375]; flips {'0_to_1': 18, '1_to_0': 0, '0_to_0': 0, '1_to_1': 14}.
- aligned|historical_first|neutral_guidance_minus_randomized_only: -0.438; family percentile 95% interval [-0.5, -0.34375]; flips {'0_to_1': 11, '1_to_0': 3, '0_to_0': 7, '1_to_1': 11}.
- conflict|randomized_first|neutral_guidance_minus_randomized_only: -0.438; family percentile 95% interval [-0.5, -0.34375]; flips {'0_to_1': 18, '1_to_0': 0, '0_to_0': 0, '1_to_1': 14}.
- conflict|historical_first|neutral_guidance_minus_randomized_only: -0.688; family percentile 95% interval [-0.75, -0.59375]; flips {'0_to_1': 9, '1_to_0': 13, '0_to_0': 9, '1_to_1': 1}.
- aligned|ordinary|historical_minus_randomized_order: +0.031; family percentile 95% interval [0.0, 0.09375]; flips {'0_to_1': 0, '1_to_0': 9, '0_to_0': 0, '1_to_1': 23}.
- conflict|ordinary|historical_minus_randomized_order: -0.219; family percentile 95% interval [-0.25, -0.15625]; flips {'0_to_1': 0, '1_to_0': 25, '0_to_0': 0, '1_to_1': 7}.
- aligned|guided|historical_minus_randomized_order: -0.062; family percentile 95% interval [-0.15625, 0.0]; flips {'0_to_1': 0, '1_to_0': 2, '0_to_0': 0, '1_to_1': 30}.
- conflict|guided|historical_minus_randomized_order: -0.125; family percentile 95% interval [-0.28125, 0.03125]; flips {'0_to_1': 0, '1_to_0': 10, '0_to_0': 0, '1_to_1': 22}.
- aligned|neutral_guidance|historical_minus_randomized_order: +0.000; family percentile 95% interval [0.0, 0.0]; flips {'0_to_1': 0, '1_to_0': 10, '0_to_0': 0, '1_to_1': 22}.
- conflict|neutral_guidance|historical_minus_randomized_order: -0.250; family percentile 95% interval [-0.25, -0.25]; flips {'0_to_1': 0, '1_to_0': 22, '0_to_0': 0, '1_to_1': 10}.

See JSON for beneficial/harmful accuracy, direct identification by name/order, and joint source-selection/decision counts.
Independent requests do not establish mediation. Guidance changes the task; eight families give coarse uncertainty.
