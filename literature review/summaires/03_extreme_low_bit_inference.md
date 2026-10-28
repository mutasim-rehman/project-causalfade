# Extreme Low-Bit Inference in Reasoning Models: Failure Modes and Targeted Recovery

- **Authors:** Alimaskina, Ekaterina; Rudas, Darya; Shveykin, Denis; Molodtsov, Gleb; Vasiliev, Pavel; Beznosikov, Aleksandr
- **Date / version:** 2026-06-01 (v1)
- **Publication status:** arXiv preprint; peer-reviewed publication not verified
- **Theme:** quantization and reasoning
- **Primary source:** [2606.02011v1](https://arxiv.org/abs/2606.02011v1)
- **Downloaded paper:** [PDF (17 pages)](../papers/03_extreme_low_bit_inference.pdf)
- **Evidence locations:** PDF pp. 1-4, 9; failure taxonomy and limitations. Page numbers refer to PDF positions.

## Research question, approach and findings

Studies Qwen3 reasoning at two model scales using GPTQ-style W2A16/W4A16 inference. Two-bit traces exhibit looping, exhausted budgets and failures to commit to answers. The authors test high-precision planning and loop-rescue procedures. On MATH-500, reported Qwen3-8B accuracy rises from 17.2% to 74.2% with loop rescue.

## Critical assessment

A large final-answer drop can therefore reflect generation control rather than lost causal knowledge. Recovery uses selective high-precision assistance, so it is not a pure two-bit treatment. The limitations explicitly restrict quantizer and model-family generalization.

## Application to CausalFade (reviewer's proposal)

Include a failure taxonomy: incorrect inference, invalid tool action, repetition, truncation and missing final answer. Keep rescued runs as a separate intervention arm. Test whether any causal-task deficit remains after accounting descriptively for these process failures.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
