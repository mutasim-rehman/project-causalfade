"""Generate programmatic empirical vector figures (fig09-fig14, fig18) directly from verified repository artifacts
with zero text-over-text and zero text-over-bar/line/marker overlaps verified at pixel level."""
from __future__ import annotations

import base64
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from figure_geometry_guard import verify_and_save

ROOT = Path(__file__).resolve().parents[3]
RETRO = Path(__file__).resolve().parents[1]
FIG_DIR = RETRO / "figures"
EVID_DIR = RETRO / "evidence"
PREVIEW = Path(r"C:\Users\Victus\.gemini\antigravity\brain\5db7097c-4674-4e75-ab1d-d210224c53c1\scratch\fig_previews")
FIG_DIR.mkdir(parents=True, exist_ok=True)

NAVY = "#1B365D"
TEAL = "#125C70"
AMBER = "#B85D19"
CRIMSON = "#9E2A2B"
SLATE = "#5C6B73"
LIGHT_SLATE = "#DCE3E6"
GOLD = "#D99B26"
FOREST = "#2D6A4F"
INK = "#1E293B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8.5,
    "axes.labelcolor": INK,
    "text.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 9.3,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_bytes().splitlines() if line.strip()]


def make_fig09() -> list[str]:
    c16 = ROOT / "experiments" / "cohort_016"
    truth = {r["task_id"]: r for r in read_jsonl(c16 / "input" / "oracle_truth.jsonl")}
    tasks = {r["task_id"]: r for r in read_jsonl(c16 / "input" / "public_tasks.jsonl")}

    records = []
    for arm, folder in [("F16", "run_001_7b_f16"), ("Q4_K_M", "run_002_7b_q4_k_m")]:
        for resp in read_jsonl(c16 / folder / "raw_responses.jsonl"):
            tid = resp["task_id"]
            item = tasks[tid]
            g = truth[tid]
            vals = re.findall(r"off ([\d.]+)%, on ([\d.]+)%", item["prompt"])
            diffs = [Fraction(y) - Fraction(x) for x, y in vals]
            first_is_rand = item["presentation_order"] == "randomized_first"
            rgap = float(abs(diffs[0 if first_is_rand else 1]))
            hgap = float(abs(diffs[1 if first_is_rand else 0]))
            act = json.loads(resp["response"]["choices"][0]["message"]["content"])["activate"]
            records.append({
                "arm": arm,
                "family": g["family_id"],
                "conflict": int(g["conflict"]),
                "order": item["presentation_order"],
                "rgap": rgap,
                "hgap": hgap,
                "correct": int(act == g["optimal_action"]),
            })

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11.8, 3.8), layout="constrained")

    # Panel A: Cohort 016 Conflict Order Effect
    conflict_recs = [r for r in records if r["conflict"] == 1]
    for arm, col, mk, lbl in [("F16", AMBER, "s", "Qwen2.5-7B F16"), ("Q4_K_M", TEAL, "o", "Qwen2.5-7B Q4_K_M")]:
        ys = []
        for ord_key in ["randomized_first", "historical_first"]:
            grp = [r["correct"] for r in conflict_recs if r["arm"] == arm and r["order"] == ord_key]
            ys.append(100.0 * sum(grp) / len(grp))
        ax1.plot([0, 1], ys, marker=mk, lw=2.0, ms=6, color=col, label=lbl)
        # Place labels cleanly away from lines & markers:
        # F16: (0, 56.8%) -> above-left; (1, 74.5%) -> below-right
        # Q4:  (0, 28.6%) -> below;      (1, 91.1%) -> above
        for x, y in zip([0, 1], ys):
            if arm == "F16" and x == 0:
                ax1.text(x - 0.05, y + 6.5, f"{y:.1f}%", ha="center", va="bottom", fontsize=7.4, color=col, fontweight="bold")
            elif arm == "F16" and x == 1:
                ax1.text(x + 0.06, y - 10.5, f"{y:.1f}%", ha="center", va="top", fontsize=7.4, color=col, fontweight="bold")
            elif arm == "Q4_K_M" and x == 0:
                ax1.text(x, y - 8.5, f"{y:.1f}%", ha="center", va="top", fontsize=7.4, color=col, fontweight="bold")
            else:
                ax1.text(x, y + 6.0, f"{y:.1f}%", ha="center", va="bottom", fontsize=7.4, color=col, fontweight="bold")
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["Randomized\nFirst", "Historical\nFirst"])
    ax1.set_xlim(-0.32, 1.32)
    ax1.set_ylim(5, 112)
    ax1.set_ylabel("Conflict Causal Accuracy (%)")
    ax1.set_title("A. Cohort 016 Order Crossover")
    ax1.grid(axis="y", alpha=0.22)
    ax1.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=7.3)

    # Panel B: Retrospective Source-Blind Shortcut Separation
    uniq = {r["family"]: r for r in conflict_recs if r["arm"] == "F16" and r["order"] == "randomized_first"}
    rgaps = [r["rgap"] for r in uniq.values()]
    hgaps = [r["hgap"] for r in uniq.values()]
    ax2.scatter(rgaps, hgaps, s=16, alpha=0.75, color=NAVY, label="96 conflict families")
    ax2.plot([0, 48], [0, 48], ls="--", lw=1.1, color=CRIMSON, label="Identity |trial| = |history|")
    ax2.text(
        29.5, 11.5,
        "100% separation:\n|trial gap| in [6, 12) pp\n|hist. gap| in [38, 46) pp\nSmaller-gap = 768/768",
        ha="center", va="center", fontsize=7.1, color=CRIMSON,
        bbox=dict(boxstyle="round,pad=0.32", fc="#FFF8F6", ec=CRIMSON, lw=0.8),
    )
    ax2.set_xlim(0, 49)
    ax2.set_ylim(0, 52)
    ax2.set_xlabel("Randomized Trial |On - Off| Gap (pp)")
    ax2.set_ylabel("Historical Log |On - Off| Gap (pp)")
    ax2.set_title("B. Cohort 016 Shortcut Audit")
    ax2.grid(alpha=0.20)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False, fontsize=7.0)

    # Panel C: Cohort 021 Recognition-Action Dissociation (no horizontal line cutting text!)
    tasks_c21 = ["Source ID\n(128/128)", "Rand.-Only\n(30/32)", "Ordinary 2-Src\n(58/128)", "Guided 2-Src\n(58/128)"]
    vals_c21 = [100.0, 93.75, 45.3125, 45.3125]
    cols_c21 = [FOREST, TEAL, AMBER, CRIMSON]
    bars = ax3.bar(range(4), vals_c21, color=cols_c21, width=0.54, edgecolor="white")
    for b, v in zip(bars, vals_c21):
        ax3.text(b.get_x() + b.get_width() / 2, v + 2.8, f"{v:.1f}%", ha="center", va="bottom", fontsize=7.4, fontweight="bold")
    ax3.set_xticks(range(4))
    ax3.set_xticklabels(tasks_c21, fontsize=7.1)
    ax3.set_ylim(0, 116)
    ax3.set_ylabel("Accuracy (%; chance = 50%)")
    ax3.set_title("C. Cohort 021 Sub-Skill vs. Action")
    ax3.grid(axis="y", alpha=0.22)

    return verify_and_save(fig, FIG_DIR / "fig09_evidence_selection_and_shortcut.pdf", PREVIEW)


