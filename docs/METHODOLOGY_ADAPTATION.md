# Methodology adaptation: origins, source findings and rationale

**Updated:** 1 November 2026. Source findings below are the authors' reports, not independently reproduced results. The adaptation and its suitability are our research proposals.

## 1. Where the approach comes from

There are four distinct sources, rather than one paper:

1. **Jacoby (1991):** process dissociation supplies the principle of putting candidate influences in agreement and conflict.
2. **Gawronski et al. (2017):** the CNI model supplies the closest formal three-parameter template.
3. **Wu and Deng (2025):** an existing application of CNI modeling to LLM moral judgments supplies an AI precedent.
4. **Heck, Arnold and Arnold (2018):** hierarchical multinomial-processing-tree methodology informs estimation and model checking.

The transfer is from cognitive/moral psychology, through prior LLM moral-judgment work, into **quantization and quantitative causal-decision evaluation**. It is not the first application of psychological processing trees to AI. The older sources are methodological foundations, distinct from the original 2025-2026 empirical-literature collection.

## 2. Foundational experimental principle: Jacoby (1991)

Larry L. Jacoby, *A Process Dissociation Framework: Separating Automatic from Intentional Uses of Memory*, Journal of Memory and Language 30(5), 513-541. [Publisher/DOI](https://doi.org/10.1016/0749-596X(91)90025-F).

The original work separates candidate influences on memory performance using agreement/opposition conditions and an explicit measurement model. Its contribution is to avoid equating an entire task with a single process.

**What transfers:** the experimental principle. **What does not:** human memory, consciousness or familiarity constructs. This source motivates how to pose the measurement question; it supplies no empirical prediction about quantization.

## 3. Closest mathematical template and relevant results: CNI (2017)

Bertram Gawronski, Joel Armstrong, Paul Conway, Rebecca Friesdorf and Mandy Hütter, *Consequences, Norms, and Generalized Inaction in Moral Dilemmas: The CNI Model of Moral Decision-Making*, Journal of Personality and Social Psychology 113(3), 343-376. [DOI](https://doi.org/10.1037/pspa0000086); [author-hosted published text](https://www.bertramgawronski.com/documents/GACFH2017JPSP.pdf).

**Method and findings:** the paper manipulates consequence and norm directions and estimates consequence sensitivity C, norm sensitivity N, and inaction preference I. Across eight studies, it examines gender, cognitive load, framing and psychopathy. Especially relevant are Studies 2a/2b: cognitive load increased modeled inaction preference without statistically significant changes in C or N. For I, Study 2a reports Delta-G-squared(1)=5.19, p=.023, d=.328; Study 2b reports 13.77, p<.001, d=.535. See printed pp. 356-357 (PDF pp. 14-15), Figures 4-5. Study 2a's fit was imperfect; model checks remain necessary.

**Why it suits us (our interpretation):** a compressed model might decline an intervention because its action preference changed, even if its sensitivity to causal evidence did not. The paper illustrates why that alternative explanation must be modeled. Cognitive load is not quantization: the human finding neither predicts the direction of our effect nor supplies its expected size. Nonsignificant C/N results are not proof of equivalence.

## 4. Exact mapping into CausalFade

A CNI-style action-probability template uses consequence-supported action D and norm-supported action R:

```text
P(action) = C_source*D
          + (1-C_source)*[N_source*R + (1-N_source)*(1-I_source)]
```

We retain the form but change its proposed constructs:

- **D -> T:** the action supported by the true SCM intervention effect, replacing a moral consequence judgment.
- **R -> S:** the action suggested by the observational association, replacing a moral norm.
- **C_source -> C:** hypothesized causal-following contribution.
- **N_source -> A:** hypothesized conditional association-following contribution.
- **1-I_source -> B:** residual activation preference; this explicitly reverses the residual inaction coding.

The adapted model is:

```text
P(activate | T,S) = C*T + (1-C)*[A*S + (1-A)*B]
```

This is a **CNI-style adaptation**, not an independently invented probability-tree structure. A mathematical mapping is not construct equivalence: norms are not associations, moral consequences are not causal identification, and an estimated C does not acquire its intended meaning merely through naming it.

We cross T and S in four conditions so both cue directions occur, rather than asking only conflict questions. We add a causal data-generating model, known intervention effects and matched precision treatments. The full derivation and identifiability restrictions appear in [the methodology](RESEARCH_METHODOLOGY.md#7-proposed-processing-tree-measurement-model).

## 5. Existing LLM application and its results: Wu and Deng (2025)

Wenya Wu and Weihong Deng, *What Counts Underlying LLMs' Moral Dilemma Judgments?*, NLP4PI 2025, pp. 144-150. [Record](https://aclanthology.org/2025.nlp4pi-1.12/); [PDF](https://aclanthology.org/2025.nlp4pi-1.12.pdf); DOI 10.18653/v1/2025.nlp4pi-1.12.

**Method and findings:** Qwen-1.5-14B, Llama3-8B and DeepSeek-R1 answer 48 dilemmas: 12 scenarios crossed by consequence/norm directions. The authors vary social exposure and dual-agent interaction and analyze acceptance, confidence and CNI parameters. They report stronger norm than consequence influence, greater action tendency for DeepSeek-R1, and model-specific social-context effects. Methods: pp. 145-146; findings: pp. 146-147; limitations: p. 148. Limitations include three-model coverage, hypothetical scenarios and simplification by the measurement model.

**Why this helps (our interpretation):** it establishes an LLM precedent for factorial behavioral decomposition. It does not validate causal/associative routes in compressed models. We replace social-context treatments with precision configurations and moral scenarios with objectively scored causal problems.

**What we should not copy automatically:** its ANOVA choices, significance thresholds or treatment of repeated responses. Our binary outcomes need appropriate likelihoods and dependence handling. Repeated greedy calls do not become independent worlds. These findings provide neither quantization effect sizes nor a power justification for CausalFade.

## 6. Hierarchical estimation foundation: TreeBUGS (2018)

Daniel W. Heck, Nina R. Arnold and Denis Arnold, *TreeBUGS: An R Package for Hierarchical Multinomial-Processing-Tree Modeling*, Behavior Research Methods 50, 264-284; published online 2017, issue 2018. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5809562/); DOI 10.3758/s13428-017-0869-7.

**Contribution:** a methods/software paper supporting hierarchical MPT estimation, beta-MPT and latent-trait models, predictors, group/individual estimates and model checks. It explains that ignoring item/participant heterogeneity can distort estimates and intervals and discusses prior sensitivity and fit-statistic limitations.

**Why it suits us (our interpretation):** world families and model configurations can vary, making indiscriminate aggregation questionable. We borrow the hierarchical measurement perspective, not the assumption that checkpoints are exchangeable human participants. A small number of checkpoint families cannot justify a broad LLM-population claim.

The current code fits a pooled constrained MLE and synthetic diagnostics. It does not run TreeBUGS, implement the proposed hierarchical Bayesian model or reproduce that paper's applications. A citation is not evidence of completed implementation.

## 7. What changes substantively in this application

These are our proposed design changes, not inherited source findings:

- **Ground truth:** an SCM defines the intervention effect instead of an evaluator assigning a moral preference.
- **Identification:** a known graph and measured confounder make backdoor adjustment valid under explicit assumptions.
- **Cue manipulation:** changing assignment changes observational association while the relevant causal effect is fixed.
- **Treatment:** precision configurations come from the same checkpoint and receive the same evidence.
- **Outcomes:** causal-effect error and decision regret supplement action rates.
- **Validation:** parameter recovery, boundary diagnostics and rival-model comparisons precede interpretation.
- **Inference:** dependence is handled at the family level; matched recall/comprehension controls are required for specificity claims.

This supplies a rationale for the adaptation, not an automatic novelty guarantee. Causal-agent benchmarks, precision comparisons and processing-tree LLM studies all already exist. The contribution must lie in a validated combination and new empirical evidence.

## 8. Why suitability is still conditional

The lineage supports questioning aggregate action rates and explicitly testing candidate influences. It does not establish causal-first processing, parameter invariance across our conditions, a literal neural route decomposition, or any quantization effect.

Our [synthetic report](../results/design_validation/VALIDATION_REPORT.md) illustrates the remaining burden: parameters are recoverable under the assumed generator away from difficult boundaries, but a symmetric logistic integration process can be observationally equivalent. An incompatible generator is rejected in an exploratory check. There were 16 nonconverged fits out of 3,600, confined to near-causal-boundary scenarios. These are development results, not LLM findings or replications of source experiments.

Before strong substantive claims, we need dependence-aware recovery/power simulations, real LLM data, rival-model discrimination, matched noncausal controls and an untouched confirmatory set. Route-order and evidence-strength manipulations are useful sensitivity analyses, not guaranteed solutions to observational equivalence.

## 9. Proposal-ready rationale

> We adapt the agreement/conflict logic of process dissociation and a CNI-style processing-tree framework from cognitive and moral psychology to causal decisions under quantization. An existing LLM moral-judgment application motivates feasibility but does not validate our causal/associative constructs. We replace norm/consequence dilemmas with SCM-generated intervention problems and independently manipulated observational cues. Matched precision configurations receive the same evidence, with residual action preference modeled separately. Recovery, boundary checks and rival-model comparisons precede interpretation. Estimated components describe behavior conditional on the measurement model, rather than directly measuring neural causal circuits.

Source methods/results were checked on 1 November 2026. This is a selective methodological review, not a systematic review. No moral-psychology effect size is imported into our power calculation. See [the full design](RESEARCH_METHODOLOGY.md), [remaining decisions](DECISIONS_BEFORE_COLLECTION.md) and [BibTeX entries](references.bib).
