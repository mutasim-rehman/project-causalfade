# Compressed Causal Reasoning: Quantization and GraphRAG Effects on Interventional and Counterfactual Accuracy

- **Authors:** Nwaiwu, Steve; Jongsawat, Nipat; Tungkasthan, Anucha
- **Date / version:** 2025-12-13; downloaded revision: 2025-12-24 (v2)
- **Publication status:** arXiv preprint; peer-reviewed publication not verified
- **Theme:** direct quantization and causality
- **Primary source:** [2512.13725v2](https://arxiv.org/abs/2512.13725v2)
- **Downloaded paper:** [PDF (13 pages)](../papers/01_compressed_causal_reasoning.pdf)
- **Evidence locations:** PDF pp. 1, 6-9, 11; Sections 5.5-6 and limitations. Page numbers refer to PDF positions.

## Research question, approach and findings

Tests Llama-3-8B at BF16, INT8 and NF4 on 3,000 stratified CLadder examples and CRASS, with greedy decoding and an additional ground-truth-graph retrieval condition. Overall NF4 degradation is reported as under one percentage point; interventional questions are more sensitive than the aggregate score suggests. The evaluation includes bootstrap uncertainty. Graph augmentation modestly improves interventional performance.

## Critical assessment

This is the closest prior study and challenges any assumption that four-bit compression necessarily destroys causal competence. One model and static questions provide limited coverage of agents or extreme compression. A small observed difference is not itself an equivalence result. Graphs supplied to the prompt are external knowledge, not recovered neural circuits.

## Application to CausalFade (reviewer's proposal)

Replicate a narrow baseline before extending to 2/3-bit models and interactive interventions. Use this as the central related-work comparison, not evidence that the proposed project has already established its conclusion.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
