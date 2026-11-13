# Sensitivity, response bias and presentation in causal decisions

**Version 0.2 — 13 November 2026. Status: methodology amendment with a prepared development implementation.** The broader validation and confirmation study remains prospective. [Cohort 018](../experiments/cohort_018/README.md) now has executable generation, validation, resumable inference, semantic scoring and descriptive analysis, with no model inference performed. Its input fixture and operational gate are fixed before inference; this is not a registered confirmatory protocol. See the [lab runbook](LAB_FOLLOWUP_RUNBOOK.md). Existing frozen cohort protocols remain unchanged.

## 1. Scientific purpose and contribution

Ask whether precision configurations change discrimination of beneficial versus harmful interventions, the propensity to activate, or the weighting of evidence source and presentation. Causal inference remains central: an SCM supplies intervention ground truth, and randomized versus confounded historical evidence must be distinguished. Supplied-evidence decisions do not establish autonomous discovery or agentic experimentation.

Retain the agreement/conflict logic of process dissociation and the CNI-style candidate tree. Add signal detection theory and graded-evidence psychophysics as a complementary measurement approach. Use psychometric construct validation to test whether the resulting measures survive changes unrelated to the causal target. Judgment-and-decision research motivates targeted presentation manipulations and explicit rival strategies, rather than another assumed latent-process taxonomy.

The intended contribution is discriminating explanations of a reproducible behavioral phenomenon. Adapting established methods is not by itself a first-ever contribution, and adding disciplines does not guarantee Q1 publication. Update the scoped literature search before freezing the study and again before submission; select journals by scope and verify any quartile against its named database, category and year.

## 2. What existing evidence establishes

- Process-dissociation design exposed action bias: in cohort 005, Q4_K_M activated on 61/64 items while its smaller conflict penalty coincided with lower overall accuracy.
- The homogeneous C/A/B tree is not validated on LLM responses. Cohort 005's F16 additivity residual conflicts with its required equality in an exploratory check. Synthetic recovery establishes implementation behavior under assumed generators, not psychological construct validity; an alternative logistic generator is observationally equivalent.
- Cohort 016 prospectively replicated a 7B Q4_K_M conflict order effect on 96 fresh families: +62.5 percentage points, 95% family-level t interval +56.6 to +68.4. F16 also changed by order, and aligned items changed substantially despite source agreement. The result supports presentation sensitivity, not selective causal damage.
- Both 14B cohort 017 arms completed 768 prompts. The automated analysis failed on a missing NumPy dependency and was subsequently recovered locally with a disclosed zero-variance inference guard. Conflict totals are Q8_0 104/192 randomized-first and 96/192 historical-first; Q4_K_M 96/192 in each order. The [paired report](../experiments/cohort_017/summary.md) does not reproduce the large 7B effect. Families were reused and Q8_0 is quantized, so the result remains exploratory.

Sources: [cohort 005](../experiments/cohort_005/summary.md), [synthetic validation](../results/design_validation/VALIDATION_REPORT.md), [cohort 016](../experiments/cohort_016/summary.md), [cohort 017](../experiments/cohort_017/README.md), and its [analysis failure log](../experiments/cohort_017/analysis.log). No percentage contribution of the psychology adaptation can be estimated: there was no with-versus-without-framework experiment.

## 3. Design and competing predictions

Develop on separate families, then freeze one primary precision contrast and one primary endpoint. A matched F16 reference is preferable when feasible; report a Q8 reference explicitly as quantized. Do not assume reference competence transfers from cohort 015: F16 conflict performance was weaker in cohort 016. Check both causal directions and presentation conditions using a predeclared development gate.

Within an independent family block, manipulate:

1. **Causal evidence:** signed intervention effect, balanced beneficial/harmful directions and several prespecified nonzero magnitudes. Include weak-to-strong levels feasible under the SCM. Exactly zero effects, if included, require a separate indifference/scoring rule and are excluded from binary beneficial/harmful SDT summaries.
2. **Observational evidence:** sign and absolute magnitude, matched across agreement/conflict conditions at each causal magnitude. Validate outcome bounds, positivity, oracle effects and distinguishability after display rounding. Freeze a feasible grid on development data; do not selectively drop failed cells after seeing responses.
3. **Position and source identity:** independently counterbalance which source appears first and which neutral study identifier denotes the randomized source. Keep the description of the true evidence-generating mechanism attached to its data. Never swap the word randomized onto confounded rates while claiming an unchanged world. Source-name permutations test superficial labels; changing design descriptions changes supplied information and requires its own treatment.
4. **Response mapping:** counterbalance neutral output tokens mapped to activate/decline, while keeping intervention meaning and utility fixed. A substantive gain/loss or action/inaction reframe changes task semantics and must be analyzed separately.
5. **Transfer variants:** prespecified meaning-preserving paraphrases and domains, with causal graph, numbers, evidence quality and answer contract held fixed where possible. Record any unavoidable matching differences.

