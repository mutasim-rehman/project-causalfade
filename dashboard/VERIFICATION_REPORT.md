# Verification Report — CAUSALFADE Research Observatory

- **Source Git Commit:** `01728ada407e8e5d59d6d7918dcd71dc0532b706`
- **Release Tag:** `cohort-029-v1.0.0` (`76206c259caa488668a7556ce1bc53cb35d220da`)
- **Verified At (UTC):** `2026-11-26T17:40:56.830539+00:00`
- **Overall Status:** `PASS` (11/11 checks passed)

## Automated Reconciliation Checks

| Check | Expected | Observed | Status |
| --- | --- | --- | --- |
| `cohort_029_raw_response_count` | `4096` | `4096` | **PASS** |
| `cohort_029_verbatim_and_frozen_scores` | `0` | `0` | **PASS** |
| `cohort_029_transition_counts_match_manuscript` | `{('causal', False): (256, 125, 7), ('causal', True): (256, 3, 8), ('arithmetic', False): (256, 119, 45), ('arithmetic', True): (256, 27, 46)}` | `{('causal', False): (256, 125, 7), ('causal', True): (256, 3, 8), ('arithmetic', False): (256, 119, 45), ('arithmetic', True): (256, 27, 46)}` | **PASS** |
| `cohort_029_transfer_causal_direction_reconciliation` | `{'off_correct': 14, 'on_correct': 497, 'activated': 995}` | `{'off_correct': 14, 'on_correct': 497, 'activated': 995}` | **PASS** |
| `cohort_029_transfer_arithmetic_direction_reconciliation` | `{'off_correct': 231, 'on_correct': 316, 'activated': 597}` | `{'off_correct': 231, 'on_correct': 316, 'activated': 597}` | **PASS** |
| `cohort_029_primary_delta_reconciliation` | `{'delta': -0.03515625, 'pairs_and_correct': {'causal': (512, 128), 'arithmetic': (512, 146)}}` | `{'delta': -0.03515625, 'pairs_and_correct': {'causal': (512, 128), 'arithmetic': (512, 146)}}` | **PASS** |
| `cohort_016_q4_conflict_order_mean_reconciliation` | `62.5` | `62.5` | **PASS** |
| `cohort_016_response_outcomes_match_manuscript` | `{'records': 1536, 'score_mismatches': 0}` | `{'records': 1536, 'score_mismatches': 0}` | **PASS** |
| `cohort_008_interruption_disposition` | `{'completed': 25, 'interrupted': 1}` | `{'completed': 25, 'interrupted': 1}` | **PASS** |
| `repo_scheduled_vs_persisted_reconciliation` | `{'scheduled': 48208, 'persisted': 48170, 'diff_from_008': 38}` | `{'scheduled': 48208, 'persisted': 48170, 'diff_from_008': 38}` | **PASS** |
| `cohort_029_upstream_50_checks` | `True` | `True` | **PASS** |

## Documented Historical Discrepancies Exposed (Not Silenced)

1. **Cohort 029 `release/RESULTS.md` Direction Table:** Manual transcription in `RESULTS.md` lines 44-47 (Causal 121/512 off, 416/512 on; Arithmetic 124/512 off, 397/512 on, 785/1024 activated) disagrees with raw `events.jsonl` and `secondary.json` (Causal 14/512 off, 497/512 on, 995/1024 activated; Arithmetic 231/512 off, 316/512 on, 597/1024 activated). The dashboard uses and displays the verified raw-journal ground truth and explicitly documents this discrepancy.
2. **Cohort 008 Interrupted Run (`run_001_f16`):** 26 persisted records (25 completed + 1 interrupted) out of 64 scheduled tasks, accounting for the exact 38-row difference between 48,208 scheduled requests and 48,170 persisted raw responses repository-wide.
3. **Cohorts 009-011 Cell-Count Halving Bug:** Repaired in `b90cb63`; original `*_v1_undercounted_counts.json` preserved in the repository.
4. **Cohort 016 Smaller-Gap Shortcut:** Retrospective audit (`manuscript/scripts/extract.py`) established that choosing the sign of the smaller printed `|on - off|` gap solves 768/768 Cohort 016 prompts without reading provenance.
5. **Cohort 029 Human Independence Gate:** Production freeze recorded `authorship` and `review` as `undocumented`; post-freeze signed records are preserved with explicit limitations.
