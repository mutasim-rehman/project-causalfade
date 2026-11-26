# Internal Scientific & Editorial Quality-Assurance Report (`REVIEW_REPORT.md`)

**Monograph Title:** *The Life of CausalFade: A Scientific Retrospective of Hypotheses, Experiments, Failures, Methodological Evolution, and Discovery*  
**Authors:** Mutasim ur Rehman (`i242514@isb.nu.edu.pk`), Ahmad Raza (`i242574@isb.nu.edu.pk`), and Umar Asghar (`i242532@isb.nu.edu.pk`) — Department of Artificial Intelligence & Data Science, National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad, Pakistan  
**Audited Repository Snapshot (`HEAD`):** `b7371530caa62d6e43a8e83ef6db361f6640f63a` (`origin/main`)  
**Confirmatory Release Tag:** `cohort-029-v1.0.0` (`76206c259caa488668a7556ce1bc53cb35d220da`)  
**Audit Date:** November 26, 2026

---

## Executive Audit Summary

Prior to finalizing this monograph, we conducted an internal eight-perspective audit spanning historical accuracy, causal theory, statistical inference, machine learning & quantization fidelity, artifact reproducibility, undergraduate pedagogical clarity, LaTeX typography/editorial rigor, and adversarial scientific skepticism. Below we document the scope checked by each perspective, specific defects caught and corrected during drafting and compilation, and residual scope boundaries disclosed to readers.

| Audit Perspective | Primary Scope Audited | Issues Identified & Remediated | Final Verdict |
| :--- | :--- | :--- | :--- |
| **1. Research Historian** | 320 Git commits (`4e2fe4f` to `b737153`), 31 cohort units, contemporaneous vs. retrospective claims, undocumented decisions | Separated Wave 1 (Oct 28), Wave 2 (Nov 1), and Wave 3 (Nov 19–25) literature; labeled Cohort 029 `Q4_K_M`-only model choice as undocumented; classified `CausalFade_Q1_Peer_Review_Report_2026-11-19.docx` explicitly as simulated/AI red-teaming rather than formal journal review. | **Pass** |
| **2. Causal Inference Specialist** | SCMs, $d$-separation, $\doop$-calculus, backdoor vs. mediator weighting, transportability, Rung 2 vs. Rung 3 boundaries | Verified exact algebraic derivations for `world-0000` (Cohort 001), confounder-vs.-mediator joint invariance (Cohorts 026–028), and `family-096` (`-57/10000`, `+311/20000`, `+107/10000`, `-211/20000` in Cohort 029). Kept Rung 3 counterfactuals strictly separated from Rung 2 scope. | **Pass** |
| **3. Statistician** | Family-cluster inference, Welch–Satterthwaite df, Hoeffding bounded CIs, zero-variance guards, non-equivalence interpretation | Verified $\widehat{\Delta} = -3.515625\text{ pp}$, $\widehat{\mathrm{SE}} = 2.1324\text{ pp}$, $\hat{\nu} = 67.53$, Welch $t$ CI $[-7.7713, +0.7400]\text{ pp}$, and Hoeffding radius $2\sqrt{\ln(40)/256} = 24.0081\text{ pp} \implies [-27.5237, +20.4924]\text{ pp}$. Enforced non-equivalence interpretation throughout. | **Pass** |
| **4. Machine Learning Researcher** | GGUF K-quantization (`BPW`), `llama.cpp` `b12176` runtime behavior, uncalibrated PTQ vs. `imatrix`/QAT, token inflation | Documented uncalibrated `llama-quantize` provenance (`docs/SSD_ASSET_REUSE.md`), Cohort 003 `--no-repack` SIMD check, Cohort 024 `Llama Q4_K_M`'s 448 control length-cap truncations, and `Mistral F16`'s 256/256 first-option policy. | **Pass** |
| **5. Reproducibility Auditor** | Immutability of tracked files & `manuscript/`, SHA-256 verification, raw count reconciliation (`48,208` scheduled / `48,170` persisted) | Caught and reconciled the manual prose transcription contradiction in `experiments/cohort_029/release/RESULTS.md` (`121/512, 416/512` vs. machine-verified `14/512, 497/512, 995` in `events.jsonl` and `secondary.json`) without modifying `RESULTS.md`. Confirmed `git diff` is completely empty on tracked files. | **Pass** |
| **6. Undergraduate Student Reader** | 6-layer pedagogical explanations, math-to-intuition bridges, technical glossary, clearly marked teaching examples | Added labeled **Constructed Teaching Example** blocks (e.g., round-number confounder-vs.-mediator table in Chapter 3) distinct from archived **Worked Examples**, plus Appendices O (Notation) and P (Glossary). | **Pass** |
| **7. Academic Editor** | LaTeX build cleanliness, PDF bookmarks, vector Type-42 font embedding, table wrapping, citation completeness | Eliminated stray Markdown tokens and `\n` escape errors via `sanitize_tex.py`, resolved duplicate `hyperref` page-i anchor (`\pagenumbering{Alph}` on `titlepage`), wrapped 64-char SHA-256 hashes in `\nolinkurl`, and applied ragged-right wrapping with breakable `/` in narrow `longtable` columns. Verified 39/39 BibTeX entries resolve cleanly with zero `??` citations or cross-references. | **Pass** |
| **8. Skeptical Scientific Reviewer** | Anti-hype check, exploratory-vs.-confirmatory firewall, shortcut disclosure, uncertified metadata disclosure | Ensured zero incomparable cross-cohort accuracy curves were plotted; highlighted Cohort 016's retrospective `768/768` smaller-gap shortcut directly alongside its $p=1.24\times 10^{-37}$ order test; disclosed `certified: false` placeholder strings (`Raza`, `Umar Asghar`) in Cohort 029's `blind_review.json`. | **Pass** |

