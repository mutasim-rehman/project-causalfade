"""Versioned within-world response-contract development experiment."""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
from statistics import mean

import numpy as np

from .worlds import World
from .sensitivity import (ORDERS, STRENGTHS, OBSERVATIONAL_STRENGTH, cluster_interval,
                          describe, digest, read_jsonl, render as old_render, sdt,
                          write_json, write_jsonl)

VERSION = "response-contract-development-v1"
CONTRACTS = ("semantic", "neutral_forward", "neutral_reverse")
GATE = {"valid_rate": .90, "causal_accuracy": .625,
        "conflict_accuracy_each_order": .55, "comprehension_accuracy": .875}


def contract_instruction(contract):
    if contract == "semantic":
        return ('Return exactly one JSON object: {"decision":"activate"} or '
                '{"decision":"leave_off"}.')
    mapping = ('choice=K means activate X; choice=M means leave X off.' if contract == "neutral_forward"
               else 'choice=K means leave X off; choice=M means activate X.')
    return mapping + ' Return exactly one JSON object: {"choice":"K"} or {"choice":"M"}.'


def render(row):
    kind = row["task_type"]
    if kind in ("causal", "noncausal"):
        # The v1 renderer supplies the same validated evidence/wording; strip only its old contract.
        evidence = old_render({**row, "mapping": 0}).rsplit("\n", 1)[0]
    elif kind == "encoding_check":
        evidence = ('The requested action is activate X.' if row["optimal_action"] else
                    'The requested action is leave X off.') + ' Encode that requested action.'
    else:
        first = row["presentation_order"] == ORDERS[0]
        evidence = (f'Study {row["randomized_name"]} assigned X randomly. '
                    f'Study {row["historical_name"]} used historical operator choices. '
                    f'Study {row["randomized_name"] if first else row["historical_name"]} is listed first. '
                    'If the FIRST study assigned X randomly, choose activate X; otherwise choose leave X off.')
    return evidence + "\n" + contract_instruction(row["contract"]) + \
        ' Do not include a Markdown fence, explanation, another field, or any other text.'


def _append(tasks, truth, row, seed):
    task_id = hashlib.sha256(json.dumps([seed, VERSION, row], sort_keys=True).encode()).hexdigest()[:24]
    row = {**row, "task_id": task_id}
    tasks.append({"task_id": task_id, "family_id": row["family_id"],
                  "evidence_mode": "exact", "prompt": render(row)})
    truth.append(row)


def generate(directory, families=8, seed=20261115):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError(directory)
    if families != 8:
        raise ValueError("Version 1 fixes eight development families")
    rng = random.Random(seed)
    tasks, truth = [], []
    names = [0, 1] * 4
    rng.shuffle(names)
    for f in range(families):
        family = f"contracts-{seed}-{f:04d}"
        gap, offset = rng.uniform(.68, .78), rng.uniform(-.04, .04)
        randomized_name, historical_name = (("B", "A") if names[f] else ("A", "B"))
        common = dict(family_id=family, evidence_mode="exact", severity_gap=gap,
                      rate_offset=offset, randomized_name=randomized_name,
                      historical_name=historical_name)
        for strength, t, s, order, kind in itertools.product(
                STRENGTHS, (0, 1), (0, 1), ORDERS, ("causal", "noncausal")):
            assignment = (OBSERVATIONAL_STRENGTH - strength if t == s else
                          OBSERVATIONAL_STRENGTH + strength) / gap
            world = World(family, t, s, strength, gap, assignment)
            stem = hashlib.sha256(json.dumps([family, strength, t, s, order, kind]).encode()).hexdigest()[:20]
            base = {**world.truth(), **common, "task_type": kind, "presentation_order": order,
                    "decision_stem_id": stem,
                    "do_success_x0": float(world.do_means[0] + offset),
                    "do_success_x1": float(world.do_means[1] + offset),
                    "randomized_rates": (world.do_means + offset).tolist(),
                    "historical_rates": (world.observational_means + offset).tolist()}
            for contract in CONTRACTS:
                _append(tasks, truth, {**base, "contract": contract,
                                       "token_to_action": ({"K": 1, "M": 0} if contract == "neutral_forward" else
                                                           {"K": 0, "M": 1} if contract == "neutral_reverse" else
                                                           {"activate": 1, "leave_off": 0})}, seed)
        for contract, action in itertools.product(CONTRACTS, (0, 1)):
            _append(tasks, truth, {**common, "task_type": "encoding_check",
                                   "contract": contract, "optimal_action": action,
                                   "presentation_order": ORDERS[action],
                                   "token_to_action": ({"K": 1, "M": 0} if contract == "neutral_forward" else
                                                       {"K": 0, "M": 1} if contract == "neutral_reverse" else
                                                       {"activate": 1, "leave_off": 0})}, seed)
        for action in (0, 1):
            _append(tasks, truth, {**common, "task_type": "source_check",
                                   "contract": "semantic", "optimal_action": action,
                                   "presentation_order": ORDERS[0] if action else ORDERS[1],
                                   "token_to_action": {"activate": 1, "leave_off": 0}}, seed)
    by_id = {r["task_id"]: r for r in truth}
    for _ in range(100):
        rng.shuffle(tasks)
        ordered_stems = [by_id[t["task_id"]].get("decision_stem_id") for t in tasks]
        if all(not a or a != b for a, b in zip(ordered_stems, ordered_stems[1:])):
            break
    else:
        raise RuntimeError("Could not separate adjacent decision twins")
    directory.mkdir(parents=True)
    write_jsonl(directory / "public_tasks.jsonl", tasks)
    write_jsonl(directory / "oracle_truth.jsonl", truth)
    manifest = {"version": VERSION, "classification": "development_only_not_confirmatory",
                "families": families, "tasks": 832, "seed": seed, "contracts": list(CONTRACTS),
                "causal_strengths": list(STRENGTHS), "observational_strength": OBSERVATIONAL_STRENGTH,
                "gate": GATE, "gate_subset": "semantic",
                "schedule_policy": "one complete seeded shuffle; fresh context per request; twins interleaved",
                "analysis_specification": "scheduled-task accuracy; semantic gate; family-cluster paired differences and intervals; contract-specific SDT",
                "file_sha256": {name: digest(directory / name) for name in
                                ("public_tasks.jsonl", "oracle_truth.jsonl")}}
    write_json(directory / "manifest.json", manifest)
    validate(directory)
    return manifest


