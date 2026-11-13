"""Development-only causal sensitivity tasks and strict semantic scoring.

The response key remains ``activate`` for transport compatibility, but its
binary value is a response token. Always decode the per-task mapping first.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
from statistics import NormalDist, mean

import numpy as np

from .worlds import World

VERSION = "sensitivity-development-v1"
ORDERS = ("randomized_first", "historical_first")
STRENGTHS = (0.04, 0.12)
OBSERVATIONAL_STRENGTH = 0.36
GATE = {"valid_rate": 0.90, "causal_accuracy": 0.625,
        "conflict_accuracy_each_order": 0.55, "comprehension_accuracy": 0.875}


def digest(path):
    with Path(path).open("rb") as stream:
        h = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()]


def write_json(path, value):
    path = Path(path)
    staging = path.with_suffix(path.suffix + ".tmp")
    staging.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    staging.replace(path)


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, sort_keys=True, allow_nan=False) + "\n"
                                  for r in rows), encoding="utf-8", newline="\n")


def render(truth):
    mapping = truth["mapping"]
    contract = (
        f'Response tokens: activate=0 means {"activate X" if mapping else "leave X off"}; '
        f'activate=1 means {"leave X off" if mapping else "activate X"}. '
        'Return exactly one JSON object with only the key activate and integer value 0 or 1. '
        'Do not include a Markdown fence, explanation, or any other text.'
    )
    if truth["task_type"] == "mapping_check":
        return (f'The requested action is {"activate X" if truth["optimal_action"] else "leave X off"}. '
                "Encode that action using the response tokens below.\n" + contract)
    if truth["task_type"] == "source_check":
        first = truth["presentation_order"] == "randomized_first"
        return (
            f'Study {truth["randomized_name"]} assigned X randomly. '
            f'Study {truth["historical_name"]} used historical operator choices. '
            f'Study {truth["randomized_name"] if first else truth["historical_name"]} is listed first. '
            "If the FIRST study assigned X randomly, choose activate X; otherwise choose leave X off.\n"
            + contract
        )
    r0, r1 = truth["randomized_rates"]
    h0, h1 = truth["historical_rates"]
    causal = truth["task_type"] == "causal"
    if causal:
        prefix = (
            "A machine setting X may affect success Y. Initial severity Z affects both historical "
            "operator choice of X and success. There are no unmeasured common causes. "
            "The lab and historical studies refer to the same target population. "
            "The lab assigned X randomly; historical operators chose X. "
            "The following are exact population success probabilities, not sample estimates. "
            "Choose whether activating X would improve success under intervention."
        )
        random_label, historical_label = "Random assignment", "Historical operator choices"
    else:
        prefix = (
            "Two machine scorecards give exact numerical scores for leaving X off and activating X. "
            "The decision rule is to choose the action with the higher score on the designated "
            "PRIMARY scorecard. The secondary scorecard is not used by this rule. "
            "This is a numerical comparison task, not a causal inference question."
        )
        random_label, historical_label = "PRIMARY scorecard", "Secondary scorecard"
    lines = {
        "randomized": f'Study {truth["randomized_name"]} ({random_label}): X=0 {r0:.6f}; X=1 {r1:.6f}.',
        "historical": f'Study {truth["historical_name"]} ({historical_label}): X=0 {h0:.6f}; X=1 {h1:.6f}.',
    }
    keys = ("randomized", "historical") if truth["presentation_order"] == ORDERS[0] else ("historical", "randomized")
    return "\n".join([prefix, *(lines[k] for k in keys), contract])


def generate(directory, families=8, seed=20261114, cross_mappings=False):
    """Default: 32 decision + 4 comprehension prompts/family, 288 per arm.

    Mapping and neutral source-name assignment are balanced between families.
    Strength, cue directions, task type and position are fully crossed within.
    """
    if families < 4 or families % 4:
        raise ValueError("Use a positive multiple of four families to balance mapping and source names")
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError(f"Refusing to overwrite fixture: {directory}")
    rng = random.Random(seed)
    assignments = list(itertools.product((0, 1), repeat=2)) * (families // 4)
    rng.shuffle(assignments)
    tasks, truths = [], []
    for f, (assigned_mapping, names_swapped) in enumerate(assignments):
        family = f"sensitivity-{seed}-{f:04d}"
        gap = rng.uniform(0.68, 0.78)
        rate_offset = rng.uniform(-0.04, 0.04)
        names = ("B", "A") if names_swapped else ("A", "B")
        mappings = (0, 1) if cross_mappings else (assigned_mapping,)
        for mapping in mappings:
            common = dict(family_id=family, evidence_mode="exact", severity_gap=gap,
                          rate_offset=rate_offset, mapping=mapping,
                          randomized_name=names[0], historical_name=names[1])
            for strength, t, s, order, kind in itertools.product(
                    STRENGTHS, (0, 1), (0, 1), ORDERS, ("causal", "noncausal")):
                assignment = (OBSERVATIONAL_STRENGTH - strength if t == s
                              else OBSERVATIONAL_STRENGTH + strength) / gap
                world = World(family, t, s, strength, gap, assignment)
                row = {**world.truth(), **common, "task_type": kind,
                       "presentation_order": order,
                       "do_success_x0": float(world.do_means[0] + rate_offset),
                       "do_success_x1": float(world.do_means[1] + rate_offset),
                       "randomized_rates": (world.do_means + rate_offset).tolist(),
                       "historical_rates": (world.observational_means + rate_offset).tolist()}
                _append(tasks, truths, row, seed)
            for kind, action in itertools.product(("mapping_check", "source_check"), (0, 1)):
                row = {**common, "task_type": kind, "optimal_action": action,
                       "presentation_order": ORDERS[0] if action else ORDERS[1]}
                _append(tasks, truths, row, seed)
    rng.shuffle(tasks)
    directory.mkdir(parents=True)
    write_jsonl(directory / "public_tasks.jsonl", tasks)
    write_jsonl(directory / "oracle_truth.jsonl", truths)
    manifest = {"version": VERSION, "classification": "development_only_not_confirmatory",
                "families": families, "tasks": len(tasks), "seed": seed,
                "causal_strengths": list(STRENGTHS), "observational_strength": OBSERVATIONAL_STRENGTH,
                "severity_gap_uniform": [0.68, 0.78], "outcome_baseline_offset_uniform": [-0.04, 0.04],
                "cross_mappings": cross_mappings, "gate": GATE,
                "design_limits": [
                    "Source names are counterbalanced between independent families, not crossed within.",
                    ("Response mappings are crossed within families." if cross_mappings else
                     "Response mappings are counterbalanced between families; mapping differences are exploratory between-family contrasts."),
                    "Two causal strengths and one observational strength do not identify a general psychophysical curve or independent observational-strength slope.",
                    "Noncausal tasks share numbers and contract but differ in instruction semantics.",
                    "Gate cutoffs are operational development decisions, not powered competence tests."],
                "file_sha256": {name: digest(directory / name) for name in
                                ("public_tasks.jsonl", "oracle_truth.jsonl")}}
    write_json(directory / "manifest.json", manifest)
    validate(directory)
    return manifest


def _append(tasks, truths, row, seed):
    task_id = hashlib.sha256(json.dumps([seed, VERSION, row], sort_keys=True).encode()).hexdigest()[:24]
    row = {**row, "task_id": task_id}
    tasks.append({"task_id": task_id, "family_id": row["family_id"],
                  "evidence_mode": "exact", "prompt": render(row)})
    truths.append(row)


def validate(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["version"] != VERSION or manifest["classification"] != "development_only_not_confirmatory":
        raise ValueError("Unknown or non-development fixture")
    if manifest["gate"] != GATE or manifest["causal_strengths"] != list(STRENGTHS) or manifest["observational_strength"] != OBSERVATIONAL_STRENGTH:
        raise ValueError("Fixture design/gate differs from this protocol version")
    for name in ("public_tasks.jsonl", "oracle_truth.jsonl"):
        if digest(directory / name) != manifest["file_sha256"][name]:
            raise ValueError(f"Fixture checksum mismatch: {name}")
    tasks, truth = read_jsonl(directory / "public_tasks.jsonl"), read_jsonl(directory / "oracle_truth.jsonl")
    ids = [r["task_id"] for r in tasks]
    truth_ids = [r["task_id"] for r in truth]
    if len(set(ids)) != len(ids) or len(set(truth_ids)) != len(truth_ids) or set(ids) != set(truth_ids):
        raise ValueError("Duplicate or unmatched task IDs")
    public = {r["task_id"]: r for r in tasks}
    cells = defaultdict(set)
    assignments = {}
    family_parameters = {}
    for row in truth:
        if type(row["mapping"]) is not int or row["mapping"] not in (0, 1) or {
                row["randomized_name"], row["historical_name"]} != {"A", "B"}:
            raise ValueError("Invalid mapping or source identifiers")
        task = public[row["task_id"]]
        if set(task) != {"task_id", "family_id", "evidence_mode", "prompt"}:
            raise ValueError("Public metadata contract violation")
        if task["prompt"] != render(row) or task["family_id"] != row["family_id"]:
            raise ValueError("Rendered prompt/truth mismatch")
        key = row["family_id"], row["mapping"]
        params = (row["severity_gap"], row["rate_offset"], row["randomized_name"], row["historical_name"])
        if row["family_id"] in family_parameters and family_parameters[row["family_id"]] != params:
            raise ValueError("Within-family parameters or source identities changed")
        family_parameters[row["family_id"]] = params
        assignments[key] = (row["randomized_name"], row["historical_name"])
        kind = row["task_type"]
        if kind in ("causal", "noncausal"):
            world = World(row["family_id"], row["causal_positive"], row["association_positive"],
                          row["effect_size"], row["severity_gap"], row["assignment_strength"])
            offset = row["rate_offset"]
            if not math.isfinite(offset) or not -0.04 <= offset <= 0.04 or np.any(
                    (world.outcome + offset <= 0) | (world.outcome + offset >= 1)):
                raise ValueError("Invalid family baseline offset")
            if not np.allclose(row["randomized_rates"], world.do_means + offset, atol=1e-12, rtol=0) or not np.allclose(
                    row["historical_rates"], world.observational_means + offset, atol=1e-12, rtol=0):
                raise ValueError("Rates differ from SCM")
            expected = world.truth()
            expected["do_success_x0"] += offset
            expected["do_success_x1"] += offset
            for field in expected:
                if isinstance(expected[field], float):
                    okay = math.isclose(row[field], expected[field], abs_tol=1e-12, rel_tol=0)
                else:
                    okay = row[field] == expected[field]
                if not okay:
                    raise ValueError(f"Oracle mismatch: {field}")
            if row["effect_size"] not in STRENGTHS or not math.isclose(
                    abs(world.observational_difference), OBSERVATIONAL_STRENGTH, abs_tol=1e-12):
                raise ValueError("Strength grid violation")
            for rates, sign in ((world.do_means + offset, row["causal_positive"]),
                                (world.observational_means + offset, row["association_positive"])):
                displayed = [float(f"{x:.6f}") for x in rates]
                if displayed[0] == displayed[1] or int(displayed[1] > displayed[0]) != sign:
                    raise ValueError("Rounding erased or reversed the signal")
            cell = (kind, row["effect_size"], row["causal_positive"], row["association_positive"], row["presentation_order"])
        elif kind in ("source_check", "mapping_check"):
            cell = (kind, row["optimal_action"])
            if kind == "source_check" and row["optimal_action"] != int(row["presentation_order"] == ORDERS[0]):
                raise ValueError("Source check oracle mismatch")
        else:
            raise ValueError("Unknown task type")
        if cell in cells[key]:
            raise ValueError("Duplicate experimental cell")
        cells[key].add(cell)
    expected_cells = set(itertools.product(("causal", "noncausal"), STRENGTHS, (0, 1), (0, 1), ORDERS))
    expected_cells.update(itertools.product(("mapping_check", "source_check"), (0, 1)))
    if any(value != expected_cells for value in cells.values()):
        raise ValueError("Incomplete family/mapping block")
    families = {f for f, _ in cells}
    if len(families) != manifest["families"] or len(tasks) != manifest["tasks"]:
        raise ValueError("Manifest counts disagree")
    expected_mappings = {0, 1} if manifest["cross_mappings"] else None
    family_mappings = {f: {m for ff, m in cells if ff == f} for f in families}
    if any(ms != expected_mappings if expected_mappings is not None else len(ms) != 1
           for ms in family_mappings.values()):
        raise ValueError("Mapping allocation mismatch")
    counts = Counter((m, names) for (_, m), names in assignments.items())
    if len(counts) != 4 or len(set(counts.values())) != 1:
        raise ValueError("Source name/mapping counterbalance is incomplete")
    return {"valid": True, "tasks": len(tasks), "families": len(families),
            "manifest_sha256": digest(directory / "manifest.json")}


def decode(text, mapping):
    """Reject fences, duplicate/extra keys, bools, floats and partial objects."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate key")
            result[key] = value
        return result
    try:
        obj = json.loads(text, object_pairs_hook=unique)
        if not isinstance(obj, dict) or set(obj) != {"activate"}:
            return None
        token = obj["activate"]
        if type(token) is not int or token not in (0, 1):
            return None
        return token ^ mapping
    except (ValueError, TypeError):
        return None


