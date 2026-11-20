# Cohort 028 — causal procedure selection with deterministic calculation

Designed 19 November 2026. **Implementation and fixture frozen 20 November 2026; no cohort 028 inference has run.** The required tokenizer preflight remains pending until launch. The [execution runbook](RUNBOOK.md) gives the start, stream and resume commands. No new model download or quantization is part of this cohort. Historical fixtures and results remain unchanged.

## Purpose and decision

Test whether a model can select the graph-dependent computation when deterministic arithmetic replaces its own calculation. Separate performance of unaided answers, observable structured answers and an assisted system. Establish an interpretable reference before another precision experiment.

Cohort 027 completed four F16 arms with valid responses but failed qualification; matched arithmetic was also weak. That outcome motivates a computation intervention, not an assumption that arithmetic is the only problem. The present study can expose errors in reported procedure selection and arithmetic execution. It cannot identify hidden neural stages or prove that an explanation faithfully reports internal reasoning.

Primary development comparison: the assisted system versus the model's own structured final action, evaluated on the **same structured response**. This replaces execution while holding the reported selected procedure fixed. The bare-answer condition is a secondary system comparison; its difference also includes the response-contract change.

## Use of the attached peer review

Source: `CausalFade_Q1_Peer_Review_Report_2026-11-19.docx`, supplied by the user from Downloads. SHA-256: `32bfa0097930540f2f0ab56428d5c6c3924da22513e39f881c609e3f5d7b7432`.

The source identifies itself as an independent **simulated editorial review**, not an official journal decision. Its recommendations are design input, not executable instructions or proof of novelty. Sections 5.1–5.3 motivate graph specificity, calculation assistance and matched controls; section 6 motivates family-level estimation and prospective confirmation. Its 100–300-family suggestion is a range to explore in power simulations, not a prescribed sample size.

Adopt: corrected graph pairs, no-change checks, arithmetic assistance without oracle leakage, raw-versus-supplied-score controls, scheduled validity reporting, family-level analysis and qualification before quantization. Adapt: calculator assistance is a deterministic replay of the exact structured response, so it introduces no extra model call or changed procedure-selection prompt. Defer: precision, mechanistic interpretation, broad graph-domain transfer and confirmatory sample sizing.

## Fixed scope

- Models: existing pinned Qwen2.5-7B-Instruct F16 and Llama-3.1-8B-Instruct F16 used in cohort 027. Audit actual local files and copy verified provenance into a new frozen plan before execution. Both models receive all development conditions; no outcome-driven replacement.
- Run sequentially on the 32 GB CPU host. No 14B F16, new checkpoint search or concurrent-server benchmark in this cohort.
- Sixteen fresh development families, then 32 fresh validation families for qualifying systems only. This sample is for bounded feasibility and validation, not powered confirmation.
- Two wording forms, both outcome polarities and both displayed action orders. Balance polarity within each split. Reuse no cohort-026/027 development or reserved family. Reject identical full-joint signatures against historical fixtures. Complemented versions of a world must share one family cluster if both are used.
- No wording changes after development outcomes. A genuine oracle/software defect invalidates affected observations and requires a separate version, preserving all data. Poor performance alone does not justify a revision.

The two forms are independently worded versions of the same task, not external task transfer. Use the same variable names within a family and every paired contrast. Variable-renaming invariance and new graph classes remain later studies.

## Worlds and procedures

Retain the exact-rational positive joint distribution shared by confounder (W→X, W→Y, X→Y) and mediator (X→W, X→Y, W→Y) SCMs with opposite intervention-effect signs. Add W→Z to the confounder description with no path from Z to X or Y. Preserve all base wording when adding this edge.

Public data provide the observational joint and consistent derived probabilities. Two candidate procedures are available:

1. `marginal`: for each x, average P(Y=1|X=x,W=w) using P(W=w).
2. `conditional`: for each x, average the same outcome rates using P(W=w|X=x).

