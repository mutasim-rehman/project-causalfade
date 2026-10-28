# PRISM a diagnostic framework for parametric recall degradation in quantized large language models

- **Authors:** Vaish, Swastik; Gautam, Arpit Singh; Tiwari, Varun; Yadav, Jitendra Singh
- **Date / version:** 2026-10-06 online publication; journal issue metadata says 2026/12
- **Publication status:** Discover Computing 29, article 700 (2026); open-access journal article
- **Theme:** recall versus context and mechanisms
- **Primary source:** [Publisher record](https://link.springer.com/article/10.1007/s10791-026-10580-5)
- **Downloaded paper:** [PDF (38 pages)](../papers/12_prism.pdf)
- **Evidence locations:** PDF pp. 1-4, 33-34; framework and limitations. Page numbers refer to PDF positions.

## Research question, approach and findings

PRISM separates parametric recall, contextual copying and comprehension using conflict probes, synthetic entities and component-wise quantization. Across tested small-model families and quantizers, closed-book recall deteriorates while copying remains more robust. MLP/FFN quantization affects recall more than attention quantization. The work runs within an 8GB GPU budget and explicitly limits component-level conclusions and model scale.

## Critical assessment

This is the most directly relevant control for the proposed forgetting explanation. Preserved copying is insufficient evidence of preserved reasoning. The authors also caution that component sensitivity is weaker evidence than proving a component stores a fact. Publisher online date qualifies this paper despite its later issue-date metadata.

## Application to CausalFade (reviewer's proposal)

Build separate closed-book recall, supplied-context comprehension and causal-decision controls. Use fictional entities to check leakage. If feasible, adapt matched component perturbations, while distinguishing component necessity under perturbation from a claim about stored causal representations.

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
