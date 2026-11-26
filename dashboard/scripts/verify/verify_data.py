"""Automated statistical and data-integrity verification for dashboard datasets.

Reconciles extracted dashboard JSONs against raw repository artifacts, checks
numerators/denominators, verifies Cohort 029 & Cohort 016 inferential metrics,
and writes dashboard/VERIFICATION_REPORT.md + dashboard/DATA_MANIFEST.json.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_ROOT = REPO_ROOT / "dashboard"
DATA_DIR = DASHBOARD_ROOT / "public" / "data"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_checks() -> tuple[list[dict[str, Any]], bool]:
    checks: list[dict[str, Any]] = []

    overview = load_json(DATA_DIR / "overview.json")
    cohorts = load_json(DATA_DIR / "cohorts.json")["cohorts"]
    stats = load_json(DATA_DIR / "statistics.json")
    repro = load_json(DATA_DIR / "reproducibility.json")

    # 1. Check Cohort 029 raw response count across chunks == 4096
    c29_rows = []
    for i in range(1, 5):
        c29_rows.extend(load_json(DATA_DIR / "responses" / f"cohort_029_part{i}.json"))

    checks.append({
        "name": "cohort_029_raw_response_count",
        "expected": 4096,
        "observed": len(c29_rows),
        "passed": len(c29_rows) == 4096,
    })

    # 2. Recompute Cohort 029 transfer-form direction counts directly from decoded raw responses
    transfer_causal = [r for r in c29_rows if r["form"] == 1 and r["task"] == 0]
    transfer_arith = [r for r in c29_rows if r["form"] == 1 and r["task"] == 1]

    tc_off_correct = sum(1 for r in transfer_causal if r["gold_action"] == 0 and r["correct"])
    tc_on_correct = sum(1 for r in transfer_causal if r["gold_action"] == 1 and r["correct"])
    tc_activated = sum(1 for r in transfer_causal if r["predicted_action"] == 1)

    ta_off_correct = sum(1 for r in transfer_arith if r["gold_action"] == 0 and r["correct"])
    ta_on_correct = sum(1 for r in transfer_arith if r["gold_action"] == 1 and r["correct"])
    ta_activated = sum(1 for r in transfer_arith if r["predicted_action"] == 1)

    checks.append({
        "name": "cohort_029_transfer_causal_direction_reconciliation",
        "expected": {"off_correct": 14, "on_correct": 497, "activated": 995},
        "observed": {"off_correct": tc_off_correct, "on_correct": tc_on_correct, "activated": tc_activated},
        "passed": (tc_off_correct == 14 and tc_on_correct == 497 and tc_activated == 995),
    })

    checks.append({
        "name": "cohort_029_transfer_arithmetic_direction_reconciliation",
        "expected": {"off_correct": 231, "on_correct": 316, "activated": 597},
        "observed": {"off_correct": ta_off_correct, "on_correct": ta_on_correct, "activated": ta_activated},
        "passed": (ta_off_correct == 231 and ta_on_correct == 316 and ta_activated == 597),
    })

    # 3. Recompute Cohort 029 family-standardized primary contrast from families.csv extract
    transfer_fams = [f for f in stats["cohort_029"]["families"] if f["form"] == 1]
    strata_means = []
    for h in range(8):
        vals = [f["diff"] for f in transfer_fams if f["h"] == h]
        strata_means.append(sum(vals) / len(vals))
    recomputed_delta = sum(strata_means) / 8.0
    reported_delta = overview["kpis"]["delta_pp"] / 100.0
    checks.append({
        "name": "cohort_029_primary_delta_reconciliation",
        "expected": reported_delta,
        "observed": recomputed_delta,
        "passed": abs(recomputed_delta - reported_delta) < 1e-12,
    })

    # 4. Recompute Cohort 016 Q4 conflict order effect across 96 families
    q4_016 = [f for f in stats["cohort_016"]["family_effects"] if f["arm"] == "Q4_K_M"]
    mean_016 = sum(f["conflict_order_diff_pp"] for f in q4_016) / len(q4_016)
    checks.append({
        "name": "cohort_016_q4_conflict_order_mean_reconciliation",
        "expected": 62.5,
        "observed": mean_016,
        "passed": len(q4_016) == 96 and abs(mean_016 - 62.5) < 1e-9,
    })

    # 5. Repository-wide scheduled vs persisted raw responses reconciliation
    total_sched = sum(c["scheduled_requests"] for c in cohorts)
    total_persisted = sum(c["persisted_llm_responses"] for c in cohorts)
    c008_int = load_json(DATA_DIR / "responses" / "cohort_008_interrupted.json")
    checks.append({
        "name": "repo_scheduled_vs_persisted_reconciliation",
        "expected": {"scheduled": 48208, "persisted": 48170, "diff_from_008": 38},
        "observed": {
            "scheduled": total_sched,
            "persisted": total_persisted,
            "diff_from_008": 64 - len(c008_int),
        },
        "passed": total_sched == 48208 and total_persisted == 48170 and (total_sched - total_persisted) == (64 - len(c008_int)),
    })

    # 6. Cohort 029 release verifier status
    c29_verif_pass = bool(repro["cohort_029_verification"].get("passed"))
    checks.append({
        "name": "cohort_029_upstream_50_checks",
        "expected": True,
        "observed": c29_verif_pass,
        "passed": c29_verif_pass,
    })

    all_passed = all(c["passed"] for c in checks)
    return checks, all_passed


def write_outputs(checks: list[dict[str, Any]], all_passed: bool) -> None:
    overview = load_json(DATA_DIR / "overview.json")
    commit = overview["git_commit"]
    ts = datetime.now(timezone.utc).isoformat()

    # Build DATA_MANIFEST.json
    dataset_files = sorted(DATA_DIR.rglob("*.json"))
    manifest_entries = []
    for p in dataset_files:
        rel = p.relative_to(DASHBOARD_ROOT).as_posix()
        manifest_entries.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        })

    manifest = {
        "schema_version": 1,
        "git_commit": commit,
        "release_tag": overview["release_tag"],
        "generated_at": ts,
        "all_verification_checks_passed": all_passed,
        "datasets": manifest_entries,
    }
    with (DASHBOARD_ROOT / "DATA_MANIFEST.json").open("w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2)

    # Write VERIFICATION_REPORT.md
    lines = [
        "# Verification Report — CAUSALFADE Research Observatory",
        "",
        f"- **Source Git Commit:** `{commit}`",
        f"- **Release Tag:** `{overview['release_tag']}` (`{overview['release_commit']}`)",
        f"- **Verified At (UTC):** `{ts}`",
        f"- **Overall Status:** `{'PASS' if all_passed else 'FAIL'}` ({sum(1 for c in checks if c['passed'])}/{len(checks)} checks passed)",
        "",
        "## Automated Reconciliation Checks",
        "",
        "| Check | Expected | Observed | Status |",
        "| --- | --- | --- | --- |",
    ]
    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        lines.append(f"| `{c['name']}` | `{c['expected']}` | `{c['observed']}` | **{status}** |")

    lines.extend([
        "",
        "## Documented Historical Discrepancies Exposed (Not Silenced)",
        "",
        "1. **Cohort 029 `release/RESULTS.md` Direction Table:** Manual transcription in `RESULTS.md` lines 44-47 (Causal 121/512 off, 416/512 on; Arithmetic 124/512 off, 397/512 on, 785/1024 activated) disagrees with raw `events.jsonl` and `secondary.json` (Causal 14/512 off, 497/512 on, 995/1024 activated; Arithmetic 231/512 off, 316/512 on, 597/1024 activated). The dashboard uses and displays the verified raw-journal ground truth and explicitly documents this discrepancy.",
        "2. **Cohort 008 Interrupted Run (`run_001_f16`):** 26 persisted records (25 completed + 1 interrupted) out of 64 scheduled tasks, accounting for the exact 38-row difference between 48,208 scheduled requests and 48,170 persisted raw responses repository-wide.",
        "3. **Cohorts 009-011 Cell-Count Halving Bug:** Repaired in `b90cb63`; original `*_v1_undercounted_counts.json` preserved in the repository.",
        "4. **Cohort 016 Smaller-Gap Shortcut:** Retrospective audit (`manuscript/scripts/extract.py`) established that choosing the sign of the smaller printed `|on - off|` gap solves 768/768 Cohort 016 prompts without reading provenance.",
        "5. **Cohort 029 Human Independence Gate:** Production freeze recorded `authorship` and `review` as `undocumented`; post-freeze signed records are preserved with explicit limitations.",
        "",
    ])
    with (DASHBOARD_ROOT / "VERIFICATION_REPORT.md").open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main() -> None:
    checks, all_passed = run_checks()
    write_outputs(checks, all_passed)
    for c in checks:
        print(f"[verify] {c['name']}: {'PASS' if c['passed'] else 'FAIL'}")
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
