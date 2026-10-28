# Executive summary: quantization, causal reasoning and AI agents

Prepared **28 October 2026** for CausalFade, an advanced statistics course project.

## Scope and reading guide

This focused review contains **14 papers: eight first released or published in 2026 and six dated 2025**. Two of the 2025 preprints have downloaded revisions from 2026; one is an ICLR 2026 conference paper. Dates refer to arXiv first submission for preprints and proceedings/journal publication for published sources. Nothing is included solely because an older paper received a recent update. PRISM was published online on 6 October 2026; its publisher's December issue metadata is recorded separately rather than treated as a future online publication.

Every paper has a downloaded PDF and an individual Markdown summary. The [reading index](READING_INDEX.md) links all 14 papers, summaries and primary source records. The [manifest](paper_manifest.json) records versions, source URLs, file sizes, page counts and SHA-256 checksums. The `summaires` directory intentionally preserves the spelling requested for this project.

This is a targeted literature search, not a systematic review or meta-analysis. Search themes included low-bit reasoning degradation, quantization and causality, recall versus contextual knowledge, semantic shortcuts, and interactive causal agents. Sources were verified against arXiv, ACL Anthology and the publisher record, and downloaded text was inspected. Papers outside 2025-2026 and general compression methods without a clear connection to the research question were not selected. Preprint status is stated explicitly where peer-reviewed publication was not verified. Reported results have not been independently reproduced.

## Overall judgment

**The topic is suitable, but its strongest defensible target is behavioral causal decision-making under controlled compression.** The motivating claim that quantization “severs internal causal graphs” is substantially stronger than the evidence this project can obtain from answer accuracy or agent-produced graphs alone.

The reviewed literature connects three complementary strands:

- **Direct quantization and causal reasoning:** [paper 01](summaires/01_compressed_causal_reasoning.md).
- **General reasoning failures, recovery and component sensitivity:** papers [02](summaires/02_quantization_inflates_reasoning.md), [03](summaires/03_extreme_low_bit_inference.md), [04](summaires/04_reasoning_qat_systematic_study.md), [05](summaires/05_quantization_hurts_reasoning.md), [06](summaires/06_quantization_meets_reasoning.md), [07](summaires/07_when_reasoning_meets_compression.md) and [12](summaires/12_prism.md).
- **Tests of causal competence and agent experimentation:** papers [08](summaires/08_causalflip.md), [09](summaires/09_causalab.md), [10](summaires/10_active_causal_discovery_benchmark.md), [11](summaires/11_causalds.md), with background from [13](summaires/13_causaleval.md) and [14](summaires/14_causal_inference_llm_survey.md).

## What the evidence supports