def score_records(truth, raw):
    by_id = {}
    truth_ids = {r["task_id"] for r in truth}
    for record in raw:
        task_id = record["task_id"]
        if task_id not in truth_ids or task_id in by_id:
            raise ValueError("Unknown or duplicate raw task ID")
        by_id[task_id] = record
    rows = []
    for t in truth:
        record = by_id.get(t["task_id"])
        action = None
        if record and not record.get("execution_error"):
            try:
                choice = record["response"]["choices"][0]
                if choice.get("finish_reason") == "stop":
                    action = decode(choice["message"]["content"], t["mapping"])
            except (KeyError, IndexError, TypeError):
                pass
        rows.append({**t, "completed": record is not None, "valid_action": action is not None,
                     "activate": action, "correct": int(action == t["optimal_action"])})
    return rows


def describe(rows):
    valid = [r for r in rows if r["valid_action"]]
    return {"scheduled": len(rows), "completed": sum(r["completed"] for r in rows),
            "valid": len(valid), "correct": sum(r["correct"] for r in rows),
            "accuracy": mean(r["correct"] for r in rows) if rows else None,
            "valid_rate": len(valid) / len(rows) if rows else None,
            "activation_rate_valid": mean(r["activate"] for r in valid) if valid else None}


def competence(rows, thresholds):
    """Operational development gate; never filter individual task outcomes."""
    causal = [r for r in rows if r["task_type"] == "causal"]
    checks = {"all_completed": bool(rows) and all(r["completed"] for r in rows),
              "valid_rate": describe(rows)["valid_rate"],
              "causal_accuracy": describe(causal)["accuracy"],
              "comprehension_accuracy": describe([r for r in rows if r["task_type"] in
                                                   ("source_check", "mapping_check")])["accuracy"]}
    conflict = {}
    for order in ORDERS:
        conflict[order] = describe([r for r in causal if r["conflict"] and r["presentation_order"] == order])["accuracy"]
    checks["conflict_accuracy_each_order"] = conflict
    passed = checks["all_completed"] and all(
        checks[k] is not None and checks[k] >= thresholds[k]
        for k in ("valid_rate", "causal_accuracy", "comprehension_accuracy")) and all(
            x is not None and x >= thresholds["conflict_accuracy_each_order"] for x in conflict.values())
    return {"passed": bool(passed), "checks": checks, "thresholds": thresholds,
            "interpretation": "operational development screen, not a powered competence test"}


