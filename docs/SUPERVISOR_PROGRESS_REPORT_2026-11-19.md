# CausalFade — supervisor progress report

**Reporting date:** 19 November 2026  
**Coverage:** Initial literature review and methodology development through cohort 027  
**Publication objective:** Develop a rigorous contribution suitable for consideration by a Q1 journal; venue and submission readiness remain to be determined.

## Executive overview

CausalFade began by investigating whether aggressive post-training quantization makes language models more susceptible to misleading observational associations when choosing interventions. The project has developed an SCM-based experimental framework, reproducible inference and analysis tools, and a substantial archive of model responses.

The strongest confirmed finding is a large evidence-order effect in one Qwen 7B Q4 task, replicated on 96 fresh families. Subsequent experiments revealed substantial answer-position, action-preference, calculation and output-contract effects. These findings constrain the original interpretation: **we have not established selective degradation of causal reasoning under quantization.**

The research consequently moved toward validating what the intervention tasks measure. Cohorts 026 and 027 tested decisions under observationally identical distributions with different supplied causal graphs. Cohort 026 exposed a counterbalancing defect, which motivated a corrected cohort 027. In cohort 027, all four eligible F16 references completed their development runs, but none passed qualification. The pipeline therefore stopped deliberately before validation or quantization.

Current priority: establish an interpretable reference task or explicitly assisted system before further precision sweeps. The project has credible narrow findings and strong reusable infrastructure, but is not yet a submission-ready general causal-reasoning or quantization paper.

## 1. Original research question and motivation

The initial question was:

> Does aggressive post-training quantization increase reliance on misleading observational associations when selecting causal interventions, beyond its general effect on task performance?

The design contrasts situations in which observational association agrees or conflicts with the true intervention effect. The intended precision contrast compares the aligned-minus-conflicting accuracy gap between a quantized checkpoint and its higher-precision reference.

The broader commitment is to studying causal inference in language models. Quantization is an experimental factor rather than the entire scientific objective. Behavioral task scores do not by themselves identify internal causal representations or damaged neural mechanisms.

## 2. Literature and methodological foundations

The initial collection contains 14 papers from 2025–2026, with pinned versions, source records and critical summaries. It covers quantization and reasoning, causal benchmarks, shortcut-sensitive evaluation and interactive causal discovery. This is a targeted collection, not a systematic review.

Direct prior work already studies quantization and causal question answering. Paired causal questions and general answer-position bias also have precedents. Accordingly, neither “quantization affects reasoning” nor “order matters” is sufficient novelty by itself.

Methodologically, the project adapted agreement/conflict logic from process dissociation and a CNI-style processing-tree template to distinguish hypothesized causal sensitivity, association following and residual action preference. Synthetic validation examined 3,600 generated response datasets, parameter recovery, boundary behavior and misspecification. These simulations contained no LLM responses. They revealed weak boundary recovery and observational equivalence of alternative mechanisms, limiting latent-process interpretation.

The resulting contribution is presently experimental design and diagnostic interpretation, not a validated psychological decomposition of LLM reasoning.

## 3. Experimental progression

### Cohorts 001–007: feasibility, output compliance and numerical decisions

The initial 3B comparisons showed that output validity and baseline competence were major obstacles. F16 often produced fenced JSON and near-constant actions. Q2 outputs were length-capped and unusable under the tested settings. A repacking diagnostic did not restore usable output.

Formula-given controls separated reported numerical estimates from explicit action choices. In cohort 007, F16 obtained 46/48 correct estimate signs versus 31/48 for Q4, replicating an earlier numerical deficit. Explicit actions remained inconsistent with those estimates. Q8 performed more like F16 on the earlier numerical control.

These results support a numerical/execution difference under specific prompts; they do not isolate causal reasoning. A 7B reference screen also failed its competence threshold. Source-selection experiments exposed action bias and challenged the homogeneous processing-tree model.

### Cohorts 008–012: evidence order and matched-strength tasks

Source-order reversals revealed substantial sensitivity to presentation. The original cohort 008 F16 attempt was interrupted and preserved; completed replacement runs were kept distinct. Cohort 009 interleaved order conditions within a session, and cohort 010 replicated the F16 order effect on fresh families.

Cohort 011 matched observational signal magnitude across agreement/conflict conditions. Q4's apparently smaller conflict penalty coincided with a near-constant action policy, demonstrating why a smaller penalty need not imply better causal competence. Cohort 012's 7B reference again failed conflict-specific qualification.

An aggregation bug affecting reported cell counts in cohorts 009–011 was corrected and documented; family-level order effects were unaffected. Earlier reports were retained for provenance.

### Cohorts 013–017: response-contract refinement and a confirmed order effect

