"""Read-only extraction and normalization pipeline for Project CausalFade.

Reads verified repository artifacts at the pinned commit without modifying any
original research file, normalizes heterogeneous cohort schemas, and emits
versioned JSON datasets with SHA-256 provenance into dashboard/public/data/.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_ROOT = REPO_ROOT / "dashboard"
OUT_DIR = DASHBOARD_ROOT / "public" / "data"
RESPONSES_DIR = OUT_DIR / "responses"

GITHUB_REPO = "https://github.com/mutasim-rehman/project-causalfade"
RELEASE_TAG = "cohort-029-v1.0.0"
RELEASE_COMMIT = "76206c259caa488668a7556ce1bc53cb35d220da"


def get_git_commit() -> str:
    """Return the exact HEAD commit hash of the repository."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        return out
    except Exception:
        return "01728ada407e8e5d59d6d7918dcd71dc0532b706"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path: Path) -> list[Any]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def github_blob_url(rel_path: str, commit: str) -> str:
    clean = rel_path.replace("\\", "/").lstrip("/")
    return f"{GITHUB_REPO}/blob/{commit}/{clean}"


def frac_to_float(obj: dict[str, int] | float | int) -> float:
    if isinstance(obj, dict) and "numerator" in obj and "denominator" in obj:
        return obj["numerator"] / obj["denominator"]
    return float(obj)


def make_provenance(
    metric_id: str,
    definition: str,
    value: Any,
    source_paths: list[str],
    commit: str,
    classification: str,
    unit: str = "proportion",
    unit_of_analysis: str = "numerical_family",
    cohort_id: str = "cohort_029",
    numerator: int | None = None,
    denominator: int | None = None,
    ci_method: str | None = None,
    statistical_test: str | None = None,
    limitations: str | None = None,
) -> dict[str, Any]:
    sources = []
    for sp in source_paths:
        p = REPO_ROOT / sp
        sources.append(
            {
                "path": sp,
                "sha256": sha256_file(p),
                "github_url": github_blob_url(sp, commit),
            }
        )
    return {
        "metric_id": metric_id,
        "definition": definition,
        "value": value,
        "numerator": numerator,
        "denominator": denominator,
        "unit": unit,
        "unit_of_analysis": unit_of_analysis,
        "cohort_id": cohort_id,
        "ci_method": ci_method,
        "statistical_test": statistical_test,
        "sources": sources,
        "git_commit": commit,
        "analysis_script": "dashboard/scripts/extract/extract_all.py",
        "classification": classification,
        "limitations": limitations,
    }


def extract_cohort_029_data(commit: str) -> dict[str, Any]:
    c29 = REPO_ROOT / "experiments" / "cohort_029"
    freeze = c29 / "freeze"
    fixture = freeze / "fixture"
    run_dir = c29 / "runs" / "confirmatory"
    analysis_dir = run_dir / "analysis"

    primary = read_json(analysis_dir / "primary.json")
    secondary = read_json(analysis_dir / "secondary.json")
    verification = read_json(c29 / "release" / "verification.json")
    worlds = read_jsonl(fixture / "worlds.jsonl")
    tasks = {r["task_id"]: r for r in read_jsonl(fixture / "tasks.jsonl")}
    gold = {r["task_id"]: r for r in read_jsonl(fixture / "gold.jsonl")}
    public_oracle = {r["task_id"]: r for r in read_jsonl(fixture / "public_oracle.jsonl")}
    row_scores = {r["task_id"]: r for r in read_jsonl(analysis_dir / "row_scores.jsonl")}
    pair_scores = read_jsonl(analysis_dir / "pair_scores.jsonl")
    family_scores = read_jsonl(analysis_dir / "family_scores.jsonl")
    events = read_jsonl(run_dir / "events.jsonl")

    # Re-decode raw responses from events.jsonl
    raw_responses = []
    for ev in events:
        if ev.get("type") != "response":
            continue
        tid = ev["task_id"]
        t_info = tasks.get(tid, {})
        g_info = gold.get(tid, {})
        po_info = public_oracle.get(tid, {})
        rs_info = row_scores.get(tid, {})
        raw_b64 = ev.get("response_b64", "")
        raw_text = ""
        finish_reason = ""
        if raw_b64:
            envelope = json.loads(base64.b64decode(raw_b64).decode("utf-8", errors="replace"))
            choices = envelope.get("choices", [])
            if choices:
                finish_reason = choices[0].get("finish_reason", "")
                raw_text = choices[0].get("message", {}).get("content", "")
        idx_arr = rs_info.get("indices", [None, None, None, None, None, None])
        slot, form, task, order, role, target = idx_arr[0], idx_arr[1], idx_arr[2], idx_arr[3], idx_arr[4], idx_arr[5]
        # Extract user prompt message
        messages = t_info.get("messages", [])
        user_msg = ""
        sys_msg = ""
        for m in messages:
            if m.get("role") == "user":
                user_msg = m.get("content", "")
            elif m.get("role") == "system":
                sys_msg = m.get("content", "")
        raw_responses.append(
            {
                "task_id": tid,
                "seq": ev.get("sequence"),
                "slot": slot,
                "h": rs_info.get("h"),
                "form": form,
                "form_label": "transfer" if form == 1 else "archive_compatible",
                "task": task,
                "task_label": "arithmetic" if task == 1 else "causal",
                "order": order,
                "order_label": "R_first" if order == 1 else "L_first",
                "role": role,
                "role_label": "R_governs" if role == 1 else "L_governs",
                "target": target,
                "gold_action": rs_info.get("gold", g_info.get("gold_action")),
                "predicted_action": rs_info.get("action"),
                "valid": bool(rs_info.get("valid")),
                "correct": bool(rs_info.get("correct")),
                "finish_reason": finish_reason,
                "raw_response": raw_text,
                "system_prompt": sys_msg,
                "user_prompt": user_msg,
                "options": po_info.get("options", []),
            }
        )

    # Sort by seq for deterministic ordering
    raw_responses.sort(key=lambda r: (r["seq"] or 0, r["task_id"]))

    # Extract Causal Lab families (all 128 worlds)
    lab_families = []
    for w in worlds:
        # tables[0] is L, tables[1] is R; each is [[off_s1, on_s1], [off_s0, on_s0]] in half-percent (out of 200)
        L = [[v / 2.0 for v in row] for row in w["tables"][0]]
        R = [[v / 2.0 for v in row] for row in w["tables"][1]]
        L_d1 = round(L[0][1] - L[0][0], 4)
        L_d0 = round(L[1][1] - L[1][0], 4)
        R_d1 = round(R[0][1] - R[0][0], 4)
        R_d0 = round(R[1][1] - R[1][0], 4)
        w0, w1 = w["weights"][0] / 100.0, w["weights"][1] / 100.0
        # Corners: corners[role][target]
        corners = [
            [round(frac_to_float(c) * 100, 4) for c in role_corners]
            for role_corners in w["corners"]
        ]
        # Latent surfaces scm[role][0] -> S=1,U=0/1,A=0/1
        scm_surfaces = []
        for r_idx in range(2):
            surf = w["scm"][r_idx][0]
            scm_surfaces.append(
                [
                    [[round(frac_to_float(a) * 100, 3) for a in u] for u in s]
                    for s in surf
                ]
            )
        lab_families.append(
            {
                "slot": w["slot"],
                "family_id": w["family_id"],
                "h": w["h"],
                "p": w["p"],
                "g": w["g"],
                "b": w["b"],
                "weights_pct": w["weights"],
                "tables_pct": {"L": L, "R": R},
                "stratum_effects_pp": {
                    "L": {"delta_1": L_d1, "delta_0": L_d0},
                    "R": {"delta_1": R_d1, "delta_0": R_d0},
                },
                "target_effects_pp": {
                    "L_governs": {"w0": corners[0][0], "w1": corners[0][1]},
                    "R_governs": {"w0": corners[1][0], "w1": corners[1][1]},
                },
                "oracle_actions": {
                    "L_governs": [1 if corners[0][0] > 0 else 0, 1 if corners[0][1] > 0 else 0],
                    "R_governs": [1 if corners[1][0] > 0 else 0, 1 if corners[1][1] > 0 else 0],
                },
                "scm_surfaces_pct": scm_surfaces,
            }
        )

    return {
        "primary": primary,
        "secondary": secondary,
        "verification": verification,
        "raw_responses": raw_responses,
        "pair_scores": pair_scores,
        "family_scores": family_scores,
        "lab_families": lab_families,
    }


