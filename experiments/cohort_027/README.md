# Cohort 027 — graph-sensitive decisions across size and precision

Designed 19 November 2026. **Status: protocol specification, not execution-ready or frozen. No inference authorized or performed by this design task.** Exact prompts, fixture/code hashes, checkpoint availability, runtime settings and simulation results must be completed before their applicable collection stage. Historical cohorts remain unchanged.

## Objective and claim boundary

Determine whether intervention decisions respond correctly to supplied causal structure independently of answer position, and then describe how this behavior changes across matched precision variants of qualified checkpoints.

This is a staged development/validation study with a descriptive precision matrix. It is not a confirmatory test of selective causal degradation. A future confirmatory claim requires an independently frozen, powered protocol and untouched families. Model size comparisons are comparisons of trained checkpoints, not isolated causal effects of parameter count. Three model families do not constitute a random sample of all LLMs.

Cohort 026's generator coupled correct option position to task form. In the final development fixture all direct switch answers were second and all decision switch answers first. Its no-change pairs also reversed option order. Cohort 027 must correct these defects structurally, not just shuffle execution order. Retain cohort 026's recorded qualification failure, but do not interpret its form or added-node contrast as an isolated graph effect.

## Model and format scope

Candidate checkpoints, fixed before screening:

- Qwen2.5-3B-Instruct.
- Qwen2.5-7B-Instruct.
- Qwen2.5-14B-Instruct.
- Mistral-7B-Instruct-v0.3.
- Llama-3.1-8B-Instruct.

Use each checkpoint's F16 GGUF reference. Q8 is not a substitute for an unavailable F16 reference. Before any response collection, audit local assets and record available/infeasible status for all five, source revision, license, weight hashes, tokenizer/chat template, conversion command and conversion limitations. Historical paths are evidence of provenance, not proof of current availability. A resource-infeasible checkpoint may be omitted before outcomes with a reason; do not replace it after seeing performance. Cross-family scope requires both non-Qwen candidates where feasible; otherwise narrow the resulting claim.

Precision set: **F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M, Q3_K_M, Q2_K**. This is the seven-format ladder used in cohort 024, not literally every GGUF encoding. Q1 and alternate K/S, IQ or other quantizer families are excluded from this protocol. Any extension needs a pre-outcome amendment with its own budget and provenance.

Produce all six quantized variants from the same pinned F16 source per checkpoint, with one pinned quantizer build and documented commands/calibration policy. Do not mix independently downloaded conversions as if they differed only in precision. Record actual bytes and tensor types; format names are categorical treatments, not equally spaced numeric doses. Existing assets can be reused only when their provenance satisfies this requirement.

## Stage A — design validation, no model calls

Create fresh exact-rational SCM families with a common observational P(W,X,Y) compatible with both:

- Confounder: W→X, W→Y, X→Y.
- Mediator: X→W, X→Y, W→Y.

Require strictly opposite, nontrivial intervention-effect signs with positivity. An added W→Z child with no path to X or Y preserves the confounder intervention answer. Supply the identifying graph explicitly; do not penalize a model for inferring a graph from an observationally unidentified distribution.

Use eight fresh development families and sixteen fresh validation families, balanced in outcome-complement polarity within each split. Draw new seeds and compare full-joint signatures against prior cohorts and across splits to reject accidental reuse. Complementary versions of the same numeric world are dependent and must share a family identifier if both are used. Do not use cohort 026's reserved families. A future confirmation sample size and seed namespace remain undecided until power simulation.

Two forms: direct intervention comparison and decision framing. Both supply the same graph-dependent weighting rule, tables and answer contract; change only the defined question framing. The measured construct is **assisted graph-conditioned computation**, not autonomous causal discovery. These are wording forms of one mathematical task, not independent graph-domain transfer.

### Exact factorial fixture

For every family and form:

1. Main decisions: three graphs (confounder, mediator, confounder+Z) × two displayed option orders = six prompts.
2. Graph reading: confounder/mediator × two upstream/downstream option orders = four prompts.
3. Matched arithmetic: two explicit weighting rules × two action-option orders = four prompts.

Total: **14 prompts per form, 28 per family, 224 per development arm, 448 per validation arm**. The arithmetic tasks give the weights and outcome rates needed for both X settings, and ask which weighted outcome is larger without requiring graph interpretation. They must perform the same two weighted averages and comparison as the main task. Their numerical pair has opposite answers under the two rules. Controls test execution, not an identified internal stage.

