# When Reasoning Meets Compression: Understanding the Effects of LLMs Compression on Large Reasoning Models

- **Authors:** Zhang, Nan; Kwek, Eugene; Zhang, Yusen; Nguyen, Ngoc-Hieu; Mitra, Prasenjit; Zhang, Rui
- **Date / version:** 2025-04-02; downloaded revision: 2026-03-02 (v3)
- **Publication status:** ICLR 2026; stated in the downloaded paper
- **Theme:** compression and mechanisms
- **Primary source:** [2504.02010v3](https://arxiv.org/abs/2504.02010v3)
- **Downloaded paper:** [PDF (27 pages)](../papers/07_when_reasoning_meets_compression.pdf)
- **Evidence locations:** PDF pp. 1-10; benchmarking, component attribution and selective protection. Page numbers refer to PDF positions.

## Research question, approach and findings

Compares quantization, pruning and distillation on DeepSeek-R1 variants across four reasoning datasets. It combines benchmarking with activation-based attribution and targeted component protection. The authors identify vulnerable final-layer and MLP modules; protecting approximately 2% of weights improves average accuracy by a reported 6.57% in their experiment. Knowledge and reasoning respond differently to compression.

## Critical assessment

This is the most useful bridge here from behavioral evaluation to component interventions. Nevertheless, compression methods change different properties, and an attributed reasoning component is not automatically a representation of a domain causal edge. Interpret the reported percentage in the paper's own metric rather than assuming percentage points.

## Application to CausalFade (reviewer's proposal)

If the behavioral result is robust, test selected component precision restoration with equal-weight-count controls. Keep pruning and distillation outside the primary quantization comparison. Specify the exact causal claim supported by each manipulation.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