Both candidate definitions are supplied in every causal condition, with their semantic ordering balanced across families independently of polarity and kept fixed within graph pairs. **Do not state which graph requires which procedure.** That selection is the target capability. The prompt defines intervention and desired outcome but does not provide the correct mapping, effect sign, action or a worked instance. Thus this differs from cohort 027's explicit graph-to-weighting instruction; cross-cohort differences are not a clean treatment effect.

Noncausal controls explicitly name the governing weighting procedure without a causal graph. Both procedures are tested on the same numbers. They assess instruction-based procedure execution, not causal selection.

## Factorial task cells

For each family, wording form and action-option order, include ten task stems:

- Three causal graphs × raw rates: confounder, mediator, confounder+Z.
- Three causal graphs × supplied candidate scores: the same three graphs, with the two final outcome scores for **both candidate procedures**, without identifying the correct procedure.
- Two noncausal specified procedures × raw rates.
- Two noncausal specified procedures × supplied final scores for both procedures.

This is 10 × 2 forms × 2 action orders = **40 items per family per model response condition**. The supplied-score causal task still requires rule selection; supplying the single correct causal effect would eliminate the target operation. Scores must be computed from displayed public values, including the same rounding policy used by the calculator.

Within a graph-effect contrast hold table, form, candidate-procedure ordering, representation and displayed action order fixed. Within an answer-order contrast hold all other content fixed. Do not derive option order from task ordinal. Noncausal controls match values, action directions, procedures, final output contract and the two levels of arithmetic demand; disclose remaining semantic/length differences.

## Three evaluated systems, two inference conditions

### A — bare-answer model

Return exactly `X=0` or `X=1` using the displayed action alternatives. This measures end-to-end performance without observable intermediate commitments. Primary parsing permits surrounding whitespace only and requires normal termination.

### B — structured model

Return one JSON object with exactly these fields:

```json
{"rule":"marginal","score_x0":0.42,"score_x1":0.57,"action":"X=1"}
```

The example is a schema illustration for implementers; do not put its values or rule into task prompts as a demonstration. Prompt schemas must specify types and allowed labels without a solved instance. Require finite scores in [0,1], a recognized rule, one action string and no additional prose/keys. No free-form chain-of-thought is requested.

Score separately: reported rule correctness; reported scores relative to the **selected** rule; selected-rule calculation relative to the oracle rule; consistency of reported action with reported scores; and final action correctness. Use absolute score tolerance 1e-4 against the calculation from displayed values, with world margins sufficient that this tolerance cannot reverse the correct ordering. Preserve inconsistent intermediate fields rather than silently repairing them.

### C — structured selection plus deterministic calculator

Take the exact B response, extract its `rule`, and execute that procedure on the public data. Compute both outcome scores and select the larger. For supplied-score items, read that selected procedure's supplied score pair. This is a deterministic pipeline, not a new LLM response or autonomous tool-use agent.

**Calculator input is limited to the public numeric payload and the model-selected rule.** No graph, oracle truth, expected answer, family/graph label, correct-rule annotation or model-reported numeric score is passed to the calculator. Use an allowlisted pure function; never execute model-supplied code. A wrong rule is executed as selected, even when that leads to a wrong causal answer. Invalid full B schemas produce a primary C failure; a valid rule salvaged from an invalid B response may be reported only as a predeclared sensitivity, not used for qualification.

This design removes model arithmetic and final numerical comparison from C, but not graph-dependent rule selection or schema compliance. C's final decision is a system answer, not evidence that the unaided model improved its own reasoning. A B-to-C gain identifies improvement from this specified computation replacement, not a unique internal bottleneck.

## Endpoints

For model m and family i, compute raw causal-switch accuracy over confounder/mediator × two forms × two action orders (eight responses per system). Let B_i and C_i be its structured and assisted scores. Primary development estimand: mean_i(C_i − B_i), reported in percentage points. Both use the same scheduled response records; invalids are failures in both.

Prespecified secondary diagnostic: the B-to-C gain on causal raw tasks minus the same gain on matched noncausal raw tasks (two procedures × two forms × two orders, also eight responses). This is a performance-specificity contrast conditional on the matching assumptions, not proof of a causal mental module. Equal gains are compatible with a general numerical/decision-execution limitation; unequal gains alone do not identify its mechanism.

