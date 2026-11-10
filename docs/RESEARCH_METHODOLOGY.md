# CausalFade research methodology

> **10 November 2026 update.** The status below describes the original prospective design. The user authorized exploratory inference on the Ubuntu lab PC using local model weights. The [experiment index](../EXPERIMENTS.md) and [session report](../SESSION_REPORT.md) track live progress. Confirmatory choices remain open.

**Version:** 0.3, 7 November 2026. **Status:** documented design, executable synthetic validation and completed weight preparation. No LLM inference, agent evaluation or confirmatory data collection has been performed. This document is not a registered protocol.

The [implementation and research roadmap](STUDY_ROADMAP.md) records completed work, remaining deliverables, dependencies and decisions before collection. The user's current authorization is documentation and setup only; the roadmap does not authorize running research.

For source findings, the exact CNI-style mathematical mapping, the rationale for transfer and its limits, read [Methodology adaptation and source evidence](METHODOLOGY_ADAPTATION.md).

## 1. Objective and contribution

Research question: **Does post-training quantization change causal sensitivity, conditional associative influence, or baseline action preference when an agent interprets the same causal evidence?**

The proposed contribution adapts process-dissociation measurement from cognitive psychology to a controlled quantization experiment. A factorial task design separates a correct causal answer from a potentially misleading observational association. A behavioral processing tree attempts to explain the response pattern. The experiment identifies precision-configuration effects within the tested checkpoint, task population and serving stack; the tree provides a model-dependent decomposition of those effects.

Neither a significant accuracy difference nor a fitted tree proves that internal causal graphs have been severed. The world's true graph, an agent's reported graph and the neural network's computational mechanisms are different objects.

### Implemented now

- Binary structural causal simulator with four matched conditions and analytic oracle effects.
- Exact-probability and sampled-data evidence, public prompts separated from evaluator truth.
- Backdoor-adjusted, observational-association and seeded random baselines.
- Proposed processing-tree likelihood, constrained pooled maximum-likelihood fitting and parameter recovery.
- Parametric-bootstrap model-fit checks and a competing logistic evidence-integration model.
- Structured response scorer preserving missing/invalid predictions.
- Paired family-block bootstrap utility for the probability-scale conflict-penalty contrast.
- Reproducible synthetic outputs and unit tests.
- SSD model preparation: four Qwen2.5-Instruct sizes, each with F16, Q8_0, Q4_K_M, Q2_K and Q1_0 GGUF files. Quantization logs and hashes are retained; inference compatibility is not yet established.

### Planned, not implemented or established

- Live LLM/tool-agent runner, inference compatibility checks and runtime measurements. Importance-matrix calibration is absent from the prepared configurations; adding it would define another treatment.
- Hierarchical logistic experimental analysis and hierarchical Bayesian processing-tree inference.
- Power/precision simulations for the final design, interval-coverage study and confirmatory collection.
- Active experiment selection and investigator/analyst precision crossing.

The supplied synthetic response generator is **not fake quantization** and does not represent any real model. Its parameter settings are hypothetical measurement-validation cases.

## 2. Two levels of causality

**Within-world target:** the effect of a machine setting X on successful operation Y. Severity Z confounds observational comparisons.

```mermaid
flowchart LR
    Z[Initial severity Z] --> X[Activate setting X]
    Z --> Y[Successful operation Y]
    X --> Y
```

The target is `tau = E[Y | do(X=1)] - E[Y | do(X=0)]`. The observational shortcut is `delta_obs = E[Y | X=1] - E[Y | X=0]`.

**Across-model target:** the difference in behavior under prespecified precision configurations of the same base checkpoint. Evaluate all configurations on the same independently generated world families and frozen prompts. Randomize execution order to limit operational drift. This is an intervention on the inference configuration, not an observational comparison of unrelated models.

If quantizer, calibration set, kernels or cache precision differ, the estimated treatment effect concerns that entire configuration. Do not attribute a bundled effect exclusively to bit width. Generalization beyond the selected checkpoints needs additional model families.