---

## Detailed Audit Notes by Perspective

### 1. Research Historian Review
- **Chronological Integrity:** Verified all 31 cohort units (`design_validation`, `001`–`025`, `025_1`, `026`–`029`) appear as dedicated numbered sections across Chapters 5–12 with all 13 required subsections, preserving exact chronological dependencies (including Cohort 003 running on Nov 10 alongside Cohort 002, and Cohort 026's three internal timestamps: v1 at `06:54 UTC`, v2 at `07:26–07:56 UTC`, and v3 in `qwen7b_f16`/`llama8b_f16` at `08:25–08:57 UTC`).
- **Missing/Undocumented Information Explicitly Marked:** Recorded that `Qwen2.5-0.5B` and `1.5B` GGUF files were prepared on SSD (`docs/SSD_ASSET_REUSE.md`) but never queried; noted that the specific reason for running Cohort 029 exclusively on `Qwen2.5-7B Q4_K_M` without a paired `F16` arm is undocumented in `CF-TP1-v1.0.md`.

### 2. Causal Inference Specialist Review
- **Identification & Transportability:** Verified that equations (3.2)–(3.10) accurately state Markovian factorization, truncated factorization under $\doop(X=x)$, backdoor adjustment, observational treatment-conditioned weighting, and stratum transportability $V^*(a;w^*) = \sum_s \Prob^*(S=s)\Prob_{\mathrm{rct}}(Y=1\mid A=a,S=s)$ following Pearl (2009) and Pearl & Bareinboim (2014).
- **Observational Equivalence Precision:** Distinguished two separate instances of observational equivalence in the project so readers never conflate them: (a) psychometric observational equivalence between the 3-parameter $C/A/B$ tree and symmetric logistic regression on 4 binomial cells (`design_validation`), and (b) causal graphical observational equivalence between $W\to X,Y$ and $X\to W\to Y$ over the full 8-cell discrete joint distribution $\Prob(W,X,Y)$ (Cohorts 026–028).

### 3. Statistician Review
- **Clustered Degrees of Freedom & Variance:** Confirmed Cohort 029's primary estimator treats the $N=128$ world families across $H=8$ strata ($m_h=16$) as the unit of independence, matching `primary.json` (`se = 0.021323975`, `welch_df = 67.5285`).
- **Degeneracy Handling:** Verified that Cohort 017's `14B Q4_K_M` zero-variance conflict contrast (`96/192` vs. `96/192`, `s_d = 0`) is reported without undefined Student-$t$ division, and that Cohort 005's `-43.75 pp` $C/A/B$ additivity violation is accompanied by its paired family interval `[-68.75, -18.75] pp`.

### 4. Machine Learning & Quantization Researcher Review
- **Compression Nuance:** Confirmed the monograph avoids claiming that GGUF quantization universally breaks JSON or universally spares reasoning; instead, it documents scale- and prompt-dependent interactions (`3B Q2_K` 100% loop collapse vs. `7B/8B Q2_K` 99.7%–100% JSON validity in Cohort 024; `3B Q4_K_M` `-31.25 pp` formula-sign drop in Cohort 007 vs. `Llama 8B Q4_K_M` control-only truncation in Cohort 024).

### 5. Reproducibility & Visual Geometry Auditor Review
- **Repository Cleanliness Check:** Confirmed zero modifications to existing tracked files or untracked `manuscript/` files. All new files reside strictly inside `docs/scientific-retrospective/`.
- **Figure & Table Provenance & Zero-Overlap Verification:** Confirmed all 18 PDF figures (`fig01`–`fig18`) embed scalable Type-42 TrueType outlines (`pdf.fonttype = 42`) generated by `generate_figures_conceptual.py` and `generate_figures_empirical.py`, verified by `figure_geometry_guard.py` (automated pixel-level renderer bounding-box check enforcing zero text-over-text, zero text-over-bar/line/marker, zero box-border overflow, and zero legend-over-data collisions) as well as visual raster inspection. All 11 tables in `tables/` are generated by `generate_tables.py` from `evidence/*.csv` and `_extracted_summary.json`.

### 6–8. Student Reader, Academic Editor, and Skeptical Reviewer Sign-Off
- All 39 BibTeX references in `bibliography/references.bib` were cross-checked against DOIs, ACL Anthology, Springer, and pinned arXiv records in `literature review/paper_manifest.json` and `manuscript/references.bib`.
- Compilation via Tectonic (`0.15.0`) produces a clean, searchable, bookmarked PDF (`build/main.pdf` and `build/The_Life_of_CausalFade.pdf`) with complete front matter, 7 parts, 29 chapters, and 17 appendices (A–Q).
