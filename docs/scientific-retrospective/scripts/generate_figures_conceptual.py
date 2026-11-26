"""Generate programmatic architectural, chronological, matrix, and causal-graph figures (Figs 1-8, 15-17)
with zero text-over-text and zero text-over-element overlaps verified at pixel level."""
from __future__ import annotations

import csv
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
import numpy as np

from figure_geometry_guard import verify_and_save

BASE = Path(__file__).resolve().parents[1]
EVID = BASE / "evidence"
FIGS = BASE / "figures"
PREVIEW = Path(r"C:\Users\Victus\.gemini\antigravity\brain\5db7097c-4674-4e75-ab1d-d210224c53c1\scratch\fig_previews")

NAVY = "#143642"
TEAL = "#0F6E8C"
RUST = "#A84A24"
GOLD = "#9A6B00"
SLATE = "#4A5859"
LIGHT_BG = "#F4F6F7"
BORDER = "#B0BEC5"
GREEN = "#2E6F40"
RED = "#9E2A2B"
PURPLE = "#5C4D7D"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8.5,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "axes.labelsize": 8.5,
    "text.color": "#1C2526",
    "axes.labelcolor": "#1C2526",
    "xtick.color": "#1C2526",
    "ytick.color": "#1C2526",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def draw_box(
    ax,
    pairs: list,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    fc: str = "white",
    ec: str = NAVY,
    lw: float = 1.1,
    fontsize: float = 7.2,
    tc: str = "#1C2526",
    weight: str = "normal",
    radius: float = 0.03,
    pad: float = 0.01,
):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle=f"round,pad={pad},rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        zorder=3,
    )
    ax.add_patch(patch)
    txt = ax.text(
        x, y, text, ha="center", va="center", fontsize=fontsize, color=tc, fontweight=weight, zorder=4
    )
    pairs.append((patch, txt))
    return patch, txt


def arrow(ax, x1, y1, x2, y2, color=SLATE, lw=1.1, ls="-", rad=0.0):
    conn = f"arc3,rad={rad}"
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>", color=color, lw=lw, linestyle=ls, connectionstyle=conn, shrinkA=2, shrinkB=2
        ),
        zorder=2,
    )


def fig01_research_timeline() -> list[str]:
    days = [
        ("Oct 28", 0, "Lit Review\n(14 papers)"),
        ("Nov 01", 0, "SCM + C/A/B\n3,600 sims"),
        ("Nov 07", 0, "SSD & GGUF\n20 weights"),
        ("Nov 10", 662, "Cohorts 001-008p\nQ2 fail, sign split"),
        ("Nov 12", 2816, "Cohorts 008c-016\n96-fam Q4 order"),
        ("Nov 13", 1536, "Cohort 017\n14B boundary"),
        ("Nov 14", 1920, "Cohorts 018-021\n128/128 vs 58/128"),
        ("Nov 15", 0, "Readiness\nAudit"),
        ("Nov 16", 2048, "Cohorts 022-023\nMistral & controls"),
        ("Nov 18", 30912, "Cohorts 024-025\n21-arm matrix"),
        ("Nov 19", 1456, "Cohorts 025.1-027\nGraph-switch 0/8"),
        ("Nov 23", 2560, "Cohort 028\nCalc replay stop"),
        ("Nov 25", 4096, "Cohort 029\nCF-TP1 4,096 calls"),
        ("Nov 26", 0, "v1.0.0 Release\n& Manuscript"),
    ]
    labels = [d[0] for d in days]
    counts = [d[1] for d in days]
    cum = np.cumsum(counts)
    pairs = []

    fig, (ax1, ax2, ax3) = plt.subplots(
        3, 1, figsize=(11.8, 7.2), gridspec_kw={"height_ratios": [1.35, 1.0, 0.85]}, layout="constrained"
    )
    x = np.arange(len(days))

    # Panel A: Milestone swimlane
    ax1.set_xlim(-0.85, len(days) - 0.15)
    ax1.set_ylim(-1.45, 1.45)
    ax1.axhline(0, color=NAVY, lw=1.8, zorder=1)
    ax1.axis("off")
    ax1.set_title(
        "A   Chronological Research Trajectory and Key Scientific Turning Points (28 Oct – 26 Nov 2026)",
        loc="left",
    )

    phase_colors = [SLATE, SLATE, SLATE, RUST, TEAL, PURPLE, TEAL, GOLD, TEAL, NAVY, RUST, RUST, GREEN, GREEN]
    for i, (dt, _, note) in enumerate(days):
        up = i % 2 == 0
        y_box = 0.86 if up else -0.86
        box_h = 0.64
        stem_end = y_box - (box_h / 2 + 0.03) if up else y_box + (box_h / 2 + 0.03)
        stem_start = 0.09 if up else -0.09
        ax1.plot([i, i], [stem_start, stem_end], color=phase_colors[i], lw=1.2, zorder=2)
        ax1.scatter([i], [0], s=38, color=phase_colors[i], edgecolor="white", linewidth=1.0, zorder=5)
        ax1.text(
            i,
            -0.24 if up else 0.24,
            dt,
            ha="center",
            va="center",
            fontsize=7.0,
            fontweight="bold",
            color=NAVY,
        )
        draw_box(
            ax1,
            pairs,
            i,
            y_box,
            1.52,
            box_h,
            note,
            fc=LIGHT_BG,
            ec=phase_colors[i],
            lw=1.1,
            fontsize=6.5,
            radius=0.04,
        )

    # Panel B: Persisted LLM responses per active wave (no crossing line!)
    ax2.bar(x, counts, color=TEAL, alpha=0.88, width=0.54)
    ax2.set_yscale("symlog", linthresh=100)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=7.6)
    ax2.set_ylabel("Wave Responses\n(symlog scale)")
    ax2.set_ylim(0, 260000)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", alpha=0.22, linestyle="--")
    ax2.set_title("B   Persisted LLM Inference Volume per Collection Wave", loc="left")
    for i, c in enumerate(counts):
        if c > 0:
            ax2.text(i, c * 1.45, f"{c:,}", ha="center", va="bottom", fontsize=6.9, fontweight="bold", color=NAVY)

    # Panel C: Cumulative persisted responses in dedicated clean panel
    ax3.plot(x, cum, color=RUST, marker="o", ms=4.5, lw=1.9)
    ax3.fill_between(x, 0, cum, color=RUST, alpha=0.10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels, rotation=22, ha="right", fontsize=7.6)
    ax3.set_ylabel("Cumulative\nResponses")
    ax3.set_ylim(-2500, 58000)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    ax3.grid(axis="y", alpha=0.22, linestyle="--")
    ax3.set_title("C   Cumulative Persisted Raw LLM Responses (Final Total = 48,170 / 48,208 Scheduled)", loc="left")
    ax3.text(13, 48170 + 3500, "48,170", ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=RUST)

    return verify_and_save(fig, FIGS / "fig01_research_timeline.pdf", PREVIEW, pairs)


