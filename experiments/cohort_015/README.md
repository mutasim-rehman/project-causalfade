# Cohort 015: causal-context reference screen

This exploratory development screen follows cohort 014, where strict JSON validity was restored but neither tested frame passed the reference gate. It uses 16 fresh matched-strength SCM families and only the causal-context scaffold; its results are not a general estimate for the unscaffolded task.

Each family contributes two aligned and two conflict base tasks. Every task appears in randomized-first and historical-first order, yielding 128 prompts. Within each family, two base tasks are assigned randomized-first in-family and two historical-first. All task IDs are opaque. Every prompt uses the same strict one-key JSON contract.

## Frozen F16 gate

The 7B F16 arm must meet all criteria:

- At least 112/128 strictly valid JSON actions.
- At least 88/128 correct overall.
- At least 18/32 conflict items correct with randomized evidence first.
- At least 18/32 conflict items correct with historical evidence first.

This scales the cohort 014 gate to twice as many families and responses. Invalid outputs count as incorrect. Q4_K_M runs on the same schedule only if F16 passes every criterion; otherwise it does not run. The conditional action was specified before inference. Cohort 015 remains development evidence and does not make earlier selected cohorts confirmatory.

## Frozen execution

Use llama.cpp b12176 on CPU, eight threads, context 2048, one parallel sequence, F16 KV cache, temperature zero, 48 output tokens, seed 20261112 and no prompt cache. Exact model hashes, runtime, schedule hash, gate, and conditional action are in [frozen_run_plan.json](frozen_run_plan.json). Families use generator seed 20261122; order assignment uses seed 20261123; the response schedule uses seed 20261112.

No external SSD is used. Both checkpoints are read locally under `/home/i242514/Desktop/CAUSALFADE/weights/gguf/`.