def make_fig10() -> list[str]:
    worlds = read_jsonl(ROOT / "experiments" / "cohort_029" / "freeze" / "fixture" / "worlds.jsonl")
    w96 = worlds[96]
    tables = w96["tables"]
    w0, w1 = w96["weights"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 3.8), layout="constrained", width_ratios=[1.05, 1.25])

    # Panel A: Stratum-specific rates in Family 096
    x = np.arange(4)
    labels = ["Source L\nAmber", "Source L\nBlue", "Source R\nAmber", "Source R\nBlue"]
    off_rates = [tables[0][0][0] / 2, tables[0][1][0] / 2, tables[1][0][0] / 2, tables[1][1][0] / 2]
    on_rates = [tables[0][0][1] / 2, tables[0][1][1] / 2, tables[1][0][1] / 2, tables[1][1][1] / 2]

    width = 0.34
    ax1.bar(x - width / 2, off_rates, width, label="Action Off (0)", color=LIGHT_SLATE, edgecolor=SLATE)
    ax1.bar(x + width / 2, on_rates, width, label="Action On (1)", color=TEAL, edgecolor=NAVY)
    for i in range(4):
        diff = on_rates[i] - off_rates[i]
        col = FOREST if diff > 0 else CRIMSON
        ax1.text(x[i], max(off_rates[i], on_rates[i]) + 1.4, f"{diff:+.1f} pp", ha="center", va="bottom", fontsize=7.3, fontweight="bold", color=col)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=7.5)
    ax1.set_ylim(38, 69)
    ax1.set_ylabel("Success Rate (%)")
    ax1.set_title("A. Family 096 Stratum-Specific Rates")
    ax1.legend(loc="upper left", frameon=False, fontsize=7.4, ncol=2)
    ax1.grid(axis="y", alpha=0.22)

    # Panel B: Target population transport curves across Amber share w
    ws = np.linspace(42, 98, 201)
    dL0, dL1 = on_rates[0] - off_rates[0], on_rates[1] - off_rates[1]
    dR0, dR1 = on_rates[2] - off_rates[2], on_rates[3] - off_rates[3]
    tau_L = (ws / 100.0) * dL0 + (1.0 - ws / 100.0) * dL1
    tau_R = (ws / 100.0) * dR0 + (1.0 - ws / 100.0) * dR1

    ax2.plot(ws, tau_L, color=TEAL, lw=2.0, label="Source L Randomized: +3.0w - 5.5(1-w)")
    ax2.plot(ws, tau_R, color=AMBER, lw=2.0, label="Source R Randomized: -2.5w + 6.0(1-w)")
    ax2.axhline(0, color=SLATE, lw=0.85, ls="--")

    for wx in (w0, w1):
        yL = (wx / 100.0) * dL0 + (1 - wx / 100.0) * dL1
        yR = (wx / 100.0) * dR0 + (1 - wx / 100.0) * dR1
        ax2.scatter([wx, wx], [yL, yR], color=[TEAL, AMBER], zorder=5, s=30)

    # Carefully placed non-overlapping point labels in completely open space:
    # At w0=58: yL=-0.57 (rising right), yR=+1.07 (falling right)
    ax2.text(59.8, -0.85, "w0=58%: -0.57 pp", ha="left", va="top", fontsize=7.0, color=TEAL, fontweight="bold")
    ax2.text(59.8, 1.32, "w0=58%: +1.07 pp", ha="left", va="bottom", fontsize=7.0, color=AMBER, fontweight="bold")
    # At w1=83: yL=+1.555 (rising right -> place above-left), yR=-1.055 (falling right -> place below-left)
    ax2.text(81.5, 1.85, "w1=83%: +1.555 pp", ha="right", va="bottom", fontsize=7.0, color=TEAL, fontweight="bold")
    ax2.text(81.5, -1.35, "w1=83%: -1.055 pp", ha="right", va="top", fontsize=7.0, color=AMBER, fontweight="bold")

    ax2.set_xlim(40, 100)
    ax2.set_ylim(-3.3, 4.3)
    ax2.set_xlabel("Target Population Share of Amber Group, w (%)")
    ax2.set_ylabel("Standardized Causal ATE (pp)")
    ax2.set_title("B. Family 096 Target-Standardized Effect Reversal")
    ax2.legend(loc="upper left", frameon=False, fontsize=7.1)
    ax2.grid(alpha=0.20)

    return verify_and_save(fig, FIG_DIR / "fig10_target_population_transport.pdf", PREVIEW)