def validate(directory):
    directory = Path(directory)
    m = json.loads((directory / "manifest.json").read_text())
    if (m["version"], m["classification"], m["families"], m["tasks"], m["contracts"],
        m["gate"], m["gate_subset"]) != (VERSION, "development_only_not_confirmatory", 8, 832,
                                         list(CONTRACTS), GATE, "semantic"):
        raise ValueError("Protocol mismatch")
    if m["causal_strengths"] != list(STRENGTHS) or m["observational_strength"] != OBSERVATIONAL_STRENGTH:
        raise ValueError("Strength protocol mismatch")
    for name in ("public_tasks.jsonl", "oracle_truth.jsonl"):
        if digest(directory / name) != m["file_sha256"][name]:
            raise ValueError("Fixture checksum mismatch")
    tasks, truth = read_jsonl(directory / "public_tasks.jsonl"), read_jsonl(directory / "oracle_truth.jsonl")
    tids, ids = [r["task_id"] for r in tasks], [r["task_id"] for r in truth]
    if len(tasks) != 832 or len(truth) != 832 or len(set(tids)) != 832 or len(set(ids)) != 832 or set(tids) != set(ids):
        raise ValueError("Duplicate, missing, or unexpected task")
    public = {r["task_id"]: r for r in tasks}
    ordered_truth = {r["task_id"]: r for r in truth}
    ordered_stems = [ordered_truth[t["task_id"]].get("decision_stem_id") for t in tasks]
    if any(a and a == b for a, b in zip(ordered_stems, ordered_stems[1:])):
        raise ValueError("Adjacent decision twins in schedule")
    cells = defaultdict(set)
    stems = defaultdict(list)
    family_params = {}
    for r in truth:
        if r["contract"] not in CONTRACTS or r["token_to_action"] != (
                {"activate": 1, "leave_off": 0} if r["contract"] == "semantic" else
                {"K": 1, "M": 0} if r["contract"] == "neutral_forward" else {"K": 0, "M": 1}):
            raise ValueError("Contract mapping mismatch")
        p = public[r["task_id"]]
        if set(p) != {"task_id", "family_id", "evidence_mode", "prompt"} or p["prompt"] != render(r) or p["family_id"] != r["family_id"]:
            raise ValueError("Public prompt mismatch")
        params = (r["severity_gap"], r["rate_offset"], r["randomized_name"], r["historical_name"])
        if r["family_id"] in family_params and family_params[r["family_id"]] != params:
            raise ValueError("Family parameters changed")
        family_params[r["family_id"]] = params
        if {r["randomized_name"], r["historical_name"]} != {"A", "B"}:
            raise ValueError("Study names invalid")
        kind = r["task_type"]
        if kind in ("causal", "noncausal"):
            world = World(r["family_id"], r["causal_positive"], r["association_positive"],
                          r["effect_size"], r["severity_gap"], r["assignment_strength"])
            offset = r["rate_offset"]
            if not math.isfinite(offset) or not -.04 <= offset <= .04 or np.any((world.outcome+offset <= 0) | (world.outcome+offset >= 1)):
                raise ValueError("Offset or positivity violation")
            expected = world.truth()
            expected["do_success_x0"] += offset
            expected["do_success_x1"] += offset
            if any(not (math.isclose(r[k], v, abs_tol=1e-12, rel_tol=0) if isinstance(v, float) else r[k] == v)
                   for k, v in expected.items()):
                raise ValueError("Oracle mismatch")
            if not np.allclose(r["randomized_rates"], world.do_means+offset, atol=1e-12, rtol=0) or not np.allclose(r["historical_rates"], world.observational_means+offset, atol=1e-12, rtol=0):
                raise ValueError("Rate mismatch")
            if r["effect_size"] not in STRENGTHS or not math.isclose(abs(world.observational_difference), OBSERVATIONAL_STRENGTH, abs_tol=1e-12):
                raise ValueError("Strength mismatch")
            for rates, sign in ((world.do_means+offset, r["causal_positive"]), (world.observational_means+offset, r["association_positive"])):
                shown = [float(f"{x:.6f}") for x in rates]
                if shown[0] == shown[1] or int(shown[1] > shown[0]) != sign:
                    raise ValueError("Display rounding mismatch")
            cell = (kind, r["effect_size"], r["causal_positive"], r["association_positive"], r["presentation_order"], r["contract"])
            stems[(r["family_id"], r["decision_stem_id"])].append(r)
        elif kind == "encoding_check":
            cell = (kind, r["contract"], r["optimal_action"])
        elif kind == "source_check":
            if r["contract"] != "semantic" or r["optimal_action"] != int(r["presentation_order"] == ORDERS[0]):
                raise ValueError("Source check mismatch")
            cell = (kind, r["optimal_action"])
        else:
            raise ValueError("Task type invalid")
        if cell in cells[r["family_id"]]:
            raise ValueError("Duplicate cell")
        cells[r["family_id"]].add(cell)
    expected_cells = set(itertools.product(("causal", "noncausal"), STRENGTHS, (0,1), (0,1), ORDERS, CONTRACTS))
    expected_cells |= {("encoding_check", c, a) for c in CONTRACTS for a in (0,1)}
    expected_cells |= {("source_check", a) for a in (0,1)}
    if len(cells) != 8 or any(c != expected_cells for c in cells.values()) or len(stems) != 256:
        raise ValueError("Incomplete within-family crossing")
    for variants in stems.values():
        if {r["contract"] for r in variants} != set(CONTRACTS):
            raise ValueError("Missing contract variant")
        first = variants[0]
        for r in variants[1:]:
            if r["optimal_action"] != first["optimal_action"] or r["randomized_rates"] != first["randomized_rates"] or r["historical_rates"] != first["historical_rates"] or r["presentation_order"] != first["presentation_order"]:
                raise ValueError("Twin evidence or oracle mismatch")
            if render(r).rsplit("\n",1)[0] != render(first).rsplit("\n",1)[0]:
                raise ValueError("Twin public evidence mismatch")
    if Counter(r["randomized_name"] for r in truth if r["task_type"] == "source_check") != {"A": 8, "B": 8}:
        raise ValueError("Source-name imbalance")
    return {"valid": True, "tasks": len(tasks), "families": len(cells),
            "decision_stems": len(stems), "manifest_sha256": digest(directory / "manifest.json")}