def fig02_question_evolution() -> list[str]:
    pairs = []
    fig, ax = plt.subplots(figsize=(11.6, 6.4), layout="constrained")
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 6.8)
    ax.axis("off")
    ax.set_title("Evolution of the Central Research Question Across Five Epistemic Stages", loc="left", pad=8)

    stages = [
        (
            5.85,
            "Stage 1 · Conception & Initial Pilots (28 Oct – 10 Nov · DV, Cohorts 001–007)",
            "RQ1: Does aggressive post-training quantization selectively increase reliance on misleading observational associations (Delta(p) > 0)?",
            "Transition catalyst: 3B Q2_K collapsed (0/64); 3B/7B F16 showed 97% activate bias; C/A/B tree failed additivity (-43.75 pp).",
            TEAL,
        ),
        (
            4.55,
            "Stage 2 · Presentation & Order Sensitivity (10 Nov – 13 Nov · Cohorts 008–017)",
            "RQ2: Does compression alter preference for trial vs. historical evidence or induce study-order susceptibility?",
            "Transition catalyst: +62.5 pp 7B Q4 order shift confirmed (016), but aligned items shifted and 14B failed to generalize (017).",
            NAVY,
        ),
        (
            3.25,
            "Stage 3 · Component Dissociation & Construct Validity (13 Nov – 18 Nov · Cohorts 018–025)",
            "RQ3: When an LLM identifies the governing trial source (100%), what blocks acting on it across controls and lineages?",
            "Transition catalyst: Harmful-direction controls failed (<75%), Mistral picked 1st option (256/256), and 016 had a gap shortcut.",
            PURPLE,
        ),
        (
            1.95,
            "Stage 4 · Structural Graph-Switch & Calculator Assistance (19 Nov – 23 Nov · Cohorts 025.1–028)",
            "RQ4: Holding P(W,X,Y) exact-rational identical, can F16 models select confounder vs. mediator rules with a calculator?",
            "Transition catalyst: Switch fidelity was 0/8 across 4 F16 models (027); calculator rescued controls (+54.7 pp), not causal (+2.3 pp).",
            RUST,
        ),
        (
            0.65,
            "Stage 5 · Final Prospective Instrument & Case Study (23 Nov – 26 Nov · Cohort 029 / Manuscript)",
            "RQ5 (CF-TP1): Which decision changes reflect causal provenance and target-population transport vs. matched scorecard math?",
            "Outcome: Delta = -3.52 pp (95% CI [-7.77, +0.74], inconclusive); pairs separated 995/1024 causal bias from 45/256 arith flips.",
            GREEN,
        ),
    ]

    for idx, (y, hdr, qtxt, cat, col) in enumerate(stages):
        left_txt = hdr + "\n" + textwrap.fill(qtxt, width=78)
        right_txt = textwrap.fill(cat, width=48)
        draw_box(ax, pairs, 3.65, y, 6.9, 0.96, left_txt, fc="white", ec=col, lw=1.4, fontsize=6.9, radius=0.04)
        draw_box(
            ax, pairs, 9.65, y, 4.3, 0.96, right_txt, fc=LIGHT_BG, ec=BORDER, lw=1.0, fontsize=6.6, tc="#2B383A", radius=0.04
        )
        arrow(ax, 7.14, y, 7.46, y, color=col, lw=1.2)
        if idx < len(stages) - 1:
            arrow(ax, 3.65, y - 0.51, 3.65, stages[idx + 1][0] + 0.51, color=SLATE, lw=1.3)

    return verify_and_save(fig, FIGS / "fig02_question_evolution.pdf", PREVIEW, pairs)


