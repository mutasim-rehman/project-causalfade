# Observatory implementation status

The observatory continues the initial dashboard on `codex/research-observatory`. It uses the previously pinned research revision `01728ada407e8e5d59d6d7918dcd71dc0532b706` and Cohort 029 release `cohort-029-v1.0.0`.

## Delivered

- All 16 major navigation routes, including Final Findings, Research Paper and a 12-slide Presentation Mode.
- Static links for all 31 documented cohort entries, a searchable archive, classification filtering and shareable cohort comparisons.
- An interactive causal lab using frozen families and an on-demand chart engine with SVG export.
- Filterable expected-versus-observed target transition matrices for causal and matched arithmetic tasks.
- A Cohort 024 within-checkpoint precision matrix with separate validity and correctness counts.
- On-demand response archives for the final Cohort 029 study, Cohort 016 and the interrupted Cohort 008 run, with verbatim text, scoring metadata and CSV downloads. The final-study inspector can compare the two recorded targets in a frozen pair.
- A provenance inspector and downloadable snapshot inventory. The research paper, supplement and retrospective link to their committed repository copies.
- An extraction run that reconciles normalized responses, published pair summaries and the final contrast using existing records. The dashboard verification report lists the checks and the historical discrepancies.

## Coverage limits

- The response explorer currently indexes three archives. The repository-wide cohort and response counts describe a wider historical inventory.
- Cohort reports use the available retrospective ledger and run artifacts. The depth of the reports varies with the source coverage. Historical narrative and statistical modules retain the classifications in the source snapshot.
- The local static application supports offline demonstrations. Original evidence files and publication PDFs are accessed through their pinned repository links.

## Verification

- The production export and strict TypeScript check passed.
- Three dataset contract tests and nine browser tests passed. Browser coverage included all major routes at 1440 × 900, 1024 × 768 and 390 × 844, all cohort permalinks, presentation navigation, the evidence dialog, precision filters and both SVG and CSV downloads.
- Eleven scientific reconciliation checks passed. The dataset manifest checksums and 74 distinct pinned source digests also matched their corresponding files and Git blobs.