Prompt clarification initially caused explanatory continuations and invalid outputs. A stricter response contract restored validity, although competence remained weak. Cohort 015 produced a large exploratory Q4 order effect, motivating an independently frozen replication.

**Cohort 016 is the strongest confirmatory result:** on 96 fresh families, Q4 conflict accuracy was 91.1% with historical evidence first versus 28.6% with randomized evidence first. The family-level difference was **62.5 percentage points**, with a 95% t interval of **56.6–68.4 points**. The primary endpoint was this within-Q4 order effect. The 45.3-point Q4-minus-F16 order interaction was secondary and descriptive.

Large changes also occurred when both sources agreed, limiting a conflict-specific explanation. Cohort 017's 14B Q8/Q4 follow-up did not reproduce the large 7B conflict-order effect. It reused the same families and lacked an F16 arm. An analysis dependency failure was repaired locally without replacing model outputs.

### Cohorts 018–023: controls, component performance and attempted transfer

These studies examined evidence strength, semantic versus neutral response mappings, number reading, isolated randomized evidence, source identification, source guidance and matched noncausal controls.

Qwen repeatedly performed well on separate source-identification and isolated-decision tasks while performing poorly on two-source decisions. In cohort 021, source identification was 128/128, while ordinary and source-guided decisions were both 58/128. Guidance produced no aggregate rescue. Separate component requests cannot establish an internal mediation chain.

Cohort 022 introduced Mistral as an independent family, but its weak component performance prevented a clean replication of the proposed dissociation. Cohort 023 counterbalanced source identity and answer order: Qwen's isolated-versus-two-source gap persisted, but harmful-direction numerical and noncausal controls failed their frozen thresholds. This blocked a causal-specific interpretation.

### Cohort 024: three-family, seven-format matrix

The completed matrix comprised Qwen 7B, Mistral 7B and Llama 8B at seven formats: F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M, Q3_K_M and Q2_K.

All 21 arms completed: **30,912 scheduled attempts**, including **30,281 strict-valid responses**. These prompts came from eight independent SCM families; the response count must not be treated as the independent sample size.

Findings were heterogeneous. Mistral source selection followed the first displayed alternative. Qwen retained its component/action gap but failed relevant controls. Llama Q4 produced severe format-specific control-task truncation despite similar causal-item accuracy. No F16 reference passed all retrospective component/control diagnostics. Those diagnostics were not cohort-024 preregistered qualification gates.

The matrix did not establish a monotone precision trend or selective causal damage. It demonstrated the importance of preserving invalid outputs and reporting response policies alongside accuracy.

### Cohorts 025 and 025.1: retrospective archive investigation

Cohort 025 inventoried 24 prior cohort directories and 59 run files. The 58 successful runs contained 40,032 persisted attempts; the interrupted cohort 008 attempt was retained separately. Analyses examined option-reversal consistency, information dependence, item transitions, order interactions and limited guidance/strength probes.

Cohort 025.1 reproduced the archive analysis and assessed a cross-disciplinary investigation document. It separated analyses supported by existing logs from proposals requiring new data, including graph switches, richer psychophysics, factorial rescue and transportability.

Neither 025 nor 025.1 involved new model inference or independent replication. Their contribution is auditability and experimental prioritization, not a new causal-specific effect.

### Cohort 026: initial graph-switch assay

The new assay constructed observationally identical distributions compatible with different causal structures and opposite intervention answers. It included both answer polarities, graph-reading/arithmetic controls and an irrelevant-node no-change condition. Qwen and Llama F16 were tested on eight development families with one permitted wording revision.

An initial arithmetic-oracle/prompt error was repaired, with the invalidated run preserved. No final model/form passed qualification.

A subsequent review identified a further design confound: direct-form switch answers were always second, decision-form answers always first, and no-change pairs reversed answer order. Llama selected the first option on 61/64 final action prompts. Therefore the apparent form advantage and irrelevant-node failure did not isolate causal-structure use. The recorded failure remained valid, but substantive interpretation required correction.

### Cohort 027: corrected factorial design and bounded multi-model screen

Cohort 027 crossed graph, form and answer order explicitly, strengthened matched weighted-calculation controls and added shortcut-policy preflight checks. The proposed scope was five F16 references followed by validation and a conditional seven-format matrix.

Qwen 14B F16 was excluded before outcomes because the approximately 29.55 GB file could not satisfy the specified memory headroom on the 32 GB host. The four eligible models were Qwen 3B, Qwen 7B, Mistral 7B and Llama 8B.

**All four completed 224/224 development requests: 896 total, all strict-valid, with zero recorded infrastructure failures.** All four have completion events. Their saved analyses reproduce exactly and the fixture manifest verifies.

