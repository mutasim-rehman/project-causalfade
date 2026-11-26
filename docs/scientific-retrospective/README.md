# The Life of CausalFade — Scientific Retrospective Monograph

**Subtitle:** *A Scientific Retrospective of Hypotheses, Experiments, Failures, Methodological Evolution, and Discovery*  

**Authors:**
- **Mutasim ur Rehman** (`i242514@isb.nu.edu.pk`) — Department of Artificial Intelligence & Data Science, National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad, Pakistan
- **Ahmad Raza** (`i242574@isb.nu.edu.pk`) — Department of Artificial Intelligence & Data Science, National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad, Pakistan
- **Umar Asghar** (`i242532@isb.nu.edu.pk`) — Department of Artificial Intelligence & Data Science, National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad, Pakistan

**Audited Repository Snapshot (`HEAD` / `origin/main`):** `b7371530caa62d6e43a8e83ef6db361f6640f63a`  
**Annotated Confirmatory Tag (`cohort-029-v1.0.0`):** `76206c259caa488668a7556ce1bc53cb35d220da`  
**Inception Commit:** `4e2fe4f53370c05878476ed0363bf472fcd34d17` (2026-10-28)  
**Empirical Coverage:** 320 Git commits, 1 pre-LLM synthetic validation suite (`design_validation`), 30 experimental cohort units (`cohort_001` through `cohort_029`, including `cohort_025_1`), 71 local LLM run directories, 48,208 scheduled LLM inference requests, and 48,170 persisted raw responses.

---

## 1. Purpose and Scope

This self-contained directory houses the complete LaTeX source, programmatic data-extraction and visualization pipelines, machine-readable evidentiary ledgers, verified BibTeX bibliography, internal multi-perspective quality-assurance audit, and compiled searchable PDF monograph documenting the full scientific history of **Project CausalFade**.