Precision is crossed with the same task blocks. Every request starts in a fresh context; do not treat prompt twins as sequential human exposure. Randomize execution order within feasible resource blocks and preserve complete within-family pairs. A staged or balanced fractional design is acceptable if specified in advance with its identifiable effects and aliases; do not claim to estimate interactions the selected design confounds.

Candidate explanations make different predictions:

- **Causal-evidence sensitivity change:** the response curve's dependence on signed causal strength changes by precision after balancing other cues; a matched noncausal contrast is needed for selectivity.
- **Response-bias change:** a shift toward activation across balanced effect directions can occur without a comparable change in discriminability. A curve intercept alone is insufficient if other cue effects are omitted.
- **Historical-cue weighting:** action depends on signed observational strength conditional on causal evidence, not merely on physical position.
- **Position or output-token strategy:** reversing positions or token mappings changes actions despite unchanged causal implications, including on aligned items.

These explanations can coexist. Their signatures guide interventions and prediction comparison; none by itself proves an internal cognitive route.

## 4. Signal-detection summaries and psychophysical curves

Define signal as a beneficial intervention (`tau > 0`) and response yes as the semantic action activate, after decoding the frozen response mapping. For each precision and prespecified presentation/strength stratum:

```text
H = P(activate | tau > 0, valid response)
F = P(activate | tau < 0, valid response)
d_prime = Phi_inverse(H) - Phi_inverse(F)
criterion = -0.5 * [Phi_inverse(H) + Phi_inverse(F)]
```

Report hits, false alarms, denominators and validity alongside both summaries. Balance association direction and family weighting; do not pool different strengths or presentation conditions without an explicit standardization target. Invalid responses remain failures for primary scheduled-task accuracy and a separate outcome; never silently map them to decline for SDT. Conditional-validity summaries can describe different selected populations across formats.

The usual d-prime/criterion interpretation assumes an equal-variance Gaussian latent-evidence model. Binary responses alone do not establish that assumption or identify an ROC curve. Treat these as model-dependent descriptive coordinates unless additional design and fit checks support stronger interpretation. Freeze a boundary rule, such as adding 0.5 to successes and 1 to denominators for hit/false-alarm rates, and report sensitivity to that choice. This correction does not create information when responses saturate.

Fit a family-dependent binary-response model with signed causal strength, signed observational strength, source position, response mapping, precision and prespecified interactions. A candidate link is probit, but choose link, regularization, random effects and fallback rules in development. Independent evidence manipulations are needed to separate cue slopes. Plot probability of activation against signed causal effect at fixed other cues. Slopes and threshold shifts describe behavior on this scale; they are not direct measurements of neural noise or causal circuitry. Do not estimate a threshold beyond the observed evidence range or when a curve does not cross the target probability.

## 5. Construct validation and controls

Define causal competence narrowly as choosing the beneficial intervention from specified causal evidence under stated identification assumptions. Keep reliability, task robustness and construct validity distinct.

- **Robustness/reliability:** compare paired effects across prespecified paraphrases, neutral source names and output mappings, with family-cluster uncertainty. Repeating identical greedy calls is a determinism check, not independent reliability evidence.
- **Convergent evidence:** use a separate task form testing the same intervention target, such as selecting which intervention has higher success versus choosing activate/decline. Assess family-level agreement and precision effects while documenting differences in task demands; correlation alone is insufficient validation.
- **Discriminant/specificity evidence:** include matched noncausal numerical comparison and evidence-selection tasks, plus comprehension checks for source identity and response mapping. Match numerical operations, context and contract as closely as possible. A causal-versus-control precision interaction strengthens a selective interpretation; a null control result alone does not.
- **Measurement comparability:** test prespecified precision-by-wording/mapping interactions. Such interactions warn that scores depend on test administration. Formal measurement-invariance or differential-item-functioning claims require an identifiable multi-item model, anchor assumptions and adequate checkpoint/item coverage; two formats alone do not justify a latent ability scale. Do not remove affected items based on confirmatory outcomes.
- **Transfer:** hold out entire families and, for a domain-transfer claim, whole domains/templates. A new seed from the same generator tests within-generator generalization. Independent model-family replication is required before broad claims about LLMs.

Response confidence, self-reported reasoning and latency are optional separate outcomes. Do not equate prose rationales with the process that generated an answer or CPU wall time with human reaction time.

## 6. Rival models and held-out evaluation