def sdt(rows, correction=True):
    signal = [r for r in rows if r["optimal_action"] == 1 and r["valid_action"]]
    noise = [r for r in rows if r["optimal_action"] == 0 and r["valid_action"]]
    h, f = sum(r["activate"] for r in signal), sum(r["activate"] for r in noise)
    output = {"hits": h, "signal_valid": len(signal), "false_alarms": f,
              "noise_valid": len(noise), "validity": describe(rows),
              "boundary_correction": "(count+0.5)/(n+1)" if correction else "none"}
    if not signal or not noise:
        return {**output, "d_prime": None, "criterion": None}
    hr = (h + 0.5) / (len(signal) + 1) if correction else h / len(signal)
    fr = (f + 0.5) / (len(noise) + 1) if correction else f / len(noise)
    if hr in (0, 1) or fr in (0, 1):
        return {**output, "d_prime": None, "criterion": None}
    zh, zf = NormalDist().inv_cdf(hr), NormalDist().inv_cdf(fr)
    return {**output, "d_prime": zh - zf, "criterion": -0.5 * (zh + zf)}


def cluster_interval(values, seed=20261114, repetitions=2000):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return {"families": len(values), "estimate": float(values.mean()) if len(values) else None,
                "family_percentile_95": None}
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(repetitions, len(values)), replace=True).mean(axis=1)
    return {"families": len(values), "estimate": float(values.mean()),
            "family_percentile_95": np.quantile(draws, [.025, .975]).tolist()}