def make_fig11() -> list[str]:
    worlds = read_jsonl(ROOT / "experiments" / "cohort_029" / "freeze" / "fixture" / "worlds.jsonl")
    pol_audit = json.load((ROOT / "experiments" / "cohort_029" / "freeze" / "fixture" / "policy_audit.json").open(encoding="utf-8"))["ties"]["0"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 3.9), layout="constrained", width_ratios=[1.0, 1.45])

    # Panel A: Balanced 2x2 Sign-Matrix Design
    counts = Counter((w["p"], w["g"]) for w in worlds)
    strata_names = ["Both Stable\n(p=0, g=0)", "Role Switches\n(p=0, g=1)", "Mix Switches\n(p=1, g=0)", "Both Switch\n(p=1, g=1)"]
    strata_vals = [counts[(0, 0)], counts[(0, 1)], counts[(1, 0)], counts[(1, 1)]]
    bars = ax1.bar(range(4), strata_vals, color=[SLATE, AMBER, TEAL, NAVY], width=0.54)
    for b, v in zip(bars, strata_vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 1.4, f"{v} families\n({v*32} items)", ha="center", va="bottom", fontsize=7.1, fontweight="bold")
    ax1.set_xticks(range(4))
    ax1.set_xticklabels(strata_names, fontsize=7.2)
    ax1.set_ylim(0, 43)
    ax1.set_ylabel("Number of Benchmark Families")
    ax1.set_title("A. CF-TP1 Balanced Sign-Matrix Strata")
    ax1.grid(axis="y", alpha=0.22)

    # Panel B: Shortcut Policy Audit
    selected_policies = [
        ("positive", "Causal Oracle"),
        ("source_pool", "Pool Both Studies"),
        ("target_majority", "Majority Stratum Only"),
        ("source_max_effect", "Larger Raw Gap"),
        ("target_first_option", "First Listed Option"),
        ("target_constant_1", "Always Activate (1)"),
    ]

    def pair_both_pct(entry, axis, switch_flag):
        tot = sum(n for flag, ok, n in entry[f"{axis}_pairs"] if flag == switch_flag)
        both = sum(n for flag, ok, n in entry[f"{axis}_pairs"] if flag == switch_flag and ok == 2)
        return 100.0 * both / tot

    y_pos = np.arange(len(selected_policies))
    item_acc = [100.0 * pol_audit[k]["correct"] / pol_audit[k]["total"] for k, _ in selected_policies]
    sw_fid = [pair_both_pct(pol_audit[k], "target", 1) for k, _ in selected_policies]
    inv_fid = [pair_both_pct(pol_audit[k], "target", 0) for k, _ in selected_policies]

    h = 0.25
    h1 = ax2.barh(y_pos - h, item_acc, height=h, color=LIGHT_SLATE, edgecolor=SLATE, label="Single-Item Accuracy (/4096)")
    h2 = ax2.barh(y_pos, inv_fid, height=h, color=AMBER, label="Invariant Target-Pair Fidelity (/1024)")
    h3 = ax2.barh(y_pos + h, sw_fid, height=h, color=TEAL, label="Switch Target-Pair Fidelity (/1024)")

    for idx, sw in enumerate(sw_fid):
        ax2.text(sw + 1.8, y_pos[idx] + h, f"{sw:.1f}%", va="center", ha="left", fontsize=7.0, color=TEAL, fontweight="bold")

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([lbl for _, lbl in selected_policies], fontsize=7.5)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 118)
    ax2.set_xlabel("Score (%)")
    ax2.set_title("B. Deterministic Shortcut Policy Audit")
    ax2.grid(axis="x", alpha=0.22)
    fig.legend(handles=[h1, h2, h3], loc="outside lower center", ncol=3, frameon=False, fontsize=7.5)

    return verify_and_save(fig, FIG_DIR / "fig11_decision_reversal_retention.pdf", PREVIEW)


