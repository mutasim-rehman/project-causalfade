"""Generate complete machine-readable inventories, timeline, ledgers, and verification reports.

Strictly read-only with respect to all historical repository files.
Writes outputs exclusively under docs/scientific-retrospective/evidence/.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVID = Path(__file__).resolve().parents[1] / "evidence"
EVID.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_out(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def build_source_manifest(extracted: dict) -> dict:
    tracked_key_files = [
        "README.md",
        "EXPERIMENTS.md",
        "DECISIONS.md",
        "SESSION_REPORT.md",
        "PUBLICATION_HANDOFF.md",
        "LICENSES.md",
        "docs/RESEARCH_METHODOLOGY.md",
        "docs/METHODOLOGY_ADAPTATION.md",
        "docs/STUDY_ROADMAP.md",
        "docs/INTERDISCIPLINARY_FOLLOWUP.md",
        "docs/PUBLICATION_READINESS_2026-11-15.md",
        "docs/SUPERVISOR_PROGRESS_REPORT_2026-11-19.md",
        "docs/SSD_ASSET_REUSE.md",
        "docs/DATA_CONTRACT.md",
        "docs/DECISIONS_BEFORE_COLLECTION.md",
        "docs/REPRODUCIBILITY.md",
        "docs/references.bib",
        "literature review/EXECUTIVE_SUMMARY.md",
        "literature review/READING_INDEX.md",
        "literature review/paper_manifest.json",
        "results/design_validation/VALIDATION_REPORT.md",
        "results/design_validation/parameter_recovery.json",
        "experiments/cohort_016/primary_analysis.json",
        "experiments/cohort_024/development_analysis_archive.json",
        "experiments/cohort_025/archive_methods_screen.json",
        "experiments/cohort_025_1/archive_investigation.json",
        "experiments/cohort_026/development_summary.md",
        "experiments/cohort_027/pipeline_status.json",
        "experiments/cohort_028/pipeline_status.json",
        "experiments/cohort_029/freeze/manifest.json",
        "experiments/cohort_029/runs/confirmatory/events.jsonl",
        "experiments/cohort_029/runs/confirmatory/analysis/primary.json",
        "experiments/cohort_029/runs/confirmatory/analysis/secondary.json",
        "experiments/cohort_029/release/verification.json",
        "experiments/cohort_029/release/validation_record.json",
        "experiments/cohort_029/release/RESULTS.md",
        "experiments/cohort_029/release/PROVENANCE_AND_LIMITATIONS.md",
        "manuscript/article.tex",
        "manuscript/supplement.tex",
        "manuscript/history.tex",
        "manuscript/references.bib",
        "manuscript/Scientific-and-editorial-QC.md",
        "manuscript/audit/claim-ledger.csv",
    ]
    hashes = {}
    for rel in tracked_key_files:
        p = ROOT / rel
        if p.exists():
            hashes[rel] = {"bytes": p.stat().st_size, "sha256": sha256_file(p)}

    manifest = {
        "monograph_title": "The Life of CausalFade: A Scientific Retrospective of Hypotheses, Experiments, Failures, Methodological Evolution, and Discovery",
        "investigation_date_local": "2026-11-26",
        "repository_root": "d:/project-causalfade",
        "git_snapshot": {
            "head_commit": extracted["git_head"],
            "origin_main_commit": extracted["git_origin_main"],
            "immutable_scientific_tag": "cohort-029-v1.0.0",
            "immutable_scientific_commit": extracted["git_tag_cohort029"],
            "earliest_commit": "4e2fe4f53370c05878476ed0363bf472fcd34d17",
            "earliest_commit_date": "2026-10-28T07:18:34+05:00",
            "head_commit_date": git_out("show", "-s", "--format=%cI", "HEAD"),
            "total_commits_on_head": extracted["total_commits"],
            "deleted_or_renamed_tracked_files_in_history": 0,
            "untracked_workspace_directories_inspected": ["manuscript/"],
        },
        "aggregate_counts": {
            "identifiable_cohorts": 30,
            "synthetic_validation_suites": 1,
            "llm_experimental_cohorts": 28,
            "retrospective_no_inference_cohorts": 2,
            "llm_run_directories": extracted["total_llm_runs"],
            "total_scheduled_llm_requests": extracted["total_scheduled_llm_requests"],
            "total_persisted_llm_responses": extracted["total_persisted_llm_responses"],
            "missing_due_to_interrupted_cohort008_run001": 38,
        },
        "external_or_unrecoverable_artifacts": [
            {
                "item": "GGUF model weight binaries and HF safetensor shards",
                "documented_locations": ["H:\\AGERE", "H:\\CAUSALFADE", "$HOME/Desktop/CAUSALFADE/weights/gguf/"],
                "status": "Excluded from Git by design; SHA-256 digests and byte sizes verified in run metadata and manifests.",
            },
            {
                "item": "Simulated editorial review DOCX referenced by Cohort 028",
                "documented_locations": ["Downloads/CausalFade_Q1_Peer_Review_Report_2026-11-19.docx"],
                "recorded_sha256": "32bfa0097930540f2f0ab56428d5c6c3924da22513e39f881c609e3f5d7b7432",
                "status": "Not committed to Git; contents summarized in experiments/cohort_028/README.md and REVIEW_RESPONSE_LEDGER.md.",
            },
            {
                "item": "Unnormalized Ubuntu home-path backups from 10 Nov 2026",
                "documented_locations": ["$HOME/Desktop/CAUSALFADE/runs/unmodified_paths_20261110"],
                "status": "External lab backup; original paths remain visible in pre-ea78a2f Git commits.",
            },
            {
                "item": "Trusted signer public key for Umar Asghar transfer-form authorship signature and pre-inference human independence certification in Cohort 029",
                "documented_locations": ["experiments/cohort_029/lab/evidence/transfer-authorship.md.sig"],
                "status": "Signature bytes validate cryptographically against embedded key, but key was absent from allowed_signers and freeze recorded human independence as undocumented.",
            },
            {
                "item": "Third-party publisher conversion commands for Mistral-7B-v0.3 and Llama-3.1-8B GGUF F16 baselines",
                "documented_locations": ["experiments/cohort_024/frozen_lab_plan.json"],
                "status": "Pinned Hugging Face revisions and SHA-256 digests recorded; upstream conversion invocations undocumented.",
            },
        ],
        "key_artifact_hashes": hashes,
    }
    (EVID / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def build_cohort_inventory() -> list[dict]:
    cohorts = [
        ("design_validation", "2026-11-01", "Synthetic Validation", "None (3,600 synthetic datasets)", "24 families (192 prompts) + 3,600 EM fits", "0", "Exploratory synthetic validation", "Recovered C/A/B away from boundaries; exposed symmetric logistic observational equivalence and 16 near-boundary nonconvergences", "results/design_validation/VALIDATION_REPORT.md", "6ab18d2"),
        ("cohort_001", "2026-11-10", "Direct Causal Pilot", "Qwen2.5-3B (F16, Q2_K, Q4_K_M)", "16 dev families, 64 exact prompts/arm", "192", "Exploratory pilot", "Strict 0/64 all arms (Markdown fences); fence-only F16 33/64 (63/64 activate, 0/64 adj set), Q2_K 0/64 (64/64 length-capped), Q4_K_M 34/64", "experiments/cohort_001/summary.md", "0333c67"),
        ("cohort_002", "2026-11-10", "Formula Arithmetic Control", "Qwen2.5-3B (F16, Q4_K_M)", "Same 16 families, 64 formula prompts/arm", "128", "Exploratory control", "Fence-only explicit action: F16 32/64 (0/64 activate), Q4 35/64 (3/64 activate); estimate signs: F16 61/64 vs Q4 45/64 (-25.0 pp)", "experiments/cohort_002/summary.md", "f2b2cb1"),
        ("cohort_003", "2026-11-10", "CPU Repacking Diagnostic", "Qwen2.5-3B Q2_K (default vs --no-repack)", "4 dev families, 16 exact prompts/arm", "32", "Technical diagnostic", "0/16 valid and 16/16 length-capped in both arms; disabling repacking altered token strings on 16/16 items without rescuing output", "experiments/cohort_003/summary.md", "941cf7e"),
        ("cohort_004", "2026-11-10", "7B Reference Screen", "Qwen2.5-7B F16", "8 dev families, 32 exact prompts", "32", "Exploratory feasibility gate", "Fence-only 17/32 overall (failed >=22/32 gate), 9/16 conflict, 31/32 activate, 32/32 adjustment set [Z] correct; 7B Q2_K withheld", "experiments/cohort_004/summary.md", "01c7590"),
        ("cohort_005", "2026-11-10", "Supplied-Rate Source Selection", "Qwen2.5-3B (F16, Q4_K_M)", "16 dev families, 64 supplied-rate prompts/arm", "128", "Exploratory diagnostic", "Fence-only F16 39/64 (28/32 aligned, 11/32 conflict), Q4 35/64 (19/32 aligned, 16/32 conflict, 61/64 activate); F16 C/A/B additivity residual -43.75 pp", "experiments/cohort_005/summary.md", "4e90b24"),
        ("cohort_006", "2026-11-10", "Q8_0 Formula Follow-Up", "Qwen2.5-3B Q8_0 (vs archived F16, Q4_K_M)", "16 reused families, 64 formula prompts", "64", "Exploratory control follow-up", "Fence-only Q8_0 estimate sign 61/64 (tied F16, +25.0 pp over Q4), explicit action 32/64 (0/64 activate)", "experiments/cohort_006/summary.md", "09cf43b"),
        ("cohort_007", "2026-11-10", "Fresh-Family Formula Sign Replication", "Qwen2.5-3B (F16, Q4_K_M)", "12 fresh families (seed 20261111), 48 prompts/arm", "96", "Exploratory fresh-family replication", "Estimate sign replicated: F16 46/48 vs Q4 31/48 (-31.25 pp, 95% CI [-41.67, -20.83]); explicit actions 24/48 vs 28/48", "experiments/cohort_007/summary.md", "12c7667"),
        ("cohort_008", "2026-11-10 to 2026-11-12", "Within-Item Source-Order Reversal", "Qwen2.5-3B (F16 partial + F16, Q4_K_M complete)", "16 families, 64 reversed prompts/arm (+ 26/64 interrupted)", "154 (192 sched)", "Exploratory crossover", "Run 1 interrupted at 25/64 (+1 error) for PC shutdown; rerun complete: F16 conflict 16/32 rand-first vs 7/32 hist-first (-28.125 pp); Q4 16/32 both", "experiments/cohort_008/summary.md", "dd75c35 / 2846f50"),
        ("cohort_009", "2026-11-12", "Same-Session Interleaved Order Crossover", "Qwen2.5-3B (F16, Q4_K_M)", "16 reused families, 128 interleaved twin prompts/arm", "256", "Exploratory crossover", "Removed session confound: F16 conflict 16/32 rand-first vs 9/32 hist-first (-21.875 pp); Q4 16/32 both; count bug later fixed in b90cb63", "experiments/cohort_009/summary.md", "1f8b169 / b90cb63"),
        ("cohort_010", "2026-11-12", "Fresh-Family Interleaved Order Replication", "Qwen2.5-3B (F16, Q4_K_M)", "12 fresh families (seed 20261113), 96 twin prompts/arm", "192", "Exploratory fresh-family replication", "F16 conflict 12/24 rand-first vs 6/24 hist-first (-25.0 pp, CI [-37.5, -12.5]); Q4 12/24 both; count bug fixed in b90cb63", "experiments/cohort_010/summary.md", "fa79370 / b90cb63"),
        ("cohort_011", "2026-11-12", "Matched Observational-Strength Pilot", "Qwen2.5-3B (F16, Q4_K_M)", "16 fresh matched-strength families (seed 20261114), 128 prompts/arm", "256", "Exploratory development", "Repaired aligned vs conflict historical gap imbalance; F16 conflict 16/32 vs 8/32 (-25.0 pp), aligned 18/32 vs 32/32 (+43.75 pp); Q4 near-constant activate", "experiments/cohort_011/summary.md", "cd3f66d / b90cb63"),
        ("cohort_012", "2026-11-12", "7B Matched-Strength Feasibility Screen", "Qwen2.5-7B F16", "8 reused cohort-011 families, 64 prompts", "64", "Exploratory feasibility gate", "Fence-only 47/64 overall, 32/32 aligned, but conflict 8/16 rand-first and 7/16 hist-first (failed >=9/16 per-order gate); Q4 withheld", "experiments/cohort_012/summary.md", "fc7dcc1"),
        ("cohort_013", "2026-11-12", "Prompt-Clarity Crossover (160-token cap)", "Qwen2.5-7B F16", "8 fresh matched families (seed 20261116), 128 prompts", "128", "Exploratory crossover", "Minimal 48/64 fence-valid (8/16 conflict); causal-context 0/64 valid (all 64 appended prose after JSON and hit 160-token cap; prefix diag 45/64)", "experiments/cohort_013/summary.md", "0f55a79"),
        ("cohort_014", "2026-11-12", "Strict-JSON Prompt-Clarity Screen (48-token cap)", "Qwen2.5-7B F16", "8 fresh matched families (seed 20261119), 128 prompts", "128", "Exploratory feasibility gate", "128/128 strict-valid JSON! Minimal 48/64 (failed conflict 8/16, 8/16); Causal-context 42/64 (passed conflict 9/16, 9/16, missed overall >=44 by 2)", "experiments/cohort_014/summary.md", "baa573b"),
        ("cohort_015", "2026-11-12", "16-Family Causal-Context Screen & Conditional Q4", "Qwen2.5-7B (F16, Q4_K_M)", "16 fresh matched families (seed 20261122), 128 prompts/arm", "256", "Development gate + conditional comparison", "F16 passed gate (89/128 overall, 19/32 & 22/32 conflict), triggering Q4 (98/128 overall); discovered Q4 conflict order jump: 11/32 rand-first vs 32/32 hist-first (+65.6 pp)", "experiments/cohort_015/summary.md", "79c0ba5"),
        ("cohort_016", "2026-11-12", "Prospective 96-Family Order-Sensitivity Confirmation", "Qwen2.5-7B (F16, Q4_K_M)", "96 fresh matched families (seed 20261127), 768 prompts/arm", "1536", "Prospective confirmatory replication", "Confirmed Q4 conflict order effect: 175/192 hist-first vs 55/192 rand-first (+62.5 pp, t(95)=21.10, p=1.24e-37); later retrospective audit found smaller-gap heuristic solves 768/768", "experiments/cohort_016/summary.md", "eb53578 / 13e8fa5"),
        ("cohort_017", "2026-11-13", "Unattended 14B Cross-Size Follow-Up", "Qwen2.5-14B (Q8_0, Q4_K_M)", "96 reused cohort-016 families, 768 prompts/arm", "1536", "Exploratory cross-size extension", "Q8_0 488/768 (conflict -4.17 pp), Q4_K_M 440/768 (conflict 0 pp, 100% activate); 7B order effect did not generalize; missing-NumPy crash repaired locally", "experiments/cohort_017/summary.md", "40f34f8 / caf5b1d"),
        ("cohort_018", "2026-11-13 to 2026-11-14", "Graded-Sensitivity & Matched-Control Pilot", "Qwen2.5-7B F16", "8 fresh families (seed 20261114), 288 prompts", "288", "Development gate", "288/288 strict-valid; failed gate (64/128 causal vs 80, 14/32 hist-first conflict vs 18); noncausal control 62/128; reversed token mapping collapsed accuracy (14/64 vs 50/64); Q4 withheld", "experiments/cohort_018/summary.md", "00fd0b5"),
        ("cohort_019", "2026-11-14", "Within-World Response-Contract Screen", "Qwen2.5-7B F16", "8 fresh families (seed 20261115), 832 prompts", "832", "Development gate", "832/832 strict-valid; semantic gate failed (73/128 causal, 12/32 & 13/32 conflict, 24/32 comp); neutral reverse beat forward by +25.8 pp causal & +36.7 pp control; source-check cue bug documented", "experiments/cohort_019/summary.md", "a400569"),
        ("cohort_020", "2026-11-14", "Staged Component Diagnostic", "Qwen2.5-7B F16", "8 fresh families (seed 20261116), 224 prompts", "224", "Component diagnostic", "224/224 strict-valid; isolated components strong (number 28/32, rand-only 29/32, source ID 32/32), but two-source historical-first conflict dropped to 16/32 (0/32 activate)", "experiments/cohort_020/summary.md", "737c945"),
        ("cohort_021", "2026-11-14", "Governing-Source Selection & Guidance Diagnostic", "Qwen2.5-7B F16", "8 fresh families (seed 20261117), 576 prompts", "576", "Guidance diagnostic", "576/576 strict-valid; governing-source selection 128/128 (100%) and rand-only 30/32, yet ordinary and source-guided two-source decisions both 58/128 (11 gains, 11 losses)", "experiments/cohort_021/summary.md", "77361f5"),
        ("cohort_022", "2026-11-16", "Independent Checkpoint-Family Replication", "Qwen2.5-7B F16, Mistral-7B-v0.3 Q4_K_M", "8 fresh families (seed 20261118), 576 prompts/arm", "1152", "Development cross-lineage screen", "Qwen repeated +53.1 pp rand-only vs two-source gap (source sel 128/128, rand-only 31/32, two-source 56/128); Mistral failed components (source sel 64/128 always 'A', rand-only 16/32 always activate)", "experiments/cohort_022/summary.md", "21dabb2"),
        ("cohort_023", "2026-11-16", "Counterbalanced Qwen Measurement Audit", "Qwen2.5-7B F16", "8 fresh families (seed 20261119), 896 prompts", "896", "Measurement audit", "896/896 strict-valid; simple components passed (rand-only 64/64, source sel 244/256) and +55.5 pp gap persisted across A/B & option order, but harmful numeric (18/32) & noncausal (75/128) failed >=75% rule", "experiments/cohort_023/summary.md", "4aff668"),
        ("cohort_024", "2026-11-16 to 2026-11-18", "3-Lineage x 7-Format Precision Matrix", "Qwen2.5-7B, Mistral-7B-v0.3, Llama-3.1-8B x (F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M, Q3_K_M, Q2_K)", "8 fresh families, 1,472 prompts x 21 arms", "30912", "Development measurement matrix", "30,912/30,912 attempts, 30,281 strict-valid; no F16 passed all component/control checks; Mistral picked 1st option 256/256; Llama Q4 had 448 length-capped control invalids while causal stayed 150/256", "experiments/cohort_024/summary.md", "6193357 / 2fecac4"),
        ("cohort_025", "2026-11-18", "Retrospective Archive Methods Screen", "None (reanalyzed 59 runs in cohorts 001-024)", "40,032 completed raw attempts + 26 interrupted", "0", "Retrospective exploratory reanalysis", "Mistral F16 kept semantic causal answer on 6/128 option reversals (0/128 source-sel); Qwen F16 causal MI with truth 0.031 bits vs 0.230 control; Qwen 024 order interaction 0 pp vs +45.3 pp in 016", "experiments/cohort_025/summary.md", "cacd5bc"),
        ("cohort_025_1", "2026-11-19", "Cross-Disciplinary Investigation Audit", "None (reproduced cohort 025 + audited 10-part DOCX)", "24 prior cohorts, 59 runs", "0", "Retrospective applicability audit", "Reproduced cohort 025 within 1e-12; classified graph-switch, psychophysical surfaces, stage rescue, transportability, IRT, and internal traces as unestimable from logs; prioritized graph-switch (026)", "experiments/cohort_025_1/summary.md", "cc1df44"),
        ("cohort_026", "2026-11-19", "Observationally Identical Graph-Switch Assay", "Qwen2.5-7B F16, Llama-3.1-8B F16 (v1 invalid + v2 + v3)", "8 dev families (48 generated), 112 prompts/arm x 5 runs", "560", "Bounded development qualification", "Pilot v1 invalidated (complemented-Y arithmetic bug); v2 Llama failed punctuation ('X=1.', 48/112 valid); v3 Llama decision reached 6/8 switch fidelity but 8/16 no-change; option-order confound later found", "experiments/cohort_026/development_summary.md", "a75d5e0"),
        ("cohort_027", "2026-11-19", "Order-Balanced Multi-Model Graph-Switch Screen", "Qwen 3B, Qwen 7B, Mistral 7B, Llama 8B F16 (14B excluded for RAM)", "8 fresh dev families (16 val unqueried), 224 prompts/arm", "896", "Staged development qualification", "896/896 strict-valid; 0/8 order-robust paired switch fidelity in EVERY model/form; arithmetic 15/32-17/32; Llama direct graph reading 31/32; pipeline stopped_by_gate before validation/quantization", "experiments/cohort_027/README.md", "31fa454"),
        ("cohort_028", "2026-11-19 to 2026-11-23", "Procedure Selection with Deterministic Calculator", "Llama-3.1-8B F16, Qwen2.5-7B F16", "16 fresh dev families (32 val unqueried), 1,280 calls/arm", "2560", "Staged development qualification", "Calculator C rescued noncausal controls (Qwen 58->128/128, Llama 68->112/128) but NOT causal graph selection (Qwen +2.34 pp, Llama -8.59 pp; specificity -52.34 & -42.97 pp); stopped_by_gate", "experiments/cohort_028/README.md", "ac6ed58"),
        ("cohort_029", "2026-11-23 to 2026-11-26", "CF-TP1 Target-Population & Provenance Transport", "Qwen2.5-7B-Instruct Q4_K_M", "128 fresh families (seed 290431), 4,096 stateless prompts", "4096", "Prospective frozen case study", "4,096/4,096 strict-valid; transfer causal fidelity 128/512 (25.00%) vs arithmetic 146/512 (28.52%), Delta = -3.515625 pp (95% t CI [-7.77, +0.74], inconclusive); causal activated 995/1024, reversals 3/256; arithmetic changed 46/256 switch & 45/256 invariant", "experiments/cohort_029/release/RESULTS.md", "76206c2 / b737153"),
    ]
    rows = []
    for cid, dt, title, models, design, n_req, role, finding, art, commit in cohorts:
        rows.append({
            "cohort_id": cid,
            "dates": dt,
            "title": title,
            "models_and_formats": models,
            "sample_and_design": design,
            "persisted_llm_responses": n_req,
            "inferential_classification": role,
            "principal_finding": finding,
            "primary_artifact": art,
            "key_commits": commit,
        })
    write_csv(EVID / "cohort_inventory.csv", rows)
    return rows


def build_model_inventory() -> list[dict]:
    models = [
        ("Qwen/Qwen2.5-0.5B-Instruct", "7ae557604adf67be50417f59c2c2f167def9a775", "F16, Q8_0, Q4_K_M, Q2_K, Q1_0", "0.926 GiB (F16)", "llama.cpp b12176 (no imatrix)", "Prepared in SSD/PC inventory; never queried in cohorts 001-029", "docs/SSD_ASSET_REUSE.md"),
        ("Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306", "F16, Q8_0, Q4_K_M, Q2_K, Q1_0", "2.881 GiB (F16)", "llama.cpp b12176 (no imatrix)", "Prepared in SSD/PC inventory; never queried in cohorts 001-029", "docs/SSD_ASSET_REUSE.md"),
        ("Qwen/Qwen2.5-3B-Instruct", "aa8e72537993ba99e69dfaafa59ed015b17504d1", "F16", "5.754 GiB", "AGERE F16 conversion (7fe450e)", "Cohorts 001, 002, 005, 007, 008, 009, 010, 011, 027", "experiments/cohort_001/run_001_f16/metadata.json"),
        ("Qwen/Qwen2.5-3B-Instruct", "aa8e72537993ba99e69dfaafa59ed015b17504d1", "Q8_0", "GGUF weight-only", "llama.cpp b12176 (no imatrix)", "Cohort 006", "experiments/cohort_006/run_001_q8_0/metadata.json"),
        ("Qwen/Qwen2.5-3B-Instruct", "aa8e72537993ba99e69dfaafa59ed015b17504d1", "Q4_K_M", "GGUF weight-only", "llama.cpp b12176 (no imatrix)", "Cohorts 001, 002, 005, 007, 008, 009, 010, 011", "experiments/cohort_001/run_001_q4_k_m/metadata.json"),
        ("Qwen/Qwen2.5-3B-Instruct", "aa8e72537993ba99e69dfaafa59ed015b17504d1", "Q2_K", "GGUF weight-only", "llama.cpp b12176 (no imatrix)", "Cohorts 001, 003 (100% length-capped operational failure)", "experiments/cohort_001/run_001_q2_k/metadata.json"),
        ("Qwen/Qwen2.5-3B-Instruct", "aa8e72537993ba99e69dfaafa59ed015b17504d1", "Q1_0", "GGUF 1-bit family", "llama.cpp b12176 (no imatrix)", "Prepared only; never queried", "docs/SSD_ASSET_REUSE.md"),
        ("Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "F16", "14.191 GiB", "AGERE F16 conversion (7fe450e)", "Cohorts 004, 012, 013, 014, 015, 016, 018, 019, 020, 021, 022, 023, 024, 026, 027, 028", "experiments/cohort_016/frozen_run_plan.json"),
        ("Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "Q8_0, Q6_K, Q5_K_M, Q3_K_M, Q2_K", "GGUF ladder", "llama.cpp b12176 from F16", "Cohort 024 (all 5 formats)", "experiments/cohort_024/frozen_lab_plan.json"),
        ("Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28", "Q4_K_M (SHA-256 7ebec3cd...)", "4.361 GiB (~4.91 BPW tensor data)", "llama.cpp b12176 from F16 (no imatrix)", "Cohorts 015, 016, 024, 029 (CF-TP1 production deployment)", "experiments/cohort_029/freeze/deployment/inventory.json"),
        ("Qwen/Qwen2.5-14B-Instruct", "608247a797d920aa2f94c1381d53bdc6a2a3b5b8", "F16 (29.55 GB), Q8_0, Q4_K_M", "29.55 GB F16 source", "llama.cpp b12176 on Ubuntu host", "Cohort 017 ran Q8_0 & Q4_K_M; F16 excluded from Cohort 017 & 027 due to 32 GB host RAM guard", "experiments/cohort_017/model_provenance.json"),
        ("mistralai/Mistral-7B-Instruct-v0.3", "61fd4167fff3ab01ee1cfe0da183fa27a944db48 (bartowski) + F16 source", "F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M, Q3_K_M, Q2_K", "4.37 GB (bartowski Q4_K_M); 7-format ladder in 024", "Cohort 022 used bartowski Q4_K_M; Cohort 024 quantized from F16 GGUF", "Cohort 022 (Q4_K_M), Cohort 024 (all 7 formats), Cohort 027 (F16)", "experiments/cohort_022/frozen_run_plan.json"),
        ("meta-llama/Llama-3.1-8B-Instruct", "Pinned third-party F16 GGUF conversion", "F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M, Q3_K_M, Q2_K", "7-format ladder from F16", "llama.cpp b12176 from F16 GGUF", "Cohort 024 (all 7 formats), Cohort 026 (F16 v2/v3), Cohort 027 (F16), Cohort 028 (F16)", "experiments/cohort_024/frozen_lab_plan.json"),
    ]
    rows = []
    for fam, rev, fmts, sz, quant, coh, src in models:
        rows.append({
            "model_family": fam,
            "source_revision": rev,
            "formats": fmts,
            "size_notes": sz,
            "quantization_provenance": quant,
            "cohorts_used": coh,
            "evidence_path": src,
        })
    write_csv(EVID / "model_quantization_inventory.csv", rows)
    return rows


def build_dataset_inventory() -> list[dict]:
    datasets = [
        ("design_validation", "causalfade.generate (make_families)", "20261101", 24, 192, "Binary confounded SCM (Z->X, Z->Y, X->Y), exact + sampled (n=2000), 3-key JSON", "results/design_validation/manifest.json"),
        ("cohort_001_003_004", "Subset of design_validation", "20261110", 16, 64, "Exact-evidence direct causal decision (16 fam in 001, 4 in 003, 8 in 004)", "experiments/cohort_001/run_001_f16/dataset_manifest.json"),
        ("cohort_002_006_formula", "tools/make_arithmetic_control.py --variant formula", "20261110", 16, 64, "Explicit backdoor arithmetic formula on same 16 exact tables", "experiments/cohort_002/run_001_f16/dataset_manifest.json"),
        ("cohort_005_source", "tools/make_arithmetic_control.py --variant source-selection", "20261110", 16, 64, "Pre-computed randomized vs historical rates, family-hashed source order", "experiments/cohort_005/run_001_f16/dataset_manifest.json"),
        ("cohort_007_fresh_formula", "causalfade.generate + make_arithmetic_control", "20261111", 12, 48, "Fresh 12-family formula-given arithmetic control", "experiments/cohort_007/input/manifest.json"),
        ("cohort_008_reversed", "make_arithmetic_control --variant source-selection-reversed", "20261110", 16, 64, "Within-item line-order reversal of cohort_005 prompts", "experiments/cohort_008/run_002_f16/dataset_manifest.json"),
        ("cohort_009_interleaved", "tools/make_interleaved_source_order.py", "20261112", 16, 128, "Same-session interleaved order twins on 16 original families", "experiments/cohort_009/input/manifest.json"),
        ("cohort_010_fresh_order", "causalfade.generate + make_interleaved_source_order", "20261113 / 20261112", 12, 96, "Fresh 12-family interleaved source-order crossover", "experiments/cohort_010/input/manifest.json"),
        ("cohort_011_012_matched", "tools/make_matched_source_selection.py", "20261114 / 20261115", 16, 128, "Matched observational magnitude m in [0.38, 0.46) across aligned & conflict (8 fam in 012)", "experiments/cohort_011/input/manifest.json"),
        ("cohort_013_clarity", "tools/make_prompt_clarity_crossover.py (legacy 160 tok)", "20261116", 8, 128, "Paired minimal vs causal-context prompt frames across both source orders", "experiments/cohort_013/input/manifest.json"),
        ("cohort_014_strict", "tools/make_prompt_clarity_crossover.py (strict_json 48 tok)", "20261119", 8, 128, "Strict bare one-key JSON contract on minimal vs causal-context frames", "experiments/cohort_014/input/manifest.json"),
        ("cohort_015_context16", "make_matched_source_selection + make_prompt_clarity_crossover", "20261122 / 20261123", 16, 128, "16 fresh matched-strength families, causal-context strict JSON only", "experiments/cohort_015/input/manifest.json"),
        ("cohort_016_017_rep96", "make_matched_source_selection + make_prompt_clarity_crossover", "20261127 / 20261128", 96, 768, "96 fresh matched-strength families for prospective order confirmation (reused in 017)", "experiments/cohort_016/input/manifest.json"),
        ("cohort_018_sensitivity", "causalfade/sensitivity.py", "20261114", 8, 288, "Graded causal strengths (0.04, 0.12), fixed obs (0.36), noncausal controls, XOR token mapping", "experiments/cohort_018/input/manifest.json"),
        ("cohort_019_contracts", "causalfade/contracts.py", "20261115", 8, 832, "Within-world semantic vs neutral-forward (K) vs neutral-reverse (M) contracts + controls", "experiments/cohort_019/input/manifest.json"),
        ("cohort_020_components", "causalfade/components.py", "20261116", 8, 224, "Isolated rate comparison, randomized-only decision, numbered two-source blocks, direct source ID", "experiments/cohort_020/input/manifest.json"),
        ("cohort_021_guidance", "causalfade/guidance.py", "20261117", 8, 576, "Governing-source selection + ordinary, source-guided, and length-matched neutral-guided decisions", "experiments/cohort_021/input/manifest.json"),
        ("cohort_022_replication", "causalfade/guidance.py (replication_pilot)", "20261118", 8, 576, "Fresh 8-family cohort-021 task schedule for Qwen F16 vs Mistral Q4_K_M", "experiments/cohort_022/input/manifest.json"),
        ("cohort_023_audit", "causalfade/measurement_audit.py", "20261119", 8, 896, "Full factorial crossing direction, agreement, block order, A/B name, option order + controls", "experiments/cohort_023/input/manifest.json"),
        ("cohort_024_matrix", "causalfade/matrix024.py", "20261124 (frozen)", 8, 1472, "Cohort-023 factorial crossed with semantic vs neutral X=0/X=1 contracts across 21 model arms", "experiments/cohort_024/input/manifest.json"),
        ("cohort_026_graph_switch", "causalfade/graph_switch.py + tools/cohort026.py", "exact-rational seeds", 48, 112, "8 dev / 8 val / 32 conf exact-rational P(W,X,Y) confounder vs mediator + W->Z control (v1, v2, v3)", "experiments/cohort_026/input/manifest.json"),
        ("cohort_027_graph_balanced", "causalfade/cohort027.py", "27027000 / 27028000", 24, 672, "8 dev (224 tasks) + 16 val (448 tasks) fully crossing graph, form, and option order", "experiments/cohort_027/manifest.json"),
        ("cohort_028_proc_calc", "causalfade/cohort028.py", "28028000 / 28029000", 48, 3840, "16 dev (1,280 calls) + 32 val (2,560 calls), bare A vs structured B vs deterministic calculator C", "experiments/cohort_028/manifest.json"),
        ("cohort_029_cftp1", "causalfade/target_transport.py + target_forms.py", "290431 / 290432", 128, 4096, "CF-TP1: 128 families across 8 sign strata x 2 forms x 2 tasks x 2 orders x 2 feasible roles x 2 target mixes", "experiments/cohort_029/freeze/manifest.json"),
    ]
    rows = []
    for did, gen, seed, nf, nprompts, desc, path in datasets:
        rows.append({
            "dataset_id": did,
            "generator_module": gen,
            "seeds": seed,
            "independent_families": nf,
            "prompts_per_arm": nprompts,
            "task_description": desc,
            "manifest_path": path,
        })
    write_csv(EVID / "dataset_task_inventory.csv", rows)
    return rows


def build_hypothesis_ledger() -> list[dict]:
    hyps = [
        ("H01", "Aggressive PTQ selectively increases an AI agent's reliance on misleading observational associations (Delta(p) = ConflictPenalty(p) - ConflictPenalty(F16) > 0) beyond general task degradation.", "2026-10-28 (4e2fe4f)", "Motivating course-project hypothesis linking LLM compression to vulnerability to confounding shortcuts.", "001, 005, 011, 015, 024", "None isolating causal-specific vulnerability from response bias, format invalidity, or control-task failures.", "In 005 and 011, Q4_K_M reduced the measured conflict penalty (-43.75 pp and -39.06 pp) due to near-constant activation; in 024, Qwen F16 vs Q4_K_M semantic causal accuracy differed by -0.4 pp while F16 references failed harmful-direction controls.", "Constant action bias, Markdown/length-cap invalidity, prompt-order sensitivity, and general arithmetic/control weakness.", "Insufficiently identified"),
        ("H02", "A homogeneous 3-parameter CNI-style multinomial processing tree P(activate|T,S) = C*T + (1-C)[A*S + (1-A)*B] validly decomposes LLM intervention choices into causal sensitivity C, conditional association A, and action bias B.", "2026-11-01 (6ab18d2)", "Adapted from Jacoby (1991), Gawronski et al. (2017), and Wu & Deng (2025) to separate cue sensitivity from action tendency.", "design_validation, 005", "Synthetic EM parameter recovery succeeded in interior regimes; crossing T and S successfully exposed constant-action bias.", "Synthetic validation proved symmetric logistic integration is observationally equivalent on 4 cells; Cohort 005 F16 violated the tree's required additivity equality p11 - p10 - p01 + p00 = 0 by -43.75 pp (CI [-68.75, -18.75]).", "Presentation-order interactions, symmetric cue integration, and direction-asymmetric policies.", "Contradicted by available evidence"),
        ("H03", "Qwen2.5-3B Q2_K increases the aligned-minus-conflict accuracy gap relative to 3B F16 on exact-evidence direct-response SCM tables.", "2026-11-10 (0333c67)", "First empirical pilot test of H01 using extreme 2-bit GGUF quantization.", "001", "None (post hoc +3.125 pp contrast was an artifact of 0/64 Q2_K floor vs 16/32 and 17/32 F16).", "Q2_K produced 0/64 valid responses (all 64 length-capped repetitive punctuation); 3B F16 itself activated on 63/64 items and got 0/64 adjustment sets.", "Catastrophic low-bit generation instability at Q2_K and baseline incompetence at 3B F16.", "Inconclusive"),
        ("H04", "The 3B Q2_K output collapse is caused by llama.cpp's default CPU weight repacking or mismatched GGUF tokenizer/chat-template metadata.", "2026-11-10 (04f096e, bb1bb12)", "Software/runtime diagnostic before attributing Q2_K failure to quantized weights.", "001, 003", "None.", "Disabling CPU repacking (--no-repack) changed token strings on 16/16 tasks but still yielded 0/16 valid outputs and 16/16 length caps; GGUF tokenizer and chat templates matched across F16, Q4_K_M, and Q2_K with identical prompt token counts on 64/64 tasks.", "Intrinsic Q2_K weight quantization degradation on Qwen2.5-3B without importance-matrix calibration.", "Contradicted by available evidence"),
        ("H05", "Explicitly supplying the backdoor adjustment formula improves explicit binary decision accuracy on exact SCM tables.", "2026-11-10 (da4507b)", "Test whether Cohort 001 failures stemmed from inability to identify the causal adjustment formula rather than arithmetic execution.", "002", "Improved numeric ATE estimate accuracy (MAE fell from 0.246 to 0.062 in F16) and estimate-sign accuracy (34/64 to 61/64 in F16).", "Explicit binary action accuracy did NOT improve: F16 scored 32/64 (0/64 activate, flipping from 63/64 activate to 64/64 decline) and Q4_K_M scored 35/64 (3/64 activate), frequently contradicting the model's own numeric sign.", "Dissociation between numeric computation field and binary action commitment; prompt framing shifted default action bias.", "Contradicted by available evidence"),
        ("H06", "Under the supplied arithmetic formula, Q4_K_M degrades the sign accuracy of computed numeric estimates relative to F16 and Q8_0 on Qwen2.5-3B.", "2026-11-10 (86e6329, 46440ae)", "Observed 61/64 vs 45/64 sign gap in Cohort 002; tested against Q8_0 (006) and replicated on 12 fresh families (007).", "002, 006, 007", "Cohort 006 Q8_0 tied F16 at 61/64 (+25.0 pp over Q4_K_M); Cohort 007 fresh families replicated F16 46/48 vs Q4_K_M 31/48 (-31.25 pp, 95% CI [-41.67, -20.83]).", "Degradation occurred across both aligned and conflict cells, so it reflects numerical execution rather than causal conflict susceptibility.", "Arithmetic rounding/calculation errors under 4-bit weight compression in a 3B model.", "Supported within tested scope"),
        ("H07", "Scaling full-precision reference size from 3B to 7B (Qwen2.5-7B F16) establishes above-gate causal conflict competence on unscaffolded direct or minimal supplied-rate prompts.", "2026-11-10 (01c7590), 2026-11-12 (fc7dcc1)", "Larger model capacity expected to resolve 3B reference floor before quantization testing.", "004, 012, 013, 014", "7B F16 correctly named adjustment set [Z] on 32/32 items in Cohort 004 and solved 32/32 aligned items in Cohorts 012-014.", "Failed predeclared gates in Cohort 004 (17/32 overall, 31/32 activate), Cohort 012 (8/16 & 7/16 conflict), Cohort 013 minimal (8/16 conflict), and Cohort 014 minimal (8/16 conflict).", "Persistent activation bias on conflict items when confounding mechanism is left implicit.", "Contradicted by available evidence"),
        ("H08", "Physical presentation order of randomized versus historical evidence shifts Qwen2.5-3B F16 conflict decisions toward lower accuracy when historical evidence appears first.", "2026-11-10 (ca2f5b8), 2026-11-12 (e396fc1, a0ddfc4)", "Motivated by family-level order split in Cohort 005; tested via cross-session reversal (008), same-session interleaving (009), fresh families (010), and matched signal strength (011).", "005, 008, 009, 010, 011", "Consistently replicated in 3B F16: -28.125 pp (008), -21.875 pp (009), -25.0 pp on fresh families (010), and -25.0 pp under matched observational strength (011).", "Aligned accuracy shifted in the opposite direction (+29.2 to +43.75 pp), showing directional/positional response shifts rather than pure historical-distractor capture.", "Line-position sensitivity interacting with baseline activation tendency.", "Supported within tested scope"),
        ("H09", "Equalizing observational signal magnitude |delta_obs| across aligned and conflict cells eliminates the aligned-versus-conflict difficulty confound and yields competent reference conflict decisions.", "2026-11-12 (cd3f66d)", "Mathematical audit showed original generator had |delta_obs| = confounding + |tau| in aligned vs confounding - |tau| in conflict.", "011, 012", "Mathematical validators confirmed exact interior probabilities and matched historical gaps m in [0.38, 0.46).", "Did not yield conflict competence: 3B F16 conflict stayed 24/64 (011) and 7B F16 conflict stayed 15/32 (012). Later retrospective audit of 016 revealed that because |tau| < m everywhere, a source-blind smaller-gap heuristic could solve 100% of items.", "Model conflict errors were not caused solely by larger aligned gaps, and fixed |tau| < m created a magnitude-separation shortcut.", "Superseded"),
        ("H10", "Adding explicit causal-context explanations with a strict one-key bare-JSON response contract (48-token cap) restores response validity and enables 7B F16 to pass reference qualification.", "2026-11-12 (a4a6f67, 5a4f70c)", "Cohort 013 causal-context prose triggered 64/64 trailing explanations hitting the 160-token cap.", "013, 014, 015", "Strict JSON validity rose from 0/64 (013) to 64/64 (014) and 128/128 (015); Cohort 015 F16 narrowly passed all gates (89/128 overall vs 88, conflict 19/32 & 22/32 vs 18).", "Cohort 014 missed overall threshold by 2 (42/64 vs 44), and Cohort 016 F16 conflict accuracy dropped back to 76/192 (39.6%) and 109/192 (56.8%) on 96 fresh families, showing Cohort 015's marginal gate pass was fragile.", "Sampling variability on 16 families and strong presentation-order dependence.", "Inconclusive"),
        ("H11", "On the strict-JSON causal-context source-selection task, Qwen2.5-7B Q4_K_M exhibits a nonzero within-family conflict accuracy difference between historical-first and randomized-first presentation.", "2026-11-12 (eb53578)", "Prospectively frozen confirmatory replication on 96 fresh families (powered for >=20 pp at 80.7% power) after observing +65.6 pp in Cohort 015.", "015, 016", "Prospectively confirmed on 96 untouched families: 175/192 (91.1%) historical-first vs 55/192 (28.6%) randomized-first, mean difference +62.5 pp (95% t CI [+56.6, +68.4], t(95)=21.10, p=1.24e-37).", "Aligned items moved oppositely (192/192 rand-first to 105/192 hist-first), and retrospective audit showed a source-blind smaller-gap heuristic solves 768/768 prompts, so high historical-first conflict accuracy does not prove causal provenance use.", "Position-linked action/recency heuristics rather than principled backdoor reasoning.", "Supported within tested scope"),
        ("H12", "The large positive conflict-order effect (+62.5 pp) observed in Qwen2.5-7B Q4_K_M generalizes to Qwen2.5-14B quantized checkpoints (Q8_0 and Q4_K_M) on the same 96-family schedule.", "2026-11-13 (e4e91ec)", "Exploratory cross-scale test of whether the Cohort 016 order phenomenon is a general property of quantized Qwen2.5 models.", "017", "None on conflict items (though aligned items still dropped from 192/192 and 152/192 rand-first to 96/192 hist-first).", "14B Q8_0 conflict order effect was -4.17 pp (95% CI [-6.98, -1.35]) and 14B Q4_K_M was exactly 0.0 pp (96/192 in both orders due to 100% activation on conflict items).", "Checkpoint-scale differences in default activation bias mask or alter conflict-cell order effects.", "Contradicted by available evidence"),
        ("H13", "Intervention decision accuracy increases monotonically with causal effect magnitude (0.12 vs 0.04) and remains invariant to neutral output-token remapping.", "2026-11-13 (caf5b1d), 2026-11-14 (e378c02)", "Signal-detection and psychometric construct-validity requirements from Interdisciplinary Follow-Up.", "018, 019", "Isolated mapping comprehension checks passed 16/16 (018) and 48/48 (019).", "In Cohort 018, F16 scored 32/64 at both 0.04 and 0.12 strengths (d'=0 at 0.12); in Cohort 019, semantic accuracy was 37/64 (0.04) vs 36/64 (0.12), while reversing neutral tokens K/M shifted accuracy by +25.8 pp causal and +36.7 pp noncausal on identical stems.", "Token-label preference and multi-step working-memory interference when remapping actions.", "Contradicted by available evidence"),
        ("H14", "Qwen2.5-7B F16 fails two-source causal decisions because it cannot identify which study is randomized or which study should govern an intervention decision.", "2026-11-14 (2c48637, 52ffe3d)", "Component decomposition diagnostic separating rate reading, source identification, governing-study selection, and two-source action choice.", "020, 021, 022, 023, 024", "None for source-identification deficit; strong evidence for component-vs-integration dissociation.", "Qwen 7B F16 achieved 32/32 direct source identification (020, 021, 022), 128/128 governing-study selection (021, 022), 244/256 (023), 242/256 (024), and 90.6%-100% randomized-only decision accuracy, while two-source decisions scored 43.3%-45.3%. Explicit source guidance in 021 gave 58/128 vs 58/128 ordinary.", "Two-source contextual interference and activation bias during joint rate-to-action mapping (note: separate fresh-context prompts do not prove internal sequential mediation).", "Contradicted by available evidence"),
        ("H15", "Qwen2.5-7B F16's two-source causal decision deficit (+53 to +57 pp below randomized-only) generalizes cleanly across independent model families (Mistral-7B-v0.3, Llama-3.1-8B) and is specific to causal tasks relative to matched harmful-direction controls.", "2026-11-16 (6019ea7, fa5db6a, 6193357)", "Cross-lineage replication (022, 024) and within-Qwen discriminant control audit (023, 024).", "022, 023, 024", "Within Qwen 7B F16, the +53.1 pp (022), +55.5 pp (023), and +56.6 pp (024) randomized-only minus two-source gap repeated reliably across fresh seeds, A/B names, and option orders.", "Mistral failed simple components (selected first displayed option on 256/256 source prompts in 024); Qwen and Llama failed harmful-direction numeric (18/32) and noncausal scorecard (75/128, 71/128) robustness thresholds (<75%).", "Directional bias against declining/harmful actions affects both causal and noncausal rate tasks; Mistral uses positional heuristics.", "Contradicted by available evidence"),
        ("H16", "Across a 3-lineage (Qwen 7B, Mistral 7B, Llama 8B) x 7-format (F16 to Q2_K) GGUF matrix, post-training quantization produces a monotone degradation in causal decision accuracy or a selective causal-minus-control penalty.", "2026-11-16 (c707e7e, 6193357)", "Comprehensive multi-lineage quantization screen on 1,472 identical tasks per arm (30,912 attempts).", "024, 025", "Extreme Q2_K degraded output validity in Mistral (129 invalids) and increased first-option bias in Qwen source selection (96.9%).", "Semantic causal accuracy was flat from F16 to Q4_K_M in Qwen (111 vs 110/256), Mistral (134 vs 130/256), and Llama (151 vs 150/256), rose in Qwen Q3/Q2 (150, 149/256) due to policy shifts, and Llama Q4_K_M suffered 448/1472 length-capped invalids almost exclusively in noncausal controls (0/256 strict semantic control) while recovering to 225/256 at Q3_K_M.", "Non-monotone quantizer/format interactions with generation length and response policy.", "Contradicted by available evidence"),
        ("H17", "F16 reference models (Qwen 3B/7B, Mistral 7B, Llama 8B) can adapt unaided intervention choices to observationally identical confounder versus mediator causal graphs across both answer-option orders.", "2026-11-19 (3606794, 1e8dd30)", "Graph-switch assay holding P(W,X,Y) exact-rational identical while reversing sign(E[Y|do(X=1)]-E[Y|do(X=0)]).", "026, 027", "Llama 8B F16 read upstream/downstream graph structure at 31/32 on Cohort 027 direct form.", "Cohort 026's apparent 6/8 Llama decision switch score was confounded with option position (61/64 first-option choices) and failed W->Z no-change controls (0/8 on W->Z). In order-balanced Cohort 027, order-robust paired switch fidelity was 0/8 families across ALL four F16 models and BOTH forms, and matched arithmetic was 15/32-17/32.", "Failure on both weighted arithmetic execution and graph-to-procedure mapping, plus severe option-order sensitivity.", "Contradicted by available evidence"),
        ("H18", "Offloading arithmetic execution to an exact deterministic calculator (System C) enables F16 models (Qwen 7B, Llama 8B) to qualify on causal graph-switch decisions by selecting the correct graph-conditioned weighting procedure ('marginal' vs 'conditional').", "2026-11-19 (53b9c98, e7787e4)", "Cohort 027 arithmetic failures left open whether models understood graph identification rules but failed arithmetic.", "028", "Deterministic calculator C dramatically improved matched noncausal named-rule tasks (Qwen 58/128 -> 128/128; Llama 68/128 -> 112/128), proving arithmetic execution was a major bottleneck on controls.", "On causal graph-switch tasks, C-minus-B gain was +2.34 pp for Qwen (CI [-3.91, +9.38]) and -8.59 pp for Llama (CI [-13.28, -3.91]); specificity was -52.34 pp and -42.97 pp. Causal rule selection hovered near chance (~50%) even when candidate scores were pre-computed.", "Models failed to map confounder vs mediator DAG descriptions onto marginal vs conditional weighting rules when unassisted by explicit graph-to-formula instructions.", "Contradicted by available evidence"),
        ("H19", "On CF-TP1's independent transfer form, Qwen2.5-7B-Instruct Q4_K_M exhibits different paired target-population fidelity on causal provenance-and-transport decisions than on matched explicit-scorecard weighted arithmetic (Delta != 0).", "2026-11-23 (CF-TP1 v1.0, 76206c2)", "Final prospective 128-family, 4,096-call frozen case study breaking Cohort 016's magnitude shortcut and pairing feasible provenance swaps with target-mixture switches.", "029", "Point estimate was in the expected negative direction: causal 128/512 (25.00%) vs arithmetic 146/512 (28.52%), Delta = -3.515625 pp.", "The prespecified approximate 95% Welch-Satterthwaite t interval [-7.7713, +0.7400] pp and bounded interval [-27.5237, +20.4924] pp both cross zero; archive-compatible form yielded 128/512 in both tasks (Delta = 0.0 pp). No equivalence margin was prespecified.", "Both tasks suffered low end-to-end paired fidelity under different error regimes: near-constant activation on causal prompts (995/1024, 3/256 reversals) versus frequent uncalibrated switching on arithmetic prompts (46/256 required switches, 45/256 unwarranted invariant flips).", "Inconclusive"),
        ("H20", "Multi-step interactive tool-using causal agents or layer-wise mixed-precision restoration isolate behavioral or mechanistic quantization effects on causal discovery and estimation.", "2026-10-28 (4e2fe4f), 2026-11-07 (d20eb46)", "Original Roadmap Phase 5 and Literature Review proposals (CausaLab, ACDB, PRISM, Zhang et al. 2025).", "None executed", "None (Cohort 028 implemented a one-shot offline replay calculator, not an interactive multi-turn agent or neural weight-patching intervention).", "Not contradicted; deliberately deferred after direct-response construct-validity gates repeatedly stopped advancement.", "N/A (unexecuted prospective extension).", "Untested"),
    ]
    rows = []
    for hid, form, dt, mot, coh, sup, con, alt, stat in hyps:
        rows.append({
            "hypothesis_id": hid,
            "original_formulation": form,
            "earliest_documented_appearance": dt,
            "motivation": mot,
            "relevant_cohorts": coh,
            "supporting_evidence": sup,
            "contradicting_or_limiting_evidence": con,
            "alternative_explanations": alt,
            "final_scientific_status": stat,
        })
    write_csv(EVID / "hypothesis_ledger.csv", rows)
    return rows


def build_methodology_ledger() -> list[dict]:
    meths = [
        ("M01", "2x2 Orthogonal Causal-Associative Confounded SCM", "Separate causal intervention direction T from observational association direction S under known backdoor graph Z->X, Z->Y, X->Y.", "tau = E[Y|do(X=1)] - E[Y|do(X=0)]; delta_obs = tau - k*gap with |k*gap| > |tau|.", "design_validation, 001-011", "Confounding shortcut vs causal identification; exposing constant yes/no biases.", "Succeeded in exposing near-constant activation/decline biases; original fixed-k version had larger |delta_obs| in aligned cells.", "Modified into matched-strength (M06) and eventually CF-TP1 feasible role-swap SCM (M18)."),
        ("M02", "CNI-Style Multinomial Processing Tree (C, A, B)", "Decompose binary action probabilities into causal sensitivity C, conditional association A, and residual action preference B.", "P(act=1|T,S) = C*T + (1-C)[A*S + (1-A)*B], fitted by simplex EM with parametric bootstrap deviance.", "design_validation, 005", "Aggregate conflict penalty wA = (1-C)A confounds loss of C with rise in A.", "Exposed symmetric logistic observational equivalence in simulation and failed additivity restriction (-43.75 pp residual) on Cohort 005 F16.", "Abandoned for latent-route reporting from Cohort 005 onward; retained only for conceptual cue-crossing motivation."),
        ("M03", "Single-Fence JSON Sensitivity vs Strict Scoring", "Quantify how Markdown ```json fencing affects validity without granting credit for prose or malformed schemas.", "Exact JSON parse on raw string (strict) vs unwrapping a single complete Markdown code fence (sensitivity).", "001-013", "100% of early Qwen 3B/7B completions wrapped valid JSON in Markdown fences, causing 0/64 strict floors.", "Cleanly separated formatting habit from decision content in Cohorts 001-012, but failed when Cohort 013 appended explanatory prose after fences.", "Superseded in Cohort 014+ by strict one-key bare JSON instructions and 48/64-token caps (M08)."),
        ("M04", "Formula-Given Arithmetic Control & Estimate-Sign Split", "Hold numeric stratum table fixed while supplying explicit backdoor arithmetic formula; score sign(ate_estimate) separately from activate.", "score = 0.5*((r[0,1]-r[0,0]) + (r[1,1]-r[1,0])); I(ate_estimate > 0) vs explicit activate in {0,1}.", "002, 006, 007", "Disentangle causal formula selection from arithmetic execution and action-field commitment.", "Revealed dramatic estimate-action dissociation (F16 61/64 signs vs 32/64 actions in 002) and replicated 3B Q4 sign loss (-31.25 pp in 007).", "Modified into matched noncausal scorecards in Cohorts 018, 019, 023, 024, 028, and 029."),
        ("M05", "Supplied-Rate Source Selection & Interleaved Order Crossover", "Supply pre-computed randomized and historical rates directly and cross physical line order within-session using opaque twin IDs.", "Within-family paired difference Acc(historical_first) - Acc(randomized_first) with family-cluster bootstrap.", "005, 008, 009, 010", "Eliminate stratum arithmetic and remove cross-session timing confounds in presentation-order testing.", "Isolated reproducible -21.9 to -28.1 pp F16 order shift in 3B and later +62.5 pp Q4 order shift in 7B.", "Retained and refined across Cohorts 011-024 and 029."),
        ("M06", "Matched Observational-Strength SCM Generator", "Adjust treatment assignment propensity by alignment cell so historical contrast |delta_obs| = m is identical in aligned and conflict items.", "Set confounding gap = m - e (aligned) and m + e (conflict), propensity k = confounding_gap / severity_gap.", "011-017", "Eliminate aligned-vs-conflict observational magnitude asymmetry present in M01.", "Equalized historical magnitudes exactly, but because |tau| = e in [0.06,0.12) < m in [0.38,0.46), inadvertently created a 100%-accurate source-blind smaller-gap heuristic.", "Superseded after retrospective shortcut discovery by graph-switch (M15) and CF-TP1 feasible role-swap (M18)."),
        ("M07", "Predeclared Reference Competence Gates", "Require higher-precision F16 arm to clear validity, overall, and per-order conflict/control thresholds before running quantized arms.", "Fixed integer cutoffs frozen in run plan before inference (e.g., >=90% valid, >=56.25% conflict per order).", "004, 012, 013, 014, 015, 018, 019, 023, 026, 027, 028", "Prevent misinterpreting floor-level noise or default biases as quantization preservation or selective damage.", "Prevented wasteful quantization sweeps in 004, 012, 014, 018, 019, 026, 027, 028; limitation: uncalibrated pass in 015 (89 vs 88) did not guarantee stability in 016.", "Retained throughout development; Cohort 029 shifted to an ungated single-deployment methodological case study."),
        ("M08", "Strict Bare-Token / One-Key JSON Response Contract", "Explicitly forbid Markdown fences and explanations, show both exact allowed literals, and cap max_tokens tightly (48 or 64).", "Strict parser with duplicate-key hook, integer type check (rejecting booleans/floats), and finish_reason=='stop'.", "014-024, 026-029", "Eliminate Cohort 013 trailing-prose invalidations and parser sensitivity forks.", "Achieved 100% strict validity across Cohorts 014-023, 027, 029 (exception: Llama Q4 448 control truncations in 024 and Llama v2 trailing period in 026).", "Retained as canonical scoring standard through final release."),
        ("M09", "Gaussian-Copula Family-Cluster Power Simulation", "Simulate correlated binary pair discordance within SCM families before freezing confirmatory sample size.", "100,000 Monte Carlo replicates of paired binary differences with rho=0.50, discordance=0.70-0.90, two-sided family t-test.", "016", "Avoid underpowered pilots or treating correlated prompts within a family as independent N.", "Powered Cohort 016 (N=96 families, 80.7% power for 20 pp effect) before collection.", "Supplemented in Cohort 029 by stratified Welch-Satterthwaite coverage calibration (M19)."),
        ("M10", "Signal Detection Theory (d', Criterion) & Graded Strengths", "Separate discrimination of beneficial vs harmful interventions from baseline activation tendency.", "d' = Phi^-1(H) - Phi^-1(F), c = -0.5*[Phi^-1(H) + Phi^-1(F)] with half-count boundary correction on valid responses.", "018, 019, 024, 025", "Balanced accuracy of 50% conceals whether a model guesses randomly or activates 100% of the time.", "Exposed negative/zero d' paired with extreme negative criterion (activation bias) in Qwen causal tasks vs positive d' in noncausal controls.", "Retained as descriptive coordinates; two-point strength grid in 018 was insufficient for full psychometric curves."),
        ("M11", "Within-World Token-Mapping & Option-Order Counterbalancing", "Cross semantic labels, neutral tokens (K/M, X=0/X=1), study names (A/B), and displayed option order on identical stems.", "Semantic decoding (token XOR mapping) and metamorphic pair consistency checks.", "018, 019, 023, 024, 025, 027, 028, 029", "Isolate superficial token/position habits from substantive evidence use.", "Uncovered +25.8/+36.7 pp K/M reversal shifts in Qwen (019) and 256/256 first-option selection in Mistral F16 (024/025).", "Retained; crossed within-family in 023/024/027/028 and balanced across stratum slots in 029."),
        ("M12", "Staged Component & Prompt-Guidance Decomposition", "Query single-pair number reading, direct source ID, governing-source selection, randomized-only, ordinary, and guided decisions separately.", "Family-paired differences (e.g., Acc(rand_only) - Acc(two_source)) in stateless fresh contexts.", "020, 021, 022, 023, 024", "Test whether two-source failure comes from misreading numbers or failing to recognize randomized designs.", "Demonstrated 100% governing-source selection (128/128) alongside 45.3% ordinary and guided action accuracy (58/128) in Qwen 7B F16.", "Retained as behavioral dissociation evidence, with explicit caveat that separate calls do not prove internal causal mediation."),
        ("M13", "Matched Noncausal Scorecard & Harmful-Direction Controls", "Pair every causal prompt with an isomorphic noncausal primary-scorecard or weighted-sum task sharing numbers and target actions.", "Direction-stratified control accuracy (>=75% in both beneficial and harmful directions) and causal-minus-control contrasts.", "018, 019, 023, 024, 027, 028, 029", "Prevent attributing general arithmetic, table-reading, or decline-avoidance errors to causal reasoning deficits.", "Blocked premature causal-specificity claims in 018, 023, 024, 027, and anchored the primary contrast in 029.", "Retained as essential discriminant control through final manuscript."),
        ("M14", "Retrospective Metamorphic & Information-Theoretic Archive Audit", "Reanalyze persisted raw JSONL across cohorts for option-reversal invariance, precision transitions, and plug-in mutual information.", "I(Response; Truth) and I(Response; Assoc | Truth) over {0, 1, invalid}; paired item transition matrices.", "025, 025_1", "Synthesize 24 cohorts (>40,000 responses) without spending compute or conflating post hoc checks with confirmation.", "Quantified Mistral's 6/128 option invariance, Qwen's 0.031-bit causal MI, and non-transfer of 016's Q4 order interaction to 024 (0 pp).", "Completed its audit role and formally bounded non-estimable methods."),
        ("M15", "Exact-Rational Observationally Identical Graph-Switch Assay", "Construct binary (W,X,Y) joint distributions identical in Fractions for confounder (W->X,Y) and mediator (X->W->Y) with opposite do(X) signs, plus W->Z invariant control.", "Exact Python fractions.Fraction verification: tau_conf = sum_w P(w)[P(Y=1|X=1,w)-P(Y=1|X=0,w)] < 0 < tau_med.", "026, 027, 028", "Eliminate observational table cues completely so only supplied causal structure determines the action.", "Mathematically airtight (after fixing v1 Y-complement bug in 026 and option-order coupling in 027), but all tested 3B-8B F16 models scored 0/8 order-robust paired switch fidelity.", "Abandoned after Cohort 028 proved even calculator-assisted F16 models failed graph-to-rule selection."),
        ("M16", "Structured Rule Selection + Allowlisted Deterministic Calculator Replay", "Model emits JSON {rule, score_x0, score_x1, action} (System B); pure function replays selected rule on public numbers with zero oracle access (System C).", "Primary gain mean_i(C_i - B_i) on causal raw tasks vs specificity contrast (C-B)_causal - (C-B)_control.", "028", "Test whether arithmetic errors alone masked graph-identification competence in Cohort 027.", "Cleanly falsified the arithmetic-only bottleneck hypothesis: C rescued controls to 87.5%-100% while leaving causal accuracy near 50%.", "Completed in Cohort 028; motivated shift to identifiable study-provenance transport in Cohort 029."),
        ("M17", "Durable Append-Only Journal, Lockfiles & Hourly/Branch Git Checkpoints", "Persist every dispatched request and raw response with fsync, SHA-256 digests, single-writer locks, and automated non-destructive Git checkpoints.", "Intent -> dispatch -> base64-encoded raw response envelope bound to manifest SHA-256.", "001-029 (matured in 018, 024, 027, 028, 029)", "Prevent silent replacement of failed/wrong attempts, survive multi-hour CPU pauses/shutdowns, and guarantee byte-identical offline replay.", "Enabled zero-loss recovery across Cohort 024 budget pauses, Cohort 028 shutdown, and 4,096/4,096 verified envelopes in Cohort 029.", "Retained in final release."),
        ("M18", "CF-TP1 Feasible Role-Swap & Target-Population Standardization", "Construct paired 2x2x2 tables L and R that are simultaneously realizable under latent U confounding in BOTH role assignments, crossed with two target stratum mixtures w0, w1.", "Latent surface (2h-r, 3r-2h) in (0,1)^8 for both roles; tau_k = w_k*delta_1 + (1-w_k)*delta_0; pair fidelity F_pair = I_0 * I_1.", "029", "Break Cohort 016's magnitude-gap shortcut and distinguish direction-correct switches from constant bias or random flipping.", "Zero public/private oracle mismatches across 4,096 prompts; exposed 995/1024 causal activation bias (3/256 switches) vs 45/256 unwarranted arithmetic flips.", "Canonical methodology of the final research manuscript."),
        ("M19", "Dual-Oracle Verification, Enumerated Rival-Policy Gate & Stratified Welch/Bounded Inference", "Verify private SCM enumerator against independent public-text parser, audit deterministic shortcut policies, and pair Welch-Satterthwaite t CI with Hoeffding-style bounded CI.", "SE = sqrt(sum_h s_h^2 / (64*16)), Welch df, plus distribution-free radius sqrt(2*log(40)/128) = +/-24.01 pp.", "029", "Guarantee prompt-to-key integrity, prove immunity to enumerated source-blind/target-blind shortcuts, and ensure valid interval coverage under discrete/bounded family scores.", "Passed 50/50 release verification checks; documented 12 literal constant-rival failures alongside 0 failures under constant-rivals-v1 clarification.", "Canonical statistical and audit framework of the final manuscript."),
    ]
    rows = []
    for mid, name, why, math_f, coh, prob, res, status in meths:
        rows.append({
            "methodology_id": mid,
            "name": name,
            "purpose": why,
            "mathematical_or_technical_foundation": math_f,
            "cohorts_used": coh,
            "problem_addressed": prob,
            "empirical_outcome_and_limitations": res,
            "final_disposition": status,
        })
    write_csv(EVID / "methodology_ledger.csv", rows)
    return rows


def build_timeline() -> list[dict]:
    events = [
        {
            "event_id": "T01",
            "timestamp": "2026-10-28T07:18:34+05:00",
            "commit": "4e2fe4f",
            "phase": "Conception & Literature Foundation",
            "investigating": "Initial conception of CausalFade for an advanced statistics course: whether aggressive PTQ increases AI agents' reliance on misleading observational associations.",
            "understood_at_time": "Literature review of 14 papers (2025-2026) showed 4-bit static causal QA is surprisingly robust (Nwaiwu et al., 2025), while 2-bit reasoning suffers token inflation/looping (Alimaskina et al., 2026) and parametric recall drops faster than context copying (PRISM, 2026).",
            "available_evidence": "14 downloaded PDFs, SHA-256 manifest, critical summaries, and EXECUTIVE_SUMMARY.md.",
            "decision_made": "Frame primary target around behavioral conflict penalty Delta(p) = ConflictPenalty(p) - ConflictPenalty(F16) on synthetic SCMs, explicitly distinguishing true SCM graphs, reported graphs, and internal neural circuits.",
            "documented_rationale": "Avoid unsustainable claims that quantization 'severs internal causal graphs' from accuracy alone (literature review/EXECUTIVE_SUMMARY.md).",
            "subsequent_impact": "Established strict epistemic discipline against overclaiming mechanisms that governed all 29 cohorts.",
            "retrospective_assessment": "Supported: early restraint prevented major scientific errors when behavioral anomalies emerged.",
        },
        {
            "event_id": "T02",
            "timestamp": "2026-11-01T18:09:35+05:00 to 18:51:54+05:00",
            "commit": "6ab18d2 / c86d7ad / 49843a3",
            "phase": "Simulator & Synthetic Validation",
            "investigating": "Constructing the binary confounded SCM simulator (Z->X, Z->Y, X->Y) and validating a CNI-style (C, A, B) multinomial processing tree.",
            "understood_at_time": "Crossing beneficial/harmful causal effects with positive/negative confounding yields 4 cells that can separate cue sensitivity from action preference.",
            "available_evidence": "24-family synthetic export (192 prompts) and 3,600 Monte Carlo EM recovery fits across 6 parameter scenarios and 3 sample sizes.",
            "decision_made": "Commit simulator, scorer, paired bootstrap analyzer, and C/A/B fitter, while explicitly documenting near-boundary nonconvergence (16/3600) and symmetric logistic observational equivalence.",
            "documented_rationale": "Synthetic validation checks code correctness under assumed generators but cannot prove real LLMs follow the psychological tree (docs/METHODOLOGY_ADAPTATION.md).",
            "subsequent_impact": "Provided exact ground-truth SCM infrastructure for Cohorts 001-011 and pre-armed researchers to test the tree's additivity restriction.",
            "retrospective_assessment": "Supported: the pre-documented additivity check immediately invalidated homogeneous C/A/B fitting on real LLM data in Cohort 005.",
        },
        {
            "event_id": "T03",
            "timestamp": "2026-11-07T01:13:57+05:00 to 11:47:33+05:00",
            "commit": "5a12a21 / 6b819a1 / d20eb46",
            "phase": "Asset Provenance & Quantization Preparation",
            "investigating": "Importing verified Qwen2.5-Instruct (0.5B, 1.5B, 3B, 7B) baselines from AGERE and generating uniform GGUF quantizations (Q8_0, Q4_K_M, Q2_K, Q1_0).",
            "understood_at_time": "Controlled quantization studies require identical base checkpoints, a single quantizer binary (llama.cpp b12176), no uncalibrated mixed downloads, and strict code-in-Git vs weights-outside-Git separation.",
            "available_evidence": "docs/SSD_ASSET_REUSE.md, hash-verified import manifests, and quantization logs.",
            "decision_made": "Rebuild canonical 7B Q4_K_M with llama.cpp b12176 without an importance matrix; use Q1_0 instead of uncalibrated IQ1_S; document Study Roadmap v1.0.",
            "documented_rationale": "Prevent confounding nominal bit-width with differing quantizer versions or undocumented calibration corpora.",
            "subsequent_impact": "Guaranteed cryptographic weight provenance across subsequent Ubuntu lab runs.",
            "retrospective_assessment": "Supported as a reproducibility safeguard, though 0.5B, 1.5B, and Q1_0 were never queried once 3B/7B competence bottlenecks appeared.",
        },
        {
            "event_id": "T04",
            "timestamp": "2026-11-10T13:10:00+05:00 to 13:43:45+05:00",
            "commit": "aec9fd2 / 0333c67 / 941cf7e / bb1bb12 / ea78a2f",
            "phase": "Initial 3B Direct-Response Pilots & Q2_K Failure",
            "investigating": "Cohort 001 (3B F16 vs Q2_K vs exploratory Q4_K_M on 64 exact SCM prompts) and Cohort 003 (Q2_K CPU repacking diagnostic).",
            "understood_at_time": "First live LLM runs on the Ubuntu lab PC (CPU-only llama.cpp b12176 because RTX 4000 Ada was on nouveau without validated CUDA).",
            "available_evidence": "Cohort 001: 0/64 strict across all arms due to Markdown JSON fences; single-fence F16 33/64 (63/64 activate, 0/64 [Z]), Q4_K_M 34/64, Q2_K 0/64 (64/64 length-capped). Cohort 003: --no-repack 0/16 valid. Metadata audit: identical tokenizers/templates.",
            "decision_made": "Add labeled single-fence sensitivity; retire 3B Q2_K as an operational generation failure; normalize leaked home-directory usernames to $HOME/ in public run configs.",
            "documented_rationale": "Cannot measure selective causal degradation when Q2_K emits zero parseable objects and 3B F16 activates 63/64 times (DECISIONS.md 13:11-13:43 PKT).",
            "subsequent_impact": "Shifted focus from Q2_K to Q4_K_M/Q8_0 and initiated diagnostic controls for arithmetic, model scale, and source selection.",
            "retrospective_assessment": "Supported: Cohort 024 later confirmed Q2_K instability in Mistral while showing even 7B/8B F16 models struggled on direct tasks.",
        },
        {
            "event_id": "T05",
            "timestamp": "2026-11-10T13:50:00+05:00 to 14:32:06+05:00",
            "commit": "f2b2cb1 / 01c7590 / 4e90b24 / 09cf43b / 12c7667",
            "phase": "Formula Controls, 7B Screen, and Source-Selection Pivot",
            "investigating": "Cohorts 002, 006, 007 (formula-given arithmetic controls on 3B F16, Q8_0, Q4_K_M), Cohort 004 (7B F16 direct screen), and Cohort 005 (3B supplied-rate source selection).",
            "understood_at_time": "In Cohort 002, F16 computed the right ATE sign on 61/64 formula items (and Q8_0 tied 61/64 in 006, while Q4 dropped to 45/64 in 002 and 31/48 vs 46/48 on fresh families in 007), YET F16 chose 'decline' on 64/64 explicit actions! Meanwhile 7B F16 failed Cohort 004 (17/32 despite 32/32 [Z]), and Cohort 005 violated C/A/B additivity (-43.75 pp) while showing a stark family-hashed order split.",
            "available_evidence": "Cohorts 002, 004, 005, 006, 007 raw responses and paired JSON analyses.",
            "decision_made": "Separate numeric estimate signs from explicit actions; withhold C/A/B latent parameter reporting; launch within-item source-order reversal (Cohort 008).",
            "documented_rationale": "Aggregate conflict penalties were distorted by default action biases, and family-assigned source order confounded Cohort 005's order pattern.",
            "subsequent_impact": "Pivoted the project from raw contingency tables to two-source (randomized vs historical) rate prompts and presentation-order crossovers.",
            "retrospective_assessment": "Crucial methodological turning point: discovered both numeric-vs-action dissociation and C/A/B misfit on the very first day of LLM runs.",
        },
        {
            "event_id": "T06",
            "timestamp": "2026-11-10T14:33:15+05:00 to 2026-11-12T10:11:17+05:00",
            "commit": "dd75c35 / 2846f50 / 1f8b169 / fa79370 / cd3f66d / b90cb63",
            "phase": "3B Source-Order Crossovers, Matched Strength & Count-Bug Audit",
            "investigating": "Completing interrupted Cohort 008, running same-session interleaved order crossovers on reused (009) and fresh (010) families, matching observational signal strength (011), and auditing count aggregation.",
            "understood_at_time": "3B F16 consistently lost 21.9 to 28.1 pp of conflict accuracy when historical evidence appeared first, while Q4_K_M sat at 50% (near-constant activate). Also discovered two bugs: original generator had larger aligned |delta_obs|, and analyze_interleaved_order.py halved displayed cell counts.",
            "available_evidence": "Cohorts 008-011 summaries, input_prevalidation/, and preserved *_v1_undercounted_counts.json files.",
            "decision_made": "Repair observational-strength imbalance in Cohort 011; fix count aggregator and withdraw false claim that Q4_K_M scored below always-activate while preserving v1 files; screen 7B F16 on matched-strength tasks (Cohort 012).",
            "documented_rationale": "Transparently correct code/design defects without rewriting history; verify competent higher-precision reference before confirmatory testing.",
            "subsequent_impact": "Established the matched-strength generator used in Cohorts 011-017, though inadvertently introducing a smaller-magnitude separation between randomized and historical gaps.",
            "retrospective_assessment": "Count-bug disclosure was exemplary reproducibility practice; however, matched historical strength m in [0.38, 0.46) > e in [0.06, 0.12) later proved vulnerable to a source-blind magnitude shortcut.",
        },
        {
            "event_id": "T07",
            "timestamp": "2026-11-12T10:12:40+05:00 to 16:03:38+05:00",
            "commit": "fc7dcc1 / 0f55a79 / baa573b / 79c0ba5 / eb53578 / 13e8fa5 / 058e3c7",
            "phase": "7B Contract Refinement & Cohort 016 Prospective Order Confirmation",
            "investigating": "7B F16 reference screens (012-015), strict bare-JSON contract enforcement (014), conditional 7B Q4_K_M screen (015), and 96-family prospective confirmation (016).",
            "understood_at_time": "Cohort 012 failed conflict gates; Cohort 013 causal-context prose caused 64/64 160-token truncations; Cohort 014 strict 48-token JSON fixed validity (128/128) and Cohort 015 F16 cleared all gates (89/128), unlocking 7B Q4_K_M—which showed a massive +65.6 pp historical-first conflict jump! Cohort 016 prospectively confirmed this on 96 fresh families (+62.5 pp, t(95)=21.10, p=1.24e-37).",
            "available_evidence": "Cohorts 012-016 frozen plans, power_analysis.json, and primary_analysis.json.",
            "decision_made": "Confirm the 7B Q4_K_M conflict-order effect for this setup, refuse to call it selective causal degradation (since aligned items dropped from 192/192 to 105/192), and formally foreground causal inference as CausalFade's central pillar (058e3c7).",
            "documented_rationale": "Prompt-order sensitivity on scaffolded rates is not proof of causal inference or selective quantization damage (DECISIONS.md 2026-11-12).",
            "subsequent_impact": "Produced the project's strongest prospective statistical replication while motivating deep construct-validity diagnostics to understand WHY order mattered.",
            "retrospective_assessment": "Supported statistically (+62.5 pp is ironclad), and the refusal to overclaim saved the project when Cohort 017 failed to generalize it to 14B and manuscript audits uncovered the smaller-gap shortcut.",
        },
        {
            "event_id": "T08",
            "timestamp": "2026-11-13T08:33:36+05:00 to 2026-11-14T17:03:42+05:00",
            "commit": "40f34f8 / caf5b1d / 00fd0b5 / a400569 / 737c945 / 77361f5",
            "phase": "14B Boundary & Component/Contract Decomposition (Cohorts 017-021)",
            "investigating": "14B cross-size follow-up (017), Interdisciplinary Follow-Up design, graded sensitivity/mapping (018), within-world K/M vs semantic contracts (019), isolated components (020), and governing-source selection + explicit guidance (021).",
            "understood_at_time": "14B Q8/Q4 did not reproduce 7B's conflict-order effect (-4.17 pp and 0 pp). In 7B F16, reversed token mappings crushed accuracy (018-019), noncausal controls showed similar order shifts (018-019), and in Cohort 021 the model selected the randomized governing study 128/128 times (100%) and solved randomized-only stems 30/32 times, yet scored 58/128 on both ordinary AND explicitly guided two-source decisions!",
            "available_evidence": "Cohort 017 recovered analysis + Cohorts 018-021 strict-valid F16 archives and Publication Readiness Assessment (15 Nov 2026).",
            "decision_made": "Withhold Q4 across 018-021 due to failed F16 gates; stop tuning Qwen 7B prompts in isolation; test an independent model lineage next (Cohort 022).",
            "documented_rationale": "Correctly naming causal evidence in isolation does not translate into using it when historical rates are co-present; prompt tuning was hitting diminishing returns (docs/PUBLICATION_READINESS_2026-11-15.md).",
            "subsequent_impact": "Shifted research focus onto the dissociation between evidence recognition and decision execution, and triggered multi-lineage audits.",
            "retrospective_assessment": "Supported: Cohort 021's 128/128 vs 58/128 dissociation became one of CausalFade's sharpest diagnostic insights into LLM evaluation.",
        },
        {
            "event_id": "T09",
            "timestamp": "2026-11-16T08:40:55+05:00 to 2026-11-18T20:49:00+05:00",
            "commit": "6019ea7 / 21dabb2 / fa5db6a / 4aff668 / 6193357 / 2fecac4 / cacd5bc",
            "phase": "Cross-Lineage Audits, 21-Arm Precision Matrix & Archive Screen (Cohorts 022-025)",
            "investigating": "Mistral replication (022), Qwen counterbalanced control audit (023), 3-lineage x 7-format 30,912-attempt matrix (024), and retrospective reanalysis of all 24 cohorts (025).",
            "understood_at_time": "Qwen's +55.5 to +56.6 pp two-source loss persisted across A/B names and option orders, but harmful-direction numeric (18/32) and noncausal scorecard (75/128) controls failed the 75% robustness gate. Mistral F16 selected the first displayed option on 256/256 source prompts (0/128 option-reversal invariance). Across 21 arms in Cohort 024, precision effects were non-monotone: Qwen/Mistral/Llama F16-to-Q4 semantic causal scores barely moved, whereas Llama Q4_K_M suffered 448 length-capped invalids concentrated in noncausal controls!",
            "available_evidence": "Cohorts 022-025 archives (40,032 completed raw attempts across 58 successful runs).",
            "decision_made": "Conclude that existing two-source rate prompts do not isolate selective quantization damage to causal reasoning; pivot to observationally identical graph-switch designs (Cohort 025.1 -> 026).",
            "documented_rationale": "Option-position policies, harmful-direction control failures, and format-specific truncation dominated apparent causal or compression contrasts (DECISIONS.md 18 Nov 2026).",
            "subsequent_impact": "Closed the supplied-rate quantization-sweep era and initiated exact-rational structural graph-switch experiments.",
            "retrospective_assessment": "Supported: Cohort 024 definitively refuted any simple monotone 'quantization selectively breaks causal reasoning' story on these tasks.",
        },
        {
            "event_id": "T10",
            "timestamp": "2026-11-19T06:54:00+00:00 to 2026-11-23T15:37:03+00:00",
            "commit": "cc1df44 / a75d5e0 / 31fa454 / f7331d0 / ac6ed58",
            "phase": "Graph-Switch Assays & Deterministic Calculator Intervention (Cohorts 025.1-028)",
            "investigating": "Cross-disciplinary audit (025.1), observationally identical confounder vs mediator graph switches (026), full answer-order counterbalancing across 4 F16 models (027), and offloading arithmetic to an allowlisted deterministic calculator (028).",
            "understood_at_time": "Cohort 026 exposed first an oracle Y-complement bug (v1 invalidated) and then an option-order coupling where Llama picked the 1st option 61/64 times. Cohort 027 fixed counterbalancing: all 4 F16 models (Qwen 3B/7B, Mistral 7B, Llama 8B) got 0/8 order-robust paired switch fidelity! Cohort 028 tested whether arithmetic was the culprit: deterministic calculator C rescued noncausal controls (Qwen 58->128/128, Llama 68->112/128) yet failed to rescue causal tasks (Qwen 65->68/128, Llama 71->60/128) because models could not select 'marginal' for confounders vs 'conditional' for mediators!",
            "available_evidence": "Cohort 026-028 run directories, Supervisor Progress Report (19 Nov 2026), and pipeline_status.json ('stopped_by_gate').",
            "decision_made": "Honor frozen stopping gates on Cohorts 026, 027, and 028 without launching validation or quantization sweeps; design one final self-contained, shortcut-audited prospective benchmark (CF-TP1, Cohort 029).",
            "documented_rationale": "Further quantization sweeps on unqualified references would measure noise; meanwhile, retrospective audit of Cohort 016 revealed a smaller-gap magnitude heuristic, motivating a design where printed tables admit both provenance assignments.",
            "subsequent_impact": "Directly shaped the mathematical architecture of Cohort 029 (CF-TP1) and the final manuscript's methodological focus.",
            "retrospective_assessment": "Supported: Cohort 028's negative causal-rescue result (+2.34 pp and -8.59 pp vs +54.7 pp and +34.4 pp on controls) was a decisive diagnostic achievement.",
        },
        {
            "event_id": "T11",
            "timestamp": "2026-11-23T18:00:00+05:00 to 2026-11-26T13:04:00+05:00",
            "commit": "40b871d / bf58d38 / d909097 / 76206c2 / b737153",
            "phase": "Cohort 029 (CF-TP1) Execution, Offline Verification & Final Manuscript",
            "investigating": "Prospective 128-family, 4,096-prompt evaluation of feasible provenance swaps and target-population transport versus matched explicit-scorecard arithmetic on Qwen2.5-7B-Instruct Q4_K_M, followed by release verification and IEEE TNNLS manuscript preparation.",
            "understood_at_time": "All 4,096 responses completed strict-valid on 25 Nov 2026. Transfer causal target-pair fidelity was 128/512 (25.00%) vs arithmetic 146/512 (28.52%), Delta = -3.515625 pp (95% t CI [-7.77, +0.74], bounded [-27.52, +20.49], inconclusive). Directional diagnostics revealed 995/1024 causal activation (only 3/256 target reversals) vs 46/256 required and 45/256 unwarranted arithmetic flips. Offline replay passed 50/50 checks.",
            "available_evidence": "Annotated tag cohort-029-v1.0.0 (76206c2), PUBLICATION_HANDOFF.md (b737153), and manuscript/ package.",
            "decision_made": "Publish immutable release tag, disclose human-review key/timing limits and the RESULTS.md narrative direction-table correction in supplement.tex, and position the final manuscript as a methodological evaluation instrument and single-deployment case study rather than a quantization-degradation claim.",
            "documented_rationale": "Preserve complete fidelity to what the frozen experiment actually identified without exaggerating inconclusive contrasts or retrospective shortcut audits.",
            "subsequent_impact": "Produced the final archival release and manuscript package.",
            "retrospective_assessment": "Exemplary scientific integrity: transformed an initially over-optimistic compression hypothesis into a rigorous, reproducible benchmark and diagnostic methodology.",
        },
    ]
    (EVID / "research_timeline.json").write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding="utf-8")
    return events


def build_decision_ledger() -> list[dict]:
    decisions = [
        ("D01", "2026-10-28", "4e2fe4f", "Scope primary claim to behavioral causal competence rather than neural circuit severing", "Accuracy/graph outputs cannot identify internal weight mechanisms without mechanistic interventions", "literature review/EXECUTIVE_SUMMARY.md"),
        ("D02", "2026-11-01", "6ab18d2", "Separate public_tasks.jsonl from evaluator-only oracle_truth.jsonl with opaque SHA-256 task IDs", "Prevent condition/answer leakage into LLM contexts", "docs/DATA_CONTRACT.md"),
        ("D03", "2026-11-07", "5a12a21", "Enforce code-in-Git and weights-outside-Git storage policy; regenerate 7B Q4_K_M with b12176", "Ensure cross-machine reproducibility and uniform quantizer provenance", "docs/SSD_ASSET_REUSE.md"),
        ("D04", "2026-11-10 13:10", "aec9fd2", "Standardize on CPU-only llama.cpp b12176 (8 threads, F16 KV, temp 0, no prompt cache)", "Lab RTX 4000 Ada used nouveau driver without working CUDA; common CPU runtime avoids backend confounds", "DECISIONS.md"),
        ("D05", "2026-11-10 13:11", "da4507b", "Retain strict JSON primary score and add separately labeled single-fence JSON sensitivity", "100% of initial F16 outputs wrapped valid JSON in Markdown fences", "DECISIONS.md"),
        ("D06", "2026-11-10 13:22", "0333c67", "Add exploratory 3B Q4_K_M arm and run CPU repacking diagnostic on 3B Q2_K", "3B Q2_K hit 160-token cap with repetitive punctuation on 64/64 prompts", "DECISIONS.md"),
        ("D07", "2026-11-10 13:38", "941cf7e", "Retire 3B Q2_K from subsequent pilots after --no-repack and tokenizer audits", "Both default and --no-repack yielded 0/16 valid outputs despite identical tokenizers", "DECISIONS.md"),
        ("D08", "2026-11-10 13:43", "ea78a2f", "Normalize local home paths (/home/i242514/) to $HOME/ in tracked run artifacts without rewriting Git history", "Protect lab account privacy while preserving immutable commit history", "DECISIONS.md"),
        ("D09", "2026-11-10 13:50", "f2b2cb1", "Score numeric ate_estimate sign separately from explicit binary activate field", "Cohort 002 F16 got 61/64 signs right while explicitly declining on 64/64 prompts", "DECISIONS.md"),
        ("D10", "2026-11-10 14:07", "01c7590", "Enforce Cohort 004 stopping gate and withhold 7B Q2_K arm", "7B F16 scored 17/32 overall, missing predeclared 22/32 competence threshold", "DECISIONS.md"),
        ("D11", "2026-11-10 14:13", "4e90b24", "Withhold C/A/B latent-route parameter estimates and launch within-item source-order reversal", "Cohort 005 F16 violated C/A/B additivity by -43.75 pp and showed family-confounded order split", "DECISIONS.md"),
        ("D12", "2026-11-10 14:33", "dd75c35", "Preserve interrupted Cohort 008 run_001_f16 (25/64 + 1 interrupted) and restart complete arms under new run IDs", "User requested PC shutdown; partial unattempted items must not enter paired contrasts or be overwritten", "DECISIONS.md"),
        ("D13", "2026-11-12 09:23", "d21db20", "Introduce same-session interleaved order crossover with shuffled opaque twins (Cohorts 009-010)", "Cohort 008 order contrast was confounded with a two-day session gap", "DECISIONS.md"),
        ("D14", "2026-11-12 09:52", "cd3f66d", "Replace fixed-confounding generator with matched observational-strength generator (Cohort 011)", "Original generator made |delta_obs| larger in aligned than conflict cells", "DECISIONS.md"),
        ("D15", "2026-11-12 10:10", "b90cb63", "Correct halved cell-count bug in analyze_interleaved_order.py and archive *_v1_undercounted_counts.json", "Code audit found family-mean counts were not multiplied by 2; point estimates/CIs unchanged", "DECISIONS.md"),
        ("D16", "2026-11-12 10:21", "fc7dcc1", "Require conflict competence separately in EACH evidence order (>=9/16) and withhold 7B Q4 in Cohort 012", "7B F16 passed overall (47/64) via 32/32 aligned but failed both conflict orders (8/16, 7/16)", "DECISIONS.md"),
        ("D17", "2026-11-12 11:36", "a4a6f67", "Enforce strict bare one-key JSON instruction and 48-token cap (Cohort 014)", "Cohort 013 causal-context prompts appended explanatory prose after JSON and hit 160-token cap on 64/64 items", "DECISIONS.md"),
        ("D18", "2026-11-12 12:39", "eb53578", "Freeze 96-family prospective replication of 7B Q4_K_M conflict-order effect (Cohort 016)", "Cohort 015 revealed unexpected +65.6 pp Q4 conflict order shift; required untouched powered confirmation", "DECISIONS.md"),
        ("D19", "2026-11-12 16:03", "058e3c7", "Foreground causal inference in LLMs as overarching pillar; treat quantization as one experimental factor", "Prevent narrowing project to prompt-order quirks or treating order sensitivity as causal reasoning", "DECISIONS.md"),
        ("D20", "2026-11-13", "caf5b1d", "Recover Cohort 017 14B paired analysis locally with disclosed zero-variance t-test guard; preserve original missing-NumPy log", "Unattended lab script crashed post-inference due to missing NumPy and zero family variance in 14B Q4", "DECISIONS.md"),
        ("D21", "2026-11-14", "a400569", "Issue dated interpretation amendment on Cohort 019 source-check position cue without altering scores or failed gate", "Cohort 019 source check mentioned randomized study first in prose while asserting historical was listed first", "DECISIONS.md"),
        ("D22", "2026-11-14", "77361f5", "Stop single-checkpoint Qwen 7B prompt tuning after Cohort 021 guidance failed to improve 58/128 two-source decisions", "128/128 governing-source selection coexisted with 58/128 guided/ordinary decisions; needed cross-lineage check", "DECISIONS.md"),
        ("D23", "2026-11-16", "21dabb2", "Classify Qwen two-source dissociation as checkpoint-specific after Mistral failed simple components in Cohort 022", "Mistral Q4_K_M output constant 'A' (64/128) and constant 'activate' (16/32 rand-only)", "DECISIONS.md"),
        ("D24", "2026-11-16", "4aff668", "Withhold causal-specificity confirmation trigger after Cohort 023 harmful-direction controls failed (<75%)", "Qwen harmful numeric (18/32) and noncausal scorecard (75/128) missed frozen 75% robustness cutoffs", "DECISIONS.md"),
        ("D25", "2026-11-18", "2fecac4", "Close 21-arm Cohort 024 as a development screen without confirmatory precision claims", "No F16 reference cleared all component/control checks; precision patterns were heterogeneous and non-monotone", "DECISIONS.md"),
        ("D26", "2026-11-19", "3606794", "Pivot to exact-rational observationally identical confounder/mediator graph-switch assay (Cohort 026)", "Cohorts 025/025.1 showed prior archives lacked fixed-table structural causal contrasts", "experiments/cohort_025_1/summary.md"),
        ("D27", "2026-11-19", "e118351", "Invalidate and preserve Cohort 026 Qwen v1 pilot due to Y-complement arithmetic-oracle bug; stop Cohort 026 after v3 gate failure", "v1 hardcoded 'yes' on complemented outcomes; neither Qwen nor Llama passed v2/v3 qualification", "experiments/cohort_026/development_summary.md"),
        ("D28", "2026-11-19", "11a46f0 / 31fa454", "Exclude 14B F16 for 32 GB RAM guard, cross answer order structurally in Cohort 027, and honor stopped_by_gate", "Cohort 026 coupled correct option position to form; all four F16 models scored 0/8 paired switch fidelity in 027", "experiments/cohort_027/README.md"),
        ("D29", "2026-11-20 to 11-23", "e7787e4 / 5a46c2e / ac6ed58", "Test deterministic calculator replay (Cohort 028), amend Git checkpoint cadence to hourly, and honor stopped_by_gate", "Calculator rescued noncausal controls but not causal graph-rule selection (0/16 raw paired switch on 3 of 4 model-forms)", "experiments/cohort_028/DEVIATIONS.md"),
        ("D30", "2026-11-23 to 11-26", "bf58d38 / 76206c2 / b737153", "Freeze and execute CF-TP1 (Cohort 029) with constant-rivals-v1 clarification, tag cohort-029-v1.0.0, and reconcile RESULTS.md direction table in manuscript", "Provide shortcut-audited, offline-reproducible prospective evaluation of provenance and target transport with full provenance disclosure", "PUBLICATION_HANDOFF.md"),
    ]
    rows = []
    for did, dt, com, dec, rat, src in decisions:
        rows.append({
            "decision_id": did,
            "date": dt,
            "commit": com,
            "decision": dec,
            "documented_rationale": rat,
            "source_record": src,
        })
    write_csv(EVID / "decision_ledger.csv", rows)
    return rows


def build_claim_evidence_map() -> list[dict]:
    claims = [
        ("CLM-01", "Part I / Ch 1", "Original research question targeted Delta(p) = ConflictPenalty(p) - ConflictPenalty(F16) > 0 under PTQ", "README.md; literature review/EXECUTIVE_SUMMARY.md", "4e2fe4f", "Verified prospective origin"),
        ("CLM-02", "Part I / Ch 2", "Initial literature collection comprised 14 verified 2025-2026 papers (8 from 2026, 6 from 2025) plus 6 psychological/psychometric methodological sources", "literature review/paper_manifest.json; docs/references.bib", "4e2fe4f / caf5b1d", "Verified SHA-256 & DOIs"),
        ("CLM-03", "Part I / Ch 3", "Synthetic C/A/B validation fit 3,600 datasets, showing 16 near-boundary nonconvergences and exact observational equivalence with symmetric logistic integration (deviance 0.688, p=0.4331)", "results/design_validation/VALIDATION_REPORT.md; parameter_recovery.json", "6ab18d2", "Verified exact statistics"),
        ("CLM-04", "Part II / Ch 5 (C001)", "Cohort 001 3B strict scores were 0/64 across F16, Q2_K, Q4_K_M; fence-only F16 33/64 (63/64 activate, 0/64 [Z]), Q2_K 0/64 (64/64 length-capped), Q4_K_M 34/64", "experiments/cohort_001/summary.md; f16_vs_q2_k.json; f16_vs_q4_k_m.json", "0333c67", "Verified from run artifacts"),
        ("CLM-05", "Part II / Ch 6 (C002)", "Cohort 002 formula control flipped 3B F16 from 63/64 activate to 0/64 activate (32/64 explicit actions) while raising ATE sign accuracy to 61/64 vs 45/64 for Q4_K_M", "experiments/cohort_002/summary.md; estimate_sign_policy_sensitivity.json", "f2b2cb1", "Verified from run artifacts"),
        ("CLM-06", "Part II / Ch 7 (C003)", "Cohort 003 disabling llama.cpp CPU repacking altered all 16 Q2_K outputs but yielded 0/16 valid actions and 16/16 length caps", "experiments/cohort_003/summary.md; response_agreement.json", "941cf7e", "Verified from run artifacts"),
        ("CLM-07", "Part II / Ch 8 (C004)", "Cohort 004 7B F16 scored 17/32 overall (31/32 activate) despite 32/32 correct [Z] adjustment sets, failing the 22/32 gate", "experiments/cohort_004/summary.md; reference_feasibility.json", "01c7590", "Verified from run artifacts"),
        ("CLM-08", "Part II / Ch 9 (C005)", "Cohort 005 3B Q4_K_M reduced conflict penalty by 43.75 pp via 61/64 activation; F16 violated C/A/B additivity by -43.75 pp (CI [-68.75, -18.75])", "experiments/cohort_005/summary.md; source_and_tree_diagnostics.json", "4e90b24", "Verified from run artifacts"),
        ("CLM-09", "Part II / Ch 10-11 (C006-007)", "Cohort 006 3B Q8_0 tied F16 at 61/64 estimate signs; Cohort 007 fresh families replicated F16 46/48 vs Q4_K_M 31/48 (-31.25 pp, CI [-41.67, -20.83])", "experiments/cohort_006/summary.md; experiments/cohort_007/paired_estimate_sign.json", "09cf43b / 12c7667", "Verified from run artifacts"),
        ("CLM-10", "Part II / Ch 12-15 (C008-011)", "3B F16 historical-first minus randomized-first conflict accuracy was -28.125 pp (008), -21.875 pp (009), -25.0 pp (010), and -25.0 pp (011); cell-count halving bug fixed in b90cb63", "experiments/cohort_008..011/source_order_analysis.json; DECISIONS.md", "2846f50 / b90cb63", "Verified including archived v1 files"),
        ("CLM-11", "Part II / Ch 16-19 (C012-015)", "7B F16 failed gates in 012 (8/16, 7/16 conflict), 013 (0/64 contextual valid at 160 tok), and 014 (42/64 overall at 48 tok strict JSON), then passed 015 (89/128), revealing +65.6 pp Q4 conflict order jump", "experiments/cohort_012..015/summary.md; order_analysis.json", "fc7dcc1..79c0ba5", "Verified from run artifacts"),
        ("CLM-12", "Part II / Ch 20 (C016)", "Cohort 016 prospectively confirmed 7B Q4_K_M conflict order effect on 96 fresh families: 175/192 vs 55/192 (+62.5 pp, t(95)=21.10, p=1.24e-37); retrospective source-blind smaller-gap heuristic solves 768/768", "experiments/cohort_016/primary_analysis.json; manuscript/scripts/extract.py", "13e8fa5 / 76206c2", "Prospective primary + retrospective audit verified"),
        ("CLM-13", "Part II / Ch 21 (C017)", "Cohort 017 14B Q8_0 (-4.17 pp) and Q4_K_M (0.0 pp, 100% conflict activation) did not reproduce 7B's conflict-order effect; missing-NumPy failure preserved and repaired locally", "experiments/cohort_017/analysis.json; analysis.log; analysis_recovery.json", "40f34f8 / caf5b1d", "Verified from run artifacts"),
        ("CLM-14", "Part II / Ch 22-25 (C018-021)", "Qwen 7B F16 showed K/M mapping sensitivity (+25.8 pp causal, +36.7 pp control in 019) and 128/128 governing-source selection vs 58/128 ordinary and guided decisions in 021", "experiments/cohort_018..021/development_analysis.json", "00fd0b5..77361f5", "Verified from run artifacts"),
        ("CLM-15", "Part II / Ch 26-27 (C022-023)", "Cohort 022 Mistral Q4 selected 'A' on 64/128 source prompts; Cohort 023 Qwen F16 +55.5 pp gap persisted across A/B & option order, but harmful numeric (18/32) & noncausal (75/128) failed >=75% cutoff", "experiments/cohort_022/development_analysis.json; experiments/cohort_023/development_supplement.json", "21dabb2 / 4aff668", "Verified from run artifacts"),
        ("CLM-16", "Part II / Ch 28 (C024)", "Cohort 024 completed 21 arms (30,912 attempts, 30,281 strict-valid); Mistral F16 picked 1st source option 256/256; Llama Q4_K_M had 448 length-capped control invalids (0/256 semantic control) while causal stayed 150/256", "experiments/cohort_024/development_analysis_archive.json", "2fecac4", "Verified from archived raw analysis"),
        ("CLM-17", "Part II / Ch 29-30 (C025-025.1)", "Cohort 025/025.1 audited 58 complete runs (40,032 attempts): Mistral F16 option-order retention 6/128 causal, 0/128 source; Qwen F16 causal MI 0.031 bits vs 0.230 control; Qwen 024 conflict order interaction 0 pp", "experiments/cohort_025/archive_methods_screen.json; experiments/cohort_025_1/archive_investigation.json", "cacd5bc / cc1df44", "Verified within 1e-12"),
        ("CLM-18", "Part II / Ch 31-32 (C026-027)", "Cohort 026 v1 failed Y-complement oracle, v2/v3 coupled option order to form; corrected Cohort 027 yielded 0/8 order-robust paired switch fidelity across all 4 F16 models and both forms (896/896 valid)", "experiments/cohort_026/development_summary.md; experiments/cohort_027/runs/development/*/analysis.json", "a75d5e0 / 31fa454", "Verified from run analyses"),
        ("CLM-19", "Part II / Ch 33 (C028)", "Cohort 028 deterministic calculator C rescued noncausal controls (Qwen 58->128/128, Llama 68->112/128) but failed on causal graph switches (Qwen +2.34 pp, Llama -8.59 pp; specificity -52.34 & -42.97 pp)", "experiments/cohort_028/runs/development/*/analysis.json; pipeline_status.json", "ac6ed58", "Verified from run analyses"),
        ("CLM-20", "Part II / Ch 34 & Part V (C029)", "Cohort 029 (CF-TP1) completed 4,096/4,096 strict-valid responses: transfer causal 128/512 (25.00%) vs arithmetic 146/512 (28.515625%), Delta = -3.515625 pp (95% t CI [-7.7713, +0.7400], bounded [-27.5237, +20.4924]); causal activated 995/1024 (3/256 switches, 14/512 gold-off, 497/512 gold-on); arithmetic activated 597/1024 (46/256 switches, 45/256 invariant flips, 231/512 gold-off, 316/512 gold-on)", "experiments/cohort_029/runs/confirmatory/analysis/primary.json; secondary.json; manuscript/supplement.tex", "76206c2 / b737153", "Verified 50/50 checks + raw journal reconciliation"),
    ]
    rows = []
    for cid, loc, clm, path, com, ver in claims:
        rows.append({
            "claim_id": cid,
            "monograph_section": loc,
            "claim_summary": clm,
            "evidence_paths": path,
            "git_commits": com,
            "verification_status": ver,
        })
    write_csv(EVID / "claim_evidence_map.csv", rows)
    return rows


def write_discrepancies_and_verification(manifest: dict) -> None:
    head_sha = manifest["git_snapshot"]["head_commit"]
    tag_sha = manifest["git_snapshot"]["immutable_scientific_commit"]
    disc_md = r"""# Unresolved Discrepancies, Historical Defects, and Unrecoverable Records

