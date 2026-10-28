# What Makes Low-Bit Quantization-Aware Training Work for Reasoning LLMs? A Systematic Study

- **Authors:** Lv, Keyu; Zhang, Manyi; Xia, Xiaobo; Ni, Jingchen; Yan, Shannan; Yu, Xianzhi; Hou, Lu; Yuan, Chun; Bai, Haoli
- **Date / version:** 2026-01-21 (v1)
- **Publication status:** arXiv preprint; peer-reviewed publication not verified
- **Theme:** quantization and recovery
- **Primary source:** [2601.14888v1](https://arxiv.org/abs/2601.14888v1)
- **Downloaded paper:** [PDF (14 pages)](../papers/04_reasoning_qat_systematic_study.pdf)
- **Evidence locations:** PDF pp. 1, 3-8, 9; empirical comparisons and limitations. Page numbers refer to PDF positions.

## Research question, approach and findings

Systematically studies quantization-aware training for reasoning models. Knowledge distillation, post-training-quantization initialization and calibration/training-domain alignment form the Reasoning-QAT workflow. The authors also investigate reinforcement learning after a viable initialization. The evaluated workflow improves low-bit reasoning over PTQ baselines, including two-bit settings. Training is primarily math-oriented, with limited cross-domain transfer noted.

## Critical assessment

The quality of a low-bit model depends on its training and calibration history, not only its nominal bit width. These experiments do not directly assess causal-agent decisions. Comparing a QAT model with an untouched full-precision model bundles precision changes with additional training.

## Application to CausalFade (reviewer's proposal)

Use PTQ as the first controlled treatment. Consider QAT only as a later recovery experiment with an appropriate training-matched comparison. Record calibration data and checkpoint provenance in every run.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