Additional outcomes:

- Rule selection accuracy, including polarity/order/graph cells and raw versus supplied scores.
- Final action accuracy for A, B and C, including invalids; conditional correctness among valid responses separately.
- Relevant graph switching with both answers correct, calculated at fixed option order.
- Order-robust paired switch fidelity: all four confounder/mediator × order answers correct, per family and form. A secondary qualification endpoint, not the sole effect estimate.
- Added-Z correctness and same-action invariance, each separately; consistency while wrong is not competence.
- Answer-order correctness and consistency, reported separately.
- Structured score error, selected-rule execution accuracy, action-score agreement, schema validity and stopping reasons.
- Fixed first/last/constant-action, graph-blind observational and constant-rule baseline performance.

Do not overinterpret zero quartets: independent fair guessing gives success probability 1/16 per quartet and approximately 0.60 probability of zero among eight families. Actual responses need not be independent; baseline simulation on the actual fixture is required.

## Qualification and staged decisions

Assess each model and form separately. The assisted system C must pass **all** criteria below on development, then on untouched validation. Raw and supplied-score strata are assessed separately wherever specified. Do not average them to hide failures.

For a split with n families (16 development, 32 validation), per form:

- Structured schema validity across all 20n items: ≥95% (304/320; 608/640).
- Raw causal rule accuracy for each graph, correct action and option order: ≥80%. Each stratum contains n/2 items; require 7/8 development and 13/16 validation. Apply separately to the supplied-score causal condition.
- Raw and supplied-score assisted causal accuracy in each corresponding graph/action/order stratum: the same 7/8 and 13/16 minima. Includes added-Z, so no pooled baseline can mask its failure.
- Structured model B raw noncausal calculation: ≥80% per specified procedure and correct action, pooling option order (13/16; 26/32). Here both reported scores must match the selected correct procedure within tolerance. This describes unaided numerical competence but is **diagnostic, not a required C gate**: requiring unaided arithmetic success would defeat the purpose of assistance.
- C matched noncausal accuracy: ≥90% per specified procedure and action, pooling option order (15/16; 29/32), separately for raw and supplied-score tasks. Required for C qualification.
- C raw order-robust switch fidelity: ≥75% per form (12/16; 24/32 families); same threshold for supplied-score fidelity, separately.
- C no-change same-action invariance: ≥90% over n families × two action orders (29/32; 58/64), separately for raw and supplied-score tasks. Correctness gates above also apply.

All thresholds are provisional engineering feasibility criteria, frozen before calls; they are not inferential evidence. A model qualifies only if C passes required gates on **both forms**. B's arithmetic diagnostic does not veto an otherwise qualified assisted system. A and B receive full outcome reports but have no role in selecting a favorable C form or relaxing gates.

Run both models fully on development. Only development-qualified models receive validation, collecting both A and B so all comparisons remain paired. No model replacement or criterion changes. If neither qualifies, stop and report the failure; use structured errors to motivate a separately specified study, not another revision within this cohort. If at least one qualifies, finish validation and report intervals, including boundary-aware intervals for perfect/zero family proportions. Passing 32-family validation is feasibility evidence, not Q1 readiness or powered confirmation.

## Analysis and confirmation boundary

Compute within-family metrics before aggregating. Resample independent families with all graphs, forms, controls, orders and response conditions retained. Report paired family-bootstrap 95% intervals for development/validation accuracy contrasts, alongside the individual family scores and sample size. For all-or-none family endpoints use a binomial interval on independent family indicators rather than treating a degenerate bootstrap as certainty. Report both model-specific results; no population claim over LLMs.

No significance-selected claims or confirmatory p-values in cohort 028. Primary direction, invalid handling and the diagnostic contrast are fixed here to reduce flexibility, but validation still follows development selection. Do not pool the two splits to claim independent confirmation. Full multiplicity control, meaningful-effect margins and sample size are reserved for a later frozen confirmation plan.