Compare the C/A/B tree, continuous evidence integration, causal-source-only, historical-source-only, first/last-source and constant-action strategies. Include a learnable position/token-bias model and mixtures only where the design can identify them. Apply the tree within its stated invariance domain; adding free parameters for every cell would remove its original testable restriction.

Freeze candidate models, priors/regularization, fitting procedures, probability smoothing for deterministic baselines and fallback rules. Split entire families before fitting; estimate tuning choices only inside development/training folds. Evaluate probabilistic predictions on untouched families using log loss or another prespecified proper scoring rule, with paired family uncertainty. Report calibration, fit violations, boundary estimates and complexity. Assess whether interventions distinguish candidate predictions before spending on inference.

Better held-out prediction supports a behavioral description, not proof of a literal processing route. Where models remain observationally equivalent, report non-identification. Model comparison on already examined cohorts is exploratory, and adding a newly inspired model after test inspection requires another untouched evaluation.

## 7. Primary endpoint, power and reporting

Choose one primary checkpoint/precision contrast and one primary endpoint after development and before new confirmation. Options include a standardized precision difference in causal-strength response curves, or a prespecified format-by-presentation probability contrast. These are alternatives, not co-primary tests by default. If using d-prime as primary, first establish stable estimation and boundary behavior under the planned family structure. The original conflict-penalty contrast remains available as an explicitly assigned secondary endpoint unless chosen primary anew.

State the target population, evidence-strength weights, treatment bundle, smallest effect of interest, test direction, alpha, interval procedure, multiplicity family and stopping rule. Power/coverage simulations must reproduce family dependence, cue interactions, separation, invalidity, boundary correction and selected endpoint. Cohort 016's power calculation and sample size cannot be reused as justification for this different design. Repeated requests and task variants do not increase the independent-family count.

Freeze mathematical validators, response contracts and analysis code before inference. Use cluster-based uncertainty and/or a validated hierarchical model; a link-scale interaction is not a probability-scale effect. Keep existing cohort 016 confirmation separate from new hypotheses motivated by its results. Preserve unsuccessful reference screens and all scheduled responses. A change to improve reference competence creates a documented new task version, not a reason to selectively retain successful cases.

For publication, aim to deliver a validated measurement approach, a discriminating experiment, an independent checkpoint-family replication, and a reproducible release with a claim-to-artifact ledger. A negative or boundary result is informative when its precision and scope support the stated conclusion. No journal quartile or acceptance outcome is promised.

## 8. Implementation sequence and unresolved choices

1. The archived 14B paired report is now complete from local analysis; preserve the original lab failure log and verify the lab environment before new inference. This is not confirmation of the new design.
2. A bounded development implementation now supplies strength-grid generation, counterbalancing and rounding/oracle validators, response mapping, numerical/comprehension controls, SDT summaries and fixed-strategy scoring. Hierarchical curve fitting, fitted tree/integration comparison and formal construct validation remain prospective. The shipped design uses two causal strengths and one observational strength; source identifiers and response mappings are balanced between families, with optional separately generated within-family mapping crossing.
3. Use separate development families to establish competence, useful evidence ranges, model distinguishability, measurement robustness and feasible compute. Prioritize a manageable crossed design before broader model-family replication.
4. Select the primary endpoint and contrast, simulate power/coverage, determine family count and freeze the complete protocol in [decisions before collection](DECISIONS_BEFORE_COLLECTION.md).
5. Collect untouched families, then perform independent model-family replication and report boundary conditions.

Unresolved values include evidence grid, checkpoint/reference, response mapping tokens, control templates, model specifications, robustness tolerances, family count and primary endpoint. They must be resolved by development and prospective freezing, not invented here as if registered.

## 9. Source lineage and limits of transfer

- Jacoby (1991), Gawronski et al. (2017), Wu and Deng (2025), and Heck et al. (2018): existing agreement/conflict and processing-tree lineage; see [methodology adaptation](METHODOLOGY_ADAPTATION.md).
- Jones (2016), [A tutorial on cue combination and Signal Detection Theory](https://discovery.ucl.ac.uk/id/eprint/1504279/), DOI 10.1016/j.jmp.2016.04.006: source for comparing cue-integration predictions and sensitivity assumptions. It concerns sensory judgments, not LLM quantization; our adaptation is a research proposal. Similar sensitivities can arise from different combination models.
- Löhn et al. (2024), [Is Machine Psychology here?](https://aclanthology.org/2024.inlg-main.19/), DOI 10.18653/v1/2024.inlg-main.19: source for reliability, construct validity and requirements when transferring human psychological assessments to LLMs. It does not validate our proposed causal measure.

Source records checked on 13 November 2026. This is a targeted methodological update, not a systematic novelty review. Bibliographic entries are in [references.bib](references.bib).
