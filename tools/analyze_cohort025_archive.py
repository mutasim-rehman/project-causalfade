"""Retrospective methods screen of cohorts 001–024; no new model inference.

This is a post-outcome development analysis, not a preregistered confirmation.
Existing results and raw-file identities are preserved. No historical scorer is changed.
"""
from collections import Counter, defaultdict
import argparse
import json
import math
from pathlib import Path
from statistics import NormalDist

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(cohort, run):
    path = EXPERIMENTS / f"cohort_{cohort:03d}" / run / "results.json"
    data = read(path)
    if not isinstance(data, list) or not data or len({x["task_id"] for x in data}) != len(data):
        raise ValueError(f"Bad scored rows: {path}")
    if cohort in (15, 16, 17):
        truth_cohort = 16 if cohort == 17 else cohort
        truth_path = EXPERIMENTS / f"cohort_{truth_cohort:03d}" / "input" / "oracle_truth.jsonl"
        truth = {x["task_id"]: x for x in (json.loads(line) for line in truth_path.read_text(encoding="utf-8").splitlines())}
        if set(truth) != {x["task_id"] for x in data}:
            raise ValueError(f"Truth/result ID mismatch: {path}")
        data = [{**truth[x["task_id"]], **x} for x in data]
    return data


def valid(row):
    return bool(row.get("valid_answer", row.get("valid_action", False)))


def answer(row):
    if not valid(row):
        return "invalid"
    raw = row.get("answer")
    if raw in ("activate", "X=1", 1):
        return "on"
    if raw in ("leave_off", "X=0", 0):
        return "off"
    if raw in ("A", "B"):
        return raw
    if row.get("activate") in (0, 1):
        return "on" if row["activate"] else "off"
    return str(raw)


def joint_mi(pairs):
    total = len(pairs)
    if not total:
        return None
    both, aa, bb = Counter(pairs), Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    return sum((n / total) * math.log2(n * total / (aa[a] * bb[b])) for (a, b), n in both.items())


def dependence(data):
    """Three-category scheduled-response information; no latent process interpretation."""
    a = [(answer(r), r["causal_positive"]) for r in data]
    conditional = 0.0
    for truth in (0, 1):
        subset = [r for r in data if r["causal_positive"] == truth]
        conditional += len(subset) / len(data) * joint_mi([(answer(r), r["association_positive"]) for r in subset])
    return {"scheduled": len(data), "valid": sum(valid(r) for r in data),
            "response_alphabet": ["on", "off", "invalid"],
            "mi_answer_true_sign_bits": joint_mi(a),
            "cmi_answer_association_given_true_sign_bits": conditional,
            "estimator": "empirical plug-in; descriptive; no finite-sample correction"}


def core_decision(row, cohort):
    if cohort <= 17:
        return True
    if cohort in (18, 19):
        return row["task_type"] == "causal" and row.get("contract", "semantic") == "semantic"
    if cohort == 20:
        return row["task_type"].startswith(("aligned_", "conflict_"))
    if cohort in (21, 22):
        return row["task_type"] == "ordinary"
    return row["task_type"] == "decision" and row.get("contract", "semantic") == "semantic"


def decision_sdt(data):
    signal = [r for r in data if r["causal_positive"] == 1 and valid(r)]
    noise = [r for r in data if r["causal_positive"] == 0 and valid(r)]
    hits = sum(answer(r) == "on" for r in signal)
    false = sum(answer(r) == "on" for r in noise)
    out = {"scheduled": len(data), "valid": len(signal) + len(noise),
           "beneficial_valid": len(signal), "harmful_valid": len(noise),
           "hits": hits, "false_alarms": false, "d_prime": None, "criterion": None,
           "boundary_correction": "(count+0.5)/(valid_direction_n+1)"}
    if signal and noise:
        zh = NormalDist().inv_cdf((hits + .5) / (len(signal) + 1))
        zf = NormalDist().inv_cdf((false + .5) / (len(noise) + 1))
        out["d_prime"], out["criterion"] = zh - zf, -.5 * (zh + zf)
    return out


def outcome(r):
    return int(r["correct"])


def transitions(ref, other, predicate=lambda r: True):
    ref = {r["task_id"]: r for r in ref if predicate(r)}
    other = {r["task_id"]: r for r in other if predicate(r)}
    if set(ref) != set(other) or not ref:
        raise ValueError("Paired transition task IDs do not match")
    counts = Counter((outcome(ref[k]), outcome(other[k])) for k in ref)
    return {"n": len(ref), "p00": counts[0, 0], "p01_gain": counts[0, 1],
            "p10_loss": counts[1, 0], "p11": counts[1, 1],
            "net_other_minus_reference_pp": 100 * (counts[0, 1] - counts[1, 0]) / len(ref),
            "invalid_reference": sum(not valid(r) for r in ref.values()),
            "invalid_other": sum(not valid(r) for r in other.values())}