No model qualified on either form:

- Order-robust paired switch fidelity was **0/8 families in every model/form**.
- Ordinary switch accuracy ranged from **16/32 to 18/32**.
- Matched weighted-calculation accuracy ranged from **15/32 to 17/32**.
- Graph reading varied substantially; Llama's direct form reached **31/32**, without successful full-task performance.

The primary family endpoint requires correct answers for both graphs under both answer orders. Zero fidelity therefore does not mean every individual answer was wrong; it means no complete quartet passed.

The pipeline recorded **stopped_by_gate at 7:23 PM Pakistan time on 19 November**. Validation and quantization were not launched because their prerequisites failed. This was planned scientific stopping, not an archived inference crash. The records do not diagnose the separate reported lab-PC malfunction.

## 4. Achievements and unresolved claims

Completed assets include the SCM simulator, exact oracles, prompt generators, strict and disclosed sensitivity scorers, matched-family analyses, qualification gates, durable raw records, checkpoint provenance and reproducibility checks. Failed runs and analysis corrections are preserved.

The supported scientific findings are narrow: a confirmed order effect within one task/checkpoint configuration, replicated numerical deficits in an earlier control, and extensive evidence that presentation, action preference and task execution influence measured intervention accuracy.

The project has **not** established selective causal degradation under quantization, general preservation under compression, internal psychological/neural mechanisms, autonomous causal discovery, or a causal effect of model size alone. The potential methodological contribution—an independently validated separation of causal sensitivity from response policy and execution failure—remains incomplete.

## 5. Research direction and publication implications

The project shifted from measuring a presumed precision effect to determining whether the task can measure the intended capability. That shift was scientifically necessary: weak references and failed controls made the original contrast difficult to interpret. The main risk now is continued prompt iteration without a discriminating scientific endpoint.

Cohort 027 strengthens the case for stopping the present small-model bare-answer setup. Its calculation-control failures mean that poor main-task performance cannot be localized to causal reasoning. Additional quantization levels would not resolve this limitation.

A proposed next direction is a separately specified comparison of model-only and calculation-assisted systems. For example, the model could select the graph-dependent weighting rule while a deterministic calculator executes the arithmetic, with matched controls and full end-to-end scoring. This would study correct causal procedure selection under assistance, not claim unchanged unaided ability. It is a proposal, not completed work or an established novelty claim.

Before further large collection, agree on one manuscript-level claim, compare it explicitly with neighboring causal benchmarks, and test whether the new setup provides interpretable performance. Independent task/structure transfer and appropriately powered untouched-family confirmation would then be required. A negative or measurement-focused paper is possible, but accumulating failed pilots alone does not establish a strong journal contribution.

For the Q1 objective, current readiness is best described as **substantial exploratory research with a credible narrow replication and unresolved construct validity**. No acceptance likelihood or submission date is justified yet.

## 6. Decisions requested from the supervisor

1. Should the primary contribution focus on validated evaluation of causal decisions, with quantization secondary?
2. Is a calculation-assisted procedure-selection study the preferred next bounded experiment, or should the project move to an established causal benchmark first?
3. Which journal scope and institutional ranking system should guide the publication target?
4. Is additional memory/compute available if a higher-capacity F16 reference becomes scientifically justified?

## Evidence trail

- [Project overview](../README.md), [experiment index](../EXPERIMENTS.md), [methodology](RESEARCH_METHODOLOGY.md) and [adaptation](METHODOLOGY_ADAPTATION.md).
- [Synthetic validation](../results/design_validation/VALIDATION_REPORT.md).
- [Confirmed order replication](../experiments/cohort_016/summary.md) and [14B follow-up](../experiments/cohort_017/summary.md).
- [Measurement audit](../experiments/cohort_023/summary.md) and [precision matrix](../experiments/cohort_024/summary.md).
- [Archive screen](../experiments/cohort_025/summary.md) and [25.1 investigation](../experiments/cohort_025_1/summary.md).
- [Cohort 026 report](../experiments/cohort_026/development_summary.md), interpreted with the counterbalancing correction above.
- [Cohort 027 frozen execution plan](../experiments/cohort_027/plan.json), [inventory](../experiments/cohort_027/inventory.json), [preflight](../experiments/cohort_027/preflight.json), [run analyses](../experiments/cohort_027/runs/development/) and [terminal status](../experiments/cohort_027/pipeline_status.json).

Some overview/design documents retain historical prospective wording. For current execution status, use cohort-specific raw records, frozen plans and terminal status rather than those older statements. Counts across cohorts include reused worlds, prompt variants and revisions and should not be pooled as independent evidence.
