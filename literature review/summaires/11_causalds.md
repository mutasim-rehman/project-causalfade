# CausalDS: Benchmarking Causal Reasoning in Data-Science Agents

- **Authors:** Leban, Andrej; Saarinen, Theo; Sun, Yuekai
- **Date / version:** 2026-07-09; downloaded revision: 2026-10-14 (v2)
- **Publication status:** arXiv preprint; peer-reviewed publication not verified
- **Theme:** causal data-science agents
- **Primary source:** [2607.08093v2](https://arxiv.org/abs/2607.08093v2)
- **Downloaded paper:** [PDF (74 pages)](../papers/11_causalds.pdf)
- **Evidence locations:** PDF pp. 1-8, 60 onward; benchmark design and Appendix A.17. Page numbers refer to PDF positions.

## Research question, approach and findings

Generates causal data-science scenes from sampled SCMs, observational data and grounded narratives. Tasks span association, intervention and counterfactuals, often requiring code and tools. Some targets are intentionally unidentifiable, making abstention the correct response. The generator permits fresh exams. Limitations include synthetic realism and a graph-based identifiability policy that does not credit every alternative inferential strategy.

## Critical assessment

This is particularly relevant to an advanced statistics course because it tests whether agents can identify and estimate causal targets, not merely repeat causal language. However, failures combine reasoning, coding and data-analysis demands; no quantization comparison is established by this paper alone.

## Application to CausalFade (reviewer's proposal)

Borrow a small, transparent subset of identifiable and unidentifiable tasks. Grade identification, numerical estimation, interval coverage and abstention separately. Use ordinary statistical estimators as reference solutions, with assumptions and numerical tolerances documented.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