In strict compliance with reproducibility and historical-audit principles:
- **Zero existing repository files or `manuscript/` files were modified.**
- **Zero historical LLM experiments were re-run or fabricated.**
- Every figure (`figures/fig01_*.pdf` through `fig18_*.pdf`) and inventory table (`tables/*.tex`) is generated programmatically from verified repository artifacts.
- Contemporaneous interpretations, prospective gates, exploratory diagnostics, and retrospective audits (such as Cohort 016's 100% source-blind smaller-gap shortcut and the manual prose transcription typo in `experiments/cohort_029/release/RESULTS.md`) are explicitly distinguished.

---

## 2. Directory Structure

```text
docs/scientific-retrospective/
├── main.tex                         # Master LaTeX book entry point
├── README.md                        # Compilation, navigation, and reproducibility guide
├── REVIEW_REPORT.md                 # 8-perspective internal scientific & editorial QA audit
├── .gitignore                       # Local build-artifact ignore rules
├── chapters/                        # Modular front matter and Parts I--VII (Chapters 1--29)
│   ├── frontmatter.tex              # Title page, provenance colophon, Preface, Executive Summary
│   ├── part1_ch01_origin.tex        # Ch 1: The Origin
│   ├── part1_ch02_literature.tex    # Ch 2: The Intellectual Foundation (39 verified papers)
│   ├── part1_ch03_theory.tex        # Ch 3: The Theoretical Foundations (6-layer pedagogy)
│   ├── part2_ch04_infrastructure.tex# Ch 4: The Experimental Infrastructure
│   ├── part2_ch05_cohorts_dv_004.tex# Ch 5: design_validation & Cohorts 001--004
│   ├── part2_ch06_cohorts_005_007.tex# Ch 6: Cohorts 005--007
│   ├── part2_ch07_cohorts_008_012.tex# Ch 7: Cohorts 008--012
│   ├── part2_ch08_cohorts_013_017.tex# Ch 8: Cohorts 013--017
│   ├── part2_ch09_cohorts_018_023.tex# Ch 9: Cohorts 018--023
│   ├── part2_ch10_cohorts_024_025.tex# Ch 10: Cohorts 024, 025 & 025.1
│   ├── part2_ch11_cohorts_026_028.tex# Ch 11: Cohorts 026--028
│   ├── part2_ch12_cohort_029.tex    # Ch 12: Cohort 029 (CF-TP1 Confirmatory Study)
│   ├── part3_evolution.tex          # Chs 13--17: Evolution of RQ, Ledgers, Failures, Turning Points
│   ├── part4_scrutiny.tex           # Chs 18--20: Scientific Audits, Construct & Statistical Validity
│   ├── part5_final_framework.tex    # Chs 21--23: CF-TP1 Protocol, Final Results, Contribution
│   ├── part6_making_paper.tex       # Chs 24--25: Archive-to-Manuscript & Hypothesis Revisited
│   └── part7_lessons.tex            # Chs 26--29: Lessons, Causal AI, Open Questions, Epilogue
├── appendices/                      # Appendices A through Q
│   ├── appendices_a_to_i.tex        # Inventories, Verbatim Prompt History, Stats, Ledgers
│   └── appendices_j_to_q.tex        # Verification, Limitations, Failed Runs, Glossary, BibTeX
├── tables/                          # 11 programmatically generated LaTeX booktabs/longtables
├── figures/                         # 18 programmatic vector PDF figures (TrueType Type-42 fonts)
├── bibliography/
│   └── references.bib               # 39 DOI/ACL/Springer/arXiv-verified BibTeX records
├── evidence/                        # Machine-readable audit & traceability files
│   ├── source_manifest.json
│   ├── cohort_inventory.csv
│   ├── experiment_inventory.csv
│   ├── model_quantization_inventory.csv
│   ├── dataset_task_inventory.csv
│   ├── research_timeline.json
│   ├── hypothesis_ledger.csv
│   ├── methodology_ledger.csv
│   ├── decision_ledger.csv
│   ├── claim_evidence_map.csv
│   ├── unresolved_discrepancies.md
│   └── artifact_verification_report.md
├── scripts/                         # Deterministic extraction, figure, and table generators
│   ├── build_inventories.py
│   ├── generate_evidence_ledgers.py
│   ├── generate_figures_conceptual.py
│   ├── generate_figures_empirical.py
│   ├── generate_tables.py
│   └── sanitize_tex.py
└── build/                           # Compiled searchable & bookmarked PDF monograph
    ├── main.pdf
    └── The_Life_of_CausalFade.pdf
```

---

## 3. Deterministic Reproduction & Compilation Instructions

### Prerequisites
- **Python 3.11+** (`py` on Windows or `python3` on Linux/macOS) with `numpy`, `scipy`, and `matplotlib`.
- **Tectonic 0.15+** (recommended single-binary XeTeX + BibTeX engine; installed on Windows workstations at `%LOCALAPPDATA%\TectonicProject\bin\tectonic.exe`) or a full **TeX Live / MiKTeX** distribution (`latexmk -pdf main.tex`).

### Step-by-Step Build Commands (PowerShell / Bash from Repository Root)

```powershell
# 1. Rebuild raw experiment inventories and SHA-256 verification summaries
py docs/scientific-retrospective/scripts/build_inventories.py
py docs/scientific-retrospective/scripts/generate_evidence_ledgers.py

# 2. Regenerate all 18 vector PDF figures
py docs/scientific-retrospective/scripts/generate_figures_conceptual.py
py docs/scientific-retrospective/scripts/generate_figures_empirical.py

# 3. Regenerate all 11 LaTeX inventory and empirical tables
py docs/scientific-retrospective/scripts/generate_tables.py

# 4. Compile searchable, bookmarked PDF monograph
Push-Location docs/scientific-retrospective
tectonic -o build main.tex
Copy-Item build/main.pdf build/The_Life_of_CausalFade.pdf -Force
Pop-Location
```

Using `latexmk` under TeX Live instead of Tectonic:
```bash
cd docs/scientific-retrospective
latexmk -pdf -outdir=build main.tex
cp build/main.pdf build/The_Life_of_CausalFade.pdf
```
