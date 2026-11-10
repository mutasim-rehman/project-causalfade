# Research decisions

## 2026-11-10 13:10 PKT

Use the local CAUSALFADE folder for input weights and fixtures, and this repository for run artifacts. Start with the provisional 3B F16/Q2_K contrast on exact evidence. The known graph, exact probabilities and matched families remove sampling error in the evidence and make failures easier to interpret. Reserve the remaining model sizes and formats for later development decisions.

Use the official llama.cpp b12176 Ubuntu CPU build for both arms. The machine has an RTX 4000 Ada using nouveau, and a working CUDA setup has not been established. CPU execution avoids driver changes during the lab session and keeps the execution policy common. Eight threads and one model process at a time limit resource pressure. Validate via recorded startup, timing and complete task blocks.

## 2026-11-10 13:11 PKT

Keep the declared strict JSON scorer. The first visible F16 response wrapped a JSON object in a Markdown fence, so add a separately labeled, post hoc format sensitivity that unwraps one complete JSON fence. Preserve the original response and apply the same rule to both arms. This estimates how much format compliance changes the observed contrast without granting credit for malformed content, extra prose, or invalid action values. Compare cell-specific errors and output length so interpretation is not driven by a single aggregate accuracy.

## 2026-11-10 13:12 PKT

Prepare a formula-given arithmetic control before the paired cohort completes. It keeps the numeric table, target value, response keys and scheduling fixed and supplies the rule to compute the answer. This provides a same-item execution diagnostic if the initial F16 arm struggles. Prompt wording and length differ, so this is an exploratory scaffold comparison. Keep estimates and action choices separate, since a model can recommend an action inconsistent with its reported estimate.
