# Decisions required before confirmatory LLM collection

> **13 November 2026 update.** This checklist now applies to the proposed [sensitivity/bias follow-up](INTERDISCIPLINARY_FOLLOWUP.md). Cohort 016 already has a completed frozen primary order replication; this amendment neither changes that protocol nor upgrades its secondary results to confirmation.

This is a design record, not an approval gate for writing code. Complete and timestamp the new study's choices before collecting its untouched confirmatory set. Existing data may inform development but cannot become fresh confirmation of newly formulated hypotheses.

**Current state:** direct-response experiments and synthetic validation exist. Historical prepared treatments include Qwen2.5-Instruct 0.5B/1.5B/3B/7B at F16, Q8_0, Q4_K_M, Q2_K and Q1_0, without an importance matrix. The analyzed exploratory 14B follow-up uses Q8_0 and Q4_K_M; it has no F16 inference reference. Cohort 018 has a fixed development fixture/gate and tested execution tools, but no inference or confirmatory freeze. Prepared files do not imply every configuration is scientifically usable. The [roadmap](STUDY_ROADMAP.md) defines the next dependency sequence.

The original 3B Q2_K versus F16 recommendation is superseded by observed output failures and weak early reference competence. Select a new contrast on development evidence. The new primary endpoint, interface, minimum relevant effect, competence/failure thresholds, independent-family count, inference procedure and multiplicity families remain unresolved. Record final values and rationales before collection; do not inherit cohort 016's endpoint or power calculation by default.

- **Population:** select world families, effect/evidence-strength ranges, narrative domains and whether exact or sampled evidence is primary. Current pilot ranges are not final registration choices.
- **Primary contrast and endpoint:** select one checkpoint-specific precision comparison and one sensitivity, bias or presentation endpoint, with a practical minimum effect. Explicitly assign the original conflict-penalty contrast a primary or secondary role. Additional precisions and checkpoints are secondary or multiplicity-controlled.
- **Treatment definition:** freeze base checkpoint, quantizer, group size, calibration data, weight hashes, activation/cache precision and serving stack. Decide whether actual low-bit kernels or simulated quantized weights are the target.
- **Agent interface:** choose direct constrained inference or a bounded tool agent; freeze prompts, parser, retries, budgets, tool permissions and failure handling.
- **Controls:** implement matched recall, comprehension and noncausal numerical execution controls before claiming a selective causal deficit.
- **Development gates:** define baseline competence and protocol-failure thresholds on separate development families. Do not select confirmatory items based on full-precision correctness.
- **Sample size:** simulate power/interval precision under independent families, task heterogeneity, invalid responses and plausible effects. The 24-family export is a demonstration, not a justified sample size.
- **Measurement model:** establish recovery, identifiability, fit, prior sensitivity and competing-model checks. Do not claim cognitive-route identification from four cells alone.
- **Analysis:** implement/freeze hierarchical outcome and measurement analyses, probability-scale estimands, uncertainty procedures and multiplicity policy. The current MLE/bootstrap utilities do not substitute for those planned models.
- **Uncertainty tasks:** decide whether interval coverage or unidentifiability/abstention is in scope. Those outcomes require additional tasks and data-generating repetitions absent from the initial suite.
- **Split and stopping:** assign whole families to development/test, freeze task-generation and run-order seeds, record exclusion rules and stopping policy, and timestamp/register the plan before confirmatory collection.
- **Novelty:** update the search and describe overlap with static causal benchmarks, active causal-evidence evaluation, processing-tree LLM studies and crossed precision interventions.

Additional decisions for the interdisciplinary follow-up:

- **Strength grid:** freeze feasible signed causal/observational levels, balancing weights, rounding precision and validators. Set an explicit rule for zero effects if included; do not score indifference as a binary signal.
- **Orthogonal manipulations:** freeze source-name/position and response-token assignments. Preserve truthful design descriptions and semantic action meanings. State any fractional-design aliases and which interactions are identifiable.
- **SDT:** define signal, hit/false-alarm denominators, validity conditioning, strata, boundary correction and family-level uncertainty. Check whether equal-variance Gaussian interpretations are warranted; do not infer an ROC curve from one binary response threshold.
- **Psychophysical model:** freeze link, signed-strength terms, interactions, regularization, family structure, prediction target and separation/convergence fallback. Determine useful strength ranges on development families.
- **Construct validation:** freeze paraphrases, independent task forms, matched noncausal controls, robustness tolerances and domain/model-family holdouts. Specify the assumptions and anchors if attempting formal invariance/DIF; simple robustness checks do not establish latent measurement invariance.
- **Rival strategies:** freeze tree, continuous integration, source-only, position and constant-action candidates, smoothing, tuning folds and held-out proper scoring rule. Split whole families, including all variants, before tuning.
- **New power study:** simulate the chosen endpoint, family dependence, cue interactions, invalidity and boundaries. Set family count from these simulations; response count and the prior order-test calculation are insufficient.
- **Claim scope and publication:** retain neural-mechanism and causal-specificity limits. Seek independent model-family replication; validate journal fit and any Q1 designation by database/category/year. Neither extra theories nor small p-values guarantee acceptance.

Claims of preservation require a separately justified equivalence/noninferiority tolerance. Claims about internal circuits require separate mechanistic interventions. Neither is implied by a null main effect.
