# Artifact Verification Report

- **Source Snapshot Commit (`HEAD`):** `7f3dcf6e4a880ddc9ea116adaa8428a3006099fc`
- **Tracked `origin/main` Commit:** `b7371530caa62d6e43a8e83ef6db361f6640f63a`
- **Immutable Scientific Release Tag (`cohort-029-v1.0.0`):** `76206c259caa488668a7556ce1bc53cb35d220da`
- **Total Git Commits Audited:** `320`
- **Deleted or Renamed Files in Git History:** `0` (`git log --diff-filter=DR` verified empty)
- **Verification Mode:** Strictly read-only inspection; `git status --porcelain` confirmed zero modifications to tracked files and zero modifications to `manuscript/`.

## Summary of Verified Artifacts

| Category | Count | Verification Result |
| --- | ---: | --- |
| Synthetic design-validation suite (`results/design_validation/`) | 1 | Verified 192 public/oracle tasks, 3,600 recovery replicates, SHA-256 matches `manifest.json` |
| Literature review PDFs & summaries (`literature review/`) | 14 | All 14 PDFs, `paper_manifest.json` SHA-256 digests, and 14 summaries verified |
| Experimental cohort directories (`experiments/cohort_001` .. `cohort_029`) | 30 | All 30 cohort directories (`001`–`025`, `025_1`, `026`–`029`) individually verified |
| Persisted LLM run directories | 71 | Every run's `raw_responses.jsonl` / `attempts.jsonl` / `events.jsonl` line-counted and SHA-256 hashed |
| Total scheduled LLM requests across all cohorts | 48,208 | Verified from run schedules and manifests |
| Total persisted raw LLM records across all cohorts | 48,170 | Exact difference of 38 rows accounted for by preserved interrupted `cohort_008/run_001_f16` (26/64) |
| Cohort 029 offline release checks (`release/verification.json`) | 50 / 50 | PASS; manifest SHA-256 `5252f69d...` and journal SHA-256 `673eb723...` verified byte-for-byte |
| Manuscript claim-ledger entries (`manuscript/audit/claim-ledger.csv`) | 83 | Cross-checked against repository blobs and Cohort 029 raw journal |

All SHA-256 digests of primary artifacts are recorded in `evidence/source_manifest.json` and per-run digests in `evidence/experiment_inventory.csv`.