**Selective causal degradation remains a hypothesis.** The most directly related study reports substantial four-bit robustness in its static causal benchmarks. That makes a blanket collapse claim inappropriate and makes a careful extension scientifically worthwhile. [Primary study](https://arxiv.org/abs/2512.13725v2)

**Alternative explanations require explicit controls.** Process-level failures, recall loss and numerical execution errors all provide plausible explanations for lower causal-task scores. Papers 03, 06 and 12 motivate separating these outcomes rather than labeling every error a loss of causal reasoning. [Low-bit failure analysis](https://arxiv.org/abs/2606.02011v1), [step-level errors](https://arxiv.org/abs/2505.11574v4), [recall diagnostics](https://link.springer.com/article/10.1007/s10791-026-10580-5)

**Effects depend on the evaluation regime.** Papers 02 and 05 differ on output-length changes. Compare model families, precision formats, quantizers, prompts and budgets before interpreting this as a general disagreement. [Token-inflation study](https://arxiv.org/abs/2606.25519v2), [COLM study](https://arxiv.org/abs/2504.04823v2)

**Good predictions and faithful causal hypotheses are distinct outcomes.** CausaLab explicitly separates these, while CausalFlip challenges semantic shortcuts. Both are useful design references for avoiding an accuracy-only project. [CausaLab](https://arxiv.org/abs/2605.26029v2), [CausalFlip](https://arxiv.org/abs/2602.20094v2)

**Benchmark calibration matters.** ACDB illustrates why classical and random baselines are necessary. CausalDS adds identification, estimation and justified abstention to agent evaluation. [ACDB](https://arxiv.org/abs/2609.31675v1), [CausalDS](https://arxiv.org/abs/2607.08093v2)

These are complementary findings rather than independent estimates of one common effect. Pooling their accuracy differences would mix different tasks, treatments, models and populations.

## Recommended research question and contribution

> Does aggressive post-training quantization increase an AI agent's reliance on misleading associations when choosing interventions, beyond its general effect on task performance?

The defensible contribution is a paired experiment combining controlled precision treatments, fresh SCM-generated worlds, shortcut-conflict contrasts and agent action outcomes. This is a proposed gap suggested by this collection, **not a claim that no other paper has studied any part of it**.

Keep three kinds of graph distinct:

1. The simulator's true causal graph.
2. The causal graph the agent reports or uses explicitly.
3. The model's internal computational mechanisms.

Recovery of the second against the first measures an expressed causal hypothesis. It does not directly reveal the third.

## Practical implementation first, with a prespecified experiment

Start with one manageable open-weight checkpoint and a fixed agent harness. Compare the original precision with supported 8-, 4-, 3- and 2-bit PTQ variants, recording the actual quantizer and effective precision. Do not force unsupported formats or assume different quantizers isolate bit width. Keep activation and KV precision constant initially. Add a second checkpoint only after the pipeline works.

Generate small causal worlds with exact reference answers and paired task conditions where predictive associations agree with or conflict with beneficial interventions. Construct these conditions deliberately: preserve the target causal effect where possible, and pilot that arithmetic, wording and difficulty are sufficiently matched. Exact matching across conditions is an assumption to investigate, not a property guaranteed by calling tasks paired.

Give agents the same initial data, tool permissions and action budgets for a given world. Permit their later actions and observations to diverge; those differences are part of the precision effect on an interactive policy. Save complete trajectories, world identifiers, checkpoints, calibration data provenance, seeds, failures and stopping reasons.

Use automated reference scoring for intervention success. Record secondary outcomes separately: graph recovery, treatment-effect estimation error, interval coverage where requested, correct abstention, tokens, tool validity, repetition and truncation. Include closed-book recall, context comprehension and matched noncausal execution controls. Classical causal procedures and random policies provide comparison baselines.

## Statistical analysis: estimate a defined causal effect

Let A(p,c) be expected intervention success under precision treatment p and shortcut condition c, averaged over the prespecified world population. Define:

    ConflictPenalty(p) = A(p, aligned) - A(p, conflicting)
    Delta(p) = ConflictPenalty(p) - ConflictPenalty(full precision)

For a prespecified directional test, **H0: Delta(p) <= 0** versus **H1: Delta(p) > 0**. The result targets an increased behavioral conflict penalty. It does not establish internal graph severing or completely eliminate all general-capacity explanations; controls and matched task design strengthen that interpretation.

Evaluate all treatments on the same independently generated worlds. Randomize run order to reduce operational drift. Analyze success using a hierarchical binomial model with precision-by-conflict terms and world clustering, then report standardized probability differences and intervals. A logistic interaction coefficient is not itself the probability-scale Delta above. With few checkpoints, model-specific effects are preferable to strong population claims about all LLMs.

Use paired world-level bootstrap intervals as a robustness check. Runs, questions and paraphrases sharing a world are not independent causal-world samples. Estimate sample size by pilot-based simulation, preselect the primary precision contrast, and address multiplicity for additional contrasts. This factorial contrast does not require invoking observational difference-in-differences or a parallel-trends argument.

Treat decoding length, looping and tool-use failures as outcomes or possible mediators. Do not automatically adjust them away when estimating the total effect of quantization. Formal mediation would require additional identification assumptions and preferably randomized mediator interventions. Separately, a recovery treatment involving fine-tuning or high-precision assistance changes more than precision and needs its own comparison.

If the desired conclusion is preservation, preregister a practically meaningful tolerance and use equivalence/noninferiority analysis. Failing to reject degradation is not evidence of equivalence.

## Visualization and interpretation

After data collection, prioritize effect estimates with uncertainty: performance versus precision by conflict condition; paired-world outcome changes; precision-by-task contrasts; failure-category proportions; and accuracy versus compute. Keep graph recovery separate from final task success. Avoid fitting a precise collapse threshold to a handful of precision settings without adequate data.

Evidence for increased shortcut reliance requires more than a general accuracy drop: a meaningful conflict interaction, corroborating diagnostics and robustness to task-design choices would strengthen the conclusion. A deficit explained mainly by execution failure would support a different mechanism. Well-powered evidence of practical preservation would also be a valuable course result.

## Suggested reading order

Read **01 → 08 → 09 → 12 → 03 → 10 → 11** first. These establish the closest prior study, shortcut-sensitive tests, interactive causal evaluation, recall controls, process failures and statistical task design. Then read **05, 02, 06, 07 and 04** for quantization choices and possible mechanistic extensions. Use **13 and 14** to organize terminology and the related-work section.

The implementation and statistical proposals in this document are reviewer recommendations drawn from the collection; they are not methods already validated by these papers for CausalFade.
