# CausalFade implementation and research roadmap

> **10 November 2026 update.** The status below describes the original prospective design. The user authorized exploratory inference on the Ubuntu lab PC using local model weights. The [experiment index](../EXPERIMENTS.md) and [session report](../SESSION_REPORT.md) track live progress. Confirmatory choices remain open.

**Version 1.0 — 7 November 2026.** This is a prospective work plan. Documentation and model preparation are complete; live LLM work has not started. Research runs remain on hold under the user's instruction. Recording a future phase here does not authorize executing it.

## Research deliverable and scope

Working title: **Quantization and causal decision-making in small LLM agents: a process-dissociation study.**

The project tests whether matched quantized versions of Qwen2.5-Instruct become more susceptible to misleading observational associations when choosing interventions. It combines an SCM with known causal effects, agreement/conflict conditions adapted from psychology, paired configuration comparisons, and advanced statistical modeling. The primary evidence concerns behavioral effects of deployment configurations. Internal circuit or causal-graph destruction would require a separate mechanistic study.

The core course submission should include a bounded analyst agent, its direct-response diagnostic baseline, a reproducible task environment, a justified sample size, effect estimates with uncertainty, measurement-model diagnostics, and interpretable figures. Active causal discovery, multiple model families, fine-tuning and component restoration are extensions after the core study is complete.

The scientific specification is [RESEARCH_METHODOLOGY.md](RESEARCH_METHODOLOGY.md). The source adaptation, original findings and reasons for transfer are in [METHODOLOGY_ADAPTATION.md](METHODOLOGY_ADAPTATION.md). The data format is defined in [DATA_CONTRACT.md](DATA_CONTRACT.md).

## Completed baseline

- Literature collection: 14 papers from 2025–2026 with summaries and source records, plus foundational methodological references.
- Simulator: independent SCM families, four causal/association cells per family, exact and sampled evidence, analytic oracle and classical reference baselines.
- Measurement development: constrained pooled processing-tree fit, synthetic recovery, model-fit diagnostics, rival-model example, scorer and paired family bootstrap.
- Portable storage: repository contains code; `H:\CAUSALFADE` contains data artifacts and model weights. No code or executable files were found on the SSD in the completed setup inventory.
- Model preparation: Qwen2.5-Instruct 0.5B, 1.5B, 3B and 7B, each with F16, Q8_0, Q4_K_M, Q2_K and Q1_0 GGUF files. All 16 quantized variants are present; the four F16 references are retained.
- Quantization provenance: llama.cpp b12176, eight quantization threads, no importance matrix, matched F16 sources, SHA-256 records and conversion logs. The older AGERE 7B Q4 file is archived outside the canonical grid.

These are setup and synthetic-validation accomplishments. There are no LLM findings, completed inferential comparisons or power-justified confirmatory sample sizes.

## Phase 1 — Lab environment and file validation

**Status: pending; lab setup only when authorized.**

Clone/pull the repository on the lab PC. Create the environment on its local disk and connect the SSD. Resolve the data root explicitly if its drive letter changes. Pin the inference backend, record GPU/driver/OS/library versions, verify model and dataset hashes, and confirm output paths point to the SSD. Do not place code, installers or virtual environments there.

The lab has 32 GB RAM and 10 GB VRAM. Plan CPU execution or offload for 7B F16; determine context/KV-cache limits empirically rather than assuming all models fit fully on GPU. Freeze compute/cache types and offload policy, and document any differences across formats. The model files alone do not provide an installed inference environment.

**Deliverables:** machine manifest, environment specification, path/config file and storage validation report. **Exit condition:** required assets are accessible, hashes match, adequate space exists for logs, and the backend supports the intended formats. No causal benchmark results are required to complete this setup phase.

## Phase 2 — Durable direct-response runner

**Status: not implemented; requires authorization to begin live model work.**

Build the inference adapter in the repository. For each task, provide only the public prompt in a fresh context; withhold oracle truth and condition labels. Apply a frozen chat template and explicit decoding policy. Save raw text, parser status, parsed response, token counts, duration, stopping reason and configuration hashes to the SSD.

Implement durable task-level checkpointing, manifest validation, duplicate detection, interruption logging and a fixed infrastructure-retry policy. Resume only unfinished tasks under a matching run configuration. Verify resumption and parser behavior on development fixtures before research collection. Repeated greedy responses are not independent observations.