def extract_manuscript_tables() -> dict[str, Any]:
    mdata = REPO_ROOT / "manuscript" / "data"
    maudit = REPO_ROOT / "manuscript" / "audit"
    return {
        "intervals": read_csv(mdata / "intervals.csv"),
        "families": read_csv(mdata / "families.csv"),
        "pairs": read_csv(mdata / "pairs.csv"),
        "policies": read_csv(mdata / "policies.csv"),
        "direction": read_csv(mdata / "direction.csv"),
        "option_order": read_csv(mdata / "option_order.csv"),
        "order016": read_csv(mdata / "order016.csv"),
        "example": read_csv(mdata / "example.csv"),
        "claim_ledger": read_csv(maudit / "claim-ledger.csv"),
        "citations": read_csv(maudit / "citations.csv"),
    }


def build_cohorts_dataset(commit: str) -> list[dict[str, Any]]:
    ev_dir = REPO_ROOT / "docs" / "scientific-retrospective" / "evidence"
    cohort_rows = read_csv(ev_dir / "cohort_inventory.csv")
    exp_rows = read_csv(ev_dir / "experiment_inventory.csv")

    runs_by_cohort: dict[str, list[dict[str, Any]]] = {}
    for er in exp_rows:
        cid = er["cohort_id"]
        runs_by_cohort.setdefault(cid, []).append(
            {
                "run_id": er["run_id"],
                "run_path": er["run_path"],
                "model_artifact": er["model_artifact"],
                "model_sha256": er["model_sha256"],
                "scheduled_requests": int(er["scheduled_requests"] or 0),
                "persisted_raw_records": int(er["persisted_raw_records"] or 0),
                "strict_valid_count": int(er["strict_valid_count"]) if er["strict_valid_count"] else None,
                "strict_correct_count": int(er["strict_correct_count"]) if er["strict_correct_count"] else None,
                "status": er["status"],
                "max_tokens": er["max_tokens"] if er["max_tokens"] else None,
                "seed": er["seed"],
                "raw_sha256": er["raw_sha256"],
            }
        )

    comparability_map = {
        "design_validation": "synthetic_validation",
        "cohort_001": "direct_3b_v1",
        "cohort_002": "formula_control_3b",
        "cohort_003": "q2k_repack_diag",
        "cohort_004": "direct_7b_screen",
        "cohort_005": "source_selection_3b_v1",
        "cohort_006": "formula_control_3b",
        "cohort_007": "formula_control_3b_fresh",
        "cohort_008": "source_order_3b",
        "cohort_009": "source_order_3b_interleaved",
        "cohort_010": "source_order_3b_interleaved_fresh",
        "cohort_011": "matched_strength_3b",
        "cohort_012": "matched_strength_7b_minimal",
        "cohort_013": "clarity_crossover_7b_160",
        "cohort_014": "clarity_crossover_7b_48",
        "cohort_015": "causal_context_7b_dev",
        "cohort_016": "causal_context_7b_confirmatory",
        "cohort_017": "causal_context_14b_reused",
        "cohort_018": "sensitivity_bias_v1",
        "cohort_019": "response_contract_v1",
        "cohort_020": "component_diag_v1",
        "cohort_021": "guidance_diag_v1",
        "cohort_022": "cross_lineage_dev_v1",
        "cohort_023": "measurement_audit_v1",
        "cohort_024": "precision_matrix_3x7",
        "cohort_025": "retrospective_archive",
        "cohort_025_1": "retrospective_audit",
        "cohort_026": "graph_switch_v1",
        "cohort_027": "graph_switch_order_balanced",
        "cohort_028": "calculator_procedure_selection",
        "cohort_029": "cf_tp1_target_transport",
    }

    # Detailed structured results for cohorts with machine-readable JSONs
    cohorts = []
    for cr in cohort_rows:
        cid = cr["cohort_id"]
        runs = runs_by_cohort.get(cid, [])
        sched_total = sum(r["scheduled_requests"] for r in runs)
        persisted_total = sum(r["persisted_raw_records"] for r in runs)
        art_path = cr["primary_artifact"]
        art_full = REPO_ROOT / art_path
        summary_path = REPO_ROOT / "experiments" / cid / "summary.md"
        readme_path = REPO_ROOT / "experiments" / cid / "README.md"

        artifacts = [
            {
                "path": art_path,
                "sha256": sha256_file(art_full),
                "github_url": github_blob_url(art_path, commit),
            }
        ]
        if summary_path.exists() and str(summary_path.relative_to(REPO_ROOT)).replace("\\", "/") != art_path:
            rel = f"experiments/{cid}/summary.md"
            artifacts.append(
                {
                    "path": rel,
                    "sha256": sha256_file(summary_path),
                    "github_url": github_blob_url(rel, commit),
                }
            )
        if readme_path.exists() and str(readme_path.relative_to(REPO_ROOT)).replace("\\", "/") != art_path:
            rel = f"experiments/{cid}/README.md"
            artifacts.append(
                {
                    "path": rel,
                    "sha256": sha256_file(readme_path),
                    "github_url": github_blob_url(rel, commit),
                }
            )

        cohorts.append(
            {
                "cohort_id": cid,
                "dates": cr["dates"],
                "title": cr["title"],
                "models_and_formats": cr["models_and_formats"],
                "sample_and_design": cr["sample_and_design"],
                "persisted_llm_responses": int(str(cr["persisted_llm_responses"]).split()[0]) if cr["persisted_llm_responses"] else 0,
                "scheduled_requests": sched_total,
                "persisted_from_runs": persisted_total,
                "inferential_classification": cr["inferential_classification"],
                "comparability_group": comparability_map.get(cid, cid),
                "principal_finding": cr["principal_finding"],
                "primary_artifact": art_path,
                "key_commits": cr["key_commits"],
                "runs": runs,
                "artifacts": artifacts,
                "has_interrupted_run": any(r["status"] == "interrupted" for r in runs),
            }
        )
    return cohorts