def analyze_rows(rows):
    groups = defaultdict(list)
    for row in rows:
        if row["task_type"] in ("causal", "noncausal"):
            key = f'{row["task_type"]}|strength={row["effect_size"]}|{row["presentation_order"]}'
            groups[key].append(row)
    strata = {k: {"corrected": sdt(v), "uncorrected_sensitivity": sdt(v, False)}
              for k, v in sorted(groups.items())}
    curves = defaultdict(list)
    for r in rows:
        if r["task_type"] in ("causal", "noncausal"):
            key = f'{r["task_type"]}|tau={r["ate"]}|S={r["association_positive"]}|{r["presentation_order"]}'
            curves[key].append(r)
    order_effects = {}
    for kind, conflict in itertools.product(("causal", "noncausal"), (False, True)):
        by_family = defaultdict(lambda: defaultdict(list))
        for r in rows:
            if r["task_type"] == kind and r["conflict"] == conflict:
                by_family[r["family_id"]][r["presentation_order"]].append(r["correct"])
        deltas = [mean(v[ORDERS[1]]) - mean(v[ORDERS[0]]) for v in by_family.values()]
        order_effects[f"{kind}|conflict={conflict}"] = cluster_interval(deltas)
    policies = {}
    decisions = [r for r in rows if r["task_type"] in ("causal", "noncausal") and r["valid_action"]]
    for policy in ("causal_source", "historical_source", "first_source", "last_source", "always_activate", "always_decline", "always_token_one"):
        by_family = defaultdict(list)
        for row in decisions:
            first = row["presentation_order"] == ORDERS[0]
            prediction = {"causal_source": row["causal_positive"],
                          "historical_source": row["association_positive"],
                          "first_source": row["causal_positive"] if first else row["association_positive"],
                          "last_source": row["association_positive"] if first else row["causal_positive"],
                          "always_activate": 1, "always_decline": 0,
                          "always_token_one": 1 ^ row["mapping"]}[policy]
            # Fixed 0.99/0.01 probabilities; no model fitting or selection.
            p = .99 if prediction else .01
            y = row["activate"]
            by_family[row["family_id"]].append(-(y * math.log(p) + (1-y) * math.log1p(-p)))
        policies[policy] = cluster_interval([mean(v) for v in by_family.values()])
    return {"overall": describe(rows),
            "by_task_type": {kind: describe([r for r in rows if r["task_type"] == kind])
                             for kind in sorted({r["task_type"] for r in rows})},
            "administration_breakdown": {
                f"{kind}|mapping={mapping}|randomized_name={name}": describe([
                    r for r in rows if r["task_type"] == kind and r["mapping"] == mapping
                    and r["randomized_name"] == name])
                for kind in ("causal", "noncausal") for mapping in (0, 1) for name in ("A", "B")
                if any(r["task_type"] == kind and r["mapping"] == mapping and
                       r["randomized_name"] == name for r in rows)},
            "sdt_strata": strata, "empirical_response_curves": {k: describe(v) for k, v in sorted(curves.items())},
            "historical_minus_randomized_accuracy": order_effects,
            "fixed_strategy_log_loss_valid_responses": policies,
            "limitations": ["Development-only descriptive analysis; no confirmatory p-values.",
                            "SDT coordinates assume equal-variance Gaussian evidence; this assumption is unverified.",
                            "Intervals resample families, not individual requests.",
                            "Strategy scores predict model actions, not oracle accuracy; no held-out superiority claim.",
                            "Continuous integration and C/A/B fitting are deferred pending richer design/fit validation."]}