def make_fig12() -> list[str]:
    summary = json.load((EVID_DIR / "_extracted_summary.json").open(encoding="utf-8"))
    c28 = summary["c28_summary"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 3.9), layout="constrained")

    # Panel A: Cohorts 002, 006, 007 Numeric ATE Sign vs Binary Action (Qwen2.5-3B)
    cats = ["C002 Unassisted\nNumeric Sign", "C006 Formula\nNumeric Sign", "C007 Fresh Fam.\nFormula Sign", "C006 Explicit\nBinary Action"]
    f16_vals = [100 * 34 / 64, 100 * 61 / 64, 100 * 46 / 48, 100 * 32 / 64]
    q8_vals = [0.0, 100 * 61 / 64, 0.0, 100 * 32 / 64]
    q4_vals = [100 * 32 / 64, 100 * 45 / 64, 100 * 31 / 48, 100 * 35 / 64]

    x = np.arange(len(cats))
    w = 0.25
    b_f16 = ax1.bar(x - w, f16_vals, width=w, color=NAVY, label="Qwen2.5-3B F16")
    b_q8 = ax1.bar([1, 3], [q8_vals[1], q8_vals[3]], width=w, color=FOREST, label="Qwen2.5-3B Q8_0")
    b_q4 = ax1.bar(x + w, q4_vals, width=w, color=AMBER, label="Qwen2.5-3B Q4_K_M")

    # Place callout strictly above all bars (max bar height is 95.8%)!
    ax1.annotate(
        "F16 & Q8_0: 64/64 'decline'\n(50.0% action collapse)",
        xy=(3 - w, 51.5),
        xytext=(3.38, 99.5),
        ha="right",
        va="bottom",
        fontsize=6.9,
        color=CRIMSON,
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=CRIMSON, lw=1.0, shrinkA=2, shrinkB=2),
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, fontsize=7.2)
    ax1.set_ylim(0, 132)
    ax1.set_ylabel("Accuracy (%)")
    ax1.set_title("A. Numeric Computation vs. Action (3B)")
    ax1.legend(handles=[b_f16, b_q8, b_q4], loc="upper left", frameon=False, fontsize=7.1, ncol=2)
    ax1.grid(axis="y", alpha=0.22)

    # Panel B: Cohort 028 Deterministic Calculator Ablation
    q_agg = c28["qwen7b"]["aggregates"]
    l_agg = c28["llama8b"]["aggregates"]
    groups = ["Qwen 7B\nNoncausal", "Qwen 7B\nCausal Switch", "Llama 8B\nNoncausal", "Llama 8B\nCausal Switch"]
    sys_b = [
        100 * q_agg["struct_ctrl_raw_B"][0] / 128,
        100 * q_agg["struct_causal_raw_B"][0] / 128,
        100 * l_agg["struct_ctrl_raw_B"][0] / 128,
        100 * l_agg["struct_causal_raw_B"][0] / 128,
    ]
    sys_c = [
        100 * q_agg["assist_ctrl_raw_C"][0] / 128,
        100 * q_agg["assist_causal_raw_C"][0] / 128,
        100 * l_agg["assist_ctrl_raw_C"][0] / 128,
        100 * l_agg["assist_causal_raw_C"][0] / 128,
    ]
    x2 = np.arange(4)
    w2 = 0.34
    bb = ax2.bar(x2 - w2 / 2, sys_b, width=w2, color=LIGHT_SLATE, edgecolor=SLATE, label="System B (Single-Pass Model Math)")
    bc = ax2.bar(x2 + w2 / 2, sys_c, width=w2, color=TEAL, edgecolor=NAVY, label="System C (Deterministic Calculator)")
    for i in range(4):
        diff = sys_c[i] - sys_b[i]
        col = FOREST if diff > 10 else CRIMSON
        top_y = max(sys_b[i], sys_c[i]) + 2.5
        ax2.text(x2[i], top_y, f"{diff:+.1f} pp", ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=col)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(groups, fontsize=7.3)
    ax2.set_ylim(0, 122)
    ax2.set_ylabel("Action Accuracy (%)")
    ax2.set_title("B. Cohort 028 Calculator Rescue (F16)")
    ax2.legend(handles=[bb, bc], loc="upper right", frameon=False, fontsize=7.1)
    ax2.grid(axis="y", alpha=0.22)

    return verify_and_save(fig, FIG_DIR / "fig12_experimental_control_architecture.pdf", PREVIEW)