**Deliverables:** runner, parser, provenance writer and resume facility. **Exit condition:** interruptions cannot silently lose completed records, invalid responses remain in the denominator, and evaluator labels never enter model context. Later load/format checks may use separate diagnostic prompts; they are not research outcomes and must be logged separately.

## Phase 3 — Bounded analyst agent and matched controls

**Status: planned.**

Add an environment where the agent chooses whether to inspect observational strata, request deterministic arithmetic, and submit its final intervention recommendation. Keep the graph known and the evidence fixed. Log every tool call, argument, return value, failure and stopping decision. Freeze tool permissions, token/call limits and retry behavior.

Implement matched recall, context-comprehension and noncausal arithmetic controls. Preserve response format, calculation burden and context characteristics where feasible. Prevent tools from directly returning oracle labels or the correct final answer. Deterministic arithmetic tools may calculate quantities the agent explicitly requests; the policy for doing so is part of the agent treatment.

**Deliverables:** bounded agent interface, tool logs, control tasks and an amended data contract. **Exit condition:** direct-response and agent modes can be scored separately; a tool-selection failure is distinguishable from a calculation/parser failure. The study still measures causal identification/estimation on a known graph, not causal discovery.

## Phase 4 — Development pilot and feasibility

**Status: planned; this is research, not SSD preparation.**

Generate a development-only set of independent families. Run a small, explicitly exploratory pilot to assess F16 competence, format/tool failure, response length, latency and offload behavior. Inspect whether the task population produces meaningful agreement/conflict variation. Include all format failures rather than removing the weakest settings after seeing their accuracy.

Choose prompts, budgets and competence/failure thresholds using these development families. If Q1_0 or a small F16 model is practically unusable, report that outcome and define its role before confirmatory collection. A severely degraded configuration may support an operational-failure conclusion while providing little information about selective associative reliance.

**Deliverables:** feasibility report, frozen candidate prompts and proposed scientific thresholds. **Exit condition:** the primary comparison is executable and interpretable, the reference has sufficient task competence, and choices are made without examining confirmatory outcomes. No pilot observation enters the later untouched confirmatory analysis.

## Phase 5 — Statistical validation, power and protocol freeze

**Status: planned; existing synthetic recovery is insufficient for this phase.**

Simulate the actual family-dependent design, plausible baseline performance and effect sizes, invalid outputs, random-effect variation, near-boundary tree parameters, and machine blocks if needed. Evaluate interval coverage, false-positive rate, convergence and power for the primary probability-scale contrast. Evaluate fit-test calibration and recovery before interpreting hierarchical C/A/B estimates.

Determine the required independent-family count from a justified minimum effect and target precision/power. A 90% power target can be evaluated as a planning objective, but the effect threshold and final target remain undecided. Also quantify Monte Carlo uncertainty in the power estimate. The existing 24-family export and 3,600 synthetic fits do not constitute a sample-size justification.

Working planning proposal: 3B Q2_K versus 3B F16, exact evidence. The final primary agent mode, contrast, practical effect threshold and preservation margin must be recorded in [DECISIONS_BEFORE_COLLECTION.md](DECISIONS_BEFORE_COLLECTION.md). A pilot-driven change before freezing is permissible and must be disclosed.

Assign whole families to development and confirmatory sets; all four cells, evidence variants and paraphrases follow the same split. Freeze prompts, task population, randomization schedule, weights, execution settings, hypotheses, analysis implementation, failure handling, multiplicity policy and stopping rule. Timestamp/register the protocol and archive the Git commit and hashes.

**Deliverables:** simulation/power report, final family count, frozen protocol and analysis scripts. **Exit condition:** all scientific decisions have values and rationales, the planned inference behaves adequately in simulation, and the confirmatory families remain unseen by model/prompt selection.

## Phase 6 — Confirmatory collection on the lab PC

**Status: blocked by prior phase dependencies and the user's current research hold.**

Evaluate frozen configurations on the same balanced families, with randomized execution order within feasible blocks. Record the schedule and deviations. Preserve raw responses, all attempts and operational failures. If changing machines, verify environment hashes and a separate development overlap set, record the transition, and avoid confounding one precision condition with one machine.

For N independent families, four cells and 20 configurations require **80N scheduled responses per evidence layer and agent mode**. Exact plus sampled evidence requires 160N; adding a second interface mode doubles that again. Controls, stochastic repetitions and diagnostic runs add separate costs. All cells/variants remain dependent within their family; response count is not independent sample size.

