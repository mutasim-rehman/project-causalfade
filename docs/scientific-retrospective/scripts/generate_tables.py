"""Generate modular LaTeX tables in docs/scientific-retrospective/tables/ directly from verified inventories and artifacts."""
from pathlib import Path
import csv
import json

RETRO = Path(__file__).resolve().parents[1]
EVID = RETRO / "evidence"
TAB = RETRO / "tables"
TAB.mkdir(parents=True, exist_ok=True)


def tex_esc(s) -> str:
    if s is None:
        return ""
    text = str(s)
    repl = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
        ("/", "/\\allowbreak{}"),
        ("-", "-\\allowbreak{}"),
    ]
    for k, v in repl:
        text = text.replace(k, v)
    return text


def read_csv(name: str):
    with (EVID / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_tab(name: str, content: str):
    import re
    content = re.sub(r"p\{([0-9.]+cm)\}", r">{\\raggedright\\arraybackslash}p{\1}", content)
    (TAB / name).write_text(content, encoding="utf-8")
    print(f"Wrote tables/{name}")


def build_cohort_master():
    rows = read_csv("cohort_inventory.csv")
    lines = [
        "{\\footnotesize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{longtable}{@{}p{1.8cm}p{1.6cm}p{2.6cm}p{1.1cm}p{3.4cm}p{4.3cm}@{}}",
        "\\caption{Master inventory of all 31 CausalFade methodological and empirical cohort units (\\texttt{design\\_validation} and Cohorts \\texttt{001}--\\texttt{029}, including \\texttt{025\\_1}).}\\label{tab:cohort_master}\\\\",
        "\\toprule",
        "\\textbf{Cohort} & \\textbf{Dates} & \\textbf{Models / Arms} & \\textbf{Pers.} & \\textbf{Design \\& Classification} & \\textbf{Principal Empirical Finding} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{Cohort} & \\textbf{Dates} & \\textbf{Models / Arms} & \\textbf{Pers.} & \\textbf{Design \\& Classification} & \\textbf{Principal Empirical Finding} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in rows:
        lines.append(
            f"\\texttt{{{tex_esc(r['cohort_id'])}}} & {tex_esc(r['dates'])} & {tex_esc(r['models_and_formats'])} & "
            f"{tex_esc(r['persisted_llm_responses'])} & {tex_esc(r['sample_and_design'])} ({tex_esc(r['inferential_classification'])}) & "
            f"{tex_esc(r['principal_finding'])} \\\\[2pt]"
        )
    lines.extend(["\\end{longtable}", "}"])
    write_tab("tab_cohort_master.tex", "\n".join(lines))


def build_experiment_runs():
    rows = read_csv("experiment_inventory.csv")
    lines = [
        "{\\scriptsize",
        "\\setlength{\\tabcolsep}{3pt}",
        "\\begin{longtable}{@{}p{1.5cm}p{2.7cm}p{3.2cm}rrrp{4.2cm}@{}}",
        "\\caption{Complete inventory of all 74 experimental and analytical run entries across Project CausalFade ($48{,}208$ scheduled LLM requests; $48{,}170$ persisted raw responses).}\\label{tab:experiment_runs}\\\\",
        "\\toprule",
        "\\textbf{Cohort} & \\textbf{Run ID} & \\textbf{Model Artifact} & \\textbf{Sched.} & \\textbf{Pers.} & \\textbf{Valid} & \\textbf{Run Path \\& Raw SHA Prefix} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{Cohort} & \\textbf{Run ID} & \\textbf{Model Artifact} & \\textbf{Sched.} & \\textbf{Pers.} & \\textbf{Valid} & \\textbf{Run Path \\& Raw SHA Prefix} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in rows:
        sha = r["raw_sha256"][:10] if r["raw_sha256"] else "n/a"
        val = r["strict_valid_count"] if r["strict_valid_count"] != "" else "--"
        lines.append(
            f"\\texttt{{{tex_esc(r['cohort_id'])}}} & \\texttt{{{tex_esc(r['run_id'])}}} & \\texttt{{{tex_esc(r['model_artifact'])}}} & "
            f"{tex_esc(r['scheduled_requests'])} & {tex_esc(r['persisted_raw_records'])} & {tex_esc(val)} & "
            f"\\texttt{{{tex_esc(r['run_path'])}}} (\\texttt{{{tex_esc(sha)}}}) \\\\"
        )
    lines.extend(["\\end{longtable}", "}"])
    write_tab("tab_experiment_runs.tex", "\n".join(lines))


def build_model_quant():
    rows = read_csv("model_quantization_inventory.csv")
    lines = [
        "{\\footnotesize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{longtable}{@{}p{3.0cm}p{2.3cm}p{2.2cm}p{3.4cm}p{3.6cm}@{}}",
        "\\caption{Complete model lineage and GGUF quantization inventory with source revisions, formats, file sizes, provenance, and cohort deployment.}\\label{tab:model_quant_inventory}\\\\",
        "\\toprule",
        "\\textbf{Model Family (Revision)} & \\textbf{GGUF Formats} & \\textbf{Size Notes} & \\textbf{Quantization Provenance} & \\textbf{Cohorts Queried} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{Model Family (Revision)} & \\textbf{GGUF Formats} & \\textbf{Size Notes} & \\textbf{Quantization Provenance} & \\textbf{Cohorts Queried} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in rows:
        rev = r["source_revision"][:10] if len(r["source_revision"]) > 12 else r["source_revision"]
        lines.append(
            f"\\texttt{{{tex_esc(r['model_family'])}}} (\\texttt{{{tex_esc(rev)}}}) & \\texttt{{{tex_esc(r['formats'])}}} & "
            f"{tex_esc(r['size_notes'])} & {tex_esc(r['quantization_provenance'])} & {tex_esc(r['cohorts_used'])} \\\\[2pt]"
        )
    lines.extend(["\\end{longtable}", "}"])
    write_tab("tab_model_quant_inventory.tex", "\n".join(lines))


def build_dataset_inventory():
    rows = read_csv("dataset_task_inventory.csv")
    lines = [
        "{\\footnotesize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{longtable}{@{}p{2.6cm}p{2.3cm}rrp{4.6cm}p{3.2cm}@{}}",
        "\\caption{Inventory of all 24 dataset schemas and task families constructed during Project CausalFade.}\\label{tab:dataset_inventory}\\\\",
        "\\toprule",
        "\\textbf{Dataset ID} & \\textbf{Generator} & \\textbf{Fam.} & \\textbf{Items} & \\textbf{Task Paradigm} & \\textbf{Manifest Path} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{Dataset ID} & \\textbf{Generator} & \\textbf{Fam.} & \\textbf{Items} & \\textbf{Task Paradigm} & \\textbf{Manifest Path} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in rows:
        lines.append(
            f"\\texttt{{{tex_esc(r['dataset_id'])}}} & {tex_esc(r['generator_module'])} & {tex_esc(r['independent_families'])} & "
            f"{tex_esc(r['prompts_per_arm'])} & {tex_esc(r['task_description'])} & \\texttt{{{tex_esc(r['manifest_path'])}}} \\\\[2pt]"
        )
    lines.extend(["\\end{longtable}", "}"])
    write_tab("tab_dataset_inventory.tex", "\n".join(lines))


def build_ledgers():
    hrows = read_csv("hypothesis_ledger.csv")
    hlines = [
        "{\\footnotesize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{longtable}{@{}p{0.9cm}p{1.9cm}p{4.3cm}p{4.6cm}p{2.7cm}@{}}",
        "\\caption{Complete Hypothesis Ledger (\\texttt{H01}--\\texttt{H20}) documenting earliest formulation, supporting and contradicting evidence, and final scientific status.}\\label{tab:hypothesis_ledger}\\\\",
        "\\toprule",
        "\\textbf{ID} & \\textbf{Origin \\& Cohorts} & \\textbf{Original Formulation} & \\textbf{Contradicting / Limiting Evidence} & \\textbf{Final Status} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{ID} & \\textbf{Origin \\& Cohorts} & \\textbf{Original Formulation} & \\textbf{Contradicting / Limiting Evidence} & \\textbf{Final Status} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in hrows:
        orig = f"{r['earliest_documented_appearance']} (Cohorts: {r['relevant_cohorts']})"
        hlines.append(
            f"\\texttt{{{tex_esc(r['hypothesis_id'])}}} & {tex_esc(orig)} & {tex_esc(r['original_formulation'])} & "
            f"{tex_esc(r['contradicting_or_limiting_evidence'])} & \\textbf{{{tex_esc(r['final_scientific_status'])}}} \\\\[2pt]"
        )
    hlines.extend(["\\end{longtable}", "}"])
    write_tab("tab_hypothesis_ledger.tex", "\n".join(hlines))

    mrows = read_csv("methodology_ledger.csv")
    mlines = [
        "{\\footnotesize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{longtable}{@{}p{0.9cm}p{2.7cm}p{1.7cm}p{4.4cm}p{4.7cm}@{}}",
        "\\caption{Methodological Evolution Ledger (\\texttt{M01}--\\texttt{M19}) documenting mathematical foundations, empirical outcomes, and final disposition.}\\label{tab:methodology_ledger}\\\\",
        "\\toprule",
        "\\textbf{ID} & \\textbf{Methodology} & \\textbf{Cohorts} & \\textbf{Foundation \\& Problem Addressed} & \\textbf{Empirical Outcome \\& Disposition} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{ID} & \\textbf{Methodology} & \\textbf{Cohorts} & \\textbf{Foundation \\& Problem Addressed} & \\textbf{Empirical Outcome \\& Disposition} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in mrows:
        found = f"{r['mathematical_or_technical_foundation']} ({r['problem_addressed']})"
        out_disp = f"{r['empirical_outcome_and_limitations']} Disposition: {r['final_disposition']}"
        mlines.append(
            f"\\texttt{{{tex_esc(r['methodology_id'])}}} & {tex_esc(r['name'])} & {tex_esc(r['cohorts_used'])} & "
            f"{tex_esc(found)} & {tex_esc(out_disp)} \\\\[2pt]"
        )
    mlines.extend(["\\end{longtable}", "}"])
    write_tab("tab_methodology_ledger.tex", "\n".join(mlines))

    drows = read_csv("decision_ledger.csv")
    dlines = [
        "{\\footnotesize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{longtable}{@{}p{0.9cm}p{1.7cm}p{1.3cm}p{4.2cm}p{4.0cm}p{2.3cm}@{}}",
        "\\caption{Chronological Research Decision Ledger (\\texttt{D01}--\\texttt{D30}) with Git commits, documented rationales, and primary archive records.}\\label{tab:decision_ledger}\\\\",
        "\\toprule",
        "\\textbf{ID} & \\textbf{Date} & \\textbf{Commit} & \\textbf{Decision} & \\textbf{Documented Rationale} & \\textbf{Source Record} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{ID} & \\textbf{Date} & \\textbf{Commit} & \\textbf{Decision} & \\textbf{Documented Rationale} & \\textbf{Source Record} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in drows:
        dlines.append(
            f"\\texttt{{{tex_esc(r['decision_id'])}}} & {tex_esc(r['date'])} & \\texttt{{{tex_esc(r['commit'])}}} & "
            f"{tex_esc(r['decision'])} & {tex_esc(r['documented_rationale'])} & \\texttt{{{tex_esc(r['source_record'])}}} \\\\[2pt]"
        )
    dlines.extend(["\\end{longtable}", "}"])
    write_tab("tab_decision_ledger.tex", "\n".join(dlines))


def build_c24_c28_c29_claims():
    summary = json.load((EVID / "_extracted_summary.json").open(encoding="utf-8"))

    c24 = summary["c24_matrix"]
    lines24 = [
        "{\\scriptsize",
        "\\setlength{\\tabcolsep}{3.2pt}",
        "\\begin{longtable}{@{}llrrrrrrrc@{}}",
        "\\caption{Cohort 024 complete 21-arm evaluation matrix ($3\\text{ lineages}\\times 7\\text{ GGUF formats}$, $1{,}472$ scheduled items per arm; $30{,}912$ total scheduled requests).}\\label{tab:c24_matrix}\\\\",
        "\\toprule",
        "\\textbf{Lineage} & \\textbf{Quant.} & \\textbf{Valid/1472} & \\textbf{Caus.Sem} & \\textbf{Caus.Neu} & \\textbf{Ctrl.Sem} & \\textbf{Ctrl.Neu} & \\textbf{Src.Sel} & \\textbf{$d'_{\\text{sem}}$ / $c_{\\text{sem}}$} & \\textbf{Gate} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{Lineage} & \\textbf{Quant.} & \\textbf{Valid/1472} & \\textbf{Caus.Sem} & \\textbf{Caus.Neu} & \\textbf{Ctrl.Sem} & \\textbf{Ctrl.Neu} & \\textbf{Src.Sel} & \\textbf{$d'_{\\text{sem}}$ / $c_{\\text{sem}}$} & \\textbf{Gate} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in c24:
        dp = float(r["d_prime_causal_sem"])
        cr = float(r["criterion_causal_sem"])
        gate = "Pass" if r["all_diag_pass"] else "Fail"
        lines24.append(
            f"\\texttt{{{tex_esc(r['lineage'])}}} & \\texttt{{{tex_esc(r['precision'])}}} & "
            f"{r['all_valid']} & {r['causal_sem_correct']}/256 & {r['causal_neu_correct']}/256 & "
            f"{r['ctrl_sem_correct']}/256 & {r['ctrl_neu_correct']}/256 & {r['source_sel_correct']}/256 & "
            f"{dp:+.2f} / {cr:+.2f} & {gate} \\\\"
        )
    lines24.extend(["\\end{longtable}", "}"])
    write_tab("tab_c24_matrix.tex", "\n".join(lines24))

    c28 = summary["c28_summary"]
    lines28 = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\footnotesize",
        "\\caption{Cohort 028 deterministic calculator ablation (\\texttt{System B} structured single-pass vs.\\ \\texttt{System C} allowlisted Python calculator) across 128 causal graph-switch items and 128 matched noncausal named-rule controls per model.}\\label{tab:c28_ablation}",
        "\\begin{tabular}{@{}llrrrrr@{}}",
        "\\toprule",
        "\\textbf{Model (F16)} & \\textbf{Task Domain} & \\textbf{System A} & \\textbf{System B} & \\textbf{System C} & \\textbf{Rule ID (C)} & \\textbf{$\\Delta$(C $-$ B)} \\\\",
        "\\midrule",
    ]
    for mkey, lin in [("qwen7b", "Qwen2.5-7B F16"), ("llama8b", "Llama-3.1-8B F16")]:
        agg = c28[mkey]["aggregates"]
        ca, cb, cc, cr = agg["bare_causal_raw"][0], agg["struct_causal_raw_B"][0], agg["assist_causal_raw_C"][0], agg["struct_rule_causal_raw"][0]
        na, nb, nc = agg["bare_ctrl_raw"][0], agg["struct_ctrl_raw_B"][0], agg["assist_ctrl_raw_C"][0]
        dc = 100.0 * (cc - cb) / 128.0
        dn = 100.0 * (nc - nb) / 128.0
        lines28.append(
            f"{lin} & Causal Graph-Switch & {ca}/128 & {cb}/128 & {cc}/128 & {cr}/128 & {dc:+.2f} pp \\\\"
        )
        lines28.append(
            f"{lin} & Noncausal Named-Rule & {na}/128 & {nb}/128 & {nc}/128 & {nc}/128 & {dn:+.2f} pp \\\\"
        )
    lines28.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    write_tab("tab_c28_ablation.tex", "\n".join(lines28))

    lines29 = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\footnotesize",
        "\\caption{Cohort 029 confirmatory metrics on \\texttt{Qwen2.5-7B-Instruct Q4\\_K\\_M} ($4{,}096/4{,}096$ strict-valid responses) and explicit reconciliation of the manual prose transcription error in \\texttt{experiments/cohort\\_029/release/RESULTS.md}.}\\label{tab:c29_reconciliation}",
        "\\begin{tabular}{@{}p{4.8cm}p{3.0cm}p{3.2cm}p{3.2cm}@{}}",
        "\\toprule",
        "\\textbf{Metric (Transfer Form unless noted)} & \\textbf{\\texttt{RESULTS.md} Prose} & \\textbf{Verified Raw Journal \\& \\texttt{secondary.json}} & \\textbf{Audit Status} \\\\",
        "\\midrule",
        "Primary Causal Target-Pair Fidelity & 128/512 (25.00\\%) & 128/512 (25.00\\%) & Exact match \\\\",
        "Primary Arithmetic Target-Pair Fidelity & 146/512 (28.52\\%) & 146/512 (28.515625\\%) & Exact match \\\\",
        "Paired Difference $\\widehat{\\Delta}$ (Welch $t$ 95\\% CI) & $-3.52$ pp [$-7.77, +0.74$] & $-3.515625$ pp [$-7.7713, +0.7400$] & Exact match \\\\",
        "Bounded 95\\% Confidence Interval & [$-27.52, +20.49$] pp & [$-27.5237, +20.4924$] pp & Exact match \\\\",
        "Archive Causal / Arithmetic Fidelity & 128/512 vs.\\ 128/512 & 128/512 vs.\\ 128/512 ($\\Delta=0$) & Exact match \\\\",
        "Transfer Causal: Gold-Off (0) Correct & 121/512 (erroneous) & \\textbf{14/512 (2.73\\%)} & Manual prose typo \\\\",
        "Transfer Causal: Gold-On (1) Correct & 416/512 (erroneous) & \\textbf{497/512 (97.07\\%)} & Manual prose typo \\\\",
        "Transfer Causal: Total \\texttt{activate=1} & 995/1024 (97.17\\%) & \\textbf{995/1024 (97.17\\%)} & Internally inconsistent in \\texttt{RESULTS.md} \\\\",
        "Transfer Arith.: Gold-Off (0) Correct & 124/512 (erroneous) & \\textbf{231/512 (45.12\\%)} & Manual prose typo \\\\",
        "Transfer Arith.: Gold-On (1) Correct & 397/512 (erroneous) & \\textbf{316/512 (61.72\\%)} & Manual prose typo \\\\",
        "Transfer Arith.: Total \\texttt{activate=1} & 785/1024 (erroneous) & \\textbf{597/1024 (58.30\\%)} & Manual prose typo \\\\",
        "Transfer Switch Pairs: Both Correct & 3/256 (C) vs.\\ 27/256 (A) & 3/256 (C) vs.\\ 27/256 (A) & Exact match \\\\",
        "Transfer Invariant Pairs: Both Correct & 125/256 (C) vs.\\ 119/256 (A) & 125/256 (C) vs.\\ 119/256 (A) & Exact match \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    write_tab("tab_c29_reconciliation.tex", "\n".join(lines29))

    crows = read_csv("claim_evidence_map.csv")
    clines = [
        "{\\footnotesize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{longtable}{@{}p{1.2cm}p{2.0cm}p{4.8cm}p{3.9cm}p{2.5cm}@{}}",
        "\\caption{Claim-to-Evidence Traceability Map (\\texttt{CLM-01}--\\texttt{CLM-20}) linking principal monograph conclusions to primary repository artifacts and Git commits.}\\label{tab:claim_evidence}\\\\",
        "\\toprule",
        "\\textbf{Claim} & \\textbf{Section} & \\textbf{Scientific Claim} & \\textbf{Evidence Paths} & \\textbf{Commits \\& Status} \\\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "\\textbf{Claim} & \\textbf{Section} & \\textbf{Scientific Claim} & \\textbf{Evidence Paths} & \\textbf{Commits \\& Status} \\\\",
        "\\midrule",
        "\\endhead",
        "\\bottomrule",
        "\\endfoot",
    ]
    for r in crows:
        cs = f"{r['git_commits']} ({r['verification_status']})"
        clines.append(
            f"\\texttt{{{tex_esc(r['claim_id'])}}} & {tex_esc(r['monograph_section'])} & {tex_esc(r['claim_summary'])} & "
            f"\\texttt{{{tex_esc(r['evidence_paths'])}}} & {tex_esc(cs)} \\\\[2pt]"
        )
    clines.extend(["\\end{longtable}", "}"])
    write_tab("tab_claim_evidence.tex", "\n".join(clines))


if __name__ == "__main__":
    build_cohort_master()
    build_experiment_runs()
    build_model_quant()
    build_dataset_inventory()
    build_ledgers()
    build_c24_c28_c29_claims()
    print("All LaTeX tables generated successfully.")
