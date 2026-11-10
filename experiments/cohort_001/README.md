# Paired 3B exact-evidence development pilot

We hypothesize that Q2_K increases the accuracy gap between aligned and conflicting evidence relative to the matched F16 checkpoint. Sixteen of the existing 24 design-validation families are sampled without replacement with seed 20261110. Both arms use the same 64 exact-evidence prompts in the same order, greedy decoding, CPU-only execution with eight threads, F16 cache and 160 output tokens. Strict JSON parsing and the existing action scorer retain invalid or missing decisions as failures. The backdoor and association policies provide reference anchors. This cohort assesses feasibility and possible failure modes on development items.

Both arms use the official llama.cpp Ubuntu x64 CPU release b12176 with archive SHA-256 d19cad855c437851b0556c67f08e7ae398f064524ba9e81ed8a9316ffb4218c4. Weight digests are measured at execution. Use the local CAUSALFADE directory as the input root. The config and schedule in each run record the complete settings and prompts. Each process handles one model to limit memory pressure.

After seeing early Q2_K generations reach the budget without a usable object, add Q4_K_M as an exploratory intermediate arm on the identical schedule. This arm checks whether usable output is retained at a less aggressive configuration. It does not change the original F16–Q2_K contrast.