**Deliverables:** immutable raw trajectories, complete run manifests and a collection audit. **Exit condition:** the prespecified stopping rule is reached, gaps are accounted for, hashes/configurations match, and infrastructure exclusions follow the frozen policy. No optional stopping for significance.

## Phase 7 — Scoring, causal comparisons and advanced statistics

**Status: planned.**

Score every scheduled item, retaining invalid/missing predictions as primary accuracy failures. Verify joins and full family blocks. Keep numeric-estimate missingness explicit and use the frozen regret policy. Preserve separate exact/sampled and direct/tool analyses.

The primary estimand is:

```text
Delta(size, format) = [Acc(format, aligned) - Acc(format, conflict)]
                   - [Acc(F16, aligned) - Acc(F16, conflict)]
H0: Delta <= 0       H1: Delta > 0
```

Fit the prespecified hierarchical binary outcome model, then standardize predictions to obtain probability-scale contrasts. Use paired family-bootstrap uncertainty as a robustness analysis, not an arbitrary permutation of deterministic format labels. Distinguish conditional sample-specific predictions from inference to new families. Use one-sided alpha .05 only for the frozen directional primary test, with calibrated inference and clearly labeled interval types.

Fit the hierarchical psychological measurement adaptation only after recovery, fit and identifiability checks support it. Model invalidity explicitly or label valid-response estimates as selected-population sensitivity analyses. Compare competing evidence-integration models on held-out families. Report C, A, B and wA with uncertainty and boundary/fit warnings; observationally equivalent models prevent strong latent-route identification.

Use prespecified paired estimation-error/regret contrasts, a task-type interaction for behavioral specificity, and Holm correction within the declared secondary comparison family. Preservation requires a justified equivalence/noninferiority margin; a nonsignificant degradation test does not establish it. Treat model size as a fixed set of checkpoints and precision configurations as categorical treatments.

**Deliverables:** scored data audit, probability-scale effects/intervals, statistical model diagnostics, sensitivity analyses and a claim ledger. **Exit condition:** conclusions remain valid under documented diagnostics or are narrowed to match failures. Do not describe C/A/B as identified neural circuits or claim pure bit-width effects across different quantizer families.

## Phase 8 — Visualization, report and reproducibility package

**Status: planned.**

Produce faceted accuracy plots for aligned/conflict tasks, effect-estimate forest plots, paired family changes, estimation-error/regret summaries, invalid/tool-failure rates and measurement-model diagnostics. Include C/A/B plots only with their fit/identifiability context. Export scientific figures as PDF/SVG and PNG using repository code; retain the numeric summaries supporting each figure on the SSD and a small versioned report where appropriate.

Write methods, source adaptation, limitations, results and a transparent distinction between pilot and confirmatory work. Update the scoped novelty search before submission. Include frozen protocol and deviations, model/task hashes, environment manifests, the run-resumption procedure, and source attribution. Back up irreplaceable data to another location.

**Deliverables:** course paper, figures, reproducibility instructions and repository release. **Exit condition:** a reviewer can trace each claim to an analysis artifact and reproduce it from the declared inputs without access to private labels through the agent interface.

## Optional extensions after the core study

- Active investigation: allow the agent to choose SCM interventions and measure intervention efficiency and causal discovery under a new design.
- Cross investigator/analyst precision to separate evidence acquisition from interpretation; randomize stage interventions before claiming mediation.
- Component precision restoration for mechanistic hypotheses, with explicit component-level interventions and appropriate controls.
- Calibrated IQ formats, calibration replicates, new causal graphs, evidence-strength matching and a second model family for wider generalization.

These are additional studies and are not required to complete the bounded analyst-agent project.

## Current next action and storage responsibilities

Current state: setup and documentation only; no live research has begun. The next permissible work is whichever setup/documentation task the user authorizes. Live diagnostic inference, pilots and confirmatory collection must wait for authorization to lift the research hold.

Keep code and dependency specifications in the repository and push changes before switching PCs. Keep model data, datasets, trajectories, logs and outputs on the SSD. Installed runtimes stay on each PC. Keep manifest copies and a second backup of irreplaceable progress. Every future run must identify its Git commit, data/model hashes and runtime configuration; a drive letter and a model filename alone are insufficient.