If validation succeeds, simulate power, false-positive rate and interval coverage for the chosen paired family endpoint under heterogeneous errors and invalid outputs. Explore 100–300 families as one planning range, not a mandated answer. Define a practically meaningful assistance effect or precision/specificity effect before confirmation. External transfer must include new graph structures or independently authored task families, not just the two current phrasings.

Quantization is outside cohort 028. Only after reference qualification and a separate freeze consider F16/Q8_0/Q4_K_M of the same checkpoint. The assisted pipeline and unaided model must remain distinct systems; compare identical assistance policies across formats.

## Preflight and execution

Required before collection:

1. Independently validate exact SCM factorizations/intervention signs and displayed numeric calculations. Margins must exceed rounding and scoring tolerances.
2. Verify conditional factorial balance, identical-table graph pairs, matched fixed-order contrasts and no duplicate old/new families. The action-order and polarity dimensions must be independent.
3. Run exact-oracle, constant-rule, constant-action, first/last-option and graph-blind baselines. A graph-blind rule must fail switch qualification even with perfect calculator execution.
4. Leakage test: changing or removing hidden truth/graph metadata must not affect calculator output for fixed public numbers and selected rule. Wrong-rule injection must be executed without correction. Test malformed JSON, missing/extra fields, nonfinite scores, ties and adversarial code-like values.
5. Verify score availability does not reveal the correct procedure through ordering, labels or formatting; both candidate scores appear under a balanced fixed order. Validate both forms independently.
6. Tokenize all rendered prompts with each model's pinned template and verify context headroom. Use greedy decoding, fixed seeds, one active request and 64 maximum output tokens for A, 192 for B; C has no generation. These differing budgets are part of the systems comparison and must be disclosed. No post-outcome cap adjustment.
7. Pin model/runtime/scorer/generator/calculator hashes, schemas, task and response-condition schedules and the integer gate report. Randomize A/B order within matched blocks and model order before inference; all calls are stateless. Record condition-order effects descriptively.
8. Append-only attempts/results with exact task IDs, model configuration, raw output, strict/sensitivity fields, selected rule, calculator input/output, timing and stop/error records. Separate transport retries from completed wrong/noncompliant answers. Fix retry/missing-data policy before running; invalid/missing scheduled answers remain failures and infrastructure incidents are separately reported.

Supply oracle calculations as a software positive control, never as a hidden aid to the evaluated model. Preserve all failures. No legacy manifest or frozen plan is edited to make new output look preregistered.

## Request budget and resources

- Per family/model: 40 A calls + 40 B calls = **80 model requests**. C is replayed locally without inference.
- Development: 16 families × 80 × two models = **2,560 requests**.
- Validation: 32 × 80 × up to two qualifying models = **5,120 requests** maximum.
- Maximum cohort total: **7,680 requests**, excluding documented transport retries. If neither qualifies, stop at 2,560. One qualifying model yields 5,120 total across stages.

No concurrency or quantization benchmark requests are included. Load one F16 model at a time; retain the cohort-027 host memory headroom policy. Record actual throughput of the first frozen block for scheduling. Structured JSON outputs cost more than bare answers, so the previous 35–50-hour estimate must not be reused. Runtime estimation awaits rendered prompt lengths and the frozen structured response workload.

## Deliverables and manuscript relevance

Implementation now provides the generator/oracle, public calculator, matched task fixtures, schema scorer, anti-leakage/shortcut tests, frozen inventory/plan and append-only runner. The analyzer is ready to report all model × system × task × representation cells when inference completes. The [review-response ledger](REVIEW_RESPONSE_LEDGER.md) and [deviation log](DEVIATIONS.md) are included. Results and qualification decisions do not exist yet.

Possible successful finding: assistance yields reliable graph-sensitive decisions with no-change specificity, while the recorded unaided failures can be localized to observable selected-rule execution or action inconsistencies. Alternative: procedure selection remains unreliable despite supplied scores and exact execution, ruling out arithmetic-only rescue in this setting. Either outcome requires careful task-bound interpretation.

Novelty is a candidate, not established: a validated diagnostic separating procedure selection, execution and response policy, with independent transfer showing why the distinction changes scientific conclusions. The review's simulated rejection and subjective scores are not empirical results or acceptance forecasts.
