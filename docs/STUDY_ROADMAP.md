# CausalFade implementation and research roadmap

**Version 1.1 — 13 November 2026.** This roadmap distinguishes completed evidence from the proposed sensitivity/bias follow-up. Existing frozen cohort protocols remain authoritative. Updating this plan does not launch inference or change historical endpoints.

## Research deliverable and scope

Working question: **Does quantization alter sensitivity to causal evidence, or primarily shift response bias and susceptibility to presentation?**

Causal inference remains central. An SCM supplies intervention ground truth, while precision, observational evidence and presentation are controlled experimental factors. Retain the psychology-inspired agreement/conflict design, add a signal-detection/psychophysics experiment, and validate the resulting measures with matched controls and rival-model predictions. More disciplinary labels are not a substitute for a discriminating result.

The scientific specification is [RESEARCH_METHODOLOGY.md](RESEARCH_METHODOLOGY.md). The [interdisciplinary follow-up](INTERDISCIPLINARY_FOLLOWUP.md) defines the new study proposal; [METHODOLOGY_ADAPTATION.md](METHODOLOGY_ADAPTATION.md) documents source lineage, contributions and limitations. New collection choices belong in [DECISIONS_BEFORE_COLLECTION.md](DECISIONS_BEFORE_COLLECTION.md). The current data contract is [DATA_CONTRACT.md](DATA_CONTRACT.md); new fields must be versioned before use.

## Completed work and evidence limits

- Literature collection and methodological source records, simulator, oracle effects and classical baselines.
- Synthetic C/A/B recovery and model-fit diagnostics, including boundary failures and observational equivalence. These are not LLM construct validation.
- Durable direct-response runner, provenance, raw outputs and scoring; experiments 001–016 analyzed.
- Matched-strength SCM source tasks, source-order crossovers, response-contract development and competence screens.
- Cohort 016: both 7B formats completed 768 responses on 96 fresh families. Its frozen primary Q4_K_M conflict order effect replicated at +62.5 percentage points (95% family t interval +56.6 to +68.4).
- Cohort 017: both 14B formats completed 768 responses each; paired analysis and summary were recovered locally after the missing-NumPy failure. Original failure artifacts remain unchanged.
- Cohort 018: eight-family development fixture, semantic scorer, validators, resumable gated runner and descriptive analysis are implemented and tested; no inference has run. Use the [lab runbook](LAB_FOLLOWUP_RUNBOOK.md).

The large order effect is confirmed only for cohort 016's checkpoint, scaffold and population. Aligned-item shifts, action bias, reference weaknesses and the descriptive 14B boundary result limit causal-specificity and generalization claims. No validated latent C/A/B decomposition or autonomous causal-discovery result exists. See the [experiment index](../EXPERIMENTS.md) and [session report](../SESSION_REPORT.md).

## Phase 1 — Close the existing analysis gap

**Status: complete locally; no new inference required.** The [paired report](../experiments/cohort_017/summary.md) includes the analysis repair and exploratory scope. Verify lab dependencies before new runs; the steps below describe the completed recovery procedure.

Restore the lab's declared analysis dependencies, rerun the archived 14B analysis, verify joins, counts and family-level uncertainty, and retain the original failure log. Correct stale index status only with traceable artifacts. Reused cohort 016 families and a Q8 quantized reference make this exploratory.

**Deliverable:** cohort 017 paired report with scope limits, environment and provenance. **Exit condition:** every reported quantity traces to complete paired records and the analysis succeeds reproducibly.

## Phase 2 — Implement the new measurement design

**Status: bounded development implementation ready.** `tools/sensitivity_pilot.py` and `causalfade/sensitivity.py` implement a two-strength fixture, controls, semantic scoring, resume/gating and descriptive analysis. The following requirements describe the broader design; full psychophysical fitting and fitted rival-model comparisons remain prospective.

Build graded signed causal/observational strength fixtures with exact oracle validation, positivity/probability checks and display-rounding checks. Counterbalance evidence position, neutral source identifiers and output-token mappings while preserving truthful source mechanisms and semantic action. Include aligned and conflict cells, both causal directions and matched noncausal controls.

Implement semantic response decoding, SDT hit/false-alarm summaries, validity reporting, boundary handling, family-dependent response-curve analysis and rival-strategy prediction scoring. Version the task manifest and data contract. Record mapping, strength, source position, variant and parent-family identifiers outside model-visible labels.

**Deliverable:** executable generator, validators, scorer and analysis utilities. **Exit condition:** oracle consistency, complete counterbalancing, separation of evaluator truth and prompt content, and a dependence-aware analysis on development/synthetic inputs.

## Phase 3 — Development, competence and construct validation

**Status: proposed.**

