# Publication readiness assessment — 15 November 2026

**Verdict: a substantial research prototype with credible narrow findings, but not yet a submission-ready AAAI main-track or strong general-AI journal paper.** The remaining work is primarily scientific validation and generalization, followed by manuscript construction. A reasonable planning allowance is **3–6 months of focused work** for a competitive submission candidate, conditional on early validation succeeding. This is an expert planning judgment, not an acceptance probability or a promise of publication.

## Scope and verification

This assessment examined the project overview and methodology, experiment index, all 21 cohort summaries, key frozen plans, analysis and generation code, synthetic-validation report, selected raw records, and current primary-source literature and venue guidance. No standalone submission manuscript was found in the repository inventory. Accordingly, this assesses the research package, not an unseen paper's writing quality. This is not a line-by-line audit of every artifact or an independent reproduction of the downloaded literature.

Local checks performed:

- `py -m unittest discover -s tests -q`: **53 tests passed**, in 29.07 seconds, Python 3.13 / NumPy 2.3.5.
- Inventory: **35 run directories with results**, 7,136 scored rows and 7,098 raw JSONL records. These are storage counts, not independent observations. They include reused families and an interrupted attempt.
- The row-count discrepancy is the documented interrupted cohort 008 run: 64 scheduled/scored rows versus 26 raw records. Do not pool it with the completed replacement as independent evidence.
- Independently decoded cohort 016 raw JSON, scored against oracle actions, checked agreement with stored correctness, and recomputed family contrasts: F16 +0.171875; Q4_K_M +0.625. The Q4 family standard error was 0.0296174, consistent with the reported interval.
- Independently decoded cohort 021 raw JSON against its truth: governing-source selection 128/128; direct identification 32/32; randomized-only action 30/32; ordinary 58/128; guided 58/128; neutral guidance 56/128.
- No new model inference, model downloads, historical rescoring changes or experiment modifications were performed. Passing software tests does not establish construct validity.

## Venue clarification and timing