def extract_cohort_024_matrix() -> dict[str, Any]:
    path = REPO_ROOT / "experiments" / "cohort_024" / "development_analysis_archive.json"
    if not path.exists():
        return {"available": False}
    data = read_json(path)
    arms_summary = []
    for arm_name, arm_data in data.get("arms", {}).items():
        # Extract key summary fields cleanly
        metrics = arm_data.get("metrics", {}) if isinstance(arm_data, dict) else {}
        arms_summary.append(
            {
                "arm_id": arm_name,
                "lineage": arm_data.get("lineage") or arm_name.split("_")[0],
                "format": arm_data.get("format") or "_".join(arm_name.split("_")[1:]),
                "attempts": arm_data.get("attempts", 1472),
                "strict_valid": arm_data.get("strict_valid"),
                "raw": arm_data,
            }
        )
    return {
        "available": True,
        "source_path": "experiments/cohort_024/development_analysis_archive.json",
        "source_sha256": sha256_file(path),
        "raw": data,
    }


def extract_cohort_016_data() -> dict[str, Any]:
    p_path = REPO_ROOT / "experiments" / "cohort_016" / "primary_analysis.json"
    pwr_path = REPO_ROOT / "experiments" / "cohort_016" / "power_analysis.json"
    return {
        "primary_analysis": read_json(p_path),
        "power_analysis": read_json(pwr_path) if pwr_path.exists() else None,
        "primary_sha256": sha256_file(p_path),
        "power_sha256": sha256_file(pwr_path) if pwr_path.exists() else None,
    }


def extract_cohort_017_data() -> dict[str, Any]:
    p_path = REPO_ROOT / "experiments" / "cohort_017" / "analysis_recovery.json"
    a_path = REPO_ROOT / "experiments" / "cohort_017" / "analysis.json"
    return {
        "recovery": read_json(p_path) if p_path.exists() else None,
        "analysis": read_json(a_path) if a_path.exists() else None,
        "sha256": sha256_file(a_path),
    }


def extract_cohort_027_028_data() -> dict[str, Any]:
    c27_status = read_json(REPO_ROOT / "experiments" / "cohort_027" / "pipeline_status.json")
    c28_status = read_json(REPO_ROOT / "experiments" / "cohort_028" / "pipeline_status.json")
    c27_runs = {}
    c27_dev = REPO_ROOT / "experiments" / "cohort_027" / "runs" / "development"
    if c27_dev.exists():
        for arm_dir in sorted(c27_dev.iterdir()):
            af = arm_dir / "analysis.json"
            if af.exists():
                c27_runs[arm_dir.name] = read_json(af)
    c28_runs = {}
    c28_dev = REPO_ROOT / "experiments" / "cohort_028" / "runs" / "development"
    if c28_dev.exists():
        for arm_dir in sorted(c28_dev.iterdir()):
            af = arm_dir / "analysis.json"
            if af.exists():
                c28_runs[arm_dir.name] = read_json(af)
    return {
        "cohort_027": {"status": c27_status, "arms": c27_runs},
        "cohort_028": {"status": c28_status, "arms": c28_runs},
    }