def pair_key(r, omitted):
    return tuple(r.get(k) for k in ("family_id", "task_type", "contract", "causal_positive",
                                      "condition", "presentation_order", "randomized_name", "answer_order") if k != omitted)


def metamorphic(data, factor, predicate=lambda r: True):
    groups = defaultdict(list)
    for row in data:
        if predicate(row):
            groups[pair_key(row, factor)].append(row)
    if not groups or any(len(v) != 2 for v in groups.values()):
        raise ValueError(f"Incomplete {factor} pairs")
    total = len(groups)
    both_valid = 0
    transformed = 0
    both_correct = 0
    for pair in groups.values():
        a, b = pair
        both_correct += bool(a["correct"] and b["correct"])
        if valid(a) and valid(b):
            both_valid += 1
            expected_same = not (factor == "randomized_name" and a["task_type"] == "source_selection")
            transformed += (answer(a) == answer(b)) == expected_same
    return {"pairs": total, "both_valid_pairs": both_valid,
            "prediction_transform_correct_on_valid_pairs": transformed,
            "both_oracle_correct_pairs": both_correct}


def order_cells(data, predicate):
    selected = [r for r in data if predicate(r)]
    out = {}
    for order in ("historical_first", "randomized_first"):
        cell = [r for r in selected if r["presentation_order"] == order]
        if not cell:
            raise ValueError("Missing evidence-order cell")
        out[order] = {"correct": sum(outcome(r) for r in cell), "n": len(cell)}
    out["historical_minus_randomized_pp"] = 100 * (out["historical_first"]["correct"] / out["historical_first"]["n"]
                                                - out["randomized_first"]["correct"] / out["randomized_first"]["n"])
    return out


def inventory():
    out = {}
    for cohort in range(1, 25):
        folder = EXPERIMENTS / f"cohort_{cohort:03d}"
        runs = {}
        for result in sorted(folder.rglob("results.json")):
            run = result.parent
            if not (run.name.startswith("run_") or run.parent.name == "runs"):
                continue
            data = read(result)
            raw_path = run / "raw_responses.jsonl"
            raw_ids = [json.loads(line)["task_id"] for line in raw_path.read_text(encoding="utf-8").splitlines()]
            result_ids = [r["task_id"] for r in data]
            status_path = run / "status.json"
            status = read(status_path)["status"] if status_path.exists() else "unrecorded"
            if status == "success" and (len(raw_ids) != len(result_ids) or set(raw_ids) != set(result_ids)
                                        or len(raw_ids) != len(set(raw_ids))):
                raise ValueError(f"Successful run raw/result coverage mismatch: {run}")
            runs[run.name] = {"status": status, "scored": len(data), "raw_attempts": len(raw_ids),
                              "stored_strict_valid": sum(valid(r) for r in data),
                              "families": len({r["family_id"] for r in data}),
                              "raw_ids_unique": len(raw_ids) == len(set(raw_ids)),
                              "raw_ids_in_results": set(raw_ids) <= set(result_ids),
                              "results_sha256": sha256(result), "raw_sha256": sha256(raw_path)}
        out[f"cohort_{cohort:03d}"] = runs
    return out