Within the added-node pair preserve the entire base description, including W's temporal relation to X; append only the irrelevant child statement. Hold table, form, answer contract and option order fixed when comparing graphs. Estimate option-order changes separately within each graph. Reuse the confounder response as the baseline for switch and no-change comparisons rather than duplicating identical requests.

Freeze complete rendered prompt examples and audit all conditional balance tables before inference. The specification is not frozen merely because this README exists.

### Mandatory preflight tests

- Exact oracle: normalized positive joint distribution, both graph factorizations reconstruct it, correct interventional calculations and unchanged effect after adding Z.
- Independent numerical oracle from displayed rounded joint/derived rates agrees in sign and answer; reject contradictory displays or near-ties.
- Every family/form/graph appears under both answer orders. Correct-position counts balance within form, graph and polarity; graph contrasts match at fixed answer order.
- Control labels, rule, polarity and answer order have the declared denominators. No option assignment depends on task ordinal.
- No repeated world signatures across old, development and validation sets; controls linked to their parent family.
- Oracle responder passes every gate. Always-first, always-last, constant-X=0, constant-X=1 and graph-blind observational responders fail causal qualification. Each order-robust switch score must be zero for those shortcut responders.
- Scorer tests cover whitespace, punctuation, multiple tokens, truncated answers, refusals and missing responses. Audit metrics must distinguish validity from correctness.
- Manifest binds prompts, oracle, worlds, schedule, scorer, generator and plan; runner verifies each actual file digest, not just the manifest digest. Save preflight output.

## Stage B — higher-precision qualification

Run all available fixed F16 references on the same 224 development prompts. No model replacement, outcome-driven prompt revision or selective item deletion is allowed. A genuine fixture/oracle error invalidates the affected stage; preserve its data and issue a separately versioned repair before any further collection. Scientific failure is not an implementation error.

Assess every form separately. A checkpoint must pass all gates on **both forms**. Only development-qualified checkpoints receive the sixteen-family validation block. Apply the same fractional gates, rounded upward to integer counts, on validation. A validation failure stops that checkpoint's quantization expansion; do not revise using validation outcomes. If none qualify, stop cohort 027 and report the failure.

### Qualification counts per form

| Gate | Eight-family development | Sixteen-family validation |
|---|---:|---:|
| Strict validity, all scheduled prompts | ≥107/112 | ≥213/224 |
| Graph-reading accuracy, overall | ≥26/32 | ≥52/64 |
| Graph-reading accuracy, each correct label | ≥13/16 | ≥26/32 |
| Matched arithmetic accuracy, overall | ≥26/32 | ≥52/64 |
| Matched arithmetic accuracy, each correct action | ≥13/16 | ≥26/32 |
| Switch accuracy, each correct action × option order | ≥6/8 | ≥12/16 |
| Added-Z correctness, overall | ≥13/16 | ≥26/32 |
| Added-Z correctness, each correct action | ≥7/8 | ≥13/16 |
| Order-robust paired switch fidelity | ≥6/8 families | ≥12/16 families |

These are feasibility thresholds, not significance tests or guarantees of competence outside this task population. The added-Z gate is calculated on the variant alone; good baseline responses cannot mask failure on that variant. Report baseline correctness and no-change consistency separately. Family-level fidelity requires **all four confounder/mediator × order responses correct**. Invalid or missing responses are wrong. Both forms are required for expansion; a favorable form alone is not eligible.

## Stage C — complete descriptive precision ladder

For every checkpoint passing both development and validation, run all six quantized variants on the original 224 development prompts. Finish all six despite poor output quality; stop only for documented infrastructure/resource failure. Do not promote selected levels or pool failed formats away. Qualification uses F16 only; quantized controls can fail and those failures are outcomes, not grounds for dropping an arm.

Stage C estimates exploratory within-checkpoint differences on screened development tasks. It does not repurpose the validation set as a repeatedly inspected quantization benchmark. Qualification may select unusually favorable references, so these precision estimates must be confirmed independently before general claims. A failed F16 checkpoint is retained in the F16 report but not expanded under this protocol; expanding failures for descriptive purposes requires a separately declared objective.

## Execution and scoring policy