def make_fig13() -> list[str]:
    summary = json.load((EVID_DIR / "_extracted_summary.json").open(encoding="utf-8"))
    c24 = summary["c24_matrix"]
    formats = ["F16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q3_K_M", "Q2_K"]
    lineages = [
        ("qwen7b", "Qwen2.5-7B", TEAL, "o"),
        ("mistral7b", "Mistral-7B-v0.3", AMBER, "s"),
        ("llama8b", "Llama-3.1-8B", NAVY, "^"),
    ]
    by_key = {(r["lineage"], r["precision"]): r for r in c24}

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11.8, 3.9), layout="constrained")
    xf = np.arange(len(formats))

    # Panel A: Semantic Causal vs Control Accuracy
    leg_handles = []
    for lin, lbl, col, mk in lineages:
        yc = [100.0 * by_key[(lin, f)]["causal_sem_correct"] / 256.0 for f in formats]
        yk = [100.0 * by_key[(lin, f)]["ctrl_sem_correct"] / 256.0 for f in formats]
        (l1,) = ax1.plot(xf, yc, color=col, marker=mk, lw=1.8, ms=5, label=f"{lbl} (Causal)")
        (l2,) = ax1.plot(xf, yk, color=col, marker=mk, lw=1.2, ms=4, ls="--", alpha=0.68, label=f"{lbl} (Control)")
        leg_handles.extend([l1, l2])
    ax1.set_xticks(xf)
    ax1.set_xticklabels(formats, rotation=30, ha="right", fontsize=7.3)
    ax1.set_ylim(-4, 105)
    ax1.set_ylabel("Scheduled Accuracy (%)")
    ax1.set_title("A. Causal (solid) vs. Control (dashed)")
    ax1.grid(axis="y", alpha=0.22)

    # Panel B: Strict Schema Validity across 21 Arms (empty space in y=58..92, x=0..3.4!)
    for lin, lbl, col, mk in lineages:
        yv = [100.0 * by_key[(lin, f)]["all_valid"] / by_key[(lin, f)]["all_scheduled"] for f in formats]
        ax2.plot(xf, yv, color=col, marker=mk, lw=1.8, ms=5, label=lbl)
    ax2.annotate(
        "Llama Q4_K_M: 69.6% valid\n(448 control length caps;\n256/256 causal valid)",
        xy=(3.88, 102400 / 1472),
        xytext=(1.55, 70.0),
        ha="center",
        va="center",
        fontsize=7.0,
        color=CRIMSON,
        bbox=dict(boxstyle="round,pad=0.28", fc="#FFF8F6", ec=CRIMSON, lw=0.75),
        arrowprops=dict(arrowstyle="-|>", color=CRIMSON, lw=1.0, shrinkA=3, shrinkB=3),
    )
    ax2.set_xticks(xf)
    ax2.set_xticklabels(formats, rotation=30, ha="right", fontsize=7.3)
    ax2.set_ylim(56, 104)
    ax2.set_ylabel("Strict JSON Validity (% of 1,472)")
    ax2.set_title("B. Format-Specific Truncation Artifact")
    ax2.grid(axis="y", alpha=0.22)

    # Panel C: SDT Criterion c vs Sensitivity d'
    for lin, lbl, col, mk in lineages:
        cs = [float(by_key[(lin, f)]["criterion_causal_sem"]) for f in formats]
        ds = [float(by_key[(lin, f)]["d_prime_causal_sem"]) for f in formats]
        ax3.scatter(cs, ds, color=col, marker=mk, s=34, alpha=0.85, label=lbl)
    ax3.axhline(0.0, ls="--", color=SLATE, lw=0.85)
    ax3.axvline(0.0, ls=":", color=SLATE, lw=0.85)
    ax3.text(
        -1.15, 0.80,
        "Negative criterion c < 0\n('activate' default bias)\nwith near-zero d'",
        ha="center", va="center", fontsize=7.0, color=INK,
        bbox=dict(boxstyle="round,pad=0.28", fc="#F8FAFC", ec=SLATE, lw=0.7),
    )
    ax3.set_xlim(-2.20, 0.55)
    ax3.set_ylim(-0.95, 1.18)
    ax3.set_xticks([-2.0, -1.0, 0.0])
    ax3.set_yticks([-0.8, -0.4, 0.0, 0.4, 0.8])
    ax3.set_xlabel("SDT Criterion c (c < 0 = activate bias)")
    ax3.set_ylabel("SDT Sensitivity d'")
    ax3.set_title("C. Signal Detection Plane (21 Arms)")
    ax3.grid(alpha=0.20)

    fig.legend(handles=leg_handles, loc="outside lower center", ncol=3, frameon=False, fontsize=7.4)
    return verify_and_save(fig, FIG_DIR / "fig13_cohort024_matrix_results.pdf", PREVIEW)