def decode(text, contract):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("Duplicate key")
            out[key] = value
        return out
    try:
        obj = json.loads(text, object_pairs_hook=unique)
        if not isinstance(obj, dict):
            return None
        if contract == "semantic":
            return {"activate": 1, "leave_off": 0}.get(obj["decision"]) if set(obj) == {"decision"} and type(obj.get("decision")) is str else None
        if set(obj) != {"choice"} or type(obj.get("choice")) is not str:
            return None
        return ({"K": 1, "M": 0} if contract == "neutral_forward" else {"K": 0, "M": 1}).get(obj["choice"])
    except (ValueError, TypeError, KeyError):
        return None


def score_records(truth, raw):
    ids = {r["task_id"] for r in truth}
    records = {}
    for r in raw:
        if r["task_id"] not in ids or r["task_id"] in records:
            raise ValueError("Unknown or duplicate raw task ID")
        records[r["task_id"]] = r
    rows = []
    for t in truth:
        record = records.get(t["task_id"])
        action = None
        if record and not record.get("execution_error"):
            try:
                choice = record["response"]["choices"][0]
                if choice.get("finish_reason") == "stop":
                    action = decode(choice["message"]["content"], t["contract"])
            except (KeyError, IndexError, TypeError):
                pass
        rows.append({**t, "completed": record is not None, "valid_action": action is not None,
                     "activate": action, "correct": int(action == t["optimal_action"])})
    return rows


