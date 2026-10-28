# CausaLab: A Scalable Environment for Interactive Causal Discovery Toward AI Scientists

- **Authors:** Yang, Junlin; Zhang, Dylan; Song, Xiangchen; Dai, Qirun; Liu, Xiao; Chen, Yuen; Vashishtha, Aniket; Shi, Jing; Tan, Chenhao; Peng, Hao
- **Date / version:** 2026-05-25; downloaded revision: 2026-05-28 (v2)
- **Publication status:** arXiv preprint; peer-reviewed publication not verified
- **Theme:** interactive causal agents
- **Primary source:** [2605.26029v2](https://arxiv.org/abs/2605.26029v2)
- **Downloaded paper:** [PDF (34 pages)](../papers/09_causalab.pdf)
- **Evidence locations:** PDF pp. 1-3, 7-12; setup, mechanism scores and limitations. Page numbers refer to PDF positions.

## Research question, approach and findings

Introduces an interactive synthetic laboratory with a hidden SCM. Agents observe records, intervene and predict a held-out outcome; explicit hypotheses permit graph and mechanism scoring. In a six-node observational setting, GPT-5.2-high achieves 92% task accuracy but 0.471 all-edge F1. Mixed observation/intervention strategies improve structural fidelity. The evaluated worlds contain 3-7 nodes and mostly linear mechanisms.

## Critical assessment

This demonstrates why predictive accuracy and recovered structure should be scored separately. An agent-written graph is still an externalized hypothesis, not a direct measurement of its neural representation. Synthetic mechanisms and a finite model/prompt suite constrain generalization.

## Application to CausalFade (reviewer's proposal)

Use this as the main interactive design reference. Score intervention success, graph recovery and exploration behavior independently. For precision comparisons, reuse world seeds and observation budgets, but allow actions and resulting observations to differ naturally across agents.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
