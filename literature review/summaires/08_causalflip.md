# CausalFlip: A Benchmark for LLM Causal Judgment Beyond Semantic Matching

- **Authors:** Wang, Yuzhe; Zhu, Yaochen; Li, Jundong
- **Date / version:** 2026-02-23; downloaded revision: 2026-06-25 (v2)
- **Publication status:** arXiv preprint; abstract page says under review
- **Theme:** causal versus associative behavior
- **Primary source:** [2602.20094v2](https://arxiv.org/abs/2602.20094v2)
- **Downloaded paper:** [PDF (10 pages)](../papers/08_causalflip.pdf)
- **Evidence locations:** PDF pp. 1-7; paired construction and experimental comparisons. Page numbers refer to PDF positions.

## Research question, approach and findings

Builds semantically similar question pairs with opposite causal answers using chain, confounder and collider relationships. Additional noisy prefixes leave the underlying causal logic unchanged while stressing semantic shortcuts. The authors compare training paradigms and report that explicit chain-of-thought supervision can still be misled, while their internalized-reasoning approach improves causal grounding.

## Critical assessment

This closely matches the proposed distinction between causal reasoning and semantic association. It is a question-answering benchmark, however, and does not itself show quantization causes shortcut reliance. Synthetic event triples also cover only a limited slice of causal reasoning.

## Application to CausalFade (reviewer's proposal)

Adapt paired contrasts for every precision setting and test the precision-by-shortcut-conflict interaction. Counterbalance answer labels and paraphrases. Use the pairs as diagnostics alongside an interactive environment, so the project remains about agents making interventions.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