### Prepared configurations and hardware

Use Qwen2.5-Instruct at 0.5B, 1.5B, 3B and 7B. Within each size, compare five configurations: F16 reference, Q8_0, Q4_K_M, Q2_K and Q1_0. This gives 20 model configurations. Treat size and GGUF format as categorical factors. A continuous regression on filename bit labels would conflate quantizer algorithms, mixed tensor types and storage overhead.

All 16 quantized files were prepared from their matched retained F16 GGUFs using the official llama.cpp Windows CPU release b12176, eight quantization threads and no importance matrix. The canonical 7B Q4_K_M was rebuilt with that release; its earlier AGERE copy is archived and excluded from the main grid. The original Hugging Face checkpoints contain BF16 weights; the reference used here is the converted F16 GGUF, not the original BF16 checkpoint. See [asset provenance](SSD_ASSET_REUSE.md#gguf-quantization-prepared-for-lab-use).

Q1_0 replaces the earlier proposed IQ1_S for this preparation. These are different formats. IQ1_S was not prepared; any future calibrated IQ configuration needs an explicit calibration corpus, split and protocol amendment. Nominal bit labels do not give exact whole-model bits per weight. Record tensor types and actual byte sizes alongside format names.

The lab specification is 32 GB system RAM and 10 GB VRAM. The 7B F16 GGUF is larger than VRAM and needs CPU execution or partial CPU/GPU offload. Freeze and report the offload policy per configuration; validate any machine change on a separate overlap set. A CPU-only sensitivity run or another justified common execution policy is needed before attributing hardware-dependent numerical differences to quantization. Do not interpret latency across different offload policies as a pure precision effect.

Preparation checks establish file presence, headers and recorded hashes. They do not establish inference quality, runtime compatibility, numerical parity or the scientific adequacy of the low-bit conditions.

## 3. Structural causal model and exact identification

The simulator uses independent exogenous random draws with:

```text
Z ~ Bernoulli(0.5)
X | Z=z ~ Bernoulli(e_z)
Y | Z=z, X=x ~ Bernoulli(mu_z + (x - 0.5) * tau)
mu_0 = 0.5 + gap/2
mu_1 = 0.5 - gap/2
```

The intervention `do(X=x)` replaces the assignment equation for X while leaving the distribution of Z and outcome equation unchanged. Severity is measured before X. There are no unmeasured common causes, no interference, and no selection or missingness in the initial suite. Consistency and positivity are explicit task assumptions.

Under these assumptions, backdoor adjustment identifies the effect:

```text
tau = sum_z P(Z=z) * {P(Y=1 | X=1,Z=z) - P(Y=1 | X=0,Z=z)}
```

The target population weights P(Z=z)=0.5 are supplied to the agent. Outcome probabilities are strictly between zero and one. Assignment probabilities are strictly interior. The reference estimator uses these known target weights, so its target is not implicitly changed to the empirical sample's composition.

For condition indicators T and S, set `tau=(2T-1)*effect_size` and `k=-(2S-1)*assignment_strength`, with `e_0=(1-k)/2`, `e_1=(1+k)/2`. Then:

```text
delta_obs = tau - k * gap
```

Require `assignment_strength * gap > effect_size`. Therefore S determines the observational sign even when it conflicts with T. Changing assignment changes S while preserving the causal effect. Changing the causal effect's sign preserves its magnitude within a family. The generator validates probability bounds and these sign constraints rather than discovering them after seeing responses.

The validation generator draws effect magnitude 0.06-0.12, severity gap 0.50-0.70 and assignment strength 0.65-0.90. These are pilot ranges, not final population definitions. Absolute observational magnitudes differ between aligned and conflict cells; an analysis must acknowledge that and investigate evidence-strength matching rather than claim perfect difficulty matching.

## 4. Four conditions and psychological adaptation

Each family has T,S = (0,0), (0,1), (1,0), (1,1), where 1 favors activating X and 0 favors declining it. T=S is aligned; T!=S is conflict. All four share effect magnitude, severity gap and assignment-strength magnitude. Two causal directions and two association directions prevent a simple yes/no preference from masquerading as evidence sensitivity.

Process dissociation supplies the experimental principle: put candidate influences in agreement and opposition. The closest formal template is Gawronski et al.'s (2017) CNI model, also used in LLM moral-judgment research. Our C,A,B tree retains that type of mathematical structure with changed constructs and B=1-I for residual action coding. It is a proposed CNI-style adaptation, not a newly invented tree or a literal implementation of Jacoby's memory paradigm. Human psychological labels are not assumed to apply to neural computation; see the [mapping and source findings](METHODOLOGY_ADAPTATION.md).

The initial task is a constrained evidence-interpretation decision. It supplies the graph and confounder, so it **does not measure causal discovery**. It measures application of causal identification and estimation given sufficient information. Do not describe static JSON answers as an already implemented autonomous scientific agent.

### Evidence layers

- **Exact:** population cell probabilities are provided. This is the primary diagnostic for the initial measurement study; finite-sample ambiguity cannot explain an error.
- **Sampled:** 2,000 observational rows are summarized by counts for every (Z,X) cell. This evaluates statistical estimation under finite evidence as a separate layer. Do not reject or resample datasets just because an empirical association has the unwanted sign; that would condition on realized noise. Record the true sign and, in later analysis, the empirical evidence strength separately.

Missing sample strata produce an undefined adjusted reference estimate rather than silent smoothing. Exact and sampled items from the same family are dependent and must not be treated as new independent worlds.

## 5. Agent inputs, controls and run provenance

Only `prompt` from public_tasks.jsonl should enter a fresh model context. Opaque task IDs contain no readable condition labels. `oracle_truth.jsonl`, baseline answers and evaluator fields must stay outside the model's context, retrieval and tools. They are not secrets from researchers; they are withheld evaluation labels. Reset conversation state between tasks. Do not send multiple family variants together in a conversational batch.

The current prompt requests `ate_estimate`, binary integer `activate`, and `adjustment_set`. For this graph the minimal valid adjustment set is [Z]. A future runner may permit a bounded calculator/data-analysis tool, but its permissions, interaction budget and error policy must be fixed before collection. Exact and sampled conditions must use the same answer contract.

Control and record base checkpoint revision/hash, quantized weight hash, quantizer and group size, calibration data and seed, activation/cache precision, compute dtype, tokenizer and chat template, serving backend/version, hardware, decoding policy, output budget, tool configuration, prompt hash, run order, random seed and stopping reason. Include same-bit calibration replicates when feasible to estimate configuration instability.

Do not treat repeated identical greedy calls as independent trials. Use independent world families for the experimental sampling unit. Stochastic decoding repetitions and paraphrases remain nested within family and checkpoint.

### Agent implementation for the course project

The current generator produces a direct-response measurement task. The planned course submission adds a bounded analyst agent that can choose to inspect observational strata, request deterministic arithmetic, and submit the structured final decision. The environment supplies the known graph and evidence; it does not expose evaluator labels. Tool choice, arguments, returned values, failures and final actions must be logged. This supports an agent-level analysis without claiming causal discovery.

Implement direct response first to validate the measurement pipeline, then the bounded tool interface. Treat interface mode as a separate experimental factor or separate study stratum; do not pool responses across modes. Before confirmatory collection, designate one mode as primary. Freeze allowed tools, call/token limits, calculator semantics, retries and stopping rules on development data. An active investigator that intervenes on the SCM is a later extension with its own protocol.

Confirmatory gates include above-chance full-precision task competence, low protocol-failure rates, and evidence that the selected suite exercises the desired contrast. Gates and thresholds must be fixed on development data, then checked once on an untouched confirmatory split; do not filter individual items by whether full precision happened to answer correctly.

## 6. Observable outcomes and missing responses

**Decision accuracy:** agreement with T. Missing or invalid actions are failures in the primary intention-to-evaluate accuracy denominator. Report their rate separately. The scorer rejects duplicate and unknown IDs rather than silently choosing a response.

**Conflict penalty:** `accuracy_aligned - accuracy_conflict`, averaged with equal weighting over the two causal directions. Its change under compression is the primary proposed behavioral contrast.

**Effect error:** signed `ate_estimate - tau`, summarized by bias, MAE and RMSE. Non-numeric estimates are missing; report their count and denominator. Avoid implying that valid-only numeric performance represents every attempted task.

**Decision regret:** expected success under the optimal action minus expected success under the agent's action. Here valid wrong actions incur `abs(tau)`; correct actions incur zero. Invalid actions have undefined regret in the current scorer. Prespecify whether later decision deployment treats invalid output as no action; do not silently change this rule.

**Adjustment:** [Z] is a reference identification check in this restricted graph. Selecting it does not prove the rest of the calculation is correct. The current scorer checks the minimal list contract only, not arbitrary valid causal programs.

**Secondary future tasks:** unidentifiability/abstention, graph recovery, uncertainty intervals and active experiment selection. They require separate task designs; the current all-identifiable suite cannot establish these capabilities.

If confidence intervals are later requested, evaluate empirical coverage and width over new datasets from fixed worlds. Require an estimator and interval procedure; verbal confidence is not a confidence interval. The present suite does not estimate interval coverage.

## 7. Proposed processing-tree measurement model

Let C be a causal-following route probability, A a conditional association-following probability when that route fails, and B a residual activation preference. The model is:

```text
P(activate=1 | T,S) = C*T + (1-C)*[A*S + (1-A)*B]
```

This assumes causal priority, deterministic responses on a successful route, and invariant C,A,B across the matched cells within a modeled group. These are falsifiable measurement assumptions, not facts about model cognition.

An equivalent mixture uses four nonnegative weights summing to one:

```text
wC = C
wA = (1-C)*A
wYes = (1-C)*(1-A)*B
wNo = (1-C)*(1-A)*(1-B)
p_TS = wC*T + wA*S + wYes
```

The implemented MLE fits these simplex weights with EM. It is pooled and homogeneous; it is not hierarchical Bayesian inference. Cell successes follow binomial likelihoods only in the synthetic validation. Real repeated-family responses require a dependence model or cluster-based inference.

### Identification and limits

With population response probabilities ordered 00,01,10,11:

```text
wYes = p00
wC = p10 - p00
wA = p01 - p00
wNo = 1 - p11
required equality: p11 = p10 + p01 - p00
C = wC
A = wA / (1-wC)
B = wYes / (wYes+wNo)
```

Nonnegative-weight constraints and the equality are model restrictions. The four cells supply four response probabilities for three free parameters: only one equality check, plus inequality constraints. This is a weakly constrained diagnostic design, not a richly identified neural mechanism.

When C=1, A and B are unidentified. When the residual branch has zero mass, B is unidentified. Near either boundary, estimates can be unstable despite apparently good prediction. The fitter reports undefined ratios at a small denominator threshold and exposes convergence flags. Numerical tolerance is not a scientific identifiability threshold.

For balanced T, the model implies:

```text
conflict_penalty = wA = (1-C)*A
```

Thus a larger conflict penalty cannot itself tell whether C fell or A rose. That motivates the decomposition, while also showing that it is not an independent replication of the accuracy result.

### Observational equivalence

A continuous logistic evidence-integration process can generate the same four cell probabilities. The validation explicitly includes such a case. A passing fit test and accurate parameter recovery under tree-generated data cannot distinguish these latent mechanisms. Interpret C,A,B as behavioral coordinates conditional on the model unless extra manipulations discriminate the alternatives.

## 8. Statistical analysis plan for future LLM data

### Primary behavioral estimand

For a selected precision p versus full precision f:

```text
Delta = [Acc(p, aligned)-Acc(p, conflict)]
      - [Acc(f, aligned)-Acc(f, conflict)]
H0: Delta <= 0
H1: Delta > 0
```

Select one primary precision contrast and practical effect threshold before confirmatory collection. Full precision is a reference configuration, not an assumed perfect or superior agent.

The working recommendation for planning is 3B Q2_K versus matched 3B F16 on exact evidence, because it includes substantial compression while keeping the reference model smaller than 7B. This is a proposed choice, not a registered primary comparison. Pilot feasibility and competence checks may change it before the plan is frozen; any change must be documented without consulting confirmatory outcomes. Keep evidence layer and agent mode explicit in the final estimand.

Fit a hierarchical logistic model for correctness with precision, conflict, causal direction and prespecified interactions, accounting for family dependence. Treat a small set of checkpoints as fixed effects or report checkpoint-specific contrasts rather than estimating a broad LLM population from two examples. Include evidence layer as a separate stratum initially. Standardize predictions over the balanced task population to obtain Delta on the probability scale: a logistic interaction coefficient is not Delta.

For a checkpoint-specific analysis, a candidate specification is `logit Pr(correct_fqk=1) = alpha + beta_q + gamma*k + eta_q*k + theta*T + u_f + v_f*k`, with F16 as the format reference and k indicating conflict. The random family intercept and conflict slope account for repeated matched cells; simulation must establish whether the planned family count supports this structure. If singular fits or separation are anticipated, freeze a regularized alternative and its interpretation in advance. Do not choose between models according to which yields significance. In a joint size analysis, use size-specific fixed contrasts and retain the shared family structure.

For each format, obtain standardized aligned and conflict accuracy by averaging predicted probabilities over the prespecified family/covariate population. Then subtract the corresponding F16 conflict penalty. State whether predictions integrate over family random effects or describe the observed families; these target different populations. Prefer population-level predictions when claiming generalization to newly sampled worlds.

The proposed primary test uses a one-sided alpha of .05 for Delta>0. Report the estimate, a two-sided 95% interval for estimation, and the matching one-sided lower confidence bound or calibrated one-sided p-value for the directional decision. A two-sided 95% interval and one-sided .05 test are not interchangeable decision rules. Validate the chosen inference method by simulation under the clustered design. Keep the result exploratory until that calibration and protocol freeze are complete.

Use family-level paired bootstrap intervals as a robustness analysis, resampling complete families with all conditions/configurations together. Clarify inference is over the synthetic-world population. If randomized prompt/assignment schedules are used for randomization inference, permutations must follow that actual design; arbitrary swaps of deterministic precision labels are not automatically a valid randomization test.

### Explanatory parameters

Fit the hierarchical tree only after parameter-recovery, fit and identifiability diagnostics are adequate. Model precision-specific C,A,B with prespecified weakly informative priors and sensitivity checks. Item-family heterogeneity requires repeated structure and sufficient data; do not introduce freely varying parameters per item that the design cannot identify.

Report Delta_C, Delta_A, Delta_B and Delta_wA with posterior intervals and practical-effect probabilities. Describe B as residual action bias, not a response preference measured independently of the tree. Do not present a Bayesian credible interval as a frequentist confidence interval. The current percentile bootstrap example is neither of those planned hierarchical analyses.

Invalid actions have no binary activate value. Never recode them as decline for the tree. Plan a two-part model for response validity and binary action conditional on validity, with family dependence. A simpler valid-response tree is a labeled sensitivity analysis whose parameters describe the selected valid-response population. Format-dependent invalidity can change that population, so it cannot by itself support an unconditional mechanism claim. The primary correctness analysis continues to count invalid responses as failures.

### Secondary estimation outcomes

Report paired differences in RMSE, bias and regret with family-bootstrap uncertainty and explicit valid-response denominators. Include both directions of decision flips; better average accuracy can conceal harmed tasks. Control multiplicity for prespecified secondary contrasts, for example with Holm correction, and label later analyses exploratory. Additional tests should correspond to additional questions, not inflate the number of significance tests.

There are 16 possible within-size quantized-versus-F16 contrasts in the prepared grid. If one is designated primary, list the remaining contrasts in an explicit secondary family and apply Holm adjustment within that family. This does not establish global family-wise error control over unrelated endpoints. Define separate endpoint families or a gatekeeping procedure in the frozen plan. Size trends, sampled-evidence replication and alternative agent modes require declared analysis roles.

### Preservation and specificity

Failure to reject degradation does not establish preservation. Equivalence/noninferiority requires a justified tolerance fixed before confirmatory data. A selective causal deficit also requires matched recall, context-comprehension and noncausal numerical controls. The current simulator does not implement those additional controls; it cannot exclude all general-capacity explanations.

For equivalence, define a substantively justified margin epsilon and test whether Delta lies within [-epsilon,+epsilon], using a procedure and interval calibrated for the paired families. For noninferiority, specify the permitted increase in conflict penalty. Leave the margin undecided until a scientific justification is recorded; do not derive it from the observed confirmatory effect. An overall-accuracy loss and a change in conflict penalty answer different questions.

For specificity, compare quantization effects on causal and matched control tasks through a prespecified task-type interaction on the probability scale. Match arithmetic operations, response format, context length and evidence strength where possible. This contrast assesses behavioral selectivity under those matching assumptions; it does not prove a latent causal route is damaged. Basic recall/comprehension alone cannot rule out every general reasoning explanation.

Do not adjust away token count or tool failure in the total-effect analysis: they can be consequences of precision. Analyze them as outcomes. A causal mediation interpretation requires additional assumptions or stage interventions and is not supplied by processing-tree labels.

## 9. Validation, model comparison and sample-size planning

The executable study simulates six C,A,B settings at 50, 200 and 1,000 independent responses per cell, with 200 repetitions each (3,600 fitted datasets). It reports parameter bias, RMSE, undefined estimates, boundary frequency and EM nonconvergence. Summaries exclude nonconverged/undefined estimates and report their counts; such exclusion can itself distort recovery summaries, especially near boundaries.

For one illustrative interior fit, 500 model-based bootstrap samples give percentile intervals. This is not a coverage study. Model-fit diagnostics use a refitted parametric-bootstrap binomial deviance against unrestricted four-cell probabilities. Boundary behavior makes an unqualified chi-square reference undesirable. A logistic integration model is also fit, with held-out negative log loss on independently generated synthetic responses.

The initial symmetric logistic comparison exposed observational equivalence. An asymmetric violating generator was added afterward and is labeled exploratory in the report. Do not describe these development checks as preregistered evidence or a power analysis.

Before real confirmatory collection, expand simulations to evaluate estimator coverage, fit-test size/power, family heterogeneity, invalid outputs, plausible effect sizes and dependence. Determine the number of independent families from the desired precision/power for Delta, not from the 24-family demonstration export or the number of synthetic binomial responses. Fit tests, parameter intervals and power under real LLM variation remain open validation work.

Use development-only data for choosing prompts and thresholds. Split by whole family, including every evidence layer, label direction and paraphrase. Freeze the generator/configuration, analysis script and primary contrast, then register or timestamp the final plan before collecting the untouched test set. Version 0.3 is not that registration.

## 9a. Portable execution, resumption and analysis deliverables

All source code, prompts/templates, analysis scripts and dependency specifications belong in the Git repository. The external SSD holds weights, generated datasets, raw trajectories, runtime logs, scored results and provenance. Installed environments and executables stay on the current PC. Git commit plus model/task hashes identify an experiment across machines; the drive letter is not an experiment identifier.

The future runner must create a durable run manifest and write a completed task record before advancing its checkpoint. Use stable keys including run ID, configuration, task ID and repetition. Resume only missing records under the identical frozen configuration; reject conflicting duplicates and preserve raw failed attempts. A retry policy must not replace an incorrect valid answer with a later preferred answer. If a process fails mid-task, retain the interruption and apply the same predefined infrastructure-retry policy across formats.

When changing PCs, record machine/driver/backend versions and use a separate development overlap set to detect drift. Do not introduce a new machine silently halfway through a format condition. Balance run order in complete family blocks where feasible, and account for unavoidable machine blocks in the analysis. Capture interruptions and missingness rather than silently discarding incomplete difficult configurations. Maintain a second backup of irreplaceable trajectories; the external SSD alone does not guarantee progress preservation.

Planned figures are accuracy by format and conflict, probability-scale paired contrast forest plots, effect-error/regret distributions, invalid-output and tool-failure rates, model-fit/recovery diagnostics, and C/A/B intervals only when the measurement model is supported. Facet by checkpoint and keep exact/sampled and direct/tool modes distinct. Export publication figures as PDF/SVG plus PNG previews using repository plotting code; archive the numeric estimates behind every figure. No actual research figures have been produced by documenting this plan.

## 10. Novelty, feasibility and claims

Direct quantization/causal-question evaluation already exists. Interactive causal investigation and crossed precision interventions also have precedents. Processing-tree methods have been used on LLM moral judgments. The proposed contribution is therefore a **validated adaptation to precision-related changes in causal evidence interpretation**, not the invention of process dissociation, factorial designs or causal-agent evaluation.

The initial binary, known-graph, homogeneous-effect worlds deliberately trade realism for exact ground truth. Extension to unfamiliar narratives, varied evidence strength and alternative causal structures should follow validation. Active investigator/analyst crossing is a later experimental module, not a requirement to make the first study enormous.

Permissible eventual claim: a particular compression configuration changes causal-decision behavior on the defined task population, with a model-dependent decomposition if validated. Impermissible shortcut: parameter change proves an internal causal circuit was destroyed.

## 11. Reproduction and source references

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for commands and artifacts, [DATA_CONTRACT.md](DATA_CONTRACT.md) for inputs and scoring, and [DECISIONS_BEFORE_COLLECTION.md](DECISIONS_BEFORE_COLLECTION.md) for unresolved choices.

Sources supporting the methodological lineage and overlap (the adaptation itself is proposed here):

The direct formal source is Gawronski et al. (2017), *Consequences, Norms, and Generalized Inaction in Moral Dilemmas*, DOI [10.1037/pspa0000086](https://doi.org/10.1037/pspa0000086). Its relevant cognitive-load findings and the adaptation are explained in the [source-evidence document](METHODOLOGY_ADAPTATION.md). This supplements the references below.

1. Jacoby (1991), [A Process Dissociation Framework](https://doi.org/10.1016/0749-596X(91)90025-F). The foundational method predates the project's 2025-2026 empirical-paper collection and is cited as methodological background.
2. Heck, Arnold & Arnold (2018), [TreeBUGS](https://pmc.ncbi.nlm.nih.gov/articles/PMC5809562/): hierarchical processing-tree estimation and measurement modeling.
3. Wu & Deng (2025), [What Counts Underlying LLMs' Moral Dilemma Judgments?](https://aclanthology.org/2025.nlp4pi-1.12/): precedent for processing-tree-based decomposition in LLM research.
4. Nwaiwu et al. (2025), [Compressed Causal Reasoning](https://arxiv.org/abs/2512.13725): direct overlap with precision-versus-causal-question evaluation.
5. [ACED-Bench](https://arxiv.org/abs/2610.14381) (2026): related active causal-evidence evaluation.
6. [Measuring the Task Value of Precision Upgrades in Closed-Loop Agents](https://arxiv.org/abs/2610.24346) (2026): related crossed precision interventions.

The reviewed sources motivate the design; they do not establish that our proposed tree correctly describes compressed models. Novelty remains a scoped literature assessment, not a guarantee of priority.
