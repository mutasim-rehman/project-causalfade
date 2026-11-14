"""Cohort 020 staged component diagnostic on fresh SCM families."""
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
from .sensitivity import (STRENGTHS, OBSERVATIONAL_STRENGTH, cluster_interval,
                          describe, digest, read_jsonl, write_json, write_jsonl)

VERSION = "component-diagnostic-development-v1"
SEED = 20261116
ORDERS = ("randomized_first", "historical_first")
KINDS = ("number", "randomized_only", "aligned_randomized_first", "aligned_historical_first",
         "conflict_randomized_first", "conflict_historical_first")


def _blocks(row):
    r0, r1 = row["randomized_rates"]
    h0, h1 = row["historical_rates"]
    blocks = {
        "randomized": (f'Study {row["randomized_name"]}\nAssignment method: X was assigned randomly.\n'
                       f'Success probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.'),
        "historical": (f'Study {row["historical_name"]}\nAssignment method: operators chose X.\n'
                       f'Success probabilities: X=0 {h0:.6f}; X=1 {h1:.6f}.')}
    order = ("randomized", "historical") if row["presentation_order"] == ORDERS[0] else ("historical", "randomized")
    return "\n\n".join(f"{i}. {blocks[key]}" for i, key in enumerate(order, 1))


def render(row):
    kind = row["task_type"]
    if kind == "number":
        r0, r1 = row["randomized_rates"]
        return (f'Exact success probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.\n'
                'Which rate is larger? Return exactly one JSON object: {"larger":"X=0"} or {"larger":"X=1"}. '
                'No other fields, fences, explanation, or text.')
    if kind == "source_identification":
        return (_blocks(row) + '\n\nWhich study assigned X randomly? Return exactly one JSON object: '
                '{"randomized_study":"A"} or {"randomized_study":"B"}. '
                'No other fields, fences, explanation, or text.')
    preface = ('A machine setting X may affect success Y. Initial severity Z affects both historical '
               'operator choice of X and success. There are no unmeasured common causes. '
               'The studies refer to the same target population. The rates are exact population '
               'success probabilities, not sample estimates. Decide whether activating X '
               'improves success under intervention.')
    if kind == "randomized_only":
        r0, r1 = row["randomized_rates"]
        evidence = (f'Study {row["randomized_name"]}\nAssignment method: X was assigned randomly.\n'
                    f'Success probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.')
    else:
        evidence = _blocks(row)
    return (preface + '\n\n' + evidence + '\n\nReturn exactly one JSON object: '
            '{"decision":"activate"} or {"decision":"leave_off"}. '
            'No other fields, fences, explanation, or text.')


def _append(public, truth, row, seed):
    task_id = hashlib.sha256(json.dumps([seed, VERSION, row], sort_keys=True).encode()).hexdigest()[:24]
    row = {**row, "task_id": task_id}
    public.append({"task_id": task_id, "family_id": row["family_id"], "prompt": render(row)})
    truth.append(row)