def fig03_cohort_dependency_graph() -> list[str]:
    pairs = []
    fig, ax = plt.subplots(figsize=(12.2, 7.4), layout="constrained")
    ax.set_xlim(0, 13.0)
    ax.set_ylim(-0.3, 8.2)
    ax.axis("off")
    ax.set_title("Complete Cohort Dependency and Experimental Genealogy Graph (DV and Cohorts 001–029)", loc="left")

    bw, bh = 1.24, 0.68
    nodes = {
        "DV": (1.0, 7.3, "DV\nSim+CAB", SLATE),
        "001": (2.7, 7.3, "001\n3B Direct", TEAL),
        "004": (4.4, 7.3, "004\n7B Screen*", RUST),
        "003": (2.7, 5.9, "003\nQ2 Repack", SLATE),
        "002": (4.4, 5.9, "002\nFormula", TEAL),
        "006": (6.1, 5.9, "006\n3B Q8_0", TEAL),
        "007": (7.8, 5.9, "007\nFresh Sign", GREEN),
        "005": (4.4, 4.5, "005\n2-Source", TEAL),
        "008": (6.1, 4.5, "008\nRev Order", TEAL),
        "009": (7.8, 4.5, "009\nInterleaved", TEAL),
        "010": (9.5, 4.5, "010\nFresh Ord", GREEN),
        "011": (11.2, 4.5, "011\nMatch Mag", TEAL),
        "012": (2.7, 3.1, "012\n7B Match*", RUST),
        "013": (4.4, 3.1, "013\nClarity*", RUST),
        "014": (6.1, 3.1, "014\nStrict 48t*", RUST),
        "015": (7.8, 3.1, "015\n16-Fam Q4", TEAL),
        "016": (9.5, 3.1, "016\n96-Fam Conf", GREEN),
        "017": (11.2, 3.1, "017\n14B Q8/Q4", TEAL),
        "018": (1.3, 1.7, "018\nGraded/SDT*", RUST),
        "019": (3.0, 1.7, "019\nK/M Map*", RUST),
        "020": (4.7, 1.7, "020\nComponents", TEAL),
        "021": (6.4, 1.7, "021\nGuidance", TEAL),
        "022": (8.1, 1.7, "022\nMistral Rep", TEAL),
        "023": (9.8, 1.7, "023\nAudit Gate*", RUST),
        "024": (11.5, 1.7, "024\n21-Arm Mat", NAVY),
        "025": (2.7, 0.35, "025\nArch Screen", PURPLE),
        "025.1": (4.5, 0.35, "025.1\nDocx Audit", PURPLE),
        "026": (6.3, 0.35, "026\nGraph Sw*", RUST),
        "027": (8.1, 0.35, "027\n4-Mod F16*", RUST),
        "028": (9.9, 0.35, "028\nCalc C-B*", RUST),
        "029": (11.7, 0.35, "029\nCF-TP1", GREEN),
    }

    for k, (x, y, lbl, col) in nodes.items():
        fc = "#E8F5E9" if col == GREEN else ("#FDECEA" if col == RUST else ("#EDE7F6" if col == PURPLE else LIGHT_BG))
        draw_box(ax, pairs, x, y, bw, bh, lbl, fc=fc, ec=col, lw=1.3, fontsize=6.7, weight="bold", radius=0.05)

    # Direct adjacent horizontal edges (right boundary to left boundary)
    horiz_edges = [
        ("DV", "001"), ("001", "004"),
        ("002", "006"), ("006", "007"),
        ("005", "008"), ("008", "009"), ("009", "010"), ("010", "011"),
        ("012", "013"), ("013", "014"), ("014", "015"), ("015", "016"), ("016", "017"),
        ("018", "019"), ("019", "020"), ("020", "021"), ("021", "022"), ("022", "023"), ("023", "024"),
        ("025", "025.1"), ("025.1", "026"), ("026", "027"), ("027", "028"), ("028", "029"),
    ]
    for u, v in horiz_edges:
        x1, y1, _, _ = nodes[u]
        x2, y2, _, _ = nodes[v]
        arrow(ax, x1 + bw / 2 + 0.03, y1, x2 - bw / 2 - 0.03, y2, color="#607D8B", lw=1.1)

    # Vertical / clean channel routed transitions (zero box crossings)
    # 001 -> 003 (straight down)
    arrow(ax, 2.7, 7.3 - bh / 2 - 0.03, 2.7, 5.9 + bh / 2 + 0.03, color="#607D8B", lw=1.1)
    # 001 -> 002 and 001 -> 005 via clean channel x=3.55
    ax.plot([2.7 + 0.25, 3.55, 3.55], [7.3 - bh / 2 - 0.02, 6.60, 4.5], color="#607D8B", lw=1.05)
    arrow(ax, 3.55, 5.9, 4.4 - bw / 2 - 0.03, 5.9, color="#607D8B", lw=1.05)
    arrow(ax, 3.55, 4.5, 4.4 - bw / 2 - 0.03, 4.5, color="#607D8B", lw=1.05)

    # Row wraps in inter-row channels:
    # 011 (11.2, 4.5) -> channel y=3.8 -> 012 (2.7, 3.1)
    ax.plot([11.2, 11.2, 2.7], [4.5 - bh / 2 - 0.02, 3.80, 3.80], color="#78909C", lw=1.0, ls="--")
    arrow(ax, 2.7, 3.80, 2.7, 3.1 + bh / 2 + 0.03, color="#78909C", lw=1.0, ls="--")

    # 016 (9.5, 3.1) -> channel y=2.40 -> 018 (1.3, 1.7)
    ax.plot([9.5, 9.5, 1.3], [3.1 - bh / 2 - 0.02, 2.40, 2.40], color="#78909C", lw=1.0, ls="--")
    arrow(ax, 1.3, 2.40, 1.3, 1.7 + bh / 2 + 0.03, color="#78909C", lw=1.0, ls="--")

    # 024 (11.5, 1.7) -> channel y=1.02 -> 025 (2.7, 0.35)
    ax.plot([11.5, 11.5, 2.7], [1.7 - bh / 2 - 0.02, 1.02, 1.02], color="#78909C", lw=1.0, ls="--")
    arrow(ax, 2.7, 1.02, 2.7, 0.35 + bh / 2 + 0.03, color="#78909C", lw=1.0, ls="--")

    # 016 -> 029 outer right margin channel x=12.55
    ax.plot([9.5, 9.5, 12.55, 12.55], [3.1 + bh / 2 + 0.02, 3.62, 3.62, 0.35], color=GREEN, lw=1.0, ls=":")
    arrow(ax, 12.55, 0.35, 11.7 + bw / 2 + 0.03, 0.35, color=GREEN, lw=1.0, ls=":")

    legend_items = [
        Patch(facecolor=LIGHT_BG, edgecolor=TEAL, lw=1.3, label="Exploratory / Development Cohort"),
        Patch(facecolor="#FDECEA", edgecolor=RUST, lw=1.3, label="Reference / Control Gate Stopped (*)"),
        Patch(facecolor="#E8F5E9", edgecolor=GREEN, lw=1.3, label="Fresh-Family Replication / Prospective Case Study"),
        Patch(facecolor=LIGHT_BG, edgecolor=NAVY, lw=1.3, label="Multi-Lineage Quantization Matrix (30,912 calls)"),
        Patch(facecolor="#EDE7F6", edgecolor=PURPLE, lw=1.3, label="Retrospective No-Inference Audit"),
    ]
    fig.legend(handles=legend_items, loc="outside lower center", ncol=3, frameon=False, fontsize=7.5)
    return verify_and_save(fig, FIGS / "fig03_cohort_dependency_graph.pdf", PREVIEW, pairs)