Stateless requests, no conversation history or examples derived from prior outputs. Use fixed greedy decoding, a common seed, batch/concurrency and cache settings; pin and record each checkpoint's correct chat template. Proposal: 64 output tokens and context capacity sufficient for every rendered request plus output margin. Freeze exact settings after tokenizer-based preflight, not after model outcomes. Provide an unambiguous bare-token instruction; X=1 is a response string, not necessarily one tokenizer token.

Primary decoder: strip surrounding whitespace only; exact allowed answer and normal stop required. No fence removal, prefix extraction or punctuation repair in primary scoring. Prespecify a secondary exact-answer-plus-single-terminal-period sensitivity, never used for qualification. Preserve raw text, finish reason, token counts, elapsed time, errors and strict/sensitivity answers.

Randomize prompt schedule within each arm; use the same frozen schedule for paired formats. Randomize model order within each stage and precision-arm order before stage C. Log environment and timestamps. Keep complete attempts append-only; define resume keys and transport-retry rules before execution. Never retry a validly completed wrong/noncompliant answer to improve its score. Record resource failures distinctly; do not silently replace them with capability failures. Primary scheduled denominators retain unresolved missing attempts as failures with a separately reported infrastructure count.

### CPU concurrency and memory policy — 19 November amendment

The planned host has 32 GB RAM. RAM fit alone does not establish a throughput benefit: simultaneous servers share CPU cores and memory bandwidth. **Run stage-B F16 screening and validation sequentially.** Verify 14B F16 memory feasibility independently; never substitute Q8 for its reference.

Stage C may use **at most two model servers concurrently**, with one active request per server, only after the bounded benchmark below qualifies the actual pairing/configuration. Otherwise use sequential execution. Split a fixed host CPU-thread budget between concurrent servers, including prompt/batch thread settings; do not give each server the full sequential thread allocation. Inventory physical cores and record the thread allocation before benchmarking. Three-or-more-server execution is outside this protocol.

Target 24–26 GB combined resident inference-process memory and enforce a **28 GB upper guard**, including weights, KV caches, compute buffers and loading overhead. Record memory units explicitly and also monitor host available memory: retain at least 4 GB available to the OS and other processes. Both guards apply, including while loading the second model. Use measured process-group residency and host memory pressure, not summed GGUF file sizes or virtual address space. Do not double-count shared mapped pages when suitable proportional-memory accounting is available. Sustained inference-related swap-in/out, out-of-memory events or a memory guard breach disqualify concurrent operation. Existing inactive swap allocation alone is not evidence of active swapping.

#### Bounded throughput benchmark

Use a separately archived set of 16 non-study prompts per model, matched approximately to cohort-027 input lengths and the frozen 64-token output cap. No development, validation, reserved-family prompts or their answers may be used. This benchmark measures execution behavior, not scientific qualification.

For each proposed concurrent pair, compare two repetitions of: (a) both 16-prompt workloads executed sequentially with the full fixed thread budget; (b) those identical workloads executed concurrently with split threads. Counterbalance condition order across repetitions. This is **128 requests per candidate pair**. Preselect at most three representative pairs from the verified inventory, covering the intended small, medium and largest concurrent memory classes; maximum **384 additional benchmark requests**. Select pairs by resource footprint before performance outcomes. Untested pairings run sequentially. No open-ended configuration search is permitted.

Record end-to-end time to complete both workloads, including loading, separately from request-serving time; combined completed requests/second; peak process-group and host RAM; swap activity; per-model prompt/output tokens; thread settings; errors; finish reasons and output text. Select concurrency only when both repetitions complete without infrastructure failures or memory violations and their mean combined completion time is at least **10% shorter** than sequential execution. This is an operational benefit threshold, not statistical evidence of general acceleration.

Compare decoded answers, validity and stop outcomes for identical benchmark prompts across execution conditions. Any disagreement disqualifies that concurrent configuration pending a separate investigation; do not assume thread changes preserve output. Passing this small check does not prove identical behavior on all study prompts. Keep execution mode and thread allocations explicit in every scientific arm and qualify precision interpretations accordingly.

Freeze benchmark report, eligible pairings, allocations and deterministic scheduling/fallback rules before scientific collection. Randomize stage-C arm order as above, pairing eligible arms without changing their within-arm schedules. Each arm has a fixed declared configuration. If resources subsequently violate a guard, stop dispatching new requests, preserve all attempts and log the incident. A predeclared sequential fallback may resume unfinished requests, with the configuration transition recorded; do not replace completed outputs. Report mixed-mode arms explicitly rather than treating timings as homogeneous.