AAAI is a selective **conference**, not a Q1 journal. Its criteria explicitly permit empirical and critical contributions, so a new training algorithm is not required. What matters is a substantive, novel, sound and clearly presented contribution of interest to the AI community. [Official AAAI-27 main-track call](https://aaai.org/conference/aaai/aaai-27/main-technical-track-call/).

As of this assessment date, the AAAI-27 main-track deadline has passed: abstracts were due 21 July 2026 and papers 28 July 2026. Its instructions specify seven content pages, separate reproducibility material and anonymous review. Do not plan around an unverified future AAAI deadline. [Official submission instructions](https://aaai.org/conference/aaai/aaai-27/submission-instructions/).

For a journal route, **Journal of Artificial Intelligence Research (JAIR)** is a plausible ambitious target if the work develops a broadly useful evaluation insight. Its own guidelines require important new methods, results or insights, appropriate supporting evidence, and a contribution beyond a narrow incremental application. It is not an easier substitute for a conference rejection. [JAIR guidelines](https://www.jair.org/index.php/jair/about/submissions).

Quartiles must be named by database, category and year. SCImago lists JAIR as **Q1 in Artificial Intelligence for 2025**; this is not a claim about its Clarivate JCR quartile or your institution's eligibility rules. [SCImago journal record](https://www.scimagojr.com/journalsearch.php?clean=0&q=24330&tip=sid). Resolve the required ranking system before selecting a journal solely to satisfy “Q1.”

## What is already worth preserving

**The research engineering is well developed.** The SCM gives exact ground truth; paired worlds, mathematical validators, archived outputs, hashes, schedules and family-level analyses provide a useful foundation. Failed gates and repaired analyses are disclosed rather than hidden. These features materially reduce the work needed for a defensible release.

**There is a large prospectively replicated behavioral result.** In [cohort 016](../experiments/cohort_016/summary.md), Qwen2.5-7B Q4_K_M conflict accuracy was 175/192 with historical evidence first versus 55/192 with randomized evidence first. The family-level difference was **+62.5 percentage points**, 95% interval **+56.6 to +68.4**, across 96 fresh families. This is a strong result for that checkpoint, interface and generator.

**The negative and diagnostic results constrain explanations.** Cohort 017 does not reproduce the large 7B conflict-order effect at 14B. Cohorts 018–019 show related problems in noncausal controls and output mappings. Cohorts 020–021 distinguish reasonably strong isolated skills from much worse two-source action choices. In cohort 021, perfect governing-source selection coexists with only **45.3% ordinary action accuracy**, despite **93.8% randomized-only accuracy**. These are separate fresh-context tasks, so the dissociation is behavioral evidence, not a trace of internal computation.

**An earlier precision effect also exists, with narrower meaning.** Cohort 007 reproduces a 3B estimate-sign gap: F16 46/48 versus Q4_K_M 31/48 under the supplied arithmetic rule. The deficit is not confined to conflicts, and explicit actions often contradict estimate signs. Preserve it as execution/interface evidence rather than promoting it to selective causal degradation.

## Likely acceptance blockers

### 1. The original claim is not the confirmed claim

The motivating hypothesis concerns increased causal-conflict vulnerability under quantization. Cohort 016's frozen primary endpoint is **the order effect within Q4_K_M**, not the precision-by-conflict interaction. Its secondary Q4-minus-F16 conflict-order interaction is +45.3 points, but the F16 reference also changes with order and aligned trials change dramatically. A very small p-value for the primary cannot substitute for testing the intended substantive claim.

The large observed effect does not require more families merely to become more significant. It requires explanation, scope and independent replication. In fact, Q4 conflict accuracy averaged over order exceeds F16 here, which makes a simple “compression damages causal accuracy” story particularly misleading.

### 2. Measurement validity is unresolved

Full-precision failure does not invalidate a paper about model failures; it does undermine interpreting a precision difference as loss of an already demonstrated causal capability. Cohort 015's overall F16 gate passed by only one response (89 versus 88 required), and that gate passage did not establish reliable competence in later conditions.

Action biases can reduce a conflict penalty without improving causal reasoning. Aligned-item errors, where both sources imply the same action, are especially damaging to a pure misleading-association explanation. Cohort 019's mapping effect appears in causal and noncausal tasks. Cohort 021 guidance changes activation propensity without improving overall accuracy. The paper must explicitly distinguish validity, semantic correctness, action bias, numeric execution and causal-source use.

### 3. The evidence is narrow across models and tasks

Three sizes of Qwen2.5 are one model lineage. Cohort 017 compares Q8_0 with Q4_K_M; Q8 is not an unquantized reference, and reused families do not supply fresh task replication. More seeds from the same SCM template demonstrate within-generator stability, not transfer across domains, causal structures or model families.

My recommended minimum for a reasonably broad empirical claim is two independent model families with matched higher-precision and quantized variants, plus held-out task forms. Three families would make a broad journal argument more convincing if affordable. These are study-design recommendations, not formal venue quotas. Carefully delimited single-family work remains possible if the scientific insight is sufficiently strong.

### 4. Novelty must be sharper than “quantization affects causal reasoning”

That topic already has direct prior work. [Compressed Causal Reasoning](https://arxiv.org/abs/2512.13725) evaluates Llama 3 8B across precision settings using CLadder and CRASS and reports mostly preserved aggregate performance with more sensitive interventional categories. CausalFade could add controlled counterbalancing, behavioral failure decomposition and evidence that aggregate metrics obscure important instabilities; it cannot claim to originate the topic.

[CausalFlip](https://arxiv.org/abs/2602.20094) already targets semantic shortcuts using opposing causal answers. [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) already demonstrates position sensitivity in other tasks; its setting differs from these short causal decisions, but “order matters” alone is insufficient novelty. [How Quantization Shapes Bias](https://aclanthology.org/2026.eacl-long.17/) supplies broader multi-model, multi-benchmark evidence that compression changes behavior in setting-dependent ways; its social-bias construct differs from action propensity here.

For an agentic extension, [ACED-Bench](https://arxiv.org/abs/2610.14381) already evaluates acquisition and use of causal evidence with formal ground truth. [Precision Upgrades in Closed-Loop Agents](https://arxiv.org/abs/2610.24346) explicitly separates precision interventions and compares same-precision alternatives. Adding tool calls alone would not settle novelty. These arXiv records are research precedents, not assumed peer-reviewed acceptances.

### 5. The psychological interpretation is ahead of its validation

Synthetic parameter recovery checks implementation under assumed generators. It does not show that an LLM follows the C/A/B tree. Your own validation demonstrates an observationally equivalent alternative and weak boundary recovery; cohort 005 also challenges the homogeneous tree restriction. Two strengths and saturated responses do not justify a robust psychophysical curve or an identified internal mechanism.

Keep these methods only if they discriminate competing behavioral explanations on held-out data. A simpler, validated response model is stronger than an elaborate but unidentified psychological narrative.

### 6. A submission package still needs to be built

The repository contains research plans and cohort reports, but no standalone manuscript was identified. Some overview documents still say cohort 018 has not run, while the experiment index reaches 021. A reviewer needs one current account, regenerated figures and a compact mapping from each claim to data, analysis and limitations. Historical frozen protocols should remain unchanged; update current status summaries separately.

## Recommended scientific direction

**Lead with the reliability of intervention decisions under presentation and precision changes.** A possible working question is:

> When an LLM can identify the appropriate causal evidence, what prevents it from using that evidence to choose an intervention, and how does quantization change that behavior?

This keeps causal inference central while allowing the data to decide whether precision affects discrimination, action propensity, evidence integration or interface sensitivity. A possible future title is *Selecting Causal Evidence Is Not Enough: Presentation and Precision in LLM Intervention Decisions*. This is a proposed framing, not an established general finding.

There are two viable branches:

- **Precision/sensitivity paper:** proceed if a reference is competent across relevant conditions, and a fresh paired experiment isolates a meaningful precision effect beyond controls.
- **Evaluation/failure-mode paper:** proceed if source/action dissociation and presentation-linked action shifts generalize, even if quantization is secondary or heterogeneous. Demonstrate why common accuracy/conflict metrics mislead and validate an improved evaluation protocol.

Do not force the original directional hypothesis to be true. A rigorous boundary result can be publishable, but merely failing to reject a degradation effect does not establish preservation; that requires a prespecified practical margin and adequate precision.

## Work plan and decision gates

### First 1–2 weeks: decide whether the phenomenon survives outside the current setup

1. Write a one-page claim/evidence/limitation outline now. Separate cohort 016 confirmation from all later development claims.
2. Run one independent checkpoint family on fresh matched worlds using the same source-selection and action conditions. Start with a bounded development screen; retain all outcomes. Do not spend another sequence of cohorts tuning only Qwen2.5-7B.
3. Audit the rendered chat template, system prompt, truncation, stop behavior and response examples on a small subset. Test ordering of answer alternatives separately from evidence order. Check a small equivalent-inference overlap when feasible. This is a proposed confound audit, not a discovered runtime defect.
4. Predetermine direction-specific competence and validity criteria if pursuing a degradation claim. For a failure-mode paper, lack of competence is an outcome; the requirement is interpretable controls and replication.

**Decision:** Does the phenomenon persist across a different model lineage and reasonable presentation variants? If not, narrow the claim to a checkpoint/interface-specific case study; do not launch a broad confirmation matrix.

### Weeks 2–5: establish what the task measures

Use a compact factorial design crossing evidence order, causal direction, source identity and answer mapping within families. Include randomized-only, aligned two-source, conflicting two-source, matched numerical and noncausal selection controls. Add several feasible causal and observational strengths only if response-curve claims are retained. Match task demands and record remaining differences.

Compare explicit rival strategies: randomized-source rule, historical-source rule, first/last-source rules, constant action, numerical comparison and a fitted cue-integration/bias model. Fit and tune on development families; compare held-out predictions with a proper scoring rule and family uncertainty. Explain where models remain indistinguishable.

Test a bounded support condition, such as extracting the relevant source into a structured record before deterministic comparison. Keep it labeled as an assisted system, with matched controls and cost accounting. A useful mitigation strengthens practical relevance but is not compulsory for a strong diagnostic contribution.

**Exit:** a stable interpretable endpoint, known failure modes, useful variation and controls that distinguish the central rival explanations.

### Weeks 4–8: freeze and confirm the actual claim

Choose one primary estimand, one precision contrast if relevant, one target population and a practical effect threshold. Freeze invalid-response rules, multiplicity, fallback inference, exclusions and stopping. Simulate power, false-positive rate and interval coverage for the actual family structure and selected interaction; cohort 016's 20-point order-effect plan does not power a new smaller specificity interaction.

For selective degradation, one candidate is the causal conflict-penalty change under quantization minus the matched-control conflict-penalty change, averaged over prespecified presentation conditions. Its interpretation depends on control matching, and it must not be adopted merely because it is favorable on existing data. A presentation-focused paper should instead power its precision-by-presentation or decision-instability endpoint directly.

Collect untouched families only after the analysis is fixed. Report checkpoint-specific probability-scale effects and uncertainty; few checkpoints do not support population inference about all LLMs. Repeated identical greedy calls are not independent samples.

### Weeks 6–12: demonstrate useful scope

Replicate the central result in the second model family; add a third if making broad claims. Reserve complete templates or domains for transfer. Include an established causal benchmark where it tests a relevant capability, plus simple analytic and heuristic baselines. Benchmark breadth should serve the claim, not become an indiscriminate leaderboard exercise.

Treat quantization as a specified treatment bundle: same source checkpoint, documented conversion and quantizer/calibration, fixed activation/KV settings, matched runtime, context and decoding. If claiming effects of precision generally, add quantizer robustness; otherwise name Q4_K_M explicitly. Measure memory/latency under comparable budgets if deployment efficiency is part of the motivation.

**Exit:** either independently reproduced behavior or a precise and informative boundary, with claim scope adjusted accordingly.

### Final 2–4 weeks: manuscript and release

Build a compact narrative around a few contributions, not 21 sequential experiment reports. Put development history and failed screens in supplementary material with clear lineage. Produce figures for paired effects, direction-specific action probabilities, control contrasts and transfer; archive the exact plotted numbers.

Provide a pinned environment, one-command analysis from archived raw outputs, model provenance, scoring specifications, license review and an anonymized release as required. Distinguish code/data you may release from third-party PDFs and weights. Reproduce the headline figures in a clean environment and obtain a skeptical external manuscript review before submission.

## Effort and compute expectations

These stages overlap. **8–12 weeks is an optimistic lower bound** for a focused submission candidate if the independent-family screen and measurement checks succeed quickly; **3–6 months is a safer planning range**. A broader journal package or a major redesign can require **6–9 months or longer**. Part-time work and constrained lab access extend calendar time. Peer review and revisions are additional and venue-dependent.

The next decision does not require a huge inference budget. Cohort 021's 576 requests took 72.1 minutes on the recorded CPU setup, about 7.51 seconds/request. At exactly that observed throughput, 10,000 requests would take about 20.9 hours for one arm. This is arithmetic extrapolation, not a forecast for a different model, quantizer, prompt length or hardware; benchmark the new configuration first. Two variants and two similarly fast model families would multiply that example to about 83.5 hours. New-family sample size must come from power analysis, not this convenient request budget.

Suggested allocation of effort: roughly 40% measurement and discriminating experiments, 25% independent-model/task replication, 20% confirmatory statistics and reproducibility, and 15% manuscript/related-work synthesis. These are prioritization recommendations, not measured completion percentages.

## What to postpone

- More broad prompt searches on the same failing reference without a stopping rule.
- Scaling cohort 016 merely to reduce an already tiny p-value.
- Full agentic infrastructure before deciding whether direct-decision findings generalize.
- Mechanistic “causal circuit damage” claims without neural interventions.
- Presenting a fitted psychological parameter as a validated mental process.
- Treating all cohorts as one pooled confirmatory dataset or removing failures to improve the story.
- Optimizing for an imagined venue model-count requirement or adding every available quantization level.

The highest-value next step is a **bounded independent-model-family diagnostic with fixed source-selection/action conditions**, followed by a deliberate choice between a precision-specific paper and a broader evaluation paper. The infrastructure is ready to support that decision; the evidence does not yet justify skipping it.
