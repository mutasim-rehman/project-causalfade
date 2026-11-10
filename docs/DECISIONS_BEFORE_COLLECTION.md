# Decisions required before confirmatory LLM collection

> **10 November 2026 update.** The status below describes the original prospective design. The user authorized exploratory inference on the Ubuntu lab PC using local model weights. The [experiment index](../EXPERIMENTS.md) and [session report](../SESSION_REPORT.md) track live progress. Confirmatory choices remain open.

This is a design record, not an approval gate for writing code. The current implementation is an exploratory validation package. Complete and timestamp these scientific choices before collecting the untouched confirmatory set.

**Updated 7 November 2026:** weights are prepared at four sizes and five formats; live research remains on hold. The [roadmap](STUDY_ROADMAP.md) defines the dependency sequence. Prepared treatments are Qwen2.5-Instruct 0.5B/1.5B/3B/7B at F16, Q8_0, Q4_K_M, Q2_K and Q1_0, with no importance matrix. IQ1_S is not part of the prepared grid. Runtime/offload settings remain to be fixed.

Working planning recommendation: 3B Q2_K versus 3B F16 on exact evidence. This is provisional, not registered. The primary agent mode, minimum relevant effect, competence/failure thresholds, equivalence margin, independent-family count, inference procedure and multiplicity families remain unresolved until pilot and simulation work supports them. Record final values and their rationales before confirmatory collection.

- **Population:** select world families, effect/evidence-strength ranges, narrative domains and whether exact or sampled evidence is primary. Current pilot ranges are not final registration choices.
- **Primary contrast:** select one checkpoint-specific precision comparison and a practical minimum change in conflict penalty. Additional precisions and checkpoints are secondary or explicitly multiplicity-controlled.
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

Claims of preservation require a separately justified equivalence/noninferiority tolerance. Claims about internal circuits require separate mechanistic interventions. Neither is implied by a null main effect.
