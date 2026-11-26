"""Extract verified repository artifacts, raw responses, and statistics across all cohorts.

Reads existing repository artifacts strictly in read-only mode without modifying any historical file.
Generates machine-readable inventories in docs/scientific-retrospective/evidence/.
"""
from __future__ import annotations

import base64
import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parents[1] / "evidence"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_out(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def first_jsonl_records(path: Path, n: int = 3) -> list[dict]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
                if len(out) >= n:
                    break
    return out


def count_lines(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for line in f if line.strip())


def inspect_runs() -> tuple[list[dict], dict]:
    exp_dir = ROOT / "experiments"
    runs = []
    sample_responses = {}

    # Synthetic pre-LLM validation baseline
    dv_dir = ROOT / "results" / "design_validation"
    runs.append({
        "cohort_id": "design_validation",
        "run_id": "synthetic_parameter_recovery",
        "run_path": "results/design_validation",
        "model_artifact": "none (synthetic C/A/B EM + logistic recovery, 3600 datasets)",
        "model_sha256": "",
        "scheduled_requests": 0,
        "persisted_raw_records": 0,
        "strict_valid_count": "",
        "strict_correct_count": "",
        "status": "complete_synthetic_validation",
        "max_tokens": "",
        "threads": "",
        "temperature": "",
        "seed": 20261101,
        "raw_sha256": sha256_file(dv_dir / "recovery_replicates.csv"),
    })

    # Cohorts 001 - 023
    for c_idx in range(1, 24):
        c_name = f"cohort_{c_idx:03d}"
        c_path = exp_dir / c_name
        if not c_path.exists():
            continue
        for sub in sorted(c_path.iterdir()):
            if sub.is_dir() and sub.name.startswith("run_"):
                cfg_p = sub / "config.json"
                cfg = load_json(cfg_p) if cfg_p.exists() else {}
                stat_p = sub / "status.json"
                stat = load_json(stat_p) if stat_p.exists() else {}
                meta_p = sub / "metadata.json"
                meta = load_json(meta_p) if meta_p.exists() else {}
                raw_p = sub / "raw_responses.jsonl"
                res_p = sub / "results.json"
                sched_p = sub / "schedule.json"

                raw_count = count_lines(raw_p) if raw_p.exists() else 0
                raw_sha = sha256_file(raw_p) if raw_p.exists() else ""
                sched_count = 0
                if sched_p.exists():
                    s_obj = load_json(sched_p)
                    if isinstance(s_obj, list):
                        sched_count = len(s_obj)
                    elif isinstance(s_obj, dict):
                        sched_count = len(s_obj.get("tasks", s_obj.get("schedule", s_obj.get("items", []))))

                valid_strict = ""
                correct_strict = ""
                if res_p.exists():
                    r_obj = load_json(res_p)
                    rows = r_obj if isinstance(r_obj, list) else r_obj.get("results", r_obj.get("rows", []))
                    if isinstance(rows, list) and rows:
                        if sched_count == 0:
                            sched_count = len(rows)
                        valid_strict = sum(1 for r in rows if r.get("valid_action") or r.get("strict_valid") or r.get("valid"))
                        correct_strict = sum(1 for r in rows if r.get("correct") or r.get("strict_correct"))

                if raw_p.exists():
                    recs = first_jsonl_records(raw_p, 2)
                    if recs:
                        sample_responses[f"{c_name}/{sub.name}"] = {
                            "task_id": recs[0].get("task_id", ""),
                            "finish_reason": recs[0].get("response", {}).get("choices", [{}])[0].get("finish_reason", recs[0].get("finish_reason", "")),
                            "content": recs[0].get("response", {}).get("choices", [{}])[0].get("message", {}).get("content", recs[0].get("raw_text", ""))[:300],
                        }

                model_path = cfg.get("model", cfg.get("model_path", meta.get("model_path", "")))
                model_sha = meta.get("model_sha256", cfg.get("model_sha256", ""))
                sampling = cfg.get("sampling", {})
                runs.append({
                    "cohort_id": c_name,
                    "run_id": sub.name,
                    "run_path": f"experiments/{c_name}/{sub.name}",
                    "model_artifact": os.path.basename(str(model_path)) if model_path else "",
                    "model_sha256": model_sha,
                    "scheduled_requests": sched_count or raw_count,
                    "persisted_raw_records": raw_count,
                    "strict_valid_count": valid_strict,
                    "strict_correct_count": correct_strict,
                    "status": stat.get("status", "complete" if raw_count == sched_count else "partial"),
                    "max_tokens": cfg.get("max_tokens", sampling.get("max_tokens", "")),
                    "threads": cfg.get("threads", ""),
                    "temperature": cfg.get("temperature", sampling.get("temperature", 0)),
                    "seed": cfg.get("seed", sampling.get("seed", "")),
                    "raw_sha256": raw_sha,
                })

    # Cohort 024 (21 arms)
    c24_arch = load_json(exp_dir / "cohort_024" / "development_analysis_archive.json")
    c24_runs_dir = exp_dir / "cohort_024" / "runs"
    for sub in sorted(c24_runs_dir.iterdir()):
        if not sub.is_dir():
            continue
        cfg = load_json(sub / "config.json")
        stat = load_json(sub / "status.json")
        raw_p = sub / "raw_responses.jsonl"
        raw_count = count_lines(raw_p)
        raw_sha = sha256_file(raw_p)
        ad = c24_arch["arms"][sub.name]
        valid_c = ad["cells"]["all"]["valid"]
        corr_c = ad["cells"]["all"]["correct"]
        if sub.name in ("qwen7b_f16", "mistral7b_f16", "llama8b_q4_k_m"):
            r0 = first_jsonl_records(raw_p, 5)
            # For llama8b_q4_k_m find a length-capped one too
            sample_responses[f"cohort_024/{sub.name}"] = {
                "task_id": r0[0].get("task_id", ""),
                "finish_reason": r0[0].get("response", {}).get("choices", [{}])[0].get("finish_reason", ""),
                "content": r0[0].get("response", {}).get("choices", [{}])[0].get("message", {}).get("content", "")[:300],
            }
            if sub.name == "llama8b_q4_k_m":
                with raw_p.open("r", encoding="utf-8") as f:
                    for line in f:
                        rec = json.loads(line)
                        ch = rec.get("response", {}).get("choices", [{}])[0]
                        if ch.get("finish_reason") == "length":
                            sample_responses["cohort_024/llama8b_q4_k_m_capped"] = {
                                "task_id": rec.get("task_id", ""),
                                "finish_reason": "length",
                                "content": ch.get("message", {}).get("content", "")[:300],
                            }
                            break
        runs.append({
            "cohort_id": "cohort_024",
            "run_id": sub.name,
            "run_path": f"experiments/cohort_024/runs/{sub.name}",
            "model_artifact": os.path.basename(str(cfg.get("model_path", cfg.get("model", sub.name)))),
            "model_sha256": cfg.get("model_sha256", ""),
            "scheduled_requests": 1472,
            "persisted_raw_records": raw_count,
            "strict_valid_count": valid_c,
            "strict_correct_count": corr_c,
            "status": stat.get("status", "success"),
            "max_tokens": cfg.get("max_tokens", 64),
            "threads": cfg.get("threads", 8),
            "temperature": cfg.get("temperature", 0),
            "seed": cfg.get("seed", ""),
            "raw_sha256": raw_sha,
        })

    # Cohort 025 & 025_1
    runs.append({
        "cohort_id": "cohort_025",
        "run_id": "archive_methods_screen",
        "run_path": "experiments/cohort_025/archive_methods_screen.json",
        "model_artifact": "none (retrospective archive screen of cohorts 001-024)",
        "model_sha256": "",
        "scheduled_requests": 0,
        "persisted_raw_records": 0,
        "strict_valid_count": "",
        "strict_correct_count": "",
        "status": "complete_no_inference",
        "max_tokens": "",
        "threads": "",
        "temperature": "",
        "seed": "",
        "raw_sha256": sha256_file(exp_dir / "cohort_025" / "archive_methods_screen.json"),
    })
    runs.append({
        "cohort_id": "cohort_025_1",
        "run_id": "archive_investigation",
        "run_path": "experiments/cohort_025_1/archive_investigation.json",
        "model_artifact": "none (retrospective cross-disciplinary applicability audit)",
        "model_sha256": "",
        "scheduled_requests": 0,
        "persisted_raw_records": 0,
        "strict_valid_count": "",
        "strict_correct_count": "",
        "status": "complete_no_inference",
        "max_tokens": "",
        "threads": "",
        "temperature": "",
        "seed": "",
        "raw_sha256": sha256_file(exp_dir / "cohort_025_1" / "archive_investigation.json"),
    })

    # Cohort 026 (5 runs)
    c26_runs = exp_dir / "cohort_026" / "runs"
    for sub in sorted(c26_runs.iterdir()):
        if not sub.is_dir():
            continue
        cfg = load_json(sub / "config.json")
        ana = load_json(sub / "development_analysis.json")
        raw_p = sub / "raw_responses.jsonl"
        raw_count = count_lines(raw_p)
        raw_sha = sha256_file(raw_p)
        val_total = ana.get("valid", "")
        corr_total = sum(
            fd["counts"]["arithmetic"]["correct"]
            + fd["counts"]["graph"]["correct"]
            + fd["counts"]["no_change"]["correct"]
            + fd["counts"]["switch"]["correct"]
            for fd in ana["forms"].values()
        )
        r0 = first_jsonl_records(raw_p, 1)[0]
        sample_responses[f"cohort_026/{sub.name}"] = {
            "task_id": r0.get("task_id", ""),
            "utc": r0.get("utc", ""),
            "content": r0.get("response", {}).get("choices", [{}])[0].get("message", {}).get("content", "")[:200],
        }
        runs.append({
            "cohort_id": "cohort_026",
            "run_id": sub.name,
            "run_path": f"experiments/cohort_026/runs/{sub.name}",
            "model_artifact": os.path.basename(str(cfg.get("model", cfg.get("model_path", sub.name)))),
            "model_sha256": cfg.get("model_sha256", ""),
            "scheduled_requests": 112,
            "persisted_raw_records": raw_count,
            "strict_valid_count": val_total,
            "strict_correct_count": corr_total,
            "status": "invalidated_oracle_defect" if "invalidated" in sub.name else "complete_failed_gate",
            "max_tokens": cfg.get("max_tokens", 64),
            "threads": cfg.get("threads", 8),
            "temperature": cfg.get("temperature", 0),
            "seed": cfg.get("seed", ""),
            "raw_sha256": raw_sha,
        })

    # Cohort 027 (4 development runs)
    c27_runs = exp_dir / "cohort_027" / "runs" / "development"
    for sub in sorted(c27_runs.iterdir()):
        if not sub.is_dir():
            continue
        cfg = load_json(sub / "config.json")
        ana = load_json(sub / "analysis.json")
        att_p = sub / "attempts.jsonl"
        raw_count = count_lines(att_p)
        raw_sha = sha256_file(att_p)
        val_total = sum(fd["cells"]["validity"]["correct"] for fd in ana["forms"].values())
        # Note: confounder is shared between switch and added_z; compute exact row correctness from results.jsonl
        res_rows = [json.loads(line) for line in (sub / "results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        corr_total = sum(1 for r in res_rows if r.get("strict_correct") or r.get("correct"))
        r0 = first_jsonl_records(att_p, 1)[0]
        sample_responses[f"cohort_027/{sub.name}"] = {
            "task_id": r0.get("task_id", ""),
            "content": str(r0.get("raw_text", r0.get("content", r0)))[:250],
        }
        runs.append({
            "cohort_id": "cohort_027",
            "run_id": f"development/{sub.name}",
            "run_path": f"experiments/cohort_027/runs/development/{sub.name}",
            "model_artifact": os.path.basename(str(cfg.get("model_path", cfg.get("model", sub.name)))),
            "model_sha256": cfg.get("model_sha256", ""),
            "scheduled_requests": 224,
            "persisted_raw_records": raw_count,
            "strict_valid_count": val_total,
            "strict_correct_count": corr_total,
            "status": "complete_stopped_by_gate",
            "max_tokens": cfg.get("max_tokens", 64),
            "threads": cfg.get("threads", 8),
            "temperature": cfg.get("temperature", 0),
            "seed": cfg.get("seed", ""),
            "raw_sha256": raw_sha,
        })

    # Cohort 028 (2 development runs)
    c28_runs = exp_dir / "cohort_028" / "runs" / "development"
    for sub in sorted(c28_runs.iterdir()):
        if not sub.is_dir():
            continue
        cfg = load_json(sub / "config.json")
        ana = load_json(sub / "analysis.json")
        att_p = sub / "attempts.jsonl"
        raw_count = count_lines(att_p)
        raw_sha = sha256_file(att_p)
        val_total = ana["validity"]["bare"]["correct"] + ana["validity"]["structured"]["correct"]
        res_rows = [json.loads(line) for line in (sub / "results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        corr_total = sum(1 for r in res_rows if r.get("a_correct") or r.get("b_correct"))
        recs = first_jsonl_records(att_p, 4)
        sample_responses[f"cohort_028/{sub.name}"] = [
            {"task_id": r.get("task_id", ""), "raw": str(r.get("raw_text", r.get("content", "")))[:250]} for r in recs[:2]
        ]
        runs.append({
            "cohort_id": "cohort_028",
            "run_id": f"development/{sub.name}",
            "run_path": f"experiments/cohort_028/runs/development/{sub.name}",
            "model_artifact": os.path.basename(str(cfg.get("model_path", cfg.get("model", sub.name)))),
            "model_sha256": cfg.get("model_sha256", ""),
            "scheduled_requests": 1280,
            "persisted_raw_records": raw_count,
            "strict_valid_count": val_total,
            "strict_correct_count": corr_total,
            "status": "complete_stopped_by_gate",
            "max_tokens": "64 (bare) / 192 (structured)",
            "threads": cfg.get("threads", 8),
            "temperature": cfg.get("temperature", 0),
            "seed": cfg.get("seed", ""),
            "raw_sha256": raw_sha,
        })

    # Cohort 029 (1 confirmatory run)
    c29_ev = exp_dir / "cohort_029" / "runs" / "confirmatory" / "events.jsonl"
    c29_inv = load_json(exp_dir / "cohort_029" / "freeze" / "deployment" / "inventory.json")
    c29_rows = exp_dir / "cohort_029" / "runs" / "confirmatory" / "analysis" / "row_scores.jsonl"
    row_corr = sum(1 for line in c29_rows.read_text(encoding="utf-8").splitlines() if line.strip() and json.loads(line).get("correct"))
    ev_samples = []
    with c29_ev.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("type") == "response" or rec.get("event") == "response":
                raw_txt = ""
                if "response_b64" in rec:
                    raw_txt = base64.b64decode(rec["response_b64"]).decode("utf-8", errors="replace")
                ev_samples.append({
                    "task_id": rec.get("task_id", ""),
                    "utc": rec.get("utc", rec.get("timestamp", "")),
                    "decoded_content": json.loads(raw_txt)["choices"][0]["message"]["content"] if raw_txt else "",
                })
                if len(ev_samples) >= 2:
                    break
    sample_responses["cohort_029/confirmatory"] = ev_samples[0] if ev_samples else {}

    runs.append({
        "cohort_id": "cohort_029",
        "run_id": "confirmatory",
        "run_path": "experiments/cohort_029/runs/confirmatory",
        "model_artifact": "qwen2.5-7b-instruct-q4_k_m.gguf",
        "model_sha256": "7ebec3cd0f2d49bd4a8d068dc5f0e335f3647eec6dc4104d81416533a63bc5bc",
        "scheduled_requests": 4096,
        "persisted_raw_records": 4096,
        "strict_valid_count": 4096,
        "strict_correct_count": row_corr,
        "status": "complete_confirmatory_release",
        "max_tokens": 48,
        "threads": 8,
        "temperature": 0,
        "seed": 20261126,
        "raw_sha256": sha256_file(c29_ev),
    })

    return runs, {"sample_responses": sample_responses, "c29_inventory": c29_inv}


def extract_c24_matrix() -> list[dict]:
    c24 = load_json(ROOT / "experiments" / "cohort_024" / "development_analysis_archive.json")
    rows = []
    for arm_name, ad in c24["arms"].items():
        cells = ad["cells"]
        sdt_sem = ad["signal_detection"]["decision|semantic"]
        sdt_ctrl = ad["signal_detection"]["noncausal_control|semantic"]
        rows.append({
            "arm": arm_name,
            "lineage": ad["lineage"],
            "precision": ad["precision"],
            "all_valid": cells["all"]["valid"],
            "all_scheduled": cells["all"]["scheduled"],
            "causal_sem_correct": cells["decision|semantic"]["correct"],
            "causal_sem_valid": cells["decision|semantic"]["valid"],
            "causal_sem_scheduled": cells["decision|semantic"]["scheduled"],
            "causal_neu_correct": cells["decision|neutral"]["correct"],
            "ctrl_sem_correct": cells["noncausal_control|semantic"]["correct"],
            "ctrl_sem_valid": cells["noncausal_control|semantic"]["valid"],
            "ctrl_neu_correct": cells["noncausal_control|neutral"]["correct"],
            "ctrl_neu_valid": cells["noncausal_control|neutral"]["valid"],
            "source_sel_correct": cells["source_selection"]["correct"] if "source_selection" in cells else cells.get("governing_source", {}).get("correct", ""),
            "rand_only_sem_correct": cells["randomized_only|semantic"]["correct"],
            "num_check_correct": cells["numeric_comparison"]["correct"] if "numeric_comparison" in cells else "",
            "d_prime_causal_sem": sdt_sem.get("d_prime"),
            "criterion_causal_sem": sdt_sem.get("criterion"),
            "d_prime_ctrl_sem": sdt_ctrl.get("d_prime"),
            "all_diag_pass": ad["all_diagnostic_checks_pass"],
        })
    return rows


def extract_c28_summary() -> dict:
    out = {}
    for m in ("llama8b", "qwen7b"):
        d = load_json(ROOT / "experiments" / "cohort_028" / "runs" / "development" / m / "analysis.json")
        cells = d["descriptive_cells"]
        agg = {
            "bare_causal_raw": [0, 0],
            "struct_causal_raw_B": [0, 0],
            "assist_causal_raw_C": [0, 0],
            "struct_rule_causal_raw": [0, 0],
            "struct_score_match_selected_causal_raw": [0, 0],
            "bare_ctrl_raw": [0, 0],
            "struct_ctrl_raw_B": [0, 0],
            "assist_ctrl_raw_C": [0, 0],
            "bare_causal_sup": [0, 0],
            "struct_causal_sup_B": [0, 0],
            "assist_causal_sup_C": [0, 0],
            "struct_rule_causal_sup": [0, 0],
        }
        for k, v in cells.items():
            parts = k.split("|")
            if len(parts) == 6:
                cond, form, rep, kind, tgt, order = parts
                if rep == "raw" and kind == "causal" and tgt in ("confounder", "mediator"):
                    if cond == "bare":
                        agg["bare_causal_raw"][0] += v["a_accuracy"]["correct"]
                        agg["bare_causal_raw"][1] += v["scheduled"]
                    elif cond == "structured":
                        agg["struct_causal_raw_B"][0] += v["b_accuracy"]["correct"]
                        agg["struct_causal_raw_B"][1] += v["scheduled"]
                        agg["assist_causal_raw_C"][0] += v["c_accuracy"]["correct"]
                        agg["assist_causal_raw_C"][1] += v["scheduled"]
                        agg["struct_rule_causal_raw"][0] += v["rule_correct"]["correct"]
                        agg["struct_rule_causal_raw"][1] += v["scheduled"]
                        agg["struct_score_match_selected_causal_raw"][0] += v["score_match_selected"]["correct"]
                        agg["struct_score_match_selected_causal_raw"][1] += v["scheduled"]
                elif rep == "supplied" and kind == "causal" and tgt in ("confounder", "mediator"):
                    if cond == "bare":
                        agg["bare_causal_sup"][0] += v["a_accuracy"]["correct"]
                        agg["bare_causal_sup"][1] += v["scheduled"]
                    elif cond == "structured":
                        agg["struct_causal_sup_B"][0] += v["b_accuracy"]["correct"]
                        agg["struct_causal_sup_B"][1] += v["scheduled"]
                        agg["assist_causal_sup_C"][0] += v["c_accuracy"]["correct"]
                        agg["assist_causal_sup_C"][1] += v["scheduled"]
                        agg["struct_rule_causal_sup"][0] += v["rule_correct"]["correct"]
                        agg["struct_rule_causal_sup"][1] += v["scheduled"]
                elif rep == "raw" and kind == "control":
                    if cond == "bare":
                        agg["bare_ctrl_raw"][0] += v["a_accuracy"]["correct"]
                        agg["bare_ctrl_raw"][1] += v["scheduled"]
                    elif cond == "structured":
                        agg["struct_ctrl_raw_B"][0] += v["b_accuracy"]["correct"]
                        agg["struct_ctrl_raw_B"][1] += v["scheduled"]
                        agg["assist_ctrl_raw_C"][0] += v["c_accuracy"]["correct"]
                        agg["assist_ctrl_raw_C"][1] += v["scheduled"]
        forms_summary = {}
        for fn, fd in d.get("forms", {}).items():
            forms_summary[fn] = {
                "qualified": fd["qualified"],
                "schema_validity": fd["cells"]["schema_validity"],
                "raw_paired_switch": fd["cells"]["raw_paired_switch"],
                "supplied_paired_switch": fd["cells"]["supplied_paired_switch"],
                "raw_no_change_invariance": fd["cells"]["raw_no_change_invariance"],
                "supplied_no_change_invariance": fd["cells"]["supplied_no_change_invariance"],
            }
        out[m] = {
            "validity": d["validity"],
            "primary_gain_pp": d["primary_gain_pp"],
            "specificity_pp": d["specificity_pp"],
            "qualified": d["qualified"],
            "aggregates": agg,
            "forms": forms_summary,
        }
    return out


def main():
    runs, extra = inspect_runs()
    exp_csv = OUT_DIR / "experiment_inventory.csv"
    with exp_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(runs[0].keys()))
        w.writeheader()
        w.writerows(runs)

    c24_matrix = extract_c24_matrix()
    c28_summary = extract_c28_summary()

    llm_runs = [r for r in runs if r["scheduled_requests"] > 0]
    deep = {
        "git_head": git_out("rev-parse", "HEAD"),
        "git_origin_main": git_out("rev-parse", "origin/main"),
        "git_tag_cohort029": git_out("rev-parse", "cohort-029-v1.0.0^{}"),
        "total_commits": int(git_out("rev-list", "--count", "HEAD")),
        "total_run_entries": len(runs),
        "total_llm_runs": len(llm_runs),
        "total_scheduled_llm_requests": sum(r["scheduled_requests"] for r in llm_runs),
        "total_persisted_llm_responses": sum(r["persisted_raw_records"] for r in llm_runs),
        "c24_matrix": c24_matrix,
        "c28_summary": c28_summary,
        "sample_responses": extra["sample_responses"],
    }
    (OUT_DIR / "_extracted_summary.json").write_text(json.dumps(deep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(runs)} total entries ({len(llm_runs)} LLM runs) to {exp_csv}")
    print(f"Total scheduled LLM requests: {deep['total_scheduled_llm_requests']}")
    print(f"Total persisted LLM responses: {deep['total_persisted_llm_responses']}")
    print("Cohort 028 aggregates:", json.dumps(c28_summary, indent=2))


if __name__ == "__main__":
    main()