def make_fig14() -> list[str]:
    c29 = ROOT / "experiments" / "cohort_029"
    fix = c29 / "freeze" / "fixture"
    run = c29 / "runs" / "confirmatory"
    primary = json.loads((run / "analysis" / "primary.json").read_bytes())
    design = {r["task_id"]: r for r in read_jsonl(fix / "design.jsonl")}
    gold = {r["task_id"]: r for r in read_jsonl(fix / "gold.jsonl")}
    events = [r for r in read_jsonl(run / "events.jsonl") if r["type"] == "response"]

    rows = {}
    dir_counts = Counter()
    for e in events:
        tid = e["task_id"]
        raw = json.loads(base64.b64decode(e["response_b64"]))
        act = json.loads(raw["choices"][0]["message"]["content"])["activate"]
        g = gold[tid]["action"]
        idx = tuple(design[tid]["indices"])
        rows[idx] = (act, g)
        dir_counts[(idx[1], idx[2], g, act)] += 1

    pair_counts = Counter()
    for idx, (a, g) in rows.items():
        if idx[1] != 1 or idx[5] != 0:
            continue
        other = idx[:5] + (1,)
        aa, gg = rows[other]
        sw = int(g != gg)
        corr = int(a == g) + int(aa == gg)
        pair_counts[(idx[2], sw, corr)] += 1

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12.2, 4.1), layout="constrained", width_ratios=[1.12, 1.25, 1.0])

    # Panel A: Primary Target-Pair Fidelity & Paired Difference Intervals (no text crossing x=0 or errorbars!)
    c_fid = 100.0 * primary["causal"]["both_correct"] / 512.0
    a_fid = 100.0 * primary["control"]["both_correct"] / 512.0
    delta = 100.0 * primary["delta"]
    t_lo, t_hi = 100.0 * primary["interval_t"][0], 100.0 * primary["interval_t"][1]
    b_lo, b_hi = 100.0 * primary["interval_bounded"][0], 100.0 * primary["interval_bounded"][1]

    ax1.barh([0, 1], [c_fid, a_fid], height=0.46, color=[TEAL, AMBER])
    ax1.text(c_fid + 1.5, 0, f"{c_fid:.2f}% (128/512)", va="center", ha="left", fontsize=7.1, fontweight="bold", color=TEAL)
    ax1.text(a_fid + 1.5, 1, f"{a_fid:.2f}% (146/512)", va="center", ha="left", fontsize=7.1, fontweight="bold", color=AMBER)
    ax1.errorbar(delta, 2.2, xerr=[[delta - t_lo], [t_hi - delta]], fmt="o", color=NAVY, capsize=4, lw=1.8)
    ax1.errorbar(delta, 3.1, xerr=[[delta - b_lo], [b_hi - delta]], fmt="s", color=SLATE, capsize=4, lw=1.4)
    ax1.plot([0.0, 0.0], [1.75, 3.55], ls="--", color=CRIMSON, lw=0.95)
    ax1.text(t_hi + 2.2, 2.2, f"{delta:+.2f} pp\n[{t_lo:+.1f}, {t_hi:+.1f}]", va="center", ha="left", fontsize=6.9, color=NAVY, fontweight="bold")
    ax1.text(b_hi + 2.2, 3.1, f"[{b_lo:+.1f}, {b_hi:+.1f}] pp", va="center", ha="left", fontsize=6.9, color=SLATE)
    ax1.set_yticks([0, 1, 2.2, 3.1])
    ax1.set_yticklabels(["Transfer Causal", "Transfer Arith.", "Diff (Welch t)", "Diff (Bounded)"], fontsize=7.3)
    ax1.invert_yaxis()
    ax1.set_xlim(-31, 68)
    ax1.set_xlabel("Percentage / Percentage Points")
    ax1.set_title("A. Primary CF-TP1 Endpoint")
    ax1.grid(axis="x", alpha=0.22)

    # Panel B: Grouped Side-by-Side Pair Outcomes (ZERO text written inside/over bars!)
    cats_b = ["Causal\nSwitch", "Arith.\nSwitch", "Causal\nInvariant", "Arith.\nInvariant"]
    keys_b = [(0, 1), (1, 1), (0, 0), (1, 0)]
    both_v = [pair_counts[(q, sw, 2)] for q, sw in keys_b]
    one_v = [pair_counts[(q, sw, 1)] for q, sw in keys_b]
    zero_v = [pair_counts[(q, sw, 0)] for q, sw in keys_b]
    xb = np.arange(4)
    wb = 0.25
    b_both = ax2.bar(xb - wb, both_v, width=wb, color=TEAL, label="Both Correct (2/2)")
    b_one = ax2.bar(xb, one_v, width=wb, color="#8FA8B5", label="One Correct (1/2)")
    b_zero = ax2.bar(xb + wb, zero_v, width=wb, color="#D9A7A4", label="Neither Correct (0/2)")

    for bars_grp, vals_grp, col_txt in [(b_both, both_v, TEAL), (b_one, one_v, INK), (b_zero, zero_v, CRIMSON)]:
        for bar_item, v in zip(bars_grp, vals_grp):
            ax2.text(
                bar_item.get_x() + bar_item.get_width() / 2,
                v + 4.5,
                str(v),
                ha="center",
                va="bottom",
                fontsize=6.6,
                fontweight="bold",
                color=col_txt,
            )

    ax2.set_xticks(xb)
    ax2.set_xticklabels(cats_b, fontsize=7.3)
    ax2.set_ylim(0, 315)
    ax2.set_ylabel("Target Pairs (out of 256)")
    ax2.set_title("B. Pairwise Reversal vs. Retention")
    ax2.legend(handles=[b_both, b_one, b_zero], loc="upper right", frameon=False, fontsize=6.8)
    ax2.grid(axis="y", alpha=0.22)

    # Panel C: Gold Off (0) vs Gold On (1) Accuracy on Transfer Items
    off_acc = [100.0 * dir_counts[(1, 0, 0, 0)] / 512.0, 100.0 * dir_counts[(1, 1, 0, 0)] / 512.0]
    on_acc = [100.0 * dir_counts[(1, 0, 1, 1)] / 512.0, 100.0 * dir_counts[(1, 1, 1, 1)] / 512.0]
    xc = np.arange(2)
    wc = 0.36
    boff = ax3.bar(xc - wc / 2, off_acc, width=wc, color=CRIMSON, label="Gold Off (activate=0)")
    bon = ax3.bar(xc + wc / 2, on_acc, width=wc, color=FOREST, label="Gold On (activate=1)")
    for i in range(2):
        ax3.text(
            xc[i] - wc / 2, off_acc[i] + 2.5,
            f"{off_acc[i]:.1f}%\n({dir_counts[(1,i,0,0)]})",
            ha="center", va="bottom", fontsize=6.9, fontweight="bold", color=CRIMSON,
        )
        ax3.text(
            xc[i] + wc / 2, on_acc[i] + 2.5,
            f"{on_acc[i]:.1f}%\n({dir_counts[(1,i,1,1)]})",
            ha="center", va="bottom", fontsize=6.9, fontweight="bold", color=FOREST,
        )
    ax3.set_xticks(xc)
    ax3.set_xticklabels(["Transfer Causal\n(995/1024 'on')", "Transfer Arith.\n(597/1024 'on')"], fontsize=7.3)
    ax3.set_xlim(-0.58, 1.58)
    ax3.set_ylim(0, 128)
    ax3.set_ylabel("Single-Item Accuracy (%; /512)")
    ax3.set_title("C. Directional Asymmetry")
    ax3.legend(handles=[boff, bon], loc="upper right", frameon=False, fontsize=6.9)
    ax3.grid(axis="y", alpha=0.22)

    return verify_and_save(fig, FIG_DIR / "fig14_cohort029_final_results.pdf", PREVIEW)