def analyze():
    catalog = inventory()
    prior024 = read(EXPERIMENTS / "cohort_024" / "development_analysis_archive.json")
    for arm, record in catalog["cohort_024"].items():
        if record["raw_sha256"] != prior024["audit"]["raw_sha256"][arm]:
            raise ValueError("Cohort 024 raw hash differs from prior rescore: " + arm)
    output = {"classification": "post_outcome_retrospective_development_screen_no_inference",
              "source_cohorts": list(catalog), "inventory": catalog,
              "inventory_note": "Stored strict-parser validity is counted; early cohort summaries sometimes report a separately documented fence-tolerant interpretation. The interrupted cohort 008 attempt is inventoried, not used as completed evidence.",
              "method_applicability": {
                  "graph_switch": "not estimable: no archived identical-observation, different-graph intervention pairs",
                  "psychophysical_capture_threshold": "not estimable: no dense independently crossed causal and observational strength grid; cohort 018 has two causal strengths and fixed observational magnitude",
                  "metamorphic_invariance": "answer order, source name, evidence order, and response contract estimable within cohort 024; graph equivariance absent",
                  "signal_detection": "strict-parser core-decision summaries supplied for all 58 successful runs; early fenced responses can yield null coordinates; equal-variance latent interpretation unverified",
                  "information_dependence": "descriptive scheduled three-category response dependence estimable in cohort 024",
                  "precision_by_presentation_interaction": "descriptive within-cohort evidence-order interaction estimable in cohorts 015–017 and 024; do not pool distinct prompt scaffolds",
                  "assay_quality_and_generalizability": "component/control success and family variation measurable; eight families in cohort 024 do not validate a latent scale or broad transfer",
                  "four_parameter_lapse_curve": "not identified: no dense graded asymptotes; strict-invalid output can be counted directly",
                  "crossed_sdt_glmm": "trial-level descriptive slopes could be fit, but a heteroskedastic latent scale and psychological d-prime are not identified from these binary logs alone",
                  "paired_precision_transitions": "estimable for same-task within-lineage arms of cohorts 015, 016, 017, 024; 017 Q8 is not F16",
                  "source_hint_rescue": "partial observational comparison in cohort 021; source and neutral hints only, not full factorial or length-matched placebo",
                  "irt_dif": "not identified: no validated stable anchor scale; cohort 024 controls fail in key arms",
                  "double_pass": "no clean independent same-checkpoint strict-valid exact-repeat block; interrupted cohort 008 is unsuitable",
                  "transportability": "not estimable: no target-population switch tasks",
                  "mechanistic_logits_activation_patching": "not estimable: archived responses lack token logits and internal activations",
                  "latency_diffusion_meta_dprime": "not estimable: no validated cognitive RT or confidence task"},
              "core_decision_sdt": {}, "metamorphic_024": {}, "information_024": {}, "precision_transitions": {},
              "evidence_order": {}, "order_interactions": {}, "source_hint_021": {}, "strength_018": {}}

    for cohort in range(1, 25):
        name = f"cohort_{cohort:03d}"
        for run, record in catalog[name].items():
            if record["status"] != "success":
                continue
            selected = [r for r in rows(cohort, f"runs/{run}" if cohort == 24 else run) if core_decision(r, cohort)]
            if selected:
                output["core_decision_sdt"][f"{cohort:03d}|{run}"] = decision_sdt(selected)

    # Cohort 018 permits only a two-point strength comparison, not a threshold fit.
    pilot = rows(18, "run_001_7b_f16")
    for kind in ("causal", "noncausal"):
        for strength in (.04, .12):
            for true_sign in (0, 1):
                for association_sign in (0, 1):
                    subset = [r for r in pilot if r["task_type"] == kind and r["effect_size"] == strength
                              and r["causal_positive"] == true_sign and r["association_positive"] == association_sign]
                    if not subset:
                        raise ValueError("Missing cohort 018 strength cell")
                    output["strength_018"][f"{kind}|effect={strength}|true={true_sign}|association={association_sign}"] = {
                        "scheduled": len(subset), "valid": sum(valid(r) for r in subset),
                        "correct": sum(outcome(r) for r in subset),
                        "activate_valid": sum(r.get("activate") == 1 for r in subset if valid(r))}

    # Same-arm behavioral transformations in the complete 024 factorial fixture.
    root24 = EXPERIMENTS / "cohort_024" / "runs"
    arm_names = sorted(p.name for p in root24.iterdir() if (p / "results.json").is_file())
    for arm in arm_names:
        data = rows(24, f"runs/{arm}")
        transformations = {}
        for kind in ("decision", "source_selection", "noncausal_control", "randomized_only", "numerical_control"):
            for contract in (("semantic", "neutral") if kind in ("decision", "noncausal_control", "randomized_only") else ("semantic",)):
                pred = lambda r, k=kind, c=contract: r["task_type"] == k and r["contract"] == c
                tag = f"{kind}|{contract}"
                transformations[f"answer_order|{tag}"] = metamorphic(data, "answer_order", pred)
                transformations[f"source_name|{tag}"] = metamorphic(data, "randomized_name", pred)
                if kind in ("decision", "source_selection", "noncausal_control"):
                    transformations[f"evidence_order|{tag}"] = metamorphic(data, "presentation_order", pred)
        for kind in ("decision", "noncausal_control", "randomized_only"):
            transformations[f"response_contract|{kind}"] = metamorphic(data, "contract", lambda r, k=kind: r["task_type"] == k)
        output["metamorphic_024"][arm] = transformations
        output["information_024"][arm] = {
            f"{kind}|{contract}": dependence([r for r in data if r["task_type"] == kind and r["contract"] == contract])
            for kind in ("decision", "noncausal_control") for contract in ("semantic", "neutral")}
        if arm.endswith(("_f16", "_q4_k_m")):
            output["evidence_order"][f"024|{arm}|semantic_conflict"] = order_cells(
                data, lambda r: r["task_type"] == "decision" and r["contract"] == "semantic" and r["condition"] == "conflict")

    # Direct within-lineage precision comparisons on exactly matched task IDs.
    pairs = [(15, "run_001_7b_f16", "run_002_7b_q4_k_m"),
             (16, "run_001_7b_f16", "run_002_7b_q4_k_m"),
             (17, "run_001_14b_q8_0", "run_002_14b_q4_k_m")]
    for cohort, ref_name, other_name in pairs:
        ref, other = rows(cohort, ref_name), rows(cohort, other_name)
        output["precision_transitions"][f"{cohort:03d}|{other_name}"] = {
            "reference": ref_name, "all": transitions(ref, other),
            "conflict": transitions(ref, other, lambda r: bool(r["conflict"])),
            "aligned": transitions(ref, other, lambda r: not r["conflict"])}
        for name, data in ((ref_name, ref), (other_name, other)):
            output["evidence_order"][f"{cohort:03d}|{name}|conflict"] = order_cells(data, lambda r: bool(r["conflict"]))
    for lineage in ("qwen7b", "mistral7b", "llama8b"):
        ref = rows(24, f"runs/{lineage}_f16")
        for arm in [x for x in arm_names if x.startswith(lineage + "_") and x != lineage + "_f16"]:
            other = rows(24, f"runs/{arm}")
            detail = {"reference": lineage + "_f16"}
            for tag, kind, contract in (("causal_semantic", "decision", "semantic"),
                                        ("causal_neutral", "decision", "neutral"),
                                        ("noncausal_semantic", "noncausal_control", "semantic"),
                                        ("source_selection", "source_selection", "semantic")):
                detail[tag] = transitions(ref, other, lambda r, k=kind, c=contract: r["task_type"] == k and r["contract"] == c)
            output["precision_transitions"][f"024|{arm}"] = detail

    for cohort, ref_name, other_name in pairs:
        a = output["evidence_order"][f"{cohort:03d}|{ref_name}|conflict"]["historical_minus_randomized_pp"]
        b = output["evidence_order"][f"{cohort:03d}|{other_name}|conflict"]["historical_minus_randomized_pp"]
        output["order_interactions"][f"{cohort:03d}|{other_name}"] = {
            "other_minus_reference_order_gap_pp": b - a, "reference": ref_name,
            "note": "post-outcome descriptive; cohort 017 compares Q4 with Q8, not F16" if cohort == 17 else "post-outcome descriptive; earlier frozen analyses govern original claims"}
    for lineage in ("qwen7b", "mistral7b", "llama8b"):
        ref_name, other_name = lineage + "_f16", lineage + "_q4_k_m"
        a = output["evidence_order"][f"024|{ref_name}|semantic_conflict"]["historical_minus_randomized_pp"]
        b = output["evidence_order"][f"024|{other_name}|semantic_conflict"]["historical_minus_randomized_pp"]
        output["order_interactions"][f"024|{other_name}"] = {
            "other_minus_reference_order_gap_pp": b - a, "reference": ref_name,
            "note": "post-outcome semantic conflict subset; eight families; distinct from cohort 016 scaffold"}

    guide = rows(21, "run_001_7b_f16")
    lookup = defaultdict(dict)
    for r in guide:
        if r["task_type"] in ("ordinary", "guided", "neutral_guidance"):
            lookup[(r["family_id"], r["stem_id"])][r["task_type"]] = r
    if len(lookup) != 128 or any(set(v) != {"ordinary", "guided", "neutral_guidance"} for v in lookup.values()):
        raise ValueError("Cohort 021 hint matching failed")
    for kind in ("ordinary", "guided", "neutral_guidance"):
        output["source_hint_021"][kind] = {"correct": sum(v[kind]["correct"] for v in lookup.values()),
                                            "n": len(lookup)}
    for kind in ("guided", "neutral_guidance"):
        counts = Counter((v["ordinary"]["correct"], v[kind]["correct"]) for v in lookup.values())
        output["source_hint_021"][f"{kind}_versus_ordinary"] = {"p00": counts[0, 0], "p01_gain": counts[0, 1],
                                                                  "p10_loss": counts[1, 0], "p11": counts[1, 1]}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result = analyze()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Cohort 025 archive screen: {len(result['source_cohorts'])} prior cohorts -> {args.out}")


if __name__ == "__main__":
    main()
