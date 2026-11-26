# Unresolved Discrepancies, Historical Defects, and Unrecoverable Records

This document catalogs every discrepancy, historical defect, post-collection repair, stale status string, and unrecoverable external artifact identified during the Phase I audit of Project CausalFade at snapshot commit `7f3dcf6e4a880ddc9ea116adaa8428a3006099fc` (scientific release tag `cohort-029-v1.0.0` at `76206c259caa488668a7556ce1bc53cb35d220da`). None of these historical files were altered.

---

## 1. Narrative vs. Raw-Journal Discrepancy in Cohort 029 `release/RESULTS.md`

- **Location:** `experiments/cohort_029/release/RESULTS.md` (lines 44–47) versus `experiments/cohort_029/runs/confirmatory/events.jsonl`, `row_scores.jsonl`, `secondary.json`, and `manuscript/supplement.tex` (lines 68–79).
- **Discrepancy:** The manually drafted direction table in `release/RESULTS.md` reports transfer-form `Gold action 0 correct` / `Gold action 1 correct` / `Activated` as:
  - Causal: `121/512`, `416/512`, `995/1,024`
  - Arithmetic: `124/512`, `397/512`, `785/1,024`
  Those numbers are arithmetically incompatible with `Activated = 512 - (# correct off) + (# correct on)` (`512 - 121 + 416 = 807 != 995`, and `512 - 124 + 397 = 785`, which does not match the transfer-arithmetic cells).
- **Verified Ground Truth from Raw Journal & Machine-Readable Cells:** Re-decoding all 4,096 base64 response payloads in `events.jsonl` and summing `secondary.json` (`row_cells` where `form == 1`) yields:
  - **Transfer Causal:** Gold Off (`0`) correct = **14/512** (said On = 498); Gold On (`1`) correct = **497/512** (said Off = 15); Total Correct = **511/1,024**; Total Activated = `498 + 497` = **995/1,024**.
  - **Transfer Arithmetic:** Gold Off (`0`) correct = **231/512** (said On = 281); Gold On (`1`) correct = **316/512** (said Off = 196); Total Correct = **547/1,024**; Total Activated = `281 + 316` = **597/1,024**.
- **Impact on Primary Endpoint:** Zero. Primary target-pair fidelity (`128/512` vs `146/512`), $\\widehat{\\Delta} = -3.515625$ pp, Welch $t$ interval $[-7.7713, +0.7400]$ pp, and bounded interval $[-27.5237, +20.4924]$ pp are unaffected and verified byte-for-byte.

---

## 2. Cohort 029 Pre-Inference Human Authorship & Blind-Review Provenance Limits

- **Location:** `experiments/cohort_029/freeze/evidence/provenance.json`, `experiments/cohort_029/lab/`, and `experiments/cohort_029/release/PROVENANCE_AND_LIMITATIONS.md`.
- **Finding:** Although CF-TP1 v1.0 Section 9 specified pre-inference signed human authorship and independent blind review, the actual production freeze (`5252f69d...`) recorded `"authorship": "undocumented"` and `"review": "undocumented"`.
  1. Umar Asghar's `transfer-authorship.md` (disclosing Claude assistance from his brief) has a valid detached SSH signature over its bytes, but its signing key was not present in `allowed_signers`, preventing cryptographic identity authentication against a pre-registered trust list.
  2. Reviewer `Raza` completed `answers.csv` (matching 32/32 scheduled and 16/16 worked items) and returned a valid SSH signature (`review-attestation-returned-signed.md.sig`), but reviewer identity is abbreviated (`Raza`) and the signed attestation was reconciled *after* the production freeze rather than recorded as a pre-inference freeze gate.
- **Disposition:** Treated transparently as an uncertified pre-inference human independence gate.

---

## 3. Cohort 029 Literal vs. Clarified Rival-Policy Gate (`constant-rivals-v1`)

- **Location:** `experiments/cohort_029/freeze/fixture/policy_audit.json` and `experiments/cohort_029/freeze/policy-clarification.md`.
- **Finding:** CF-TP1 Section 6C literally required every non-equivalent shortcut policy to make errors under *both* gold actions (`0` and `1`). Constant-action policies (`always_on`, `always_off`, and degenerate endpoint weight thresholds) mathematically make errors under only one gold action, causing **12 literal gate failures** (6 per tie-breaking convention). Before inference, `policy-clarification.md` (`constant-rivals-v1`) froze a specific constant-policy gate (50% item accuracy, errors in $\\ge 16$ transfer-causal families, 0/1,024 target-switch pairs solved), which passed with 0 failures while preserving the 12 literal failures in `policy_audit.json`.

---

## 4. Cohort 026 Directory Naming vs. Execution Chronology (`v2` vs. `v3`)

