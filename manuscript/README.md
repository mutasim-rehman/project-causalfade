# CausalFade manuscript package

**Recommended reading order.** Read the [IEEE TNNLS review draft](ieee-tnnls.pdf), the [supplement](supplement.pdf), and the [submission checklist](Submission-checklist.md). The scientific and editorial review is in [Scientific-and-editorial-QC.md](Scientific-and-editorial-QC.md). This directory is separate from the immutable experimental outputs.

## Files

- `ieee-tnnls.tex` and `ieee-tnnls.pdf` are the selected two-column IEEEtran journal draft. `article.tex` contains the shared scientific text; `references.bib` is the bibliography. The older `manuscript.tex` and `make-article.tex` are superseded venue-neutral drafts.
- `supplement.tex`, `history.tex` and `supplement.pdf` cover the cohort history, mathematical and statistical detail, reproduction and the release reporting correction.
- `figures/fig1.pdf` to `figures/fig5.pdf` are individual vector graphics. `data/` contains their source tables and the exact matched family-096 prompt messages. Form 0 is archive-compatible, form 1 is transfer. Task 0 is causal, task 1 arithmetic. Axis “order” means physical source-block order.
- `data/example.csv` gives the printed rates for Figure 1. The group index is an array index: 0 denotes the first canonical stratum (S=1), 1 denotes the second (S=0). `quartets.csv` supplies its effects in percentage points and weights in percent; it also drives Figure 2. Quartet column dRK indexes governing role R and target K, both zero-based. `intervals.csv` is in proportions and drives Figure 3. `families.csv` contains its family-level source values. `pairs.csv` drives Figure 4. `order016.csv` contains the two-arm extraction for Figure 5; task IDs repeat across arms by design. `policies.csv`, `direction.csv` and `option_order.csv` give the numerical comparisons printed in the text and tables.
- `audit/claim-ledger.csv` maps each empirical claim group and historical entry to a tagged source path and SHA-256. `audit/citations.csv` maps the bibliography to publication records. The audit directory also contains manuscript-side verification, test and analysis-replay results.
- `Author-declarations.md`, `Cover-letter.md` and `Submission-checklist.md` are editorial materials for the authors. The letter is a draft. Brackets indicate information the authors still need to supply.

## Build and verify

For scientific replay use the pinned release and the supplement's Linux instructions. For figure extraction keep this directory alongside the release's `experiments/`. From the repository root, using Python with SciPy and Matplotlib, run:

```sh
python manuscript/scripts/extract.py
python manuscript/scripts/figures.py
python manuscript/scripts/ledger.py
python manuscript/scripts/check_reporting.py
```

The ledger generator reads Git blob contents at the pinned commit. To refresh bibliographic metadata, `scripts/sources.py` additionally requires requests, Beautiful Soup and network access. The stored BibTeX and figures suffice for ordinary LaTeX compilation. From the manuscript directory:

```sh
tectonic ieee-tnnls.tex
tectonic supplement.tex
```

Both builds use the shared files in this directory. A current TeX installation supporting the loaded packages and BibTeX is an alternative. Release attribution: Project CausalFade, tag `cohort-029-v1.0.0`, commit `76206c259caa488668a7556ce1bc53cb35d220da`, manifest SHA-256 `5252f69d30a0a5bb65a5efa669458e325c0531f25ab55f768531c7ca29f4c766`. [Immutable release and license scope](https://github.com/mutasim-rehman/project-causalfade/tree/76206c259caa488668a7556ce1bc53cb35d220da)
