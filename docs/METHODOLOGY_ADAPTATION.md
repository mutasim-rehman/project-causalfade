# Methodology adaptation: origins, source findings and rationale

**Updated:** 13 November 2026. Source findings below are the authors' reports, not independently reproduced results. Sections 1–9 retain the original processing-tree rationale. Section 10 records its contribution and limits after live experiments; section 11 extends the proposed methodology without claiming completed implementation.

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

As of 13 November, real LLM data and the cohort 016 fresh-family order replication exist. They do not supply the missing C/A/B construct validation, matched-control specificity analysis or rival-model discrimination. The preceding requirements remain applicable to latent-component claims.

## 9. Proposal-ready rationale

> We adapt the agreement/conflict logic of process dissociation and a CNI-style processing-tree framework from cognitive and moral psychology to causal decisions under quantization. An existing LLM moral-judgment application motivates feasibility but does not validate our causal/associative constructs. We replace norm/consequence dilemmas with SCM-generated intervention problems and independently manipulated observational cues. Matched precision configurations receive the same evidence, with residual action preference modeled separately. Recovery, boundary checks and rival-model comparisons precede interpretation. Estimated components describe behavior conditional on the measurement model, rather than directly measuring neural causal circuits.

Source methods/results were checked on 1 November 2026. This is a selective methodological review, not a systematic review. No moral-psychology effect size is imported into our power calculation. See [the full design](RESEARCH_METHODOLOGY.md), [remaining decisions](DECISIONS_BEFORE_COLLECTION.md) and [BibTeX entries](references.bib).

## 10. What the adaptation contributed in the live studies

Its demonstrated contribution is to design and interpretation, not validated psychological-route estimation. Crossing causal and associative directions and recording activation helped reveal that a smaller conflict penalty can coincide with a near-constant action policy and lower accuracy. In cohort 005, Q4_K_M activated on 61/64 prompts. The F16 additivity residual was −43.75 points (descriptive family interval −68.75 to −18.75), inconsistent with the homogeneous tree's required equality. Accordingly, the decision log withheld C/A/B latent-route estimates.

The agreement conditions also became important controls: cohort 016 reproduced large order changes even when both studies supported the same action. That limits a conflict-only explanation. The psychology-inspired framework helped motivate diagnostics, while the later order crossover and frozen replication provide their own experimental evidence. There is no controlled comparison quantifying how much research progress was caused by adopting the framework; assigning a percentage contribution would be unsupported.

The current defensible statement is: **the adaptation helped distinguish apparent conflict robustness from action bias and motivated presentation diagnostics; its latent decomposition remains unvalidated.** See [cohort 005](../experiments/cohort_005/summary.md), [cohort 016](../experiments/cohort_016/summary.md), and [synthetic validation](../results/design_validation/VALIDATION_REPORT.md).

## 11. Complementary adaptation for the next study

Retain process dissociation and add a focused signal-detection/psychophysics study, with psychometric construct validation and competing decision strategies. The [interdisciplinary follow-up specification](INTERDISCIPLINARY_FOLLOWUP.md) is the operational design and records all unresolved choices.

Jones (2016), [cue combination and Signal Detection Theory](https://discovery.ucl.ac.uk/id/eprint/1504279/), supplies a measurement approach for distinguishing discrimination from response criterion and comparing cue-combination predictions. We propose graded causal and observational evidence, crossed with presentation, to test whether precision changes evidence sensitivity or action propensity. The transfer does not imply Gaussian neural evidence, a human perceptual mechanism or unique route identification. Different integration models can predict similar sensitivities.

Löhn et al. (2024), [requirements for psychological testing of LLMs](https://aclanthology.org/2024.inlg-main.19/), motivates explicit reliability and construct-validity checks. Test meaning-preserving paraphrases, source identifiers and output mappings; add matched noncausal controls and independent task forms. Formal measurement-invariance claims require additional modeling and identification, not simply a nonsignificant wording interaction.

The judgment-and-decision component consists of independently counterbalanced source position, truthful source descriptions and action-response mappings, with held-out comparison of causal, historical, positional and constant-action strategies. These manipulations must produce distinguishable predictions before collection. Better prediction supports a behavioral model, not proof of a psychological or neural process.

The bounded [cohort 018 implementation](../experiments/cohort_018/README.md) now provides graded-evidence development tasks, SDT summaries, controls and fixed-strategy diagnostics; no model inference has run. Formal validation, psychophysical model fitting and confirmatory registration remain prospective. Established methods do not become novel merely through combination; the publication contribution must be a validated measure and new discriminating evidence. Adding further disciplinary frameworks is lower priority than controls, adequate reference competence and independent model-family replication. New source records were checked on 13 November 2026.