- **Location:** `experiments/cohort_026/runs/` and `experiments/cohort_026/development_summary.md`.
- **Finding:** Cohort 026 executed three wording/fixture versions on 19 November 2026:
  - `invalidated_pilot_qwen_v1` (`06:54 UTC`): Fixture v1, invalidated because complementing $Y$ left the arithmetic-control oracle hardcoded to `yes` and leaked an extra intervention question into the control prompt.
  - `qwen7b_f16_v2` (`07:26 UTC`) and `llama8b_f16_v2` (`07:56 UTC`): Repaired Fixture v2 (`input_v2/`), where Llama emitted `X=1.` with a trailing period (`48/112` strict-valid).
  - `qwen7b_f16` (`08:25 UTC`) and `llama8b_f16` (`08:57 UTC`): Final permitted wording revision **v3** (`input/`), which repaired Llama's punctuation (`112/112` strict-valid) and yielded `6/8` decision switch fidelity alongside `8/16` no-change failure.
  - Subsequently, Cohort 027 (`README.md`) identified that Cohort 026's generator coupled correct option position to form (direct switch answers always second, decision switch answers always first, and no-change pairs reversed option order), explaining Llama's `6/8` score via its `61/64` first-option selection policy.

---

## 5. Historical Bugs, Interruptions, and Post-Collection Repairs (Preserved in Archive)

1. **Cohort 008 Interrupted Run (`run_001_f16`):** Stopped at user shutdown request after 25 completed requests and 1 interrupted request (`26` raw JSONL lines vs `64` scheduled rows in `results.json`). Preserved separately; accounts for the 38-row difference between total scheduled requests (`48,208`) and persisted raw records (`48,170`) across the entire repository.
2. **Cohorts 009–011 Cell-Count Halving Bug (`b90cb63`):** `tools/analyze_interleaved_order.py` originally averaged two items per family before summing cell counts without multiplying by 2, halving displayed success/activation counts and prompting a false statement that Q4_K_M scored below always-activate. Repaired on 12 Nov 2026; original JSONs preserved as `*_v1_undercounted_counts.json`. Paired family differences and bootstrap CIs were unaffected.
3. **Cohort 016 Retrospective Magnitude Shortcut:** Prospectively frozen primary order effect (`+62.5` pp) is valid, but retrospective inspection (`manuscript/scripts/extract.py`) discovered that because $|\\tau| \\in [0.06, 0.12) < |\\delta_{\\text{obs}}| \\in [0.38, 0.46)$ on every item, choosing the sign of the smaller printed `|on - off|` gap solves `768/768` prompts without reading source labels.
4. **Cohort 017 Post-Inference Analysis Crash & Repair (`caf5b1d`):** Unattended Ubuntu runner completed `768/768` responses per 14B arm, then failed in `analysis.log` (`ModuleNotFoundError: No module named 'numpy'`). Repaired locally with a zero-variance `t`-test guard (`14B Q4_K_M` had zero family variance due to 100% conflict activation).
5. **Cohort 019 Ambiguous Source-Check Position Cue:** Semantic source-comprehension prompts could mention the randomized study first in prose while stating historical was "listed first," confounding its `8/16` score (documented in 14 Nov 2026 amendment without altering failed causal/conflict gates).
6. **Cohort 023 Omitted Aggregate Supplement (`analyze_measurement_audit_supplement.py`):** Frozen analyzer omitted predeclared aggregate paired and numeric-direction summaries; computed post-inference in `development_supplement.json` bound to `raw_sha256`.

---

## 6. Stale Prospective Statements in Older Documentation Files

Because historical documents were intentionally preserved rather than rewritten after later cohorts:
- `docs/RESEARCH_METHODOLOGY.md`, `docs/STUDY_ROADMAP.md`, and `docs/INTERDISCIPLINARY_FOLLOWUP.md` reflect 13–14 Nov 2026 status (stating Cohort 018 or 022+ are prospective).
- `experiments/cohort_027/README.md` (line 3) and `experiments/cohort_028/README.md` (line 3) retain design/mid-run headers ("no inference performed" / "paused with 1030/1280 responses"), whereas `pipeline_status.json`, `EXPERIMENTS.md`, and `README.md` record their completed runs and `stopped_by_gate` terminal states.

---

## 7. Information That Cannot Be Recovered from Available Records

- **Raw model weight binaries & safetensor shards** (`H:\\AGERE`, `H:\\CAUSALFADE`, `$HOME/Desktop/CAUSALFADE/weights/`): Excluded from Git; only SHA-256 digests, byte counts, and HF commit hashes are recoverable.
- **`CausalFade_Q1_Peer_Review_Report_2026-11-19.docx`**: Simulated editorial review referenced by Cohort 028 (`SHA-256: 32bfa009...`); the `.docx` file itself was in the user's `Downloads` folder and not committed to Git (unlike Cohort 025.1's `source_investigation.docx`, which *is* archived in Git).
- **Exact wall-clock hardware diagnostics of the "reported lab-PC malfunction"** mentioned briefly in `docs/SUPERVISOR_PROGRESS_REPORT_2026-11-19.md` line 114: Undocumented in repository logs.
- **Downstream open-source relicensing permission from Umar Asghar** for verbatim republication of `experiments/cohort_029/lab/transfer.json` prose outside reproducibility auditing (`LICENSES.md`).
- **Token log-probabilities, internal activations, attention weights, and chain-of-thought traces** for strict bare-JSON cohorts: Never collected (`llama-server` invoked with `temperature=0`, tight token caps, and no logprob/activation export).
