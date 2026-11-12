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

## 2026-11-10 14:04 PKT

Create a fresh 12-family replication of the 3B F16 versus Q4_K_M estimate-sign result under the formula scaffold. Choose generator seed 20261111 before any inference, use all four exact cells in each new family and retain the same control text and backend. This tests repeatability beyond the original 16 families while preserving the separate original cohort. Freeze single-fence sign scoring, keep invalid estimates in the denominator and report the paired overall difference and condition-specific rates. The expected direction is lower Q4_K_M sign accuracy. The family count fits the session budget and is not a confirmatory power calculation.

## 2026-11-10 14:07 PKT

Close the 7B screen at the F16 reference because 17/32 correct fails the predeclared 22/32 threshold. Both validity and the conflict minimum were met. Correct adjustment labels on all 32 items did not translate to competent decisions. Allocate remaining runtime to the source-selection diagnostic and the formula-sign follow-ups.

## 2026-11-10 14:13 PKT

Treat the source-selection penalty as sensitive to default actions and task presentation. Q4_K_M reduced the penalty while losing overall accuracy and activating on 61/64. F16 followed historical evidence on all 10 conflict items with historical rates first, but those items come from different families than the other order. Plan a controlled within-item reversal of the two source lines. Preserve scores, labels and evidence, and compare the shift toward following the historical direction on conflict items. Do not report C, A and B as latent route estimates given the observed additivity residual and small development set.

## 2026-11-10 14:13 PKT

Freeze the reversal diagnostic before inference. Compare historical-first versus randomized-first conflict accuracy within each task and format, keeping the family as the resampling block. The earlier order split predicts lower historical-first accuracy for F16. Report the difference between formats as exploratory. The complementary order was collected in a later block, so account for possible time-order effects in the interpretation.

## 2026-11-10 14:19 PKT

Treat Q8_0 as a candidate reference-preserving configuration for estimate sign on the formula control. It tied F16 at 61/64 on the reused sample and exceeded Q4_K_M by 16 correct signs, but matched the F16 explicit decline bias. The observed tie is not an equivalence test. Continue the separate fresh-family F16 versus Q4_K_M replication.

## 2026-11-10 14:32 PKT

Close the fresh formula replication after both complete 48-task schedules. The prespecified sign direction replicated, with a 31.25-point loss under Q4_K_M. Keep the execution result separate from the unresolved selective-degradation question because both evidence conditions suffered and explicit actions remained biased. Use the independently generated fixtures and paired family interval as the validation evidence.

## 2026-11-10 14:33 PKT

Stop the active F16 reversal and cancel the queued Q4_K_M arm for the requested PC shutdown. Preserve the partial F16 run and exclude incomplete outcomes from the paired comparison. Restart the full F16 schedule under a new run ID when research resumes.

## 2026-11-12 09:20 PKT

Resume with fresh run IDs for both source-order reversal arms. Keep the interrupted Nov 10 F16 attempt as an archived partial run. Run F16 then Q4_K_M on the frozen reversed schedule and analyze against the frozen first-order cohort. This completes the authorized interrupted diagnostic. Interpret within-item changes with the family as the inference unit, while acknowledging that source order is also separated by collection session.

## 2026-11-12 09:23 PKT

Continue beyond the completed cohort 008 result with a same-session interleaved reversal. The earlier reversal showed a large F16 order shift, but order and collection session were confounded. Duplicate each of the 64 source-selection prompts with opaque task IDs and assign first-order execution within family, balanced two per order among four base cells. Randomize prompt order using the existing runner and run seed. Run both 3B formats against identical schedules. The conflict accuracy order contrast is primary. Use the established single-fence scorer and cluster resampling on 16 families. This targeted crossover has greater value than adding checkpoints because it resolves a stated limitation in the preceding finding.

## 2026-11-12 09:25 PKT

Freeze cohort 009's fixture and generation configuration before model calls. Verified 64 item twins, unique opaque task IDs, 128 exact prompts, two first-position assignments per four-cell family, and evaluator pair joins. Inference will use the prior seed, CPU runtime, token budget, and single-fence sensitivity. F16 and Q4_K_M will run on the same randomized schedule. If either run fails, retain it and do not infer an order effect from an incomplete arm.

## 2026-11-12 09:37 PKT

Close cohort 009 after all 256 scheduled responses and paired joins verified. F16 conflict accuracy fell by 21.875 points when historical evidence was first in the same session. Q4_K_M conflict accuracy was unchanged at 8/32 in both orders. The earlier reversal direction replicated under balanced within-family assignment and shuffled prompt order. The result supports an order sensitivity in F16 on these prompts, while both model conditions remain weak. Do not infer general model or quantization effects from this 16-family development cohort.
