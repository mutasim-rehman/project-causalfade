# Causal Inference with Large Language Model: A Survey

- **Authors:** Jing Ma
- **Date / version:** Findings of NAACL 2025, April-May 2025
- **Publication status:** Findings of NAACL 2025; survey
- **Theme:** causal inference background
- **Primary source:** [Publisher record](https://aclanthology.org/2025.findings-naacl.327/)
- **Downloaded paper:** [PDF (13 pages)](../papers/14_causal_inference_llm_survey.pdf)
- **Evidence locations:** PDF pp. 1-7; preliminaries, task categories and future directions. Page numbers refer to PDF positions.

## Research question, approach and findings

Reviews LLM-assisted causal inference across tasks, methods, datasets and evaluation. It introduces structural causal models and distinguishes levels of causal queries, discussing how language-model knowledge can assist causal analysis. The survey highlights challenges including unverified causal ground truth, hallucinations and the need for better evaluation and interaction.

## Critical assessment

This supplies terminology and broad context rather than direct evidence for quantization-induced degradation. Much of the reviewed evidence comes from older studies, so the 2025 publication date does not make every underlying experiment a 2025 result. It should not be treated as an independent experimental replication.

## Application to CausalFade (reviewer's proposal)

Use it to separate causal discovery, identification, estimation and counterfactual inference in the proposal. Ground the experiment in a simulator with known assumptions, and independently justify the statistical estimator used to measure the effect of quantization.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