def generate(directory, seed=SEED):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError(directory)
    rng = random.Random(seed)
    public, truth = [], []
    for family_index in range(8):
        family = f"components-{seed}-{family_index:04d}"
        gap, offset = rng.uniform(.68, .78), rng.uniform(-.04, .04)
        for t, strength in itertools.product((0, 1), STRENGTHS):
            # Balance actual randomized name within every family and keep it fixed across a stem.
            randomized_name = "A" if (t + STRENGTHS.index(strength) + family_index) % 2 == 0 else "B"
            historical_name = "B" if randomized_name == "A" else "A"
            stem = hashlib.sha256(json.dumps([family, t, strength]).encode()).hexdigest()[:20]
            common = dict(family_id=family, stem_id=stem, causal_positive=t,
                          effect_size=strength, severity_gap=gap, rate_offset=offset,
                          randomized_name=randomized_name, historical_name=historical_name)
            worlds = {}
            for association in (t, 1-t):
                assignment = (OBSERVATIONAL_STRENGTH - strength if association == t else
                              OBSERVATIONAL_STRENGTH + strength) / gap
                worlds[association == t] = World(family, t, association, strength, gap, assignment)
            random_rates = (worlds[True].do_means + offset).tolist()
            for kind in KINDS:
                if kind in ("number", "randomized_only"):
                    aligned, order = True, ORDERS[0]
                else:
                    aligned = kind.startswith("aligned")
                    order = ORDERS[0] if kind.endswith("randomized_first") else ORDERS[1]
                world = worlds[aligned]
                row = {**world.truth(), **common, "task_type": kind,
                       "presentation_order": order, "aligned": aligned,
                       "optimal_action": t, "randomized_rates": random_rates,
                       "historical_rates": (world.observational_means + offset).tolist(),
                       "do_success_x0": float(world.do_means[0] + offset),
                       "do_success_x1": float(world.do_means[1] + offset)}
                _append(public, truth, row, seed)
        for randomized_name, order in itertools.product(("A", "B"), ORDERS):
            _append(public, truth, {"family_id": family, "task_type": "source_identification",
                                    "randomized_name": randomized_name,
                                    "historical_name": "B" if randomized_name == "A" else "A",
                                    "presentation_order": order,
                                    "randomized_rates": [.45, .55],
                                    "historical_rates": [.30, .66],
                                    "correct_study": randomized_name}, seed)
    rng.shuffle(public)
    directory.mkdir(parents=True)
    write_jsonl(directory / "public_tasks.jsonl", public)
    write_jsonl(directory / "oracle_truth.jsonl", truth)
    manifest = {"version": VERSION, "classification": "development_only_not_confirmatory",
                "families": 8, "tasks": 224, "seed": seed, "decision_tasks": 160,
                "number_checks": 32, "source_checks": 32,
                "effect_strengths": list(STRENGTHS), "observational_strength": OBSERVATIONAL_STRENGTH,
                "schedule_policy": "single seeded shuffle; fresh context per request",
                "file_sha256": {name: digest(directory/name) for name in
                                ("public_tasks.jsonl", "oracle_truth.jsonl")}}
    write_json(directory/"manifest.json", manifest)
    validate(directory)
    return manifest