def competence(rows, thresholds):
    subset = [r for r in rows if r["contract"] == "semantic"]
    causal = [r for r in subset if r["task_type"] == "causal"]
    checks = {"all_completed": bool(rows) and all(r["completed"] for r in rows),
              "semantic_valid_rate": describe(subset)["valid_rate"],
              "semantic_causal_correct": sum(r["correct"] for r in causal),
              "semantic_comprehension_correct": sum(r["correct"] for r in subset if r["task_type"] in ("encoding_check", "source_check")),
              "semantic_conflict_correct_each_order": {o: sum(r["correct"] for r in causal if r["conflict"] and r["presentation_order"] == o) for o in ORDERS}}
    passed = checks["all_completed"] and checks["semantic_valid_rate"] >= thresholds["valid_rate"] and checks["semantic_causal_correct"] >= 80 and checks["semantic_comprehension_correct"] >= 28 and all(v >= 18 for v in checks["semantic_conflict_correct_each_order"].values())
    return {"passed": bool(passed), "checks": checks, "thresholds": thresholds,
            "count_cutoffs": {"semantic_valid": 260, "semantic_causal": 80,
                              "semantic_conflict_each_order": 18, "semantic_comprehension": 28},
            "interpretation": "operational development screen, not a powered competence test"}


def analyze_rows(rows):
    by_contract_type = {f"{c}|{k}": describe([r for r in rows if r["contract"] == c and r["task_type"] == k])
                        for c in CONTRACTS for k in ("causal", "noncausal", "encoding_check", "source_check")
                        if any(r["contract"] == c and r["task_type"] == k for r in rows)}
    effects = {}
    for kind, c1, c2 in itertools.product(("causal", "noncausal"), CONTRACTS, CONTRACTS):
        if CONTRACTS.index(c1) >= CONTRACTS.index(c2):
            continue
        paired = defaultdict(dict)
        for r in rows:
            if r["task_type"] == kind:
                paired[r["family_id"], r["decision_stem_id"]][r["contract"]] = r
        by_family = defaultdict(list)
        flips = Counter()
        for (family, _), variants in paired.items():
            a, b = variants[c1], variants[c2]
            by_family[family].append(b["correct"] - a["correct"])
            if a["valid_action"] and b["valid_action"]:
                flips[f'{a["activate"]}_to_{b["activate"]}'] += 1
        effects[f"{kind}|{c2}_minus_{c1}"] = {**cluster_interval([mean(v) for v in by_family.values()]),
                                               "valid_paired_action_flips": dict(flips)}
    order = {}
    for contract, kind, conflict in itertools.product(CONTRACTS, ("causal", "noncausal"), (False, True)):
        families = defaultdict(lambda: defaultdict(list))
        for r in rows:
            if r["contract"] == contract and r["task_type"] == kind and r["conflict"] == conflict:
                families[r["family_id"]][r["presentation_order"]].append(r["correct"])
        order[f"{contract}|{kind}|conflict={conflict}"] = cluster_interval([
            mean(v[ORDERS[1]]) - mean(v[ORDERS[0]]) for v in families.values()])
    strata = {}
    for contract, strength, order_name in itertools.product(CONTRACTS, STRENGTHS, ORDERS):
        group = [r for r in rows if r["contract"] == contract and r["task_type"] == "causal" and
                 r["effect_size"] == strength and r["presentation_order"] == order_name]
        strata[f"{contract}|strength={strength}|{order_name}"] = {"corrected": sdt(group),
                                                                   "uncorrected_sensitivity": sdt(group, False)}
    return {"by_contract_and_task_type": by_contract_type, "paired_contract_accuracy": effects,
            "historical_minus_randomized_accuracy": order, "causal_sdt_strata": strata,
            "limitations": ["Family-cluster intervals use only eight development families.",
                            "SDT assumes unverified equal-variance Gaussian evidence; invalid responses are excluded only from SDT rates.",
                            "Semantic-versus-neutral changes multiple response properties, not only mapping.",
                            "Two strengths do not establish a full psychophysical curve."]}
