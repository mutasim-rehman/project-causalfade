# Active Causal Discovery Benchmark: Evaluating LLM Agents Under Budgeted Interventions

- **Authors:** Deb, Sagar; Shah, Devam; Krishnan, Ashwanth
- **Date / version:** 2026-09-16 (v1)
- **Publication status:** arXiv preprint; explicitly a preliminary benchmark audit
- **Theme:** interactive causal agents
- **Primary source:** [2609.31675v1](https://arxiv.org/abs/2609.31675v1)
- **Downloaded paper:** [PDF (12 pages)](../papers/10_active_causal_discovery_benchmark.pdf)
- **Evidence locations:** PDF pp. 1-3, 10; scoring contract and Section 6.4. Page numbers refer to PDF positions.

## Research question, approach and findings

Defines budgeted observe-intervene-submit interactions in linear-Gaussian SCMs, separating skeleton recovery, directed-graph recovery and intervention efficiency. PC with active orientation outperforms the evaluated LLM agents on directed F1. A random-DAG baseline obtains a substantial score in dense worlds. The authors identify density leakage, eight seeds per level and limited backbone coverage as important limitations.

## Critical assessment

This is useful precisely because it audits benchmark weaknesses rather than treating every nonzero score as causal understanding. Its sample size is inadequate for fine-grained rankings, and causal sufficiency and linearity narrow the target setting.

## Application to CausalFade (reviewer's proposal)

Include random, observational-only and classical causal-discovery baselines. Pilot graph density and difficulty before the main experiment. Estimate uncertainty over independent worlds and expand the number of seeds rather than inflating apparent sample size through paraphrases of the same world.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