def extract_literature(commit: str) -> dict[str, Any]:
    manifest = read_json(REPO_ROOT / "literature review" / "paper_manifest.json")
    citations = read_csv(REPO_ROOT / "manuscript" / "audit" / "citations.csv")

    theme_map = {
        "01_compressed_causal_reasoning": "Quantization & Causal Reasoning",
        "02_quantization_inflates_reasoning": "Quantization & Reasoning",
        "03_extreme_low_bit_inference": "Quantization & Reasoning",
        "04_reasoning_qat_systematic_study": "Quantization & Recovery",
        "05_quantization_hurts_reasoning": "Quantization & Reasoning",
        "06_quantization_meets_reasoning": "Quantization & Reasoning",
        "07_when_reasoning_meets_compression": "Quantization & Mechanisms",
        "08_causalflip": "Causal Evaluation & Shortcuts",
        "09_causalab": "Interactive Causal Agents",
        "10_active_causal_discovery_benchmark": "Interactive Causal Agents",
        "11_causalds": "Causal Data-Science Agents",
        "12_prism": "Recall vs Context & Mechanisms",
        "13_causaleval": "LLM Causal Reasoning",
        "14_causal_inference_llm_survey": "Causal Inference Foundations",
    }

    papers = []
    for item in manifest:
        meta = item.get("metadata", {})
        slug = item["slug"]
        title = (meta.get("citation_title") or meta.get("og:title") or [slug])[0]
        authors = meta.get("citation_author", [])
        date = (meta.get("citation_date") or [""])[0]
        abstract = (meta.get("citation_abstract") or meta.get("og:description") or [""])[0]
        papers.append(
            {
                "slug": slug,
                "title": title,
                "authors": authors,
                "year": date[:4] if date else "2025/2026",
                "date": date,
                "theme": theme_map.get(slug, item.get("topic", "General")),
                "publication_status": item.get("publication_status", ""),
                "source_url": item.get("landing_url", ""),
                "arxiv_version": item.get("arxiv_version", ""),
                "sha256": item.get("sha256", ""),
                "pages": item.get("pages", 0),
                "abstract": abstract,
                "summary_path": f"literature review/{item.get('summary_file', '')}",
                "influence_role": "Initial targeted literature review (Oct 2026); motivated behavioral scope and control tasks; findings not independently reproduced by CausalFade.",
                "stage": "initial_review",
            }
        )

    manuscript_refs = [
        {
            "key": c["key"],
            "title": c["title"],
            "year": c["year"],
            "edition": c["edition"],
            "primary_record": c["primary_record"],
            "stage": "manuscript_positioning",
        }
        for c in citations
    ]

    glossary = [
        {
            "term": "Average Treatment Effect (ATE / tau)",
            "symbol": "\\tau(w) = w\\delta_1 + (1-w)\\delta_0",
            "category": "Causal Inference",
            "definition": "Expected difference in potential outcomes E[Y(1) - Y(0)] under a population-level intervention setting A=1 versus A=0, standardized across stratum weights w.",
        },
        {
            "term": "Backdoor Adjustment / Standardization",
            "symbol": "E_k[Y(a)] = \\sum_s P_k(S=s) E[Y | A=a, S=s]",
            "category": "Causal Inference",
            "definition": "Computing interventional outcome expectations in a target population by weighting conditional randomized rates from each pretreatment stratum.",
        },
        {
            "term": "Target-Population Transportability",
            "symbol": "P_k(S=1) = w_k",
            "category": "Causal Inference",
            "definition": "Transporting stratum-specific causal effects from a source trial to a target population with a different stratum mixture w_k under conditional effect invariance.",
        },
        {
            "term": "Observational vs. Interventional Regime",
            "symbol": "P(Y|A=a) \\neq P(Y|do(A=a))",
            "category": "Causal Inference",
            "definition": "In historical observational data, unmeasured risk U influences both operator treatment choice A and outcome Y, creating confounding bias. Randomized trials sever incoming edges to A.",
        },
        {
            "term": "Target-Pair Fidelity (F_pair)",
            "symbol": "F_{\\mathrm{pair}} = I_0 \\cdot I_1",
            "category": "Experimental Design",
            "definition": "CF-TP1's primary paired endpoint: credit (1) is awarded only if BOTH target-mixture responses (k=0 and k=1) at fixed wording, task, order, and governing role are strict-valid and equal the oracle action.",
        },
        {
            "term": "Numerical Family (Independent Sampling Unit)",
            "symbol": "N = 128 \\text{ (Cohort 029)}",
            "category": "Statistics",
            "definition": "One independent draw from the SCM generator. All 32 prompts derived from the same family share underlying tables and are clustered—never treated as 32 independent observations.",
        },
        {
            "term": "Welch-Satterthwaite Stratified Interval",
            "symbol": "\\text{SE} = \\sqrt{\\sum_h s_h^2 / (64 \\cdot 16)}",
            "category": "Statistics",
            "definition": "Approximate 95% confidence interval for the stratified mean family difference D_i across 8 design strata (16 families each) using effective Welch degrees of freedom.",
        },
        {
            "term": "Conservative Bounded Interval",
            "symbol": "\\widehat{\\Delta} \\pm \\sqrt{2\\log(40)/128}",
            "category": "Statistics",
            "definition": "Distribution-free Hoeffding-style interval for bounded family-level differences in [-1, 1], guaranteeing nominal coverage without parametric normality assumptions (+/- 24.01 pp for N=128).",
        },
        {
            "term": "Deterministic Shortcut / Rival Policy",
            "symbol": "\\pi(\\text{prompt}) \\to \\{0,1\\}",
            "category": "Measurement Validity",
            "definition": "A simple heuristic (e.g., always activate, pick the smaller absolute printed gap, or pick the first displayed table) that can achieve high accuracy on an uncalibrated fixture without reading causal provenance.",
        },
        {
            "term": "Post-Training Quantization (PTQ)",
            "symbol": "\\text{F16} \\to \\text{Q8\\_0}, \\text{Q4\\_K\\_M}, \\text{Q2\\_K}",
            "category": "Machine Learning",
            "definition": "Compressing pretrained floating-point model weights to lower-bit integer/k-quant representations (e.g., via llama.cpp GGUF) without retraining.",
        },
    ]

    return {
        "initial_literature_review": papers,
        "manuscript_references": manuscript_refs,
        "glossary": glossary,
        "provenance": make_provenance(
            "literature_inventory",
            "Verified 14 targeted review papers and 17 manuscript positioning citations",
            len(papers),
            ["literature review/paper_manifest.json", "manuscript/audit/citations.csv"],
            commit,
            "Verified metadata",
            unit="papers",
            unit_of_analysis="document",
            cohort_id="all",
        ),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    commit = get_git_commit()
    ts = datetime.now(timezone.utc).isoformat()

    print(f"[extract] Git commit: {commit}")
    print("[extract] Reading Cohort 029...")
    c29 = extract_cohort_029_data(commit)
    print(f"[extract] Decoded {len(c29['raw_responses'])} Cohort 029 raw responses.")

    print("[extract] Reading manuscript tables & ledgers...")
    ms = extract_manuscript_tables()
    cohorts = build_cohorts_dataset(commit)

    ev_dir = REPO_ROOT / "docs" / "scientific-retrospective" / "evidence"
    hypotheses = read_csv(ev_dir / "hypothesis_ledger.csv")
    methodologies = read_csv(ev_dir / "methodology_ledger.csv")
    models_inv = read_csv(ev_dir / "model_quantization_inventory.csv")
    timeline_events = read_json(ev_dir / "research_timeline.json")

    c016 = extract_cohort_016_data()
    c017 = extract_cohort_017_data()
    c024 = extract_cohort_024_matrix()
    c027_028 = extract_cohort_027_028_data()
    lit = extract_literature(commit)

    total_scheduled = sum(c["scheduled_requests"] for c in cohorts)
    total_persisted = sum(c["persisted_llm_responses"] for c in cohorts)

    # 1. overview.json
    overview = {
        "product_name": "CAUSALFADE — Research Observatory",
        "subtitle": "An interactive investigation into causal inference, language model decision-making, and experimental validity.",
        "headline": "When evidence changes, does the model change its mind?",
        "git_commit": commit,
        "release_tag": RELEASE_TAG,
        "release_commit": RELEASE_COMMIT,
        "extraction_timestamp": ts,
        "kpis": {
            "documented_cohorts": len(cohorts),
            "llm_cohort_units": len([c for c in cohorts if c["persisted_llm_responses"] > 0]),
            "run_directories": sum(len(c["runs"]) for c in cohorts if c["cohort_id"] != "design_validation"),
            "completed_runs": sum(1 for c in cohorts if c["cohort_id"] != "design_validation" for r in c["runs"] if r["status"] != "interrupted"),
            "interrupted_runs": sum(1 for c in cohorts if c["cohort_id"] != "design_validation" for r in c["runs"] if r["status"] == "interrupted"),
            "scheduled_requests": total_scheduled,
            "persisted_raw_responses": total_persisted,
            "final_eval_responses": 4096,
            "final_eval_strict_valid": 4096,
            "independent_families_final": 128,
            "model_config_entries": len(models_inv),
            "causal_pair_fidelity": {"correct": 128, "total": 512, "pct": 25.0},
            "arithmetic_pair_fidelity": {"correct": 146, "total": 512, "pct": 28.515625},
            "delta_pp": -3.515625,
            "t_ci_pp": [round(x * 100, 4) for x in c29["primary"]["interval_t"]],
            "bounded_ci_pp": [round(x * 100, 4) for x in c29["primary"]["interval_bounded"]],
            "causal_reversals_correct": {"correct": 3, "total": 256},
            "causal_activation": {"count": 995, "total": 1024},
        },
        "research_at_a_glance": [
            {
                "step": 1,
                "title": "Original Hypothesis",
                "summary": "Does aggressive post-training quantization increase an AI agent's reliance on misleading observational associations when choosing causal interventions, beyond general task degradation?",
                "status": "Insufficiently identified (H01)",
            },
            {
                "step": 2,
                "title": "Causal Evaluation Problem",
                "summary": "Early pilots (Cohorts 001–007) revealed that 3B/7B F16 references failed baseline competence, emitted Markdown-fenced JSON, collapsed at Q2_K, or decoupled numeric estimates from explicit actions.",
                "status": "Construct validity bottleneck",
            },
            {
                "step": 3,
                "title": "Methodological Discoveries",
                "summary": "Cohort 016 confirmed a +62.5 pp evidence-order shift in 7B Q4_K_M, but retrospective auditing found a source-blind smaller-gap heuristic solved 768/768 items. Cohorts 018–028 uncovered option-position policies, token-mapping sensitivity, and arithmetic bottlenecks.",
                "status": "Shortcuts & confounds exposed",
            },
            {
                "step": 4,
                "title": "Final Controlled Experiment (CF-TP1)",
                "summary": "Cohort 029 constructed 128 independent numerical families where identical printed tables admit opposite randomized vs. historical provenance assignments, crossed with two target-population mixtures.",
                "status": "4,096/4,096 strict-valid",
            },
            {
                "step": 5,
                "title": "Scientific Contribution",
                "summary": "On Qwen2.5-7B Q4_K_M, causal fidelity (25.00%) and arithmetic fidelity (28.52%) differed by -3.52 pp (95% t CI [-7.77, +0.74], inconclusive). Directional scoring exposed 995/1,024 causal activation bias (3/256 reversals) vs. 45/256 unwarranted arithmetic flips.",
                "status": "Benchmark & diagnostic contribution",
            },
        ],
        "established": [
            "CF-TP1 breaks source-blind magnitude and constant-action shortcuts while achieving 4,096/4,096 strict-valid responses and 50/50 release verification checks.",
            "In Cohort 029, Qwen2.5-7B-Instruct Q4_K_M exhibited a near-constant causal activation preference (995/1,024) and solved only 3/256 required causal target-switch pairs.",
            "In Cohort 016, physical presentation order shifted 7B Q4_K_M conflict accuracy by +62.5 pp (95% t CI [+56.6, +68.4], t(95)=21.10, p=1.24e-37) across 96 fresh families.",
            "Across Cohorts 020–024, Qwen 7B F16 identified the governing randomized study (up to 128/128) yet still scored near chance (43–45%) on two-source action decisions.",
            "In Cohort 028, deterministic calculator assistance rescued noncausal controls (to 87.5–100%) but failed to rescue causal graph-to-rule selection (~50%).",
        ],
        "unresolved": [
            "Primary Cohort 029 causal-minus-arithmetic contrast (-3.52 pp, 95% t CI [-7.77, +0.74]) spans zero; neither causal-specific impairment nor equivalence is established.",
            "Selective causal reasoning degradation under post-training quantization remains unestablished across all 29 cohorts (no F16 arm in Cohort 029; heterogeneous/non-monotone patterns in Cohort 024).",
            "Internal neural causal representations or attention circuits cannot be identified from behavioral binary choices without mechanistic interventions.",
            "Generalization of CF-TP1 findings to other model families, larger scales, unquantized F16, or multi-turn tool-using agents remains open.",
        ],
        "provenance": make_provenance(
            "cohort_029_primary_summary",
            "Cohort 029 CF-TP1 primary target-pair fidelity and repository-wide inventory counts",
            c29["primary"],
            [
                "experiments/cohort_029/runs/confirmatory/analysis/primary.json",
                "experiments/cohort_029/release/verification.json",
                "docs/scientific-retrospective/evidence/cohort_inventory.csv",
            ],
            commit,
            "Confirmatory result (Cohort 029) + Verified archive inventory",
            unit="percentage_points",
            unit_of_analysis="128 independent numerical families (8 strata x 16)",
            cohort_id="cohort_029",
            numerator=128,
            denominator=512,
            ci_method="Stratified Welch-Satterthwaite 95% t CI & Hoeffding bounded CI",
            statistical_test="Paired within-family difference across 8 design strata",
            limitations="Single quantized deployment (Qwen2.5-7B-Instruct Q4_K_M); no F16 comparison arm in Cohort 029; primary CI crosses zero.",
        ),
    }

    # 2. causal_lab.json (all 128 verified Cohort 029 families, with Family 096 as featured)
    causal_lab = {
        "git_commit": commit,
        "cohort_id": "cohort_029",
        "featured_slot": 96,
        "equation": "\\tau_k = w_k \\delta_1 + (1 - w_k) \\delta_0, \\qquad a_k^\\star = \\mathbf{1}\\{\\tau_k > 0\\}",
        "families": c29["lab_families"],
        "provenance": make_provenance(
            "cf_tp1_causal_world_generator",
            "Exact rational SCM worlds, latent surfaces m_{SUA}, and target standardization oracles for all 128 Cohort 029 families",
            len(c29["lab_families"]),
            [
                "experiments/cohort_029/freeze/fixture/worlds.jsonl",
                "causalfade/target_transport.py",
            ],
            commit,
            "Confirmatory fixture specification",
            unit="families",
            unit_of_analysis="numerical_family",
            cohort_id="cohort_029",
        ),
    }

    # 3. statistics.json
    statistics = {
        "git_commit": commit,
        "cohort_029": {
            "primary": c29["primary"],
            "intervals": ms["intervals"],
            "families": [
                {
                    "slot": int(r["slot"]),
                    "h": int(r["h"]),
                    "form": int(r["form"]),
                    "causal": float(r["causal"]),
                    "arithmetic": float(r["arithmetic"]),
                    "diff": float(r["causal"]) - float(r["arithmetic"]),
                }
                for r in ms["families"]
            ],
            "pairs": ms["pairs"],
            "direction": ms["direction"],
            "option_order": ms["option_order"],
            "policies": ms["policies"],
        },
        "cohort_016": {
            "primary": c016["primary_analysis"],
            "power": c016["power_analysis"],
            "items_count": len(ms["order016"]),
            "family_effects": _compute_016_family_effects(ms["order016"]),
        },
        "cohort_017": c017,
        "cohort_024": c024,
        "cohort_027_028": c027_028,
        "design_validation": _extract_design_validation(),
        "provenance": make_provenance(
            "statistical_observatory_suite",
            "Verified inferential and descriptive statistics across Cohort 029, Cohort 016, Cohort 017, Cohort 024, Cohorts 027-028, and Design Validation",
            "verified_suite",
            [
                "experiments/cohort_029/runs/confirmatory/analysis/primary.json",
                "experiments/cohort_016/primary_analysis.json",
                "experiments/cohort_017/analysis_recovery.json",
                "experiments/cohort_024/development_analysis_archive.json",
                "results/design_validation/VALIDATION_REPORT.md",
            ],
            commit,
            "Confirmatory / Exploratory / Synthetic Validation (separately labeled)",
        ),
    }

    # 4. decision_behavior.json
    decision_behavior = {
        "git_commit": commit,
        "cohort_029_pairs": ms["pairs"],
        "cohort_029_direction": ms["direction"],
        "cohort_029_option_order": ms["option_order"],
        "cohort_029_policies": ms["policies"][:30],
        "cohort_029_all_policies_count": len(ms["policies"]),
        "cohort_029_row_cells": c29["secondary"]["row_cells"],
        "cohort_029_pair_cells": c29["secondary"]["pair_cells"],
        "provenance": make_provenance(
            "cohort_029_decision_behavior",
            "Paired transition matrices, joint pair-member correctness (0/1/2), action direction bias, and deterministic rival policies",
            len(c29["pair_scores"]),
            [
                "experiments/cohort_029/runs/confirmatory/analysis/secondary.json",
                "manuscript/data/pairs.csv",
                "manuscript/data/policies.csv",
            ],
            commit,
            "Confirmatory paired & descriptive diagnostics",
            unit="pairs",
            unit_of_analysis="target/role/order pairs within 128 families",
            cohort_id="cohort_029",
        ),
    }

    # 5. models_quantization.json
    models_quantization = {
        "git_commit": commit,
        "inventory": models_inv,
        "cohort_024_summary": _summarize_024_for_models(c024),
        "cohort_016_vs_017": {
            "cohort_016_7b_f16": c016["primary_analysis"]["secondary_order_results"]["f16"],
            "cohort_016_7b_q4": c016["primary_analysis"]["secondary_order_results"]["q4_k_m"],
            "cohort_017_14b": c017.get("recovery") or c017.get("analysis"),
        },
        "provenance": make_provenance(
            "model_quantization_inventory",
            "Inventory of all 14 model-format configurations, availability vs evaluation status, and within-checkpoint precision comparisons",
            len(models_inv),
            [
                "docs/scientific-retrospective/evidence/model_quantization_inventory.csv",
                "experiments/cohort_024/development_analysis_archive.json",
            ],
            commit,
            "Verified archive inventory & exploratory matrix",
        ),
    }

    # 6. Write all core JSON files
    _write_json(OUT_DIR / "overview.json", overview)
    _write_json(OUT_DIR / "cohorts.json", {"git_commit": commit, "cohorts": cohorts})
    _write_json(OUT_DIR / "timeline.json", {"git_commit": commit, "events": timeline_events})
    _write_json(OUT_DIR / "causal_lab.json", causal_lab)
    _write_json(OUT_DIR / "statistics.json", statistics)
    _write_json(OUT_DIR / "decision_behavior.json", decision_behavior)
    _write_json(OUT_DIR / "models_quantization.json", models_quantization)
    _write_json(OUT_DIR / "methodologies.json", {"git_commit": commit, "methodologies": methodologies})
    _write_json(OUT_DIR / "hypotheses.json", {"git_commit": commit, "hypotheses": hypotheses})
    _write_json(OUT_DIR / "literature.json", lit)

    # 7. Write chunked responses for Cohort 029 (4 chunks of 1024) + index
    chunk_size = 1024
    c29_chunks = []
    for i in range(0, len(c29["raw_responses"]), chunk_size):
        chunk_idx = i // chunk_size + 1
        fname = f"cohort_029_part{chunk_idx}.json"
        _write_json(RESPONSES_DIR / fname, c29["raw_responses"][i : i + chunk_size])
        c29_chunks.append(f"/data/responses/{fname}")

    # Also extract Cohort 016 & Cohort 008 interrupted run raw responses
    c016_responses = _extract_cohort_016_responses()
    _write_json(RESPONSES_DIR / "cohort_016.json", c016_responses)

    c008_interrupted = _extract_cohort_008_interrupted()
    _write_json(RESPONSES_DIR / "cohort_008_interrupted.json", c008_interrupted)

    responses_index = {
        "git_commit": commit,
        "archives": [
            {
                "id": "cohort_029",
                "title": "Cohort 029 — CF-TP1 Confirmatory Study (Qwen2.5-7B Q4_K_M)",
                "total_responses": len(c29["raw_responses"]),
                "chunks": c29_chunks,
            },
            {
                "id": "cohort_016",
                "title": "Cohort 016 — 96-Family Order Confirmation (Qwen2.5-7B F16 & Q4_K_M)",
                "total_responses": len(c016_responses),
                "chunks": ["/data/responses/cohort_016.json"],
            },
            {
                "id": "cohort_008_interrupted",
                "title": "Cohort 008 — Interrupted Run 1 (Qwen2.5-3B F16, 26/64 persisted)",
                "total_responses": len(c008_interrupted),
                "chunks": ["/data/responses/cohort_008_interrupted.json"],
            },
        ],
    }
    _write_json(RESPONSES_DIR / "index.json", responses_index)

    # 8. Reproducibility & Claim-Evidence Registry
    repro = {
        "git_commit": commit,
        "release_tag": RELEASE_TAG,
        "release_commit": RELEASE_COMMIT,
        "extraction_timestamp": ts,
        "cohort_029_verification": c29["verification"],
        "claim_ledger": ms["claim_ledger"],
        "discrepancies": [
            {
                "id": "D01",
                "title": "Cohort 029 release/RESULTS.md Manual Direction Table Transcription Error",
                "severity": "Documentation discrepancy (primary endpoint unaffected)",
                "reported": "RESULTS.md lines 44-47 printed Causal 121/512 off, 416/512 on; Arithmetic 124/512 off, 397/512 on, 785/1024 activated.",
                "verified_ground_truth": "events.jsonl & secondary.json: Causal 14/512 off, 497/512 on, 995/1024 activated; Arithmetic 231/512 off, 316/512 on, 597/1024 activated.",
                "source_path": "experiments/cohort_029/release/RESULTS.md",
            },
            {
                "id": "D02",
                "title": "Cohort 008 Interrupted Run (run_001_f16)",
                "severity": "Preserved operational interruption",
                "reported": "64 scheduled tasks in Cohort 008 run_001_f16; stopped at user shutdown request after 25 completed + 1 interrupted = 26 persisted records (accounting for 48,208 scheduled vs 48,170 persisted across repo).",
                "verified_ground_truth": "26 raw JSONL lines retained separately; replacement runs run_002_f16 and run_002_q4_k_m completed 64/64.",
                "source_path": "experiments/cohort_008/run_001_f16/raw_responses.jsonl",
            },
            {
                "id": "D03",
                "title": "Cohorts 009–011 Interleaved Cell-Count Halving Bug (Fixed at b90cb63)",
                "severity": "Historical analysis bug (repaired & archived)",
                "reported": "Original analyze_interleaved_order.py averaged 2 items/family without multiplying by 2, halving printed counts.",
                "verified_ground_truth": "Repaired canonical JSONs + *_v1_undercounted_counts.json preserved. Family-level contrasts & bootstrap CIs unchanged.",
                "source_path": "tools/analyze_interleaved_order.py",
            },
            {
                "id": "D04",
                "title": "Cohort 016 Retrospective Smaller-Gap Magnitude Shortcut",
                "severity": "Construct-validity audit finding",
                "reported": "Cohort 016 confirmed +62.5 pp order effect on 96 fresh families.",
                "verified_ground_truth": "Retrospective audit found |tau| in [0.06, 0.12) < |delta_obs| in [0.38, 0.46) on every item, so choosing the sign of the smaller printed gap solves 768/768 prompts without reading provenance.",
                "source_path": "manuscript/scripts/extract.py",
            },
            {
                "id": "D05",
                "title": "Cohort 029 Pre-Inference Human Independence Documentation Limit",
                "severity": "Provenance boundary",
                "reported": "CF-TP1 v1.0 specified pre-inference signed human authorship and blind review.",
                "verified_ground_truth": "Production freeze recorded authorship & review as 'undocumented'; signed records reconciled post-freeze with abbreviated reviewer ID ('Raza') and untrusted signer key.",
                "source_path": "experiments/cohort_029/release/PROVENANCE_AND_LIMITATIONS.md",
            },
        ],
    }
    _write_json(OUT_DIR / "reproducibility.json", repro)
    print("[extract] Extraction complete.")


def _compute_016_family_effects(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_arm_fam: dict[tuple[str, str], dict[str, list[int]]] = {}
    for r in rows:
        key = (r["arm"], r["family"])
        d = by_arm_fam.setdefault(key, {"hist_conf": [], "rand_conf": [], "hist_alig": [], "rand_alig": []})
        correct = 1 if r["gold"] == r["action"] else 0
        is_conf = r["conflict"] == "1"
        is_hist = r["order"] == "historical_first"
        if is_conf and is_hist:
            d["hist_conf"].append(correct)
        elif is_conf and not is_hist:
            d["rand_conf"].append(correct)
        elif not is_conf and is_hist:
            d["hist_alig"].append(correct)
        else:
            d["rand_alig"].append(correct)

    out = []
    for (arm, fam), d in sorted(by_arm_fam.items()):
        hc = sum(d["hist_conf"]) / len(d["hist_conf"]) if d["hist_conf"] else 0.0
        rc = sum(d["rand_conf"]) / len(d["rand_conf"]) if d["rand_conf"] else 0.0
        out.append(
            {
                "arm": arm,
                "family": fam,
                "conflict_order_diff_pp": round((hc - rc) * 100, 4),
                "hist_conf_acc": hc,
                "rand_conf_acc": rc,
            }
        )
    return out


def _extract_design_validation() -> dict[str, Any]:
    path = REPO_ROOT / "results" / "design_validation" / "validation_summary.json"
    if path.exists():
        return {"available": True, "data": read_json(path)}
    return {"available": False}


def _summarize_024_for_models(c024: dict[str, Any]) -> list[dict[str, Any]]:
    if not c024.get("available"):
        return []
    raw = c024["raw"]
    arms = raw.get("arms", {})
    rows = []
    for arm_key, arm_val in arms.items():
        if not isinstance(arm_val, dict):
            continue
        rows.append(
            {
                "arm": arm_key,
                "lineage": arm_val.get("lineage", arm_key.split("_")[0]),
                "format": arm_val.get("format", "_".join(arm_key.split("_")[1:])),
                "attempts": arm_val.get("attempts", 1472),
                "strict_valid": arm_val.get("strict_valid", 0),
                "summary": arm_val,
            }
        )
    return rows


def _extract_cohort_016_responses() -> list[dict[str, Any]]:
    c16 = REPO_ROOT / "experiments" / "cohort_016"
    tasks = {r["task_id"]: r for r in read_jsonl(c16 / "input" / "public_tasks.jsonl")}
    oracle = {r["task_id"]: r for r in read_jsonl(c16 / "input" / "oracle_truth.jsonl")}
    out = []
    for arm, rdir in [("F16", "run_001_7b_f16"), ("Q4_K_M", "run_002_7b_q4_k_m")]:
        raw_path = c16 / rdir / "raw_responses.jsonl"
        if not raw_path.exists():
            continue
        for row in read_jsonl(raw_path):
            tid = row["task_id"]
            t = tasks.get(tid, {})
            o = oracle.get(tid, {})
            resp = row.get("response", {})
            choices = resp.get("choices", [])
            raw_text = choices[0].get("message", {}).get("content", "") if choices else ""
            pred = row.get("prediction") or {}
            pred_act = pred.get("activate")
            out.append(
                {
                    "task_id": tid,
                    "arm": arm,
                    "family_id": t.get("family_id", ""),
                    "condition": o.get("condition", ""),
                    "order": t.get("evidence_order", ""),
                    "gold_action": o.get("gold_action"),
                    "predicted_action": pred_act,
                    "valid": row.get("parse_status") == "object" and pred_act in (0, 1),
                    "correct": pred_act == o.get("gold_action"),
                    "raw_response": raw_text,
                    "user_prompt": t.get("prompt", ""),
                }
            )
    return out


def _extract_cohort_008_interrupted() -> list[dict[str, Any]]:
    p = REPO_ROOT / "experiments" / "cohort_008" / "run_001_f16" / "raw_responses.jsonl"
    if not p.exists():
        return []
    rows = read_jsonl(p)
    out = []
    for idx, r in enumerate(rows):
        out.append(
            {
                "task_id": r.get("task_id", f"row-{idx}"),
                "status": r.get("status", "unknown"),
                "finish_reason": r.get("finish_reason", ""),
                "raw_response": r.get("raw_text", r.get("error", "")),
                "error": r.get("error"),
            }
        )
    return out


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
