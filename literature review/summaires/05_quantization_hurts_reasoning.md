# Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models

- **Authors:** Liu, Ruikang; Sun, Yuxuan; Zhang, Manyi; Bai, Haoli; Yu, Xianzhi; Yu, Tiezheng; Yuan, Chun; Hou, Lu
- **Date / version:** 2025-04-07; downloaded revision: 2025-08-18 (v2)
- **Publication status:** COLM 2025; venue stated on arXiv and in the paper
- **Theme:** quantization and reasoning
- **Primary source:** [2504.04823v2](https://arxiv.org/abs/2504.04823v2)
- **Downloaded paper:** [PDF (25 pages)](../papers/05_quantization_hurts_reasoning.pdf)
- **Evidence locations:** PDF pp. 1-8; study design and main results. Page numbers refer to PDF positions.

## Research question, approach and findings

Evaluates weight, activation and KV-cache quantization across DeepSeek-R1-distilled families and other reasoning models on mathematics, science and coding. W8A8 and W4A16 can preserve measured performance in tested settings, while lower precision introduces greater risk. Model scale, origin and task difficulty affect robustness. Unlike paper 02, this study does not find increased output lengths in its evaluated regime.

## Critical assessment

This is strong background for selecting compression conditions, but general reasoning benchmarks do not isolate causal reasoning. Claims of lossless performance should be interpreted within the tested benchmarks and uncertainty, not as a universal guarantee.

## Application to CausalFade (reviewer's proposal)

Hold activation and KV-cache precision fixed while varying weights initially. Include multiple checkpoints if feasible, and do not equate identical bit widths across different quantizers. Treat output-length disagreement as a question to test, not a contradiction to hide.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
