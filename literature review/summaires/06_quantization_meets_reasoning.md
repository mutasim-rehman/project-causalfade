# Quantization Meets Reasoning: Exploring and Mitigating Degradation of Low-Bit LLMs in Mathematical Reasoning

- **Authors:** Li, Zhen; Su, Yupeng; Wang, Songmiao; Yang, Runming; Xie, Congkai; Liu, Aofan; Li, Ming; Cao, Jiannong; Xie, Yuan; Wong, Ngai; Yang, Hongxia
- **Date / version:** 2025-05-16; downloaded revision: 2026-01-20 (v4)
- **Publication status:** arXiv preprint; peer-reviewed publication not verified
- **Theme:** quantization and reasoning
- **Primary source:** [2505.11574v4](https://arxiv.org/abs/2505.11574v4)
- **Downloaded paper:** [PDF (27 pages)](../papers/06_quantization_meets_reasoning.pdf)
- **Evidence locations:** PDF pp. 1-8; process-level analysis and recovery experiments. Page numbers refer to PDF positions.

## Research question, approach and findings

Examines AWQ, GPTQ and SmoothQuant on Qwen/LLaMA models and mathematical benchmarks using aligned solution steps. Method and execution errors increase more than high-level conceptual errors, and an early faulty step can propagate to the final answer. A targeted measure-locate-restore workflow uses small curated training sets to recover performance in evaluated low-bit settings.

## Critical assessment

The process-level distinction is valuable for separating damaged execution from lost knowledge. However, mathematical error labels and successful fine-tuning do not identify an internal causal graph. Alignment and annotation choices also matter when interpreting the first erroneous step.

## Application to CausalFade (reviewer's proposal)

Annotate the earliest observable failure in agent trajectories. Distinguish choosing an invalid causal adjustment from correctly identifying the adjustment but executing code incorrectly. Use trace categories as secondary outcomes; avoid claiming that the written trace faithfully exposes every internal computation.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