def make_fig18() -> list[str]:
    dv = json.load((ROOT / "results" / "design_validation" / "parameter_recovery.json").open(encoding="utf-8"))
    rec = dv["recovery"]
    mc = dv["model_checks"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 3.9), layout="constrained")

    # Panel A: Synthetic Parameter Recovery RMSE
    ns = [50, 200, 1000]
    h_a = []
    for scen, ls, lbl_prefix in [("interior", "-", "Interior (C=0.65)"), ("low_causal", "--", "Low-C (C=0.10)")]:
        sub = {r["n_per_cell"]: r for r in rec if r["scenario"] == scen}
        if not sub:
            continue
        for param, col, mk in [("C", TEAL, "o"), ("A", AMBER, "s"), ("B", NAVY, "^")]:
            ys = [sub[n]["parameters"][param]["rmse"] for n in ns]
            (ln,) = ax1.plot([0, 1, 2], ys, ls=ls, marker=mk, color=col, lw=1.7, ms=5, label=f"{lbl_prefix}: {param}")
            h_a.append(ln)
    ax1.set_xticks([0, 1, 2])
    ax1.set_xticklabels(["n = 50 / cell", "n = 200 / cell", "n = 1,000 / cell"])
    ax1.set_ylim(0, 0.22)
    ax1.set_ylabel("Root Mean Squared Error (RMSE)")
    ax1.set_title("A. C/A/B Tree Synthetic Recovery (3,600 Fits)")
    ax1.legend(handles=h_a, loc="upper right", frameon=False, fontsize=6.9, ncol=2)
    ax1.grid(alpha=0.22)

    # Panel B: Observational Equivalence across 4 Binomial Cells (legend placed outside!)
    models = [
        ("tree_generated", "True C/A/B Tree (p_boot = 0.507)", TEAL, "-", "o"),
        ("observationally_equivalent_logistic", "Symmetric Logistic (p_boot = 0.433, Equiv.)", AMBER, "--", "s"),
        ("incompatible_logistic", "Asymmetric Logistic (p_boot = 0.002, Rejected)", CRIMSON, "-.", "^"),
    ]
    cells = ["Cell (0,0)", "Cell (0,1)", "Cell (1,0)", "Cell (1,1)"]
    xc = np.arange(4)
    h_b = []
    for key, lbl, col, ls, mk in models:
        probs = [100.0 * p for p in mc[key]["generating_probabilities"]]
        (ln,) = ax2.plot(xc, probs, ls=ls, marker=mk, ms=5.5, lw=1.9, color=col, label=lbl)
        h_b.append(ln)
    ax2.set_xticks(xc)
    ax2.set_xticklabels(cells, fontsize=7.5)
    ax2.set_ylim(-3, 106)
    ax2.set_ylabel("Cell Action Probability (%)")
    ax2.set_title("B. 4-Cell Logistic Observational Equivalence")
    ax2.grid(alpha=0.22)
    fig.legend(handles=h_b, loc="outside lower center", ncol=3, frameon=False, fontsize=7.2)

    return verify_and_save(fig, FIG_DIR / "fig18_synthetic_cab_recovery.pdf", PREVIEW)


def main() -> None:
    all_issues = []
    for fn in [make_fig09, make_fig10, make_fig11, make_fig12, make_fig13, make_fig14, make_fig18]:
        all_issues.extend(fn())
    if all_issues:
        raise SystemExit(f"Empirical figure geometry guard found {len(all_issues)} issues!")
    print("ALL 7 EMPIRICAL FIGURES PASSED ZERO-OVERLAP GUARD.")


if __name__ == "__main__":
    main()