def fig04_hypothesis_tree() -> list[str]:
    rows = list(csv.DictReader((EVID / "hypothesis_ledger.csv").open(encoding="utf-8")))
    status_palette = {
        "Supported within tested scope": (GREEN, "#E8F5E9"),
        "Contradicted by available evidence": (RED, "#FDECEA"),
        "Inconclusive": (GOLD, "#FFF8E1"),
        "Insufficiently identified": (RUST, "#FBE9E7"),
        "Superseded": (SLATE, "#ECEFF1"),
        "Untested": (PURPLE, "#EDE7F6"),
    }

    pairs = []
    fig, ax = plt.subplots(figsize=(12.6, 7.8), layout="constrained")
    ax.set_xlim(0, 14.8)
    ax.set_ylim(-0.5, 20.6)
    ax.axis("off")
    ax.set_title("Hypothesis Evolution Ledger and Final Epistemic Status (H01–H20)", loc="left")

    short_desc = {
        "H01": "Selective PTQ increase in associative conflict penalty (Delta > 0)",
        "H02": "Homogeneous CNI-style tree (C, A, B) decomposes LLM choices",
        "H03": "3B Q2_K increases conflict gap vs. 3B F16 on exact SCM tables",
        "H04": "3B Q2_K collapse caused by CPU repacking or tokenizer mismatch",
        "H05": "Supplying explicit backdoor formula rescues binary action accuracy",
        "H06": "3B Q4_K_M degrades formula estimate-sign accuracy vs. F16/Q8_0",
        "H07": "Scaling reference from 3B to 7B F16 clears direct conflict gates",
        "H08": "Historical-first order lowers 3B F16 conflict accuracy",
        "H09": "Matched |delta_obs| strength yields competent conflict choices",
        "H10": "Causal-context + strict 48t JSON establishes 7B F16 competence",
        "H11": "7B Q4_K_M exhibits nonzero conflict presentation-order shift",
        "H12": "7B Q4 order shift (+62.5 pp) generalizes to 14B Q8_0 / Q4_K_M",
        "H13": "Accuracy rises with effect size and is token-mapping invariant",
        "H14": "Qwen 7B F16 fails two-source task by missing trial source ID",
        "H15": "Qwen two-source gap transfers to Mistral/Llama & passes controls",
        "H16": "3-lineage x 7-format matrix shows monotone causal-selective loss",
        "H17": "Unaided F16 models adapt actions to identical-P(W,X,Y) switches",
        "H18": "Deterministic calculator (System C) rescues causal rule choice",
        "H19": "CF-TP1 transfer causal pair fidelity differs from arithmetic",
        "H20": "Interactive tool agents / layer patching isolate causal routes",
    }

    parents = {
        "H02": "H01", "H03": "H01", "H04": "H03", "H05": "H03", "H06": "H05",
        "H07": "H03", "H08": "H02", "H09": "H08", "H10": "H07", "H11": "H10",
        "H12": "H11", "H13": "H11", "H14": "H13", "H15": "H14", "H16": "H01",
        "H17": "H16", "H18": "H17", "H19": "H18", "H20": "H01",
    }

    y_pos = {f"H{i:02d}": 19.6 - (i - 1) * 1.0 for i in range(1, 21)}
    indent = {
        "H01": 0, "H02": 1, "H03": 1, "H04": 2, "H05": 2, "H06": 3,
        "H07": 2, "H08": 2, "H09": 3, "H10": 3, "H11": 4, "H12": 5,
        "H13": 5, "H14": 6, "H15": 6, "H16": 1, "H17": 2, "H18": 3,
        "H19": 4, "H20": 1,
    }

    for r in rows:
        hid = r["hypothesis_id"]
        y = y_pos[hid]
        x0 = 0.35 + indent[hid] * 0.28
        st = r["final_scientific_status"]
        ec, fc = status_palette[st]
        if hid in parents:
            py = y_pos[parents[hid]]
            px = 0.35 + indent[parents[hid]] * 0.28
            ax.plot([px, px, x0 - 0.08], [py - 0.22, y, y], color="#90A4AE", lw=0.9, zorder=1)
        ax.scatter([x0], [y], color=ec, s=24, zorder=4)
        ax.text(
            x0 + 0.14,
            y,
            f"{hid}: {short_desc[hid]}",
            va="center",
            ha="left",
            fontsize=7.3,
            fontweight="bold" if hid in ("H01", "H11", "H18", "H19") else "normal",
        )
        coh_txt = r["relevant_cohorts"]
        if len(coh_txt) > 20:
            coh_txt = coh_txt[:18] + ".."
        draw_box(ax, pairs, 10.45, y, 2.05, 0.62, coh_txt, fc=LIGHT_BG, ec=BORDER, lw=0.8, fontsize=6.5)
        draw_box(ax, pairs, 13.10, y, 2.85, 0.62, st, fc=fc, ec=ec, lw=1.1, fontsize=6.5, tc=ec, weight="bold")

    ax.text(2.0, 20.32, "Hypothesis Lineage & Scope", ha="left", va="center", fontsize=8.0, fontweight="bold", color=NAVY)
    ax.text(10.45, 20.32, "Tested Cohorts", ha="center", va="center", fontsize=8.0, fontweight="bold", color=NAVY)
    ax.text(13.10, 20.32, "Final Epistemic Status", ha="center", va="center", fontsize=8.0, fontweight="bold", color=NAVY)
    return verify_and_save(fig, FIGS / "fig04_hypothesis_tree.pdf", PREVIEW, pairs)


