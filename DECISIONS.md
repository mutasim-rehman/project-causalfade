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

## 2026-11-12 09:38 PKT

Run a fresh-family replication of cohort 009's F16 source-order effect. Cohort 009 reused the original 16 families, so a new draw directly checks whether the effect persists beyond those items. Freeze SCM seed 20261113 before generation and order seed 20261112 before inference. Use 12 independent families, exact evidence, both orders per item, within-family balanced order assignment and the existing two formats. Primary outcome is the order change in F16 conflict accuracy. The format interaction is secondary. Record that this follow-up was chosen after viewing cohort 009 and remains exploratory.

## 2026-11-12 09:40 PKT

Freeze the cohort 010 fixture before inference. The source generator produced 12 fresh families and 48 exact source-selection items, and order expansion produced 96 prompts with balanced assignment. The base schedule is archived. Verification confirms 48 complete twin pairs, 12 families and four first-order assignments per side per family. Run F16 followed by Q4_K_M using identical run seed, resource settings and generation limits. Retain the data as an exploratory independent-family replication selected after viewing cohort 009.

## 2026-11-12 09:47 PKT

Close cohort 010 after complete joins and model hashes. F16 conflict accuracy fell by 25 points with historical evidence first on 12 fresh SCM families. This replicates the direction and approximate size observed in cohort 009. Q4_K_M remained 6/24 in both conflict orders. Treat the independent-family replication as stronger evidence of order sensitivity on this generated task. Keep claims bounded to this task and checkpoint. Future work should balance evidence strength, vary scenarios, and specify a validated reference competence gate before confirmatory collection.

## 2026-11-12 09:47 PKT

Following replication of the interleaved order effect on 12 new families, prioritize a confirmatory design with matched observational signal strength in aligned and conflict cells. The existing generator produces stronger observational magnitudes in aligned cells. Adjust the design while preserving causal effect magnitudes, validate probability constraints and signs, and document the target population. Freeze prompts, family split, competence thresholds and analysis before confirmatory inference. Do not pool the current exploratory families into a confirmatory estimate. These results justify the design work, but do not by themselves establish a general quantization effect.

## 2026-11-12 09:52 PKT

Prepare cohort 011 as a development-only matched-source-strength pilot. Cohorts 009–010 show that aligned cells had larger observational risk differences than conflicts because the original generator held confounding strength fixed: absolute historical difference was confounding plus the causal effect when aligned and confounding minus the effect in conflict. Preserve each family's causal-effect magnitude, sample a target historical difference of 0.38–0.46, use confounding magnitude target-minus-effect in aligned cells and target-plus-effect in conflicts, and derive condition-specific treatment assignment probabilities. This target interval overlaps the observed conflict signal ranges in cohorts 009–010 (0.2788–0.5003) and is intended to reduce aligned difficulty to the conflict level. Keep the prior 3B F16/Q4_K_M checkpoint pair, exact source-selection framing and CPU policy. Balance both evidence orders within each of 16 new families and run each format on the same shuffled 128-prompt schedule. The cohort is explicitly exploratory because its design follows inspection of prior outcomes; reserve disjoint, untouched families for any confirmatory study. The new fixture audit verified 64 four-cell tasks, 128 complete order twins, balanced within-family order assignment, exact effect signs, matched observational magnitudes, interior probabilities and rendered rates within 0.00981 percentage points of exact values. No model inference had started at this decision freeze. The first fixture expansion is preserved in `experiments/cohort_011/input_prevalidation/`; final fixture is in `input/`.

## 2026-11-12 09:54 PKT

Freeze cohort 011 inference settings after fixture validation and before model calls. The 16-family, 128-prompt schedule uses run seed 20261112; the 3B F16 and Q4_K_M files are identified by SHA-256 in `experiments/cohort_011/frozen_run_plan.json`. Run both formats sequentially with the same shuffled schedule on llama.cpp b12176 CPU, eight threads, context 2048, one sequence, F16 KV cache, temperature zero, prompt cache disabled and a 160-token cap. Preserve raw output and report strict parsing alongside the existing single-fence action sensitivity. Analyze paired order differences with family-block bootstrap; keep precision interactions exploratory. Run all scheduled prompts in both arms, retaining failures. The fixture itself is complete and model calls are now authorized under this exploratory design.

## 2026-11-12 10:10 PKT

Close cohort 011 after both model arms completed 128/128 prompts with the frozen schedule, matching model hashes, normal stops and complete paired order joins. F16 conflict accuracy was 16/32 randomized-first and 8/32 historical-first (−25 points; 16-family interval −37.5 to −12.5). After collapsing over order, F16 scored 50/64 aligned and 24/64 conflict; Q4_K_M scored 33/64 and 32/64. Q4_K_M's smaller aligned-minus-conflict penalty reflects a 63/64–64/64 activate policy and near-chance accuracy, not selective preservation. Strict parsing was 0/128 per arm because every response was a fenced JSON object; single-fence action scores are a labeled sensitivity. The balanced-strength source design passes its intended mathematical checks, but reference conflict competence remains low. Keep this cohort developmental and do not pool it into a confirmatory analysis.

## 2026-11-12 10:10 PKT — correction to interleaved cell totals

A code audit found that `tools/analyze_interleaved_order.py` averaged two items per family before reporting cell counts, then treated each family mean as one success count while retaining the two-item denominator. This halved correct and activation totals in the printed tables. The order contrasts and family bootstrap intervals were computed from family means and remain unchanged. Fix the count aggregation, rerun cohorts 009–011, preserve each prior machine-readable result with the suffix `v1_undercounted_counts`, and correct the cohort summaries and this session report. Corrected conflict totals are: cohort 009 F16 16/32 randomized-first vs 9/32 historical-first and Q4_K_M 16/32 in both; cohort 010 F16 12/24 vs 6/24 and Q4_K_M 12/24 in both; cohort 011 F16 16/32 vs 8/32 and Q4_K_M 16/32 in both. The previous claim that Q4_K_M was below the always-action baseline is withdrawn; it matched that baseline. The raw predictions and order-effect point estimates/intervals were not changed. The corrected output is now canonical, and previous outputs remain archived for transparent audit.