def validate(directory):
    directory = Path(directory)
    m = json.loads((directory/"manifest.json").read_text())
    if (m["version"], m["classification"], m["families"], m["tasks"], m["decision_tasks"],
        m["number_checks"], m["source_checks"], m["effect_strengths"], m["observational_strength"]) != (
            VERSION, "development_only_not_confirmatory", 8, 224, 160, 32, 32,
            list(STRENGTHS), OBSERVATIONAL_STRENGTH):
        raise ValueError("Protocol mismatch")
    for name in ("public_tasks.jsonl", "oracle_truth.jsonl"):
        if digest(directory/name) != m["file_sha256"][name]:
            raise ValueError("Checksum mismatch")
    public, truth = read_jsonl(directory/"public_tasks.jsonl"), read_jsonl(directory/"oracle_truth.jsonl")
    pids, tids = [x["task_id"] for x in public], [x["task_id"] for x in truth]
    if len(public) != 224 or len(truth) != 224 or len(set(pids)) != 224 or len(set(tids)) != 224 or set(pids) != set(tids):
        raise ValueError("Duplicate/missing task IDs")
    by_id = {x["task_id"]: x for x in public}
    cells, stems = defaultdict(set), defaultdict(list)
    for r in truth:
        p = by_id[r["task_id"]]
        if set(p) != {"task_id", "family_id", "prompt"} or p["family_id"] != r["family_id"] or p["prompt"] != render(r):
            raise ValueError("Public/truth mismatch")
        kind = r["task_type"]
        if kind == "source_identification":
            if {r["randomized_name"], r["historical_name"]} != {"A", "B"} or r["correct_study"] != r["randomized_name"]:
                raise ValueError("Source oracle mismatch")
            blocks = p["prompt"].split("\n\n")
            expected_first = r["randomized_name"] if r["presentation_order"] == ORDERS[0] else r["historical_name"]
            if not blocks[0].startswith(f"1. Study {expected_first}\n") or not blocks[1].startswith("2. Study "):
                raise ValueError("Rendered block order mismatch")
            cell = (kind, r["randomized_name"], r["presentation_order"])
        else:
            if kind not in KINDS or r["effect_size"] not in STRENGTHS or {r["randomized_name"], r["historical_name"]} != {"A", "B"}:
                raise ValueError("Invalid decision cell")
            w = World(r["family_id"], r["causal_positive"], r["association_positive"],
                      r["effect_size"], r["severity_gap"], r["assignment_strength"])
            offset = r["rate_offset"]
            if not math.isfinite(offset) or not -.04 <= offset <= .04 or np.any((w.outcome+offset <= 0)|(w.outcome+offset >= 1)):
                raise ValueError("Probability bounds/positivity")
            expected = w.truth()
            expected["do_success_x0"] += offset
            expected["do_success_x1"] += offset
            for key,value in expected.items():
                if not (math.isclose(r[key],value,abs_tol=1e-12,rel_tol=0) if isinstance(value,float) else r[key]==value):
                    raise ValueError("SCM oracle mismatch")
            if not np.allclose(r["randomized_rates"],w.do_means+offset,atol=1e-12,rtol=0) or not np.allclose(r["historical_rates"],w.observational_means+offset,atol=1e-12,rtol=0):
                raise ValueError("Evidence rates mismatch")
            if not math.isclose(abs(w.observational_difference),OBSERVATIONAL_STRENGTH,abs_tol=1e-12):
                raise ValueError("Historical strength mismatch")
            if r["optimal_action"] != r["causal_positive"] or r["aligned"] != (r["association_positive"] == r["causal_positive"]):
                raise ValueError("Action/sign mismatch")
            for rates, sign in ((r["randomized_rates"],r["causal_positive"]),(r["historical_rates"],r["association_positive"])):
                shown = [float(f"{x:.6f}") for x in rates]
                if shown[0] == shown[1] or int(shown[1]>shown[0]) != sign:
                    raise ValueError("Display rounding mismatch")
            if kind not in ("number", "randomized_only"):
                expected_order = ORDERS[0] if kind.endswith("randomized_first") else ORDERS[1]
                if r["presentation_order"] != expected_order or r["aligned"] != kind.startswith("aligned"):
                    raise ValueError("Condition label mismatch")
                blocks = p["prompt"].split("\n\n")
                expected_first = r["randomized_name"] if expected_order == ORDERS[0] else r["historical_name"]
                if not any(x.startswith(f"1. Study {expected_first}\n") for x in blocks):
                    raise ValueError("Rendered decision block order mismatch")
            stems[(r["family_id"],r["stem_id"])].append(r)
            cell = (r["causal_positive"],r["effect_size"],kind)
        if cell in cells[r["family_id"]]:
            raise ValueError("Duplicate cell")
        cells[r["family_id"]].add(cell)
    expected_cells = set(itertools.product((0,1),STRENGTHS,KINDS)) | set(itertools.product(("source_identification",),( "A","B"),ORDERS))
    if len(cells) != 8 or any(v != expected_cells for v in cells.values()) or len(stems) != 32:
        raise ValueError("Incomplete crossing")
    for variants in stems.values():
        if {r["task_type"] for r in variants} != set(KINDS) or len({tuple(r["randomized_rates"]) for r in variants}) != 1 or len({r["optimal_action"] for r in variants}) != 1 or len({r["randomized_name"] for r in variants}) != 1:
            raise ValueError("Stem pairing mismatch")
        historical = [r for r in variants if r["task_type"].startswith(("aligned","conflict"))]
        if any(not math.isclose(abs(r["historical_rates"][1]-r["historical_rates"][0]),.36,abs_tol=1e-12) for r in historical):
            raise ValueError("Historical magnitude mismatch")
    return {"valid":True,"tasks":224,"families":8,"stems":32,"manifest_sha256":digest(directory/"manifest.json")}


def decode(text, kind):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValueError("Duplicate key")
            d[k]=v
        return d
    try:
        obj=json.loads(text,object_pairs_hook=unique)
        if not isinstance(obj,dict): return None
        if kind=="number":
            return {"X=0":0,"X=1":1}.get(obj.get("larger")) if set(obj)=={"larger"} and type(obj.get("larger")) is str else None
        if kind=="source_identification":
            return obj.get("randomized_study") if set(obj)=={"randomized_study"} and obj.get("randomized_study") in ("A","B") else None
        return {"activate":1,"leave_off":0}.get(obj.get("decision")) if set(obj)=={"decision"} and type(obj.get("decision")) is str else None
    except (ValueError,TypeError):
        return None