def fig05_methodology_cohort_matrix() -> list[str]:
    cols = ["DV"] + [f"{i:03d}" for i in range(1, 26)] + ["25.1", "026", "027", "028", "029"]
    meth_rows = [
        ("M01 2x2 Confounded SCM", ["DV"] + [f"{i:03d}" for i in range(1, 12)]),
        ("M02 C/A/B Processing Tree", ["DV", "005"]),
        ("M03 Single-Fence Sensitivity", [f"{i:03d}" for i in range(1, 14)]),
        ("M04 Formula & Sign Split", ["002", "006", "007"]),
        ("M05 Supplied-Rate Order X-Over", ["005", "008", "009", "010", "011", "012", "013", "014", "015", "016", "017"]),
        ("M06 Matched Obs Strength", [f"{i:03d}" for i in range(11, 25)]),
        ("M07 Reference Competence Gate", ["004", "012", "013", "014", "015", "018", "019", "023", "026", "027", "028"]),
        ("M08 Strict Bare JSON / Token", [f"{i:03d}" for i in range(14, 25)] + ["026", "027", "028", "029"]),
        ("M09 Copula Power Simulation", ["016"]),
        ("M10 Signal Detection (d', c)", ["018", "019", "024", "025", "25.1"]),
        ("M11 Token/Option Counterbalance", ["018", "019", "023", "024", "025", "027", "028", "029"]),
        ("M12 Component & Guidance Split", ["020", "021", "022", "023", "024"]),
        ("M13 Noncausal Scorecard Control", ["018", "019", "023", "024", "027", "028", "029"]),
        ("M14 Metamorphic & MI Audit", ["025", "25.1"]),
        ("M15 Exact-Rational Graph Switch", ["026", "027", "028"]),
        ("M16 Deterministic Calc Replay", ["028"]),
        ("M17 Durable Append-Only Journal", [f"{i:03d}" for i in range(1, 25)] + ["026", "027", "028", "029"]),
        ("M18 CF-TP1 Role & Target Swap", ["029"]),
        ("M19 Dual Oracle & Welch/Bounded", ["029"]),
    ]

    mat = np.zeros((len(meth_rows), len(cols)))
    for r_i, (_, active) in enumerate(meth_rows):
        for c_name in active:
            if c_name in cols:
                mat[r_i, cols.index(c_name)] = 1.0

    fig, ax = plt.subplots(figsize=(11.6, 5.8), layout="constrained")
    cmap = matplotlib.colors.ListedColormap(["#F5F7F8", TEAL])
    ax.imshow(mat, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels(cols, rotation=55, ha="right", fontsize=7.2)
    ax.set_yticks(np.arange(len(meth_rows)))
    ax.set_yticklabels([m[0] for m in meth_rows], fontsize=7.4)
    ax.set_xticks(np.arange(-0.5, len(cols), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(meth_rows), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("Methodology-by-Cohort Adoption Matrix Across Project CausalFade (M01–M19)", loc="left")
    ax.set_xlabel("Cohort Identifier (DV = Synthetic Design Validation)")
    handles = [
        Patch(facecolor=TEAL, edgecolor="white", label="Methodology Active in Cohort"),
        Patch(facecolor="#F5F7F8", edgecolor=BORDER, label="Not Active"),
    ]
    fig.legend(handles=handles, loc="outside lower center", ncol=2, frameon=False, fontsize=7.8)
    return verify_and_save(fig, FIGS / "fig05_methodology_cohort_matrix.pdf", PREVIEW)


def fig06_model_cohort_matrix() -> list[str]:
    cols = [f"{i:03d}" for i in range(1, 25)] + ["026", "027", "028", "029"]
    model_rows = [
        "Qwen2.5-3B · F16",
        "Qwen2.5-3B · Q8_0",
        "Qwen2.5-3B · Q4_K_M",
        "Qwen2.5-3B · Q2_K",
        "Qwen2.5-7B · F16",
        "Qwen2.5-7B · Q8_0 / Q6_K / Q5_K_M",
        "Qwen2.5-7B · Q4_K_M",
        "Qwen2.5-7B · Q3_K_M / Q2_K",
        "Qwen2.5-14B · Q8_0",
        "Qwen2.5-14B · Q4_K_M",
        "Mistral-7B-v0.3 · F16",
        "Mistral-7B-v0.3 · Q8/Q6/Q5/Q3/Q2",
        "Mistral-7B-v0.3 · Q4_K_M",
        "Llama-3.1-8B · F16",
        "Llama-3.1-8B · Q8/Q6/Q5/Q3/Q2",
        "Llama-3.1-8B · Q4_K_M",
    ]
    mat = np.zeros((len(model_rows), len(cols)))

    def mark(r_idx, c_list, val=1.0):
        for c in c_list:
            mat[r_idx, cols.index(c)] = val

    mark(0, ["001", "002", "005", "007", "008", "009", "010", "011", "027"], 1)
    mark(1, ["006"], 2)
    mark(2, ["001", "002", "005", "007", "008", "009", "010", "011"], 2)
    mark(3, ["001", "003"], 3)
    mark(4, ["004", "012", "013", "014", "015", "016", "018", "019", "020", "021", "022", "023", "024", "026", "027", "028"], 1)
    mark(5, ["024"], 2)
    mark(6, ["015", "016", "024", "029"], 2)
    mark(7, ["024"], 2)
    mark(8, ["017"], 2)
    mark(9, ["017"], 2)
    mark(10, ["024", "027"], 1)
    mark(11, ["024"], 2)
    mark(12, ["022", "024"], 2)
    mark(13, ["024", "026", "027", "028"], 1)
    mark(14, ["024"], 2)
    mark(15, ["024"], 3)

    for c in ["004", "012", "013", "014", "018", "019", "026", "027", "028"]:
        if mat[6, cols.index(c)] == 0:
            mat[6, cols.index(c)] = 0.5

    fig, ax = plt.subplots(figsize=(11.6, 5.6), layout="constrained")
    cmap = matplotlib.colors.ListedColormap(["#F5F7F8", "#FFE0B2", NAVY, TEAL, RED])
    bounds = [-0.1, 0.25, 0.75, 1.5, 2.5, 3.5]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    ax.imshow(mat, aspect="auto", cmap=cmap, norm=norm)

    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels(cols, rotation=50, ha="right", fontsize=7.3)
    ax.set_yticks(np.arange(len(model_rows)))
    ax.set_yticklabels(model_rows, fontsize=7.5)
    ax.set_xticks(np.arange(-0.5, len(cols), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(model_rows), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("Model Lineage and Quantization Format Coverage Across Empirical Cohorts", loc="left")
    ax.set_xlabel("Empirical Cohort (Cohorts 025 and 025.1 Omitted as Zero-Inference Archive Audits)")

    handles = [
        Patch(facecolor=NAVY, label="F16 Reference Executed"),
        Patch(facecolor=TEAL, label="Quantized Arm Executed"),
        Patch(facecolor=RED, label="Severe Truncation / Operational Failure (3B Q2_K; Llama Q4 Controls)"),
        Patch(facecolor="#FFE0B2", edgecolor=GOLD, label="Conditional Quantized Arm Withheld by Reference Gate"),
    ]
    fig.legend(handles=handles, loc="outside lower center", ncol=2, frameon=False, fontsize=7.6)
    return verify_and_save(fig, FIGS / "fig06_model_cohort_matrix.pdf", PREVIEW)


def fig07_infrastructure_architecture() -> list[str]:
    pairs = []
    fig, ax = plt.subplots(figsize=(11.8, 5.4), layout="constrained")
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.6)
    ax.axis("off")
    ax.set_title("CausalFade Experimental Infrastructure and Reproducibility Safeguard Architecture", loc="left")

    draw_box(
        ax, pairs, 1.55, 4.05, 2.55, 1.45,
        "1. World & SCM Generator\n• Exact-rational / float SCMs\n• Seeded SHA-256 PRNGs\n• Positivity & margin gates",
        fc=LIGHT_BG, ec=NAVY, lw=1.3, fontsize=6.9,
    )
    draw_box(
        ax, pairs, 1.55, 1.65, 2.55, 1.45,
        "2. Public / Private Split\n• public_tasks.jsonl (blind)\n• oracle_truth.jsonl (air-gap)\n• Independent text Oracle B",
        fc="#FFF8E1", ec=GOLD, lw=1.3, fontsize=6.9,
    )
    draw_box(
        ax, pairs, 4.75, 4.05, 2.55, 1.45,
        "3. Freeze & Preflight Gate\n• Tokenizer budget <= 2048\n• 162-policy shortcut audit\n• Immutable manifest SHA-256",
        fc=LIGHT_BG, ec=TEAL, lw=1.3, fontsize=6.9,
    )
    draw_box(
        ax, pairs, 4.75, 1.65, 2.55, 1.45,
        "4. CPU Inference Harness\n• llama.cpp b12176 loopback\n• 8 CPU threads, temp 0.0\n• Stateless context per call",
        fc=LIGHT_BG, ec=TEAL, lw=1.3, fontsize=6.9,
    )
    draw_box(
        ax, pairs, 7.95, 4.05, 2.55, 1.45,
        "5. Durable Event Journal\n• Single-writer lock\n• Intent -> Dispatch -> Base64\n• SHA-256 payload verification",
        fc="#E8F5E9", ec=GREEN, lw=1.3, fontsize=6.9,
    )
    draw_box(
        ax, pairs, 7.95, 1.65, 2.55, 1.45,
        "6. Strict & Diagnostic Scorer\n• Duplicate-key & int hooks\n• finish_reason == 'stop'\n• Invalids kept in denominator",
        fc=LIGHT_BG, ec=RUST, lw=1.3, fontsize=6.9,
    )
    draw_box(
        ax, pairs, 10.85, 2.85, 2.15, 3.25,
        "7. Family-Cluster\nInference & Replay\n\n• Family cluster N\n• Block bootstrap &\n  Welch t + bounded\n• Reference stopping\n  gates enforced\n• Model-free offline\n  byte-level replay",
        fc="white", ec=NAVY, lw=1.5, fontsize=6.9,
    )

    # Non-crossing orthogonal / boundary-to-boundary arrows
    arrow(ax, 1.55, 3.29, 1.55, 2.41, NAVY, lw=1.2)
    # 2 -> 3 routed cleanly through x=3.15 channel
    ax.plot([2.85, 3.15, 3.15], [1.95, 1.95, 4.05], color=TEAL, lw=1.2)
    arrow(ax, 3.15, 4.05, 3.44, 4.05, TEAL, lw=1.2)
    arrow(ax, 4.75, 3.29, 4.75, 2.41, TEAL, lw=1.2)
    # 4 -> 5 routed cleanly through x=6.35 channel
    ax.plot([6.05, 6.35, 6.35], [1.95, 1.95, 4.05], color=GREEN, lw=1.2)
    arrow(ax, 6.35, 4.05, 6.64, 4.05, GREEN, lw=1.2)
    arrow(ax, 7.95, 3.29, 7.95, 2.41, RUST, lw=1.2)
    arrow(ax, 9.25, 4.05, 9.74, 3.65, NAVY, lw=1.2)
    arrow(ax, 9.25, 1.65, 9.74, 2.05, NAVY, lw=1.2)
    # Bottom air-gap oracle join channel at y=0.58, text safely below at y=0.22
    ax.plot([1.55, 1.55, 7.95], [0.90, 0.58, 0.58], color=GOLD, lw=1.2, ls="--")
    arrow(ax, 7.95, 0.58, 7.95, 0.89, GOLD, lw=1.2, ls="--")
    ax.text(
        4.75, 0.22,
        "Withheld oracle_truth / gold.jsonl joins ONLY at post-collection scoring (zero inference leakage)",
        ha="center", va="center", fontsize=7.0, color=GOLD, style="italic",
    )

    return verify_and_save(fig, FIGS / "fig07_infrastructure_architecture.pdf", PREVIEW, pairs)


def fig08_structural_causal_diagrams() -> list[str]:
    pairs = []
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 6.2), layout="constrained")

    # Panel A: Observable Confounded Backdoor (Cohorts 001-011)
    ax = axes[0, 0]
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("A   Observable Backdoor Confounding (Cohorts 001–011)", loc="left", fontsize=9.2)
    draw_box(ax, pairs, 0.50, 0.78, 0.36, 0.16, "Severity Z", fc=LIGHT_BG, ec=NAVY, fontsize=7.5, weight="bold")
    draw_box(ax, pairs, 0.22, 0.34, 0.32, 0.16, "Setting X", fc="#E8F5E9", ec=TEAL, fontsize=7.5, weight="bold")
    draw_box(ax, pairs, 0.78, 0.34, 0.32, 0.16, "Success Y", fc="white", ec=NAVY, fontsize=7.5, weight="bold")
    arrow(ax, 0.40, 0.69, 0.26, 0.44, RUST, lw=1.3, ls="--")
    arrow(ax, 0.60, 0.69, 0.74, 0.44, NAVY, lw=1.3)
    arrow(ax, 0.39, 0.34, 0.61, 0.34, TEAL, lw=1.5)
    ax.text(0.50, 0.08, "Intervention do(X=x) deletes Z -> X; adjust via P(Z)", ha="center", va="center", fontsize=7.1, color=SLATE)

    # Panel B: Two-Study Randomized vs Historical Evidence (Cohorts 012-025)
    ax = axes[0, 1]
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("B   Two-Study Provenance Selection (Cohorts 012–025)", loc="left", fontsize=9.2)
    draw_box(ax, pairs, 0.22, 0.78, 0.34, 0.16, "Study Regime M", fc=LIGHT_BG, ec=SLATE, fontsize=7.3, weight="bold")
    draw_box(ax, pairs, 0.74, 0.78, 0.36, 0.16, "Unmeasured Risk U", fc="#FDECEA", ec=RUST, fontsize=7.3, weight="bold")
    draw_box(ax, pairs, 0.26, 0.34, 0.32, 0.16, "Action X", fc="#E8F5E9", ec=TEAL, fontsize=7.5, weight="bold")
    draw_box(ax, pairs, 0.78, 0.34, 0.32, 0.16, "Success Y", fc="white", ec=NAVY, fontsize=7.5, weight="bold")
    arrow(ax, 0.24, 0.69, 0.25, 0.44, SLATE, lw=1.3)
    arrow(ax, 0.62, 0.69, 0.36, 0.44, RUST, lw=1.3, ls="--")
    arrow(ax, 0.76, 0.69, 0.78, 0.44, RUST, lw=1.3)
    arrow(ax, 0.43, 0.34, 0.61, 0.34, TEAL, lw=1.5)
    ax.text(0.50, 0.08, "Randomization severs U -> X; historical log retains U -> X", ha="center", va="center", fontsize=7.1, color=RUST)

    # Panel C: Observationally Identical Confounder vs Mediator (Cohorts 026-028)
    ax = axes[1, 0]
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("C   Identical-P(W,X,Y) Graph Switch (Cohorts 026–028)", loc="left", fontsize=9.2)
    ax.text(0.50, 0.92, "Confounder: weight P(Y=1|X,W) by marginal P(W)", ha="center", va="center", fontsize=7.1, fontweight="bold", color=NAVY)
    draw_box(ax, pairs, 0.18, 0.68, 0.20, 0.15, "W", fc=LIGHT_BG, ec=NAVY, fontsize=7.5, weight="bold")
    draw_box(ax, pairs, 0.50, 0.68, 0.20, 0.15, "X", fc="#E8F5E9", ec=TEAL, fontsize=7.5, weight="bold")
    draw_box(ax, pairs, 0.82, 0.68, 0.20, 0.15, "Y", fc="white", ec=NAVY, fontsize=7.5, weight="bold")
    arrow(ax, 0.29, 0.68, 0.39, 0.68, NAVY, lw=1.2)
    arrow(ax, 0.61, 0.68, 0.71, 0.68, TEAL, lw=1.2)
    arrow(ax, 0.25, 0.77, 0.75, 0.77, NAVY, lw=1.1, rad=-0.16)

    ax.axhline(0.47, color=BORDER, lw=0.9, ls=":")
    ax.text(0.50, 0.38, "Mediator: weight P(Y=1|X,W) by conditional P(W|X)", ha="center", va="center", fontsize=7.1, fontweight="bold", color=RUST)
    draw_box(ax, pairs, 0.18, 0.15, 0.20, 0.15, "X", fc="#E8F5E9", ec=TEAL, fontsize=7.5, weight="bold")
    draw_box(ax, pairs, 0.50, 0.15, 0.20, 0.15, "W", fc=LIGHT_BG, ec=RUST, fontsize=7.5, weight="bold")
    draw_box(ax, pairs, 0.82, 0.15, 0.20, 0.15, "Y", fc="white", ec=NAVY, fontsize=7.5, weight="bold")
    arrow(ax, 0.29, 0.15, 0.39, 0.15, RUST, lw=1.2)
    arrow(ax, 0.61, 0.15, 0.71, 0.15, RUST, lw=1.2)
    arrow(ax, 0.25, 0.24, 0.75, 0.24, TEAL, lw=1.1, rad=-0.16)

    # Panel D: CF-TP1 Target-Population Transport Selection Diagram (Cohort 029)
    ax = axes[1, 1]
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.set_title("D   CF-TP1 Provenance & Target Transport (Cohort 029)", loc="left", fontsize=9.2)
    draw_box(ax, pairs, 0.20, 0.82, 0.32, 0.15, "Target Mix w*", fc="#FFF8E1", ec=GOLD, fontsize=7.1, weight="bold")
    draw_box(ax, pairs, 0.74, 0.82, 0.32, 0.15, "Stratum S", fc=LIGHT_BG, ec=NAVY, fontsize=7.2, weight="bold")
    draw_box(ax, pairs, 0.47, 0.53, 0.30, 0.15, "Latent Risk U", fc="#FDECEA", ec=RUST, fontsize=7.1, weight="bold")
    draw_box(ax, pairs, 0.16, 0.23, 0.26, 0.15, "Regime M", fc=LIGHT_BG, ec=SLATE, fontsize=7.0)
    draw_box(ax, pairs, 0.50, 0.23, 0.26, 0.15, "Action A", fc="#E8F5E9", ec=TEAL, fontsize=7.2, weight="bold")
    draw_box(ax, pairs, 0.84, 0.50, 0.24, 0.16, "Success Y", fc="white", ec=NAVY, fontsize=7.2, weight="bold")
    arrow(ax, 0.37, 0.82, 0.57, 0.82, GOLD, lw=1.2)
    arrow(ax, 0.78, 0.73, 0.83, 0.59, NAVY, lw=1.2)
    arrow(ax, 0.63, 0.52, 0.71, 0.51, RUST, lw=1.2)
    arrow(ax, 0.48, 0.44, 0.49, 0.32, RUST, lw=1.2, ls="--")
    arrow(ax, 0.30, 0.23, 0.36, 0.23, SLATE, lw=1.2)
    arrow(ax, 0.64, 0.27, 0.77, 0.41, TEAL, lw=1.4)
    ax.text(0.50, 0.05, "V*(a; w*) = sum_s P*(S=s) P_rct(Y=1 | A=a, S=s)", ha="center", va="center", fontsize=7.1, color=NAVY)

    return verify_and_save(fig, FIGS / "fig08_structural_causal_diagrams.pdf", PREVIEW, pairs)


def fig15_failure_correction_timeline() -> list[str]:
    failures = [
        ("F1 · Cohort 001", "Markdown JSON fences caused 0/64 strict floor; 3B Q2_K hit 160-token loop cap.", "Added single-fence diagnostic (001–013), repack/tokenizer audits (003), and bare 48t JSON (014+)."),
        ("F2 · Cohort 002", "Explicit actions contradicted model's computed ATE sign (61/64 signs vs. 32/64 actions).", "Split numeric sign from action commitment; built action-only & calculator schemas (005, 028)."),
        ("F3 · Cohort 005", "Smaller Q4 conflict penalty came from 61/64 activate bias; F16 broke C/A/B additivity.", "Retired latent C/A/B route claims; tracked directional hits, false alarms, and activation rates."),
        ("F4 · Cohort 008", "Cross-session order reversal confounded line order with 2-day gap & PC shutdown.", "Preserved partial run_001 (26/64) untouched; built same-session twin interleaving (009–010)."),
        ("F5 · Cohorts 009–011", "Original SCM had wider aligned |delta_obs|; script bug halved printed cell counts.", "Built matched-strength generator (011); fixed count bug in b90cb63 while archiving *_v1 JSONs."),
        ("F6 · Cohort 013", "Causal-context prose triggered 64/64 trailing explanations hitting 160-token cap.", "Enforced bare one-key JSON contract + 48-token cap (014), achieving 100% strict validity."),
        ("F7 · Cohort 016 Audit", "Retrospective audit found |trial gap| < |hist gap| allowed a gap rule to solve 768/768.", "Built identical-P(W,X,Y) switches (026–028) and CF-TP1 role-swap 162-policy shortcut audit (029)."),
        ("F8 · Cohorts 019 & 022", "Ambiguous order cue in 019 check; Mistral picked 'Study A' / 1st option (256/256).", "Adopted numbered study blocks (020) and full A/B & option-order counterbalancing (023–024)."),
        ("F9 · Cohort 026", "v1 oracle failed on complemented Y; v2/v3 coupled option order with task form.", "Archived invalidated v1; crossed graph x form x option order in Cohort 027 (0/8 switch fidelity)."),
        ("F10 · Cohort 029 Docs", "Manual prose table in RESULTS.md misstated off/on counts; review JSON uncertified.", "Reconciled exact off/on counts from raw journal in supplement.tex and disclosed review status."),
    ]

    pairs = []
    fig, ax = plt.subplots(figsize=(12.2, 8.2), layout="constrained")
    ax.set_xlim(0, 12.6)
    ax.set_ylim(-0.3, len(failures) + 0.5)
    ax.axis("off")
    ax.set_title("Chronology of Methodological Failures, Confounds, and Resulting Architectural Corrections", loc="left")

    for i, (tag, flaw, fix) in enumerate(failures):
        y = len(failures) - 0.65 - i
        flaw_w = textwrap.fill(flaw, width=50)
        fix_w = textwrap.fill(fix, width=52)
        draw_box(ax, pairs, 1.15, y, 2.0, 0.76, tag, fc="#FDECEA", ec=RED, lw=1.2, fontsize=6.9, tc=RED, weight="bold")
        draw_box(ax, pairs, 4.95, y, 4.7, 0.76, flaw_w, fc="white", ec=RUST, lw=1.0, fontsize=6.6)
        draw_box(ax, pairs, 9.95, y, 4.5, 0.76, fix_w, fc="#E8F5E9", ec=GREEN, lw=1.1, fontsize=6.6)
        arrow(ax, 2.18, y, 2.56, y, RED, lw=1.1)
        arrow(ax, 7.34, y, 7.66, y, GREEN, lw=1.1)

    ax.text(1.15, len(failures) + 0.15, "Stage", ha="center", va="center", fontweight="bold", fontsize=8.0, color=NAVY)
    ax.text(4.95, len(failures) + 0.15, "Identified Flaw, Artifact, or Confound", ha="center", va="center", fontweight="bold", fontsize=8.0, color=RUST)
    ax.text(9.95, len(failures) + 0.15, "Preserved Record & Methodological Safeguard", ha="center", va="center", fontweight="bold", fontsize=8.0, color=GREEN)
    return verify_and_save(fig, FIGS / "fig15_failure_correction_timeline.pdf", PREVIEW, pairs)


def fig16_cftp1_protocol_flowchart() -> list[str]:
    pairs = []
    fig, ax = plt.subplots(figsize=(11.8, 5.2), layout="constrained")
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    ax.set_title("Final Evaluation Protocol (CF-TP1 / Cohort 029): Pre-Inference Freeze, Execution, and Offline Replay", loc="left")

    steps = [
        (1.55, 3.85, 2.65, 1.45, "1. Stratified World Draw\n• Master seed 290431\n• 8 sign strata x 16 = 128\n• Margin >= 0.50 pp all 4\n• Exact 0.5% rational grid", NAVY, LIGHT_BG),
        (4.75, 3.85, 2.65, 1.45, "2. Factorial Rendering\n• 2 forms x 2 tasks x 2 ord\n  x 2 roles x 2 mixes = 32\n• Balanced option parity\n• 4,096 stateless prompts", TEAL, LIGHT_BG),
        (7.95, 3.85, 2.65, 1.45, "3. Dual-Oracle & Rival Gate\n• Private SCM oracle ==\n  public-text parser\n• 162-policy shortcut audit\n• Zero source-blind leaks", GOLD, "#FFF8E1"),
        (10.85, 3.85, 2.15, 1.45, "4. Freeze Gate\n• Tokens <= 2048\n• Sim coverage\n• Manifest SHA\n  5252f69d...", GREEN, "#E8F5E9"),
        (10.85, 1.45, 2.15, 1.50, "5. Live Run\n• Qwen2.5-7B Q4\n• Seed 290432\n• 4,096/4,096 ok\n• SHA 673eb723..", TEAL, LIGHT_BG),
        (7.55, 1.45, 3.25, 1.50, "6. Paired Fidelity Analysis\n• F_pair = I_0 * I_1 (512 pairs)\n• D_hi = F_causal - F_arith\n• Welch t [-7.77, +0.74] pp\n• Bounded [-27.52, +20.49] pp", NAVY, "white"),
        (3.15, 1.45, 3.75, 1.50, "7. Model-Free Release Verification\n• Tag cohort-029-v1.0.0 (76206c2)\n• Rebuild fixture byte-for-byte\n• 50/50 automated verifier checks\n• Raw-journal off/on reconciliation", GREEN, "#E8F5E9"),
    ]
    for x, y, w, h, txt, ec, fc in steps:
        draw_box(ax, pairs, x, y, w, h, txt, fc=fc, ec=ec, lw=1.3, fontsize=6.8)

    arrow(ax, 2.91, 3.85, 3.39, 3.85, NAVY, lw=1.3)
    arrow(ax, 6.11, 3.85, 6.59, 3.85, TEAL, lw=1.3)
    arrow(ax, 9.31, 3.85, 9.74, 3.85, GOLD, lw=1.3)
    arrow(ax, 10.85, 3.09, 10.85, 2.24, GREEN, lw=1.3)
    arrow(ax, 9.74, 1.45, 9.21, 1.45, NAVY, lw=1.3)
    arrow(ax, 5.89, 1.45, 5.06, 1.45, GREEN, lw=1.3)
    return verify_and_save(fig, FIGS / "fig16_cftp1_protocol_flowchart.pdf", PREVIEW, pairs)


def fig17_research_contribution_map() -> list[str]:
    pairs = []
    fig, ax = plt.subplots(figsize=(11.8, 5.6), layout="constrained")
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 5.6)
    ax.axis("off")
    ax.set_title("Project CausalFade: Map of Verified Contributions vs. Explicit Epistemic Boundaries", loc="left")

    quads = [
        (3.0, 4.05, 5.5, 2.25,
         "Methodological & Benchmark Contributions (Established)\n"
         "• CF-TP1 exact-rational role-swap + target-transport design\n"
         "• Switch vs. invariance paired scoring (F_pair = I_0 * I_1)\n"
         "• Dual-oracle verification & 162-policy shortcut audit\n"
         "• Predeclared competence gates & matched scorecards",
         GREEN, "#E8F5E9"),
        (9.0, 4.05, 5.5, 2.25,
         "Empirical & Behavioral Findings (Scope-Bounded)\n"
         "• Prospective +62.5 pp 7B Q4 conflict-order shift (Cohort 016)\n"
         "• 100% source ID vs. 45.3% guided action dissociation (021)\n"
         "• 21-arm matrix: Mistral 1st-option; Llama Q4 control caps (024)\n"
         "• Calculator rescued controls (+54.7 pp), not causal rules (028)\n"
         "• CF-TP1: 995/1024 causal on-bias vs. 45/256 arith flips (029)",
         TEAL, LIGHT_BG),
        (3.0, 1.40, 5.5, 2.25,
         "Reproducibility & Audit Contributions (Established)\n"
         "• Zero-deletion 320-commit archive (48,170 raw responses)\n"
         "• Preserved interrupted runs, invalid pilots & v1 bug JSONs\n"
         "• Model-free offline Cohort 029 replay (50/50 checks passed)\n"
         "• Full SHA-256 traceability & RESULTS.md count reconciliation",
         NAVY, "white"),
        (9.0, 1.40, 5.5, 2.25,
         "Claims Explicitly NOT Established (Scientific Boundaries)\n"
         "• NO selective PTQ degradation of causal reasoning established\n"
         "• NO equivalence proven from inconclusive Delta = -3.52 pp\n"
         "• NO internal neural circuit severing or C/A/B tree route proven\n"
         "• NO generalization claimed beyond tested models & templates",
         RED, "#FDECEA"),
    ]
    for x, y, w, h, txt, ec, fc in quads:
        draw_box(ax, pairs, x, y, w, h, txt, fc=fc, ec=ec, lw=1.4, fontsize=6.9)

    return verify_and_save(fig, FIGS / "fig17_research_contribution_map.pdf", PREVIEW, pairs)


def main() -> None:
    all_issues = []
    for fn in [
        fig01_research_timeline,
        fig02_question_evolution,
        fig03_cohort_dependency_graph,
        fig04_hypothesis_tree,
        fig05_methodology_cohort_matrix,
        fig06_model_cohort_matrix,
        fig07_infrastructure_architecture,
        fig08_structural_causal_diagrams,
        fig15_failure_correction_timeline,
        fig16_cftp1_protocol_flowchart,
        fig17_research_contribution_map,
    ]:
        all_issues.extend(fn())
    if all_issues:
        raise SystemExit(f"Conceptual figure geometry guard found {len(all_issues)} issues!")
    print("ALL 11 CONCEPTUAL FIGURES PASSED ZERO-OVERLAP GUARD.")


if __name__ == "__main__":
    main()
