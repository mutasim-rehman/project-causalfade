# Quantization Inflates Reasoning: Token Inflation as a Hidden Cost of Low-Bit Reasoning Models

- **Authors:** Lian, Xinyu; Krichene, Walid; Huang, Beichen; Tanaka, Masahiro; Ruwase, Olatunji; Zhang, Li; Zhang, Minjia
- **Date / version:** 2026-06-24; downloaded revision: 2026-06-29 (v2)
- **Publication status:** arXiv preprint; peer-reviewed publication not verified
- **Theme:** quantization and reasoning
- **Primary source:** [2606.25519v2](https://arxiv.org/abs/2606.25519v2)
- **Downloaded paper:** [PDF (12 pages)](../papers/02_quantization_inflates_reasoning.pdf)
- **Evidence locations:** PDF pp. 1, 3-6; experimental setup and results. Page numbers refer to PDF positions.

## Research question, approach and findings

Evaluates low-bit reasoning across mathematical, coding, science and tool-use settings. INT3/INT4 models can maintain final-answer accuracy while producing longer, more repetitive reasoning. The authors propose a chain-of-thought token-inflation measure and examine serving costs and mitigation. Their results show that per-token efficiency and answer accuracy can miss a substantial behavioral change.

## Critical assessment

This supports measuring the process as well as the answer, but repetition is not direct evidence of associative reasoning or a damaged causal graph. Effects are conditional on model, quantizer and decoding setup. Its output-length result differs from paper 05, motivating a comparison of evaluation conditions.

## Application to CausalFade (reviewer's proposal)

Log generated tokens, latency, stop reasons and tool calls. Separate a fixed-token-budget experiment from a generous-budget sensitivity analysis; otherwise truncation may be mistaken for a selective causal deficit.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