## 2026-11-12 10:12 PKT

Run a 7B F16 feasibility screen on eight families already used in developmental cohort 011. The 3B matched-strength cohort still has weak conflict competence, so a larger full-precision reference may establish whether the simplified two-source task is interpretable before considering a precision comparison. Reusing the development families supports only feasibility and is not an independent validation. Freeze the sampled family list, shuffled schedule, 7B F16 hash and CPU settings before inference. Carry forward the earlier 7B fence-only screen rates (at least 87.5% valid, 68.75% overall accuracy and 56.25% conflict accuracy); require the conflict minimum separately in each evidence order to avoid an order-specific competence failure. If any gate fails, retain the screen and do not run Q4_K_M. If it passes, run the paired Q4_K_M arm only as a developmental comparison on the same schedule. Keep this sample out of any confirmatory analysis.

## 2026-11-12 10:21 PKT

Close cohort 012 after all 64 7B F16 responses completed with matching frozen schedule and weight hash. Fence-only scoring yielded 64/64 valid actions and 47/64 correct overall, but only 8/16 conflict correct with randomized evidence first and 7/16 with historical evidence first. Both conflict gates required 9/16, so the predeclared feasibility gate failed. Apply its stopping rule and do not run 7B Q4_K_M. This outcome shows that the current simplified task still lacks a competent full-precision reference on conflict items; it does not support or test a quantization effect. Preserve this eight-family development screen and use independent families only after task/reference development is complete.

## 2026-11-12 10:35 PKT

Develop a paired prompt-clarity control after the 7B reference failed its conflict gate. Use eight fresh matched-strength families and the same 7B F16 checkpoint. Within every task and evidence order, compare the cohort-011 minimal wording with a causal-context framing that states the true mechanism (severity affects both operator treatment choice and success), random assignment in the lab study, and population match. It does not reveal the action or prescribe which source to select. This tests whether providing the evidence-generating mechanism improves competence; it changes the task support and is not a replication of unscaffolded causal reasoning. Freeze 128 prompts, balanced evidence order per family and framing, model hash, resource settings, and analyze each framing against the prior 7B gate (56/64 valid, 44/64 correct overall, at least 9/16 conflict correct in each order). Report paired family-level gains. Keep the study exploratory; no precision arm or confirmatory claim is authorized by these outcomes.

## 2026-11-12 11:33 PKT

Close cohort 013 after all 128 7B F16 prompts completed. Under the frozen parser, the minimal frame had 64/64 valid fenced actions, 48/64 correct overall, 32/32 aligned and 8/16 conflict correct in each order; it failed the per-order conflict gate. The causal-context frame had 0/64 valid responses because all generations reached the 160-token cap and continued with explanatory prose after a leading JSON object. A separately labeled post hoc leading-object diagnostic scored it at 45/64: 16/16 aligned and 8/16 conflict randomized-first, 5/16 aligned and 16/16 conflict historical-first. The scaffold changes order dependence but does not improve overall accuracy or satisfy the frozen response contract. Keep it as development evidence and make no confirmatory claim.

Plan cohort 014 as another development screen on eight fresh matched-strength families. Retain both prompt frames and paired source orders, strengthen the final instruction to require exactly one bare JSON object with one `activate` key and no explanation, and reduce the generation cap to 48 tokens (based on the observed 14-token bare/fenced minimal responses and the need to limit long invalid continuations). Use 7B F16 only and apply the same reference gate to strict JSON validity, overall accuracy, and conflict accuracy in each order. This tests whether a clear response contract makes the matched-strength task measurable. Do not use any family from cohorts 011–013 for confirmation.

## 2026-11-12 11:36 PKT

Freeze cohort 014 after cohort 013 found that the causal-context frame produced a valid leading action followed by explanatory prose and hit the token limit on all 64 contextual prompts. Use eight fresh matched-strength families (world seed 20261119), the same paired minimal/causal-context and balanced-order design, and the same 7B F16 reference. Strengthen the final output instruction identically in both prompt frames: exactly one bare one-key JSON object, no fence or explanation. Set a 48-token cap, above three times the prior 14-token short completion while limiting long explanation continuations. Run the same 128-task frozen schedule with llama.cpp b12176 CPU, eight threads, F16 KV cache, temperature zero and prompt caching disabled. Score strict JSON validity and accuracy as primary; allow single-fence only as a sensitivity. Apply the reference gate separately to each frame (56/64 valid, 44/64 correct overall, at least 9/16 conflict correct in each order). The study tests whether the response contract permits interpretable feasibility results; it remains exploratory and does not test quantization. Keep all cohorts 011–014 out of confirmation.

## 2026-11-12 11:55 PKT

Close cohort 014 after all 128 strict-JSON responses completed normally and the frozen schedule and model hash matched. Both prompt frames fail the reference gate: minimal scores 48/64 overall but 8/16 conflict correct in each order; causal context scores 42/64 overall, two below threshold, while meeting the conflict minimum exactly at 9/16 in each order. Do not run quantization on these results. Continue with a fresh 16-family causal-context-only development screen under the same strict response contract. Predeclare a scaled gate of 112/128 valid, 88/128 overall correct and at least 18/32 conflict correct in each evidence order. Launch Q4_K_M on the identical schedule only if F16 clears all three gate criteria. Cohorts 011–015 remain development, not confirmation.