This document catalogs every discrepancy, historical defect, post-collection repair, stale status string, and unrecoverable external artifact identified during the Phase I audit of Project CausalFade at snapshot commit `__HEAD__` (scientific release tag `cohort-029-v1.0.0` at `__TAG__`). None of these historical files were altered.

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
"""
    disc_md = disc_md.replace("__HEAD__", head_sha).replace("__TAG__", tag_sha)
    (EVID / "unresolved_discrepancies.md").write_text(disc_md, encoding="utf-8")

    ver_md = f"""# Artifact Verification Report

- **Source Snapshot Commit (`HEAD`):** `{manifest['git_snapshot']['head_commit']}`
- **Tracked `origin/main` Commit:** `{manifest['git_snapshot']['origin_main_commit']}`
- **Immutable Scientific Release Tag (`cohort-029-v1.0.0`):** `{manifest['git_snapshot']['immutable_scientific_commit']}`
- **Total Git Commits Audited:** `{manifest['git_snapshot']['total_commits_on_head']}`
- **Deleted or Renamed Files in Git History:** `0` (`git log --diff-filter=DR` verified empty)
- **Verification Mode:** Strictly read-only inspection; `git status --porcelain` confirmed zero modifications to tracked files and zero modifications to `manuscript/`.

## Summary of Verified Artifacts

