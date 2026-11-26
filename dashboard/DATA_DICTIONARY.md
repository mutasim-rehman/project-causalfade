# Data Dictionary — CAUSALFADE Research Observatory

The extractor generates the datasets in `dashboard/public/data/` from repository artifacts. The manifest pins the source revision and records dataset digests. Extraction and verification times are recorded separately.

## Datasets

1. **`overview.json`**
   - Verified repository-wide KPIs (`documented_cohorts`, `run_directories`, `completed_runs`, `interrupted_runs`, `scheduled_requests`, `persisted_raw_responses`, `final_eval_responses`, `independent_families_final`), 5-step Research-at-a-Glance summary, and Established vs. Unresolved findings.
2. **`cohorts.json`**
   - 31 documented cohort entries (`design_validation`, `cohort_001`..`cohort_029`, `cohort_025_1`), including `comparability_group`, `inferential_classification`, `runs[]`, `artifacts[]` (with SHA-256 and commit-pinned GitHub URLs where available), and `has_interrupted_run`.
3. **`timeline.json`**
   - Chronological milestones (`T01`..`T14+`) with commit hashes, investigation questions, contemporaneous understanding, decisions, and retrospective assessments.
4. **`causal_lab.json`**
   - All 128 verified Cohort 029 CF-TP1 numerical families (`slot` 0..127, featuring `slot: 96` from Figure 1 of the manuscript), including exact `L` and `R` tables, stratum effects $\delta_1, \delta_0$, target mixtures $w_0, w_1$, target effects $\tau_k$, oracle actions $a_k^\star$, and latent surfaces $m_{SUA}$.
5. **`statistics.json`**
   - Verified inferential and descriptive datasets: Cohort 029 primary/secondary/intervals/128-family scores; Cohort 016 96-family order replication & Monte Carlo power analysis; Cohort 017 14B recovery; Cohort 024 3x7 matrix; Cohorts 027–028 gate results; `design_validation` synthetic recovery.
6. **`decision_behavior.json`**
   - Cohort 029 paired transition tables (`target`, `role`, `physical_order`), joint pair-member correctness (`0`, `1`, `2`), directional accuracy (`off` vs `on`), action activation rates, and deterministic rival policy benchmarks.
7. **`models_quantization.json`**
   - Model-format entries across Qwen2.5 (0.5B–14B), Mistral-7B-v0.3, and Llama-3.1-8B, with status and Cohort 024, 016 and 017 comparisons.
8. **`methodologies.json`** & **`hypotheses.json`**
   - Registries of 19 documented methodologies (`M01`–`M19`) and 20 research hypotheses (`H01`–`H20`) with explicit scientific statuses.
9. **`literature.json`**
   - 14 initial targeted review papers (`literature review/paper_manifest.json`), 17 manuscript positioning references (`manuscript/audit/citations.csv`), and a 10-term causal/statistical glossary.
10. **`reproducibility.json`**
    - Cohort 029 50-check release verification, claim-to-evidence ledger (`manuscript/audit/claim-ledger.csv`), and 5 documented historical discrepancies (`D01`–`D05`).
11. **`responses/`**
    - Lazy-loaded raw response archives: `index.json`, `cohort_029_part1..4.json` (4,096 responses), `cohort_016.json` (1,536 responses), and `cohort_008_interrupted.json` (26 persisted responses from the interrupted run).
    - Cohort 016 uses the manuscript's archived action scores and the cohort oracle. Cohort 008 preserves the run's action validity and scoring fields for completed requests. The interruption itself has an unavailable action and correctness status.
12. **`target_transitions.json`**
    - Cohort 029 target pairs joined from the frozen pair scores and row scores. `expected` and `observed` each contain the two actions in target 0 to target 1 order. `null` denotes an unavailable observed action. `family`, `form`, `task`, `order` and `role` allow descriptive filtering without recomputing the primary inference.