def score_records(truth, raw):
    ids={r["task_id"] for r in truth}
    records={}
    for record in raw:
        if record["task_id"] not in ids or record["task_id"] in records:
            raise ValueError("Unknown or duplicate raw task ID")
        records[record["task_id"]]=record
    rows=[]
    for t in truth:
        record=records.get(t["task_id"])
        answer=None
        if record and not record.get("execution_error"):
            try:
                choice=record["response"]["choices"][0]
                if choice.get("finish_reason")=="stop":
                    answer=decode(choice["message"]["content"],t["task_type"])
            except (KeyError,IndexError,TypeError): pass
        target=t["correct_study"] if t["task_type"]=="source_identification" else t["optimal_action"]
        rows.append({**t,"completed":record is not None,"valid_answer":answer is not None,
                     "answer":answer,"correct":int(answer==target)})
    return rows


def summarize(rows, action_rate=False):
    valid=[r for r in rows if r["valid_answer"]]
    result={"scheduled":len(rows),"completed":sum(r["completed"] for r in rows),
            "valid":len(valid),"correct":sum(r["correct"] for r in rows),
            "accuracy":sum(r["correct"] for r in rows)/len(rows) if rows else None,
            "valid_rate":len(valid)/len(rows) if rows else None}
    if action_rate:
        result["activation_rate_valid"]=mean(r["answer"] for r in valid) if valid else None
    return result


def analyze_rows(rows):
    by_kind={k:summarize([r for r in rows if r["task_type"]==k],k not in ("number","source_identification")) for k in (*KINDS,"source_identification")}
    by_direction={f"{k}|causal_positive={t}|strength={s}":summarize([r for r in rows if r["task_type"]==k and r.get("causal_positive")==t and r.get("effect_size")==s],k!="number") for k,t,s in itertools.product(KINDS,(0,1),STRENGTHS)}
    by_source={f"name={n}|{o}":{"scheduled":len(v),"valid":sum(r["valid_answer"] for r in v),"correct":sum(r["correct"] for r in v)} for (n,o),v in _group(rows,lambda r:(r["randomized_name"],r["presentation_order"]) if r["task_type"]=="source_identification" else None).items() if n is not None}
    by_stem=defaultdict(dict)
    for r in rows:
        if r["task_type"] in KINDS: by_stem[r["family_id"],r["stem_id"]][r["task_type"]]=r
    contrasts={}
    pairs=(("number","randomized_only"),("randomized_only","aligned_randomized_first"),
           ("randomized_only","aligned_historical_first"),("randomized_only","conflict_randomized_first"),
           ("randomized_only","conflict_historical_first"),
           ("aligned_randomized_first","aligned_historical_first"),
           ("conflict_randomized_first","conflict_historical_first"))
    for a,b in pairs:
        family=defaultdict(list); flips=Counter()
        for (fid,_),variants in by_stem.items():
            x,y=variants[a],variants[b]
            family[fid].append(y["correct"]-x["correct"])
            if x["valid_answer"] and y["valid_answer"]:
                flips[f'{x["answer"]}_to_{y["answer"]}']+=1
        contrasts[f"{b}_minus_{a}"]={**cluster_interval([mean(v) for v in family.values()]),
                                      "paired_answer_flips":{k:flips.get(k,0) for k in ("0_to_1","1_to_0","0_to_0","1_to_1")}}
    return {"by_task_type":by_kind,"by_direction_strength":by_direction,
            "direct_source_by_name_order":by_source,"paired_contrasts":contrasts,
            "limitations":["Eight development families yield coarse family-cluster intervals.",
                           "Number comparison and intervention decisions differ in task demands.",
                           "Paired contrasts do not identify internal processing stages."]}


def _group(rows,key):
    groups=defaultdict(list)
    for row in rows:
        k=key(row)
        if k is not None: groups[k].append(row)
    return groups