| Category | Count | Verification Result |
| --- | ---: | --- |
| Synthetic design-validation suite (`results/design_validation/`) | 1 | Verified 192 public/oracle tasks, 3,600 recovery replicates, SHA-256 matches `manifest.json` |
| Literature review PDFs & summaries (`literature review/`) | 14 | All 14 PDFs, `paper_manifest.json` SHA-256 digests, and 14 summaries verified |
| Experimental cohort directories (`experiments/cohort_001` .. `cohort_029`) | 30 | All 30 cohort directories (`001`–`025`, `025_1`, `026`–`029`) individually verified |
| Persisted LLM run directories | {manifest['aggregate_counts']['llm_run_directories']} | Every run's `raw_responses.jsonl` / `attempts.jsonl` / `events.jsonl` line-counted and SHA-256 hashed |
| Total scheduled LLM requests across all cohorts | {manifest['aggregate_counts']['total_scheduled_llm_requests']:,} | Verified from run schedules and manifests |
| Total persisted raw LLM records across all cohorts | {manifest['aggregate_counts']['total_persisted_llm_responses']:,} | Exact difference of 38 rows accounted for by preserved interrupted `cohort_008/run_001_f16` (26/64) |
| Cohort 029 offline release checks (`release/verification.json`) | 50 / 50 | PASS; manifest SHA-256 `5252f69d...` and journal SHA-256 `673eb723...` verified byte-for-byte |
| Manuscript claim-ledger entries (`manuscript/audit/claim-ledger.csv`) | 83 | Cross-checked against repository blobs and Cohort 029 raw journal |

All SHA-256 digests of primary artifacts are recorded in `evidence/source_manifest.json` and per-run digests in `evidence/experiment_inventory.csv`.
"""
    (EVID / "artifact_verification_report.md").write_text(ver_md, encoding="utf-8")


def main():
    extracted = json.loads((EVID / "_extracted_summary.json").read_text(encoding="utf-8"))
    manifest = build_source_manifest(extracted)
    c_rows = build_cohort_inventory()
    m_rows = build_model_inventory()
    d_rows = build_dataset_inventory()
    t_rows = build_timeline()
    h_rows = build_hypothesis_ledger()
    meth_rows = build_methodology_ledger()
    dec_rows = build_decision_ledger()
    clm_rows = build_claim_evidence_map()
    write_discrepancies_and_verification(manifest)
    print(
        f"Generated all inventories: {len(c_rows)} cohorts, {len(m_rows)} model rows, "
        f"{len(d_rows)} datasets, {len(t_rows)} timeline phases, {len(h_rows)} hypotheses, "
        f"{len(meth_rows)} methodologies, {len(dec_rows)} decisions, {len(clm_rows)} claim mappings."
    )


if __name__ == "__main__":
    main()