Concurrent latency is not an isolated model-efficiency measurement. Do not compare it directly with sequential F16 latency as a speedup attributable to quantization. Use isolated measurements for any efficiency claim.

## Endpoints and analysis

Primary development metric: family/form order-robust paired switch fidelity. For each checkpoint report both forms and their equally weighted mean; average within family before uncertainty estimation.

Primary descriptive precision contrast: Q4_K_M minus F16 in this metric. Other five F16 contrasts are secondary descriptive results. Also report ordinary switch accuracy, per-polarity/graph/order cells, added-Z accuracy, answer-order invariance, no-change invariance, matched arithmetic, graph reading, validity, first-option agreement, constant-action agreement and item transitions.

Distinguish correct directed graph changes from mere answer flipping. Report first/last/constant and graph-blind baselines beside scores. A simple causal-minus-control accuracy interaction is descriptive because control matching is imperfect and fidelity differs from single-item accuracy. No neural, mediation or latent-route claims follow.

All resampling is paired at the independent-family level, retaining forms, controls and option orders together. With eight development families, show the actual family scores and emphasize limited precision; do not treat hundreds of prompts as independent worlds. Any bootstrap intervals are exploratory and not multiplicity-adjusted. No confirmatory p-values or selected-significance claims. No inference of equivalence from a null estimate and no monotone bit-width trend assumption.

Before future confirmation, simulate the actual family endpoint, expected discordance, false-positive rate, coverage and power for a prespecified practical effect. A provisional planning target is detecting a ten-percentage-point Q4 fidelity loss at 90% power; this is not an established meaningful-effect threshold or a power result. Freeze the justified margin, sample size, multiplicity control across checkpoint contrasts and stopping rule before generating/querying confirmation families. For selective degradation, independently define and power a matched-control estimand rather than claiming it from the fidelity effect alone.

## Budget and stop decisions

- All five development F16 references: 5 × 224 = **1,120 requests**.
- Maximum validation: 5 × 448 = **2,240 requests**.
- Maximum precision expansion: 5 × 6 × 224 = **6,720 requests**.
- Maximum scientific total: **10,080 requests**, excluding documented transport retries and preflight tokenization (no inference). If none passes development: 1,120 scientific requests maximum. If fewer checkpoints are available or qualify, reduce the budget by the formula; never fill vacancies with post-outcome selections.
- Optional execution benchmark: at most **384 non-study requests**, separately archived and excluded from every scientific denominator. Maximum scientific plus benchmark budget: **10,464 requests**, excluding documented transport retries. No benchmark requests are required if sequential execution is retained.

Use existing logs only for a rough resource estimate. Record observed throughput after the first frozen arm for scheduling, without changing prompts or scientific inclusion. No wall-clock promise is made, particularly for 14B F16. Insufficient hardware means an incomplete declared arm, not a Q8 reference substitution.

Current sequential planning allowance is approximately **35–50 continuous inference hours** if all five checkpoints qualify: about 6–8 hours development, 12–16 hours validation and 16–24 hours precision expansion. These rounded ranges are extrapolated from earlier cohorts; cohort-027 prompts are not yet rendered and 14B F16 has no comparable timing measurement. Model preparation, benchmark calls, loading and interruptions add time. Do not reduce this allowance for concurrency until the paired benchmark measures a net benefit. Re-estimate using actual prompt lengths and recorded serving throughput without changing scientific inclusion rules.

Decision: qualification plus interpretable precision effects warrants independent confirmation. Qualified references with negligible precision changes warrant a separately powered preservation question if scientifically useful. Failure across references closes this setup and motivates an explicitly different assisted interface or established task, not another unbounded prompt search. A broad publication claim still requires transfer beyond these two wording forms and this graph pair.

## Required outputs before collection

1. Generator, independently checked oracle and shortcut tests.
2. Exact prompts, separate development/validation fixture access, manifest and balance report.
3. Actual model/runtime/quantizer inventory with hashes and resource feasibility; optional bounded concurrency benchmark report and frozen pair/thread/memory/fallback policy.
4. Executable analyzer and integer gate tests, append-only runner and retry policy.
5. Frozen stage-B plan and source commit/hash record, followed by all F16 gate reports.
6. Frozen eligible stage-C arm list and schedule; complete matrix including failures.

This file is the design deliverable. These implementation artifacts do not yet exist for cohort 027, so the cohort must not be described as execution-ready.