Use separate development families to choose strength ranges, wording, response contract and a feasible checkpoint-specific precision contrast. Require reference competence in both causal directions and relevant presentation strata; prior gate passage is not transferable to a new task. Retain failures. Q2_K's earlier unusable outputs rule out treating it as the default primary without new feasibility evidence.

Evaluate meaning-preserving paraphrases, neutral label changes and alternative task forms. Include matched numerical comparison, noncausal source selection and source/mapping comprehension controls. Check whether candidate strategy models make distinguishable predictions under the proposed interventions. A staged/fractional design may control compute, but its aliases and identifiable interactions must be explicit.

**Deliverable:** development-only feasibility/validity report and candidate frozen design. **Exit condition:** informative strength variation, useful reference performance, identifiable planned effects and documented limits of construct interpretation. Do not reuse these families for confirmation.

## Phase 4 — Statistical validation, power and protocol freeze

**Status: proposed; cohort 016's completed power study does not cover this design.**

Select one primary precision contrast and one primary sensitivity/bias/presentation endpoint, specify its target population and practical effect threshold, and assign other outcomes secondary/exploratory roles. Freeze response models, inference/fallback rules, boundary correction, invalid-response policy, model-comparison candidates, family splits and multiplicity handling.

Simulate the actual clustered design, cue interactions, separation, invalidity, estimator boundaries, interval coverage, false-positive rate and power. Determine independent-family count and compute budget. Do not use request count as sample size. Freeze mathematical validators and analysis code before inference. Timestamp the protocol and record hashes; formal preregistration, if used, must precede collection.

**Deliverable:** simulation report, justified family count and frozen protocol. **Exit condition:** all decisions in the checklist have values/rationales and untouched families remain unused in selection.

## Phase 5 — Prospective collection and analysis

**Status: depends on phases 2–4.**

Run frozen configurations on identical family blocks with fresh model contexts and resource-aware randomized execution. Preserve raw outputs, mappings, timing, stopping reasons, model/runtime hashes, retries and all scheduled failures. Analyze semantic actions and keep validity distinct from accuracy and conditional-validity SDT summaries.

Estimate the frozen primary contrast with family-level uncertainty and calibrated inference. Report signed-strength response curves, discrimination/criterion summaries with assumptions, matched-control specificity contrasts and held-out proper-score comparisons. Do not force latent-route estimates when fit or identifiability fails. Preservation requires a justified equivalence/noninferiority margin; nonsignificance is insufficient.

**Deliverable:** auditable results and claim-to-artifact ledger. **Exit condition:** frozen stopping rule reached, deviations recorded, uncertainty and model diagnostics complete, and claims narrowed to what the design identifies.

## Phase 6 — Independent replication and publication package

**Status: proposed.**

Prioritize a second model family with matched within-checkpoint precision contrasts, and test held-out domains/templates if claiming transfer. Another seed from the same generator is within-generator replication. Report cross-size boundary results rather than pooling away heterogeneous behavior. A Q8 reference must remain labeled quantized.

Release prompts, oracle generation, frozen plans, deviations, dependencies, analysis code and accessible run artifacts. Produce scientific figures from versioned analysis outputs, with explicit denominators, uncertainty and failure rates. Update related work before submission and explain what the new experiments distinguish beyond existing quantization and order-sensitivity studies. Verify journal scope and any Q1 classification against a named ranking source, category and year. No acceptance outcome is guaranteed.

**Deliverable:** manuscript, reproducibility package and independent replication. **Exit condition:** each substantive claim is traceable, appropriately scoped and reproducible.

## Separate agentic and mechanistic extensions

The bounded analyst agent remains unimplemented: add a known-graph environment for inspecting strata, requesting deterministic arithmetic and submitting decisions, with explicit tools/budgets/logging. Treat direct-response versus tool-agent mode as a separate treatment and amend the contract before use. Autonomous intervention selection, graph discovery and investigator/analyst precision crossing require additional protocols.

Component precision restoration can test neural-mechanism hypotheses after behavioral characterization; a fitted psychological parameter is not such an intervention. Calibrated IQ formats and calibration replicates are separate precision treatments.

## Storage and execution responsibilities

Keep research code, documentation and experiment records in the repository. The Ubuntu lab uses PC-local model weights and dataset inputs under `$HOME/Desktop/CAUSALFADE`; current runs do not require an external SSD. Historical `H:\CAUSALFADE` paths describe earlier provenance. Keep weights/runtime binaries outside Git, retain per-run hashes and environment versions, and back up irreplaceable results. Machine changes require documented settings and a separate development overlap check.

The subsequent implementation task prepared the bounded cohort 018 development tools and input fixture locally. It started no model collection; formal validation and new confirmatory freezing remain prospective.
