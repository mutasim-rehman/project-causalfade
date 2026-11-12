# November 10, 2026 research session

The session started at revision `ef0fa4e` with local inputs in `$HOME/Desktop/CAUSALFADE`. Prior work consists of synthetic design validation and prepared weights. Cohort 001 will assess feasibility of the paired 3B F16/Q2_K direct-response comparison using the existing fixtures.

The CPU runtime is llama.cpp b12176 (commit 8820b088d) on the Ubuntu lab machine. The durable runner was pushed as `aec9fd2`. The exploratory fence sensitivity and arithmetic-control generator were pushed as `da4507b`. All 26 repository tests passed after these changes. Cohort 001 is executing F16 followed by Q2_K, with 64 scheduled responses each. Initial F16 output exposed a strict JSON compliance issue. Both unmodified strict scoring and a separately labeled fence-only sensitivity will be reported.

F16 completed 64 of 64 responses, and its weight SHA-256 matched the historical manifest. All outputs were single fenced JSON objects, so strict action accuracy was 0/64. The fence-only sensitivity produced 33/64 correct actions, with activation on 63/64 and the correct adjustment set on 0/64. This establishes a reference-competence issue independent of JSON fencing.

Q2_K completed 64 requests with matching weight provenance. All 64 were length-capped and failed both parsers. The strict contrast has a complete accuracy floor. Fence-only accuracy is 51.6% for F16 and 0% for Q2_K. The +3.125-point conflict-penalty contrast arises because the weak F16 arm was one answer better in the conflict cells, while Q2_K failed in all cells. It does not show selective susceptibility. Q4_K_M is running as a post hoc intermediate-format comparator.

Q4_K_M completed the same 64 prompts. All outputs were fenced JSON and stopped normally. Fence-only accuracy was 34/64, with activation on 62/64 and correct adjustment on 0/64. Cohort 001 established a Q2_K output failure and a weak 3B direct-response reference. See the [paired pilot summary](experiments/cohort_001/summary.md).

The [Q2_K repacking diagnostic](experiments/cohort_003/summary.md) completed 32 requests. All default responses exactly repeated the corresponding earlier responses. Disabling repacking changed the text on every item but did not yield a valid action or prevent length caps on any item. The formula-given control is in progress.

A follow-up GGUF metadata audit found identical tokenizer and embedded chat-template metadata across the 3B F16, Q2_K and Q4_K_M files. The runtime reported matching prompt token counts on all 64 matched prompts. See the [metadata audit](experiments/cohort_001/tokenizer_metadata_audit.json).

The [formula-given control](experiments/cohort_002/summary.md) completed 128 requests. Under fence handling, F16 and Q4_K_M scored 32/64 and 35/64 in their explicit action fields. The sign of the reported numeric estimate was correct on 61/64 and 45/64. The control reversed the models' near-constant preference from activate to decline while improving numeric performance. All control evidence is kept alongside the original direct-response pilot.

The [7B F16 reference screen](experiments/cohort_004/summary.md) completed 32 responses. Fence-only accuracy was 17/32, with activation on 31/32. It named the correct adjustment set on every item but failed the predeclared 22/32 overall gate. The matched 7B Q2_K arm was not launched. The evidence-source selection diagnostic started after the screen.

The [source-selection diagnostic](experiments/cohort_005/summary.md) completed 128 requests. F16 was 28/32 aligned and 11/32 conflicting after fence handling. Q4_K_M was 19/32 and 16/32, with activation on 61/64. The resulting smaller Q4_K_M penalty coincided with worse overall accuracy and a stronger action bias. F16's cell rates also violated the additive equality required by the homogeneous processing tree in a descriptive check. Order varied by family and was associated with behavior. A matched reversal will check the role of order directly.

The [Q8_0 follow-up](experiments/cohort_006/summary.md) completed 64 requests on the original formula-control schedule. Q8_0 matched F16 at 61/64 correct estimate signs, with two item-level differences, and both exceeded Q4_K_M's 45/64. Q8_0 still chose decline on every explicit action. The 12-family replication of the F16 versus Q4_K_M sign difference has started.

The [fresh-family replication](experiments/cohort_007/summary.md) completed 96 requests. F16 and Q4_K_M scored 46/48 and 31/48 on estimate sign. The paired difference was −31.25 points for Q4_K_M (12-family descriptive percentile interval −41.67 to −20.83), repeating the direction of the earlier −25-point result. Explicit actions were 24/48 and 28/48 and often disagreed with the estimates. The final source-order reversal is underway.

The user requested an immediate stop for PC shutdown. Seven cohorts were completed and pushed. Cohort 008 stopped during F16 after 25 of 64 requests, with one interrupted request recorded separately. The Q4_K_M reversal did not start. Resume with a fresh F16 run directory, then run Q4_K_M and analyze both against cohort 005. The completed fresh-family replication remains the strongest arithmetic result. Selective causal degradation remains unresolved.

## Resumed 12 November 2026

The user resumed research and removed the original deadline constraint. Cohort 008 was completed with fresh run IDs to preserve the interrupted attempt. Across 16 matched families, F16 conflict accuracy was 16/32 with randomized evidence first and 7/32 with historical evidence first, a −28.125 point shift (paired family percentile interval −40.625 to −15.625). Q4_K_M scored 16/32 in both conflict orders, activating on all conflict items. See the completed [source-order reversal report](experiments/cohort_008/summary.md) and machine-readable [analysis](experiments/cohort_008/source_order_analysis.json). The initial and reversed orders were collected in separate sessions. Repeat exposure and session timing still limit attribution to line position alone.

## Resumed session, 12 November 2026

Reconstructed the Nov 10–12 experiments from the decision log, experiment index, per-run artifacts and Git history. The paused cohort 008 order reversal is now complete and pushed. Its session timing limitation motivates the current cohort 009. We generated a 128-prompt fixture from 64 matched items, with both orders for each item and balanced first-order assignment within all 16 families. Fixture hashes and family balance were verified before inference. Both arms use the prior CPU build and task interface. F16 is running and Q4_K_M is queued on the exact same task schedule.

Cohort 009 completed 256 responses in the interleaved same-session order design. With historical evidence first, F16 conflict accuracy fell from 8/32 to 4/32, a −21.875 percentage point change (16-family bootstrap interval −34.375 to −9.375). Q4_K_M was 8/32 under both orders. Its format interaction with the F16 order shift was +21.875 points (interval +9.375 to +34.375). The within-family balanced assignment and shuffled prompt schedule address the prior collection-session confound. Both conditions remain weak, and this result is limited to the tested 3B checkpoint, task prompts and world families. The [cohort summary](experiments/cohort_009/summary.md) reports the aligned-cell effects and limitations.
