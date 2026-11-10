# Research decisions

## 2026-11-10 13:10 PKT

Use the local CAUSALFADE folder for input weights and fixtures, and this repository for run artifacts. Start with the provisional 3B F16/Q2_K contrast on exact evidence. The known graph, exact probabilities and matched families remove sampling error in the evidence and make failures easier to interpret. Reserve the remaining model sizes and formats for later development decisions.

Use the official llama.cpp b12176 Ubuntu CPU build for both arms. The machine has an RTX 4000 Ada using nouveau, and a working CUDA setup has not been established. CPU execution avoids driver changes during the lab session and keeps the execution policy common. Eight threads and one model process at a time limit resource pressure. Validate via recorded startup, timing and complete task blocks.

## 2026-11-10 13:11 PKT

Keep the declared strict JSON scorer. The first visible F16 response wrapped a JSON object in a Markdown fence, so add a separately labeled, post hoc format sensitivity that unwraps one complete JSON fence. Preserve the original response and apply the same rule to both arms. This estimates how much format compliance changes the observed contrast without granting credit for malformed content, extra prose, or invalid action values. Compare cell-specific errors and output length so interpretation is not driven by a single aggregate accuracy.

## 2026-11-10 13:12 PKT

Prepare a formula-given arithmetic control before the paired cohort completes. It keeps the numeric table, target value, response keys and scheduling fixed and supplies the rule to compute the answer. This provides a same-item execution diagnostic if the initial F16 arm struggles. Prompt wording and length differ, so this is an exploratory scaffold comparison. Keep estimates and action choices separate, since a model can recommend an action inconsistent with its reported estimate.

## 2026-11-10 13:22 PKT

The completed F16 arm recommended activation 63/64 times and selected the correct adjustment set 0/64 times under fence-only scoring. Early Q2_K generations contain repetitive punctuation and hit the token cap. Complete the declared Q2_K arm and add Q4_K_M as an exploratory intermediate arm on the same prompt schedule. This tests whether failure to emit usable decisions extends to moderate compression. No comparison across this grid identifies a pure bit-width effect.

## 2026-11-10 13:23 PKT

Add a small matched Q2_K runtime diagnostic with default and disabled CPU repacking. Identical weight digests and settings except for repacking let us check one software explanation for the malformed generations. Compare response text, token-limit finishes and format validity on four complete families. This diagnostic follows the model-format comparison and takes priority over a larger repeat of the failing configuration.

## 2026-11-10 13:30 PKT

Plan an eight-family 7B F16 feasibility screen after the 3B diagnostic and control runs. The 3B F16 reference was near chance after format recovery and showed extreme activation bias. A larger reference could improve competence before further quantization comparisons. Use one CPU-only process and the same prompt and generation policies. Check at least 28/32 valid, 22/32 correct overall and 9/16 correct in conflict under the already defined fence-only rule before allocating a matched Q2_K arm. The gate concerns the next exploratory run and leaves the final confirmatory criteria undecided.

## 2026-11-10 13:38 PKT

Close the CPU repacking diagnostic after both arms completed 16/16 requests with zero usable decisions. Disabling repacking altered text on every item while preserving the failure. Use Q2_K as an operational-failure observation for this session and focus on reference competence and the working Q4_K_M format. The evidence rules out disabling repacking as a remedy on these inputs, while other backends remain open.

## 2026-11-10 13:39 PKT

Add a source-selection diagnostic after the current control and 7B screen if time permits. Reconstruct randomized and historical success rates from the public strata and present them without an action label. This removes estimation from strata while retaining the two potentially competing evidence sources. Vary presentation order by family and keep all four family variants and both precision settings matched. Declare single-fence scoring as the descriptive primary outcome before running, given established fencing behavior. A shorter answer contract and the simpler evidence representation change the task, so compare the two precisions within this new cohort and interpret cross-cohort differences as exploratory.

## 2026-11-10 13:42 PKT

Check tokenizer and embedded template metadata as possible explanations for the 3B Q2_K failure. All tokenizer fields, including the template, matched across the three 3B formats. Runtime prompt token counts matched on 64/64 tasks. Keep the runtime and preparation records attached to the result. The matched tokenizer evidence narrows one alternative explanation while leaving kernel and weight effects open.

## 2026-11-10 13:43 PKT

Normalize the absolute home prefix in publishable records after identifying the machine account name in previously pushed configs, server logs and response metadata. Preserve every line and replace only that path prefix with `$HOME/`. Unmodified files are backed up outside Git under `CAUSALFADE/runs/unmodified_paths_20261110`. Prior commits retain the original paths under the no-history-rewrite policy. Apply this check to every remaining cohort before push.

## 2026-11-10 13:50 PKT

Separate the numeric estimate's sign from the model's explicit action in control analyses. In the completed F16 formula arm, the estimate sign implied the correct action on 61/64 items, while the explicit action was always decline and scored 32/64. Preserve explicit action as the outcome and report estimate-sign accuracy as a post hoc diagnostic. The direction of the number and the decision field can diverge even on the same completion.

## 2026-11-10 13:55 PKT

Use both explicit action and estimate sign in future pilot diagnostics. The completed formula controls reveal better estimate signs but near-constant explicit decline at both precisions. Preserve the existing outcome and consider an explicitly separate deterministic sign-to-action policy if numeric competence is the research target. Treat the lower Q4_K_M estimate-sign accuracy as exploratory arithmetic or execution evidence under the scaffold.

## 2026-11-10 14:00 PKT

Plan a matched Q8_0 follow-up on the formula control. It tests whether the less compressed configuration retains more estimate-sign accuracy than Q4_K_M on the same inputs, given the large retrospective difference between Q4_K_M and F16. Declare the sign score and handling of invalid estimates before this run. Reuse the archived control arms and fixed schedule. This is a screening result for an arithmetic execution target, with no equivalence claim.
