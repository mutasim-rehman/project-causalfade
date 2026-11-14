"""Cohort 021 source-selection and guidance development fixture."""
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
                          digest, read_jsonl, write_json, write_jsonl)

VERSION = "source-guidance-development-v1"
SEED = 20261117
ORDERS = ("randomized_first", "historical_first")
CONDITIONS = ("aligned", "conflict")
TASKS = ("source_selection", "ordinary", "guided", "neutral_guidance")
SPECIFIC_GUIDANCE = "For this intervention decision, use the random-assignment study to evaluate the effect of X."
NEUTRAL_GUIDANCE = "For this intervention decision, review the displayed studies and success probabilities carefully."
DECISION_QUESTION = 'Does activating X improve success under intervention? Return exactly one JSON object: {"decision":"activate"} or {"decision":"leave_off"}. No other fields, fences, explanation, or text.'
SELECTION_QUESTION = ('Which study provides the appropriate evidence for estimating the effect of intervening on X in this target population? '
                      'Return exactly one JSON object: {"governing_study":"A"} or {"governing_study":"B"}. '
                      'No other fields, fences, explanation, or text.')
IDENTIFICATION_QUESTION = ('Which study assigned X randomly? Return exactly one JSON object: '
                           '{"randomized_study":"A"} or {"randomized_study":"B"}. '
                           'No other fields, fences, explanation, or text.')


def _blocks(row):
    r0,r1=row["randomized_rates"]
    h0,h1=row["historical_rates"]
    blocks={"randomized":f'Study {row["randomized_name"]}\nAssignment method: X was assigned randomly.\nSuccess probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.',
            "historical":f'Study {row["historical_name"]}\nAssignment method: operators chose X.\nSuccess probabilities: X=0 {h0:.6f}; X=1 {h1:.6f}.'}
    order=("randomized","historical") if row["presentation_order"]==ORDERS[0] else ("historical","randomized")
    return "\n\n".join(f"{i}. {blocks[k]}" for i,k in enumerate(order,1))


def evidence(row):
    if row["task_type"]=="direct_identification":
        return _blocks(row)
    severity=("Initial severity Z affects success. " if row["task_type"]=="randomized_only" else
              "Initial severity Z affects both historical operator choice of X and success. ")
    preface=("A machine setting X may affect success Y. "+severity+
             "The studies refer to the same target population. There are no unmeasured common causes. "
             "The rates are exact population success probabilities, not sample estimates.")
    if row["task_type"]=="randomized_only":
        r0,r1=row["randomized_rates"]
        block=f'Study {row["randomized_name"]}\nAssignment method: X was assigned randomly.\nSuccess probabilities: X=0 {r0:.6f}; X=1 {r1:.6f}.'
    else:
        block=_blocks(row)
    return preface+"\n\n"+block


def render(row):
    kind=row["task_type"]
    if kind=="direct_identification": question=IDENTIFICATION_QUESTION
    elif kind=="source_selection": question=SELECTION_QUESTION
    else:
        guidance=(SPECIFIC_GUIDANCE+"\n" if kind=="guided" else
                  NEUTRAL_GUIDANCE+"\n" if kind=="neutral_guidance" else "")
        question=guidance+DECISION_QUESTION
    return evidence(row)+"\n\n"+question


def _append(public,truth,row,seed):
    task_id=hashlib.sha256(json.dumps([seed,VERSION,row],sort_keys=True).encode()).hexdigest()[:24]
    row={**row,"task_id":task_id}
    public.append({"task_id":task_id,"family_id":row["family_id"],"prompt":render(row)})
    truth.append(row)


def generate(directory,seed=SEED):
    directory=Path(directory)
    if directory.exists(): raise FileExistsError(directory)
    rng=random.Random(seed)
    public,truth=[],[]
    for f in range(8):
        family=f"guidance-{seed}-{f:04d}"
        gap,offset=rng.uniform(.68,.78),rng.uniform(-.04,.04)
        for t,strength in itertools.product((0,1),STRENGTHS):
            randomized_name="A" if (t+STRENGTHS.index(strength)+f)%2==0 else "B"
            historical_name="B" if randomized_name=="A" else "A"
            base_id=hashlib.sha256(json.dumps([family,t,strength]).encode()).hexdigest()[:20]
            common=dict(family_id=family,base_id=base_id,causal_positive=t,effect_size=strength,
                        severity_gap=gap,rate_offset=offset,randomized_name=randomized_name,
                        historical_name=historical_name)
            worlds={}
            for condition in CONDITIONS:
                association=t if condition=="aligned" else 1-t
                assignment=(OBSERVATIONAL_STRENGTH-strength if association==t else OBSERVATIONAL_STRENGTH+strength)/gap
                worlds[condition]=World(family,t,association,strength,gap,assignment)
            randomized_rates=(worlds["aligned"].do_means+offset).tolist()
            baseline={**worlds["aligned"].truth(),**common,"task_type":"randomized_only",
                      "condition":"randomized_only","presentation_order":ORDERS[0],
                      "stem_id":base_id,"optimal_action":t,
                      "randomized_rates":randomized_rates,
                      "historical_rates":(worlds["aligned"].observational_means+offset).tolist(),
                      "do_success_x0":float(worlds["aligned"].do_means[0]+offset),
                      "do_success_x1":float(worlds["aligned"].do_means[1]+offset)}
            _append(public,truth,baseline,seed)
            for condition,order in itertools.product(CONDITIONS,ORDERS):
                world=worlds[condition]
                stem_id=hashlib.sha256(json.dumps([base_id,condition,order]).encode()).hexdigest()[:20]
                row={**world.truth(),**common,"condition":condition,"presentation_order":order,
                     "stem_id":stem_id,"optimal_action":t,"randomized_rates":randomized_rates,
                     "historical_rates":(world.observational_means+offset).tolist(),
                     "do_success_x0":float(world.do_means[0]+offset),
                     "do_success_x1":float(world.do_means[1]+offset)}
                for kind in TASKS:
                    _append(public,truth,{**row,"task_type":kind,
                                          "guidance_condition":kind if kind in ("guided","neutral_guidance") else "none"},seed)
        for randomized_name,order in itertools.product(("A","B"),ORDERS):
            _append(public,truth,{"family_id":family,"task_type":"direct_identification",
                                  "randomized_name":randomized_name,
                                  "historical_name":"B" if randomized_name=="A" else "A",
                                  "presentation_order":order,
                                  "randomized_rates":[.45,.55],"historical_rates":[.30,.66],
                                  "correct_study":randomized_name},seed)
    rng.shuffle(public)
    directory.mkdir(parents=True)
    write_jsonl(directory/"public_tasks.jsonl",public)
    write_jsonl(directory/"oracle_truth.jsonl",truth)
    manifest={"version":VERSION,"classification":"development_only_not_confirmatory",
              "families":8,"seed":seed,"tasks":576,"two_source_stems":128,
              "two_source_prompts":512,"randomized_only":32,"direct_identification":32,
              "effect_strengths":list(STRENGTHS),"observational_strength":OBSERVATIONAL_STRENGTH,
              "specific_guidance":SPECIFIC_GUIDANCE,"neutral_guidance":NEUTRAL_GUIDANCE,
              "schedule_policy":"one seeded shuffle; every prompt fresh context",
              "file_sha256":{name:digest(directory/name) for name in ("public_tasks.jsonl","oracle_truth.jsonl")}}
    write_json(directory/"manifest.json",manifest)
    validate(directory)
    return manifest


def validate(directory):
    directory=Path(directory)
    m=json.loads((directory/"manifest.json").read_text())
    if (m["version"],m["classification"],m["families"],m["tasks"],m["two_source_stems"],
        m["two_source_prompts"],m["randomized_only"],m["direct_identification"],m["effect_strengths"],
        m["observational_strength"],m["specific_guidance"],m["neutral_guidance"]) != (
            VERSION,"development_only_not_confirmatory",8,576,128,512,32,32,list(STRENGTHS),
            OBSERVATIONAL_STRENGTH,SPECIFIC_GUIDANCE,NEUTRAL_GUIDANCE):
        raise ValueError("Protocol mismatch")
    for name in ("public_tasks.jsonl","oracle_truth.jsonl"):
        if digest(directory/name)!=m["file_sha256"][name]: raise ValueError("Fixture checksum mismatch")
    public,truth=read_jsonl(directory/"public_tasks.jsonl"),read_jsonl(directory/"oracle_truth.jsonl")
    pids,tids=[p["task_id"] for p in public],[r["task_id"] for r in truth]
    if len(public)!=576 or len(truth)!=576 or len(set(pids))!=576 or len(set(tids))!=576 or set(pids)!=set(tids):
        raise ValueError("Duplicate/missing task IDs")
    by_id={p["task_id"]:p for p in public}
    cells=defaultdict(set);stems=defaultdict(list);bases=defaultdict(list)
    for r in truth:
        p=by_id[r["task_id"]]
        if set(p)!={"task_id","family_id","prompt"} or p["family_id"]!=r["family_id"] or p["prompt"]!=render(r):
            raise ValueError("Public prompt/truth mismatch")
        kind=r["task_type"]
        if kind=="direct_identification":
            if {r["randomized_name"],r["historical_name"]}!={"A","B"} or r["correct_study"]!=r["randomized_name"] or r["randomized_rates"]!=[.45,.55] or r["historical_rates"]!=[.30,.66]:
                raise ValueError("Direct identification oracle mismatch")
            cell=(kind,r["randomized_name"],r["presentation_order"])
        else:
            if kind not in (*TASKS,"randomized_only") or r["effect_size"] not in STRENGTHS or {r["randomized_name"],r["historical_name"]}!={"A","B"}:
                raise ValueError("Invalid task cell")
            world=World(r["family_id"],r["causal_positive"],r["association_positive"],
                        r["effect_size"],r["severity_gap"],r["assignment_strength"])
            offset=r["rate_offset"]
            if not math.isfinite(offset) or not -.04<=offset<=.04 or np.any((world.outcome+offset<=0)|(world.outcome+offset>=1)):
                raise ValueError("Probability bounds or positivity")
            expected=world.truth();expected["do_success_x0"]+=offset;expected["do_success_x1"]+=offset
            for key,value in expected.items():
                if not (math.isclose(r[key],value,abs_tol=1e-12,rel_tol=0) if isinstance(value,float) else r[key]==value):
                    raise ValueError("SCM oracle mismatch")
            if not np.allclose(r["randomized_rates"],world.do_means+offset,atol=1e-12,rtol=0) or not np.allclose(r["historical_rates"],world.observational_means+offset,atol=1e-12,rtol=0):
                raise ValueError("SCM rate mismatch")
            if not math.isclose(abs(world.observational_difference),OBSERVATIONAL_STRENGTH,abs_tol=1e-12):
                raise ValueError("Historical magnitude mismatch")
            if r["optimal_action"]!=r["causal_positive"]: raise ValueError("Action oracle mismatch")
            for rates,sign in ((r["randomized_rates"],r["causal_positive"]),(r["historical_rates"],r["association_positive"])):
                display=[float(f"{x:.6f}") for x in rates]
                if display[0]==display[1] or int(display[1]>display[0])!=sign:
                    raise ValueError("Display rounding mismatch")
            if kind=="randomized_only":
                if r["condition"]!="randomized_only" or "operators chose X" in p["prompt"]:
                    raise ValueError("Randomized-only prompt mentions absent source")
                cell=(r["causal_positive"],r["effect_size"],kind)
            else:
                if r["condition"] not in CONDITIONS or r["association_positive"]!=(r["causal_positive"] if r["condition"]=="aligned" else 1-r["causal_positive"]):
                    raise ValueError("Agreement/conflict mismatch")
                if r["guidance_condition"]!=(kind if kind in ("guided","neutral_guidance") else "none"):
                    raise ValueError("Guidance metadata mismatch")
                stems[(r["family_id"],r["stem_id"])].append(r)
                cell=(r["causal_positive"],r["effect_size"],r["condition"],r["presentation_order"],kind)
            bases[(r["family_id"],r["base_id"])].append(r)
        if kind!="randomized_only":
            blocks=evidence(r).split("\n\n")
            first=next((b for b in blocks if b.startswith("1. Study ")),None)
            second=next((b for b in blocks if b.startswith("2. Study ")),None)
            expected_first=r["randomized_name"] if r["presentation_order"]==ORDERS[0] else r["historical_name"]
            expected_second=r["historical_name"] if r["presentation_order"]==ORDERS[0] else r["randomized_name"]
            if not first or not second or not first.startswith(f"1. Study {expected_first}\n") or not second.startswith(f"2. Study {expected_second}\n"):
                raise ValueError("Rendered physical source order mismatch")
        if cell in cells[r["family_id"]]: raise ValueError("Duplicate experimental cell")
        cells[r["family_id"]].add(cell)
    expected=set(itertools.product((0,1),STRENGTHS,CONDITIONS,ORDERS,TASKS))
    expected|={(t,s,"randomized_only") for t,s in itertools.product((0,1),STRENGTHS)}
    expected|={("direct_identification",n,o) for n,o in itertools.product(("A","B"),ORDERS)}
    if len(cells)!=8 or any(c!=expected for c in cells.values()) or len(stems)!=128 or len(bases)!=32:
        raise ValueError("Incomplete within-family crossing")
    for variants in stems.values():
        if {r["task_type"] for r in variants}!=set(TASKS) or len({evidence(r) for r in variants})!=1 or len({r["optimal_action"] for r in variants})!=1:
            raise ValueError("Nonidentical evidence or oracle across variants")
    for variants in bases.values():
        if len(variants)!=17 or len({tuple(r["randomized_rates"]) for r in variants})!=1 or len({r["optimal_action"] for r in variants})!=1 or len({r["randomized_name"] for r in variants})!=1:
            raise ValueError("Baseline/two-source pairing mismatch")
    for family in cells:
        counts=Counter(r["randomized_name"] for r in truth if r["family_id"]==family and r["task_type"]=="randomized_only")
        if counts!={"A":2,"B":2}: raise ValueError("Within-family name imbalance")
    return {"valid":True,"tasks":576,"families":8,"stems":128,"manifest_sha256":digest(directory/"manifest.json")}


def decode(text,kind):
    def unique(pairs):
        d={}
        for key,value in pairs:
            if key in d: raise ValueError("Duplicate JSON key")
            d[key]=value
        return d
    try:
        obj=json.loads(text,object_pairs_hook=unique)
        if not isinstance(obj,dict): return None
        if kind=="source_selection":
            return obj.get("governing_study") if set(obj)=={"governing_study"} and obj.get("governing_study") in ("A","B") else None
        if kind=="direct_identification":
            return obj.get("randomized_study") if set(obj)=={"randomized_study"} and obj.get("randomized_study") in ("A","B") else None
        return {"activate":1,"leave_off":0}.get(obj.get("decision")) if set(obj)=={"decision"} and type(obj.get("decision")) is str else None
    except (ValueError,TypeError): return None


def score_records(truth,raw):
    ids={r["task_id"] for r in truth};records={}
    for record in raw:
        if record["task_id"] not in ids or record["task_id"] in records:
            raise ValueError("Unknown or duplicate raw task ID")
        records[record["task_id"]]=record
    rows=[]
    for t in truth:
        record=records.get(t["task_id"]);answer=None
        if record and not record.get("execution_error"):
            try:
                choice=record["response"]["choices"][0]
                if choice.get("finish_reason")=="stop": answer=decode(choice["message"]["content"],t["task_type"])
            except (KeyError,IndexError,TypeError): pass
        target=(t["randomized_name"] if t["task_type"]=="source_selection" else
                t["correct_study"] if t["task_type"]=="direct_identification" else t["optimal_action"])
        rows.append({**t,"completed":record is not None,"valid_answer":answer is not None,
                     "answer":answer,"correct":int(answer==target)})
    return rows


def summarize(rows,decision=False):
    valid=[r for r in rows if r["valid_answer"]]
    out={"scheduled":len(rows),"completed":sum(r["completed"] for r in rows),
         "valid":len(valid),"correct":sum(r["correct"] for r in rows),
         "accuracy":sum(r["correct"] for r in rows)/len(rows) if rows else None,
         "valid_rate":len(valid)/len(rows) if rows else None}
    if decision: out["activation_rate_valid"]=mean(r["answer"] for r in valid) if valid else None
    return out


def analyze_rows(rows):
    decision_kinds=("randomized_only","ordinary","guided","neutral_guidance")
    kinds=(*TASKS,"randomized_only","direct_identification")
    by_task={k:summarize([r for r in rows if r["task_type"]==k],k in decision_kinds) for k in kinds}
    strata={}
    for kind,condition,order in itertools.product(TASKS,CONDITIONS,ORDERS):
        group=[r for r in rows if r["task_type"]==kind and r["condition"]==condition and r["presentation_order"]==order]
        strata[f"{kind}|{condition}|{order}"]=summarize(group,kind in decision_kinds)
    direction={}
    for kind,t in itertools.product(decision_kinds,(0,1)):
        group=[r for r in rows if r["task_type"]==kind and r["causal_positive"]==t]
        direction[f"{kind}|causal_positive={t}"]=summarize(group,True)
    direct={f"name={n}|{o}":summarize([r for r in rows if r["task_type"]=="direct_identification" and r["randomized_name"]==n and r["presentation_order"]==o]) for n,o in itertools.product(("A","B"),ORDERS)}
    selection_by_name_order={f"name={n}|{o}":summarize([r for r in rows if r["task_type"]=="source_selection" and r["randomized_name"]==n and r["presentation_order"]==o]) for n,o in itertools.product(("A","B"),ORDERS)}
    by_stem=defaultdict(dict);baseline={}
    for r in rows:
        if r["task_type"]=="randomized_only": baseline[(r["family_id"],r["base_id"])]=r
        elif r["task_type"] in TASKS: by_stem[(r["family_id"],r["stem_id"])][r["task_type"]]=r
    pairs=(("ordinary","guided"),("neutral_guidance","guided"),("ordinary","neutral_guidance"))
    contrasts={}
    for condition,order,a,b in itertools.product(CONDITIONS,ORDERS,tuple(x[0] for x in pairs),tuple(x[1] for x in pairs)):
        if (a,b) not in pairs: continue
        grouped=defaultdict(list);flips=Counter()
        for (family,_),variant in by_stem.items():
            sample=variant["ordinary"]
            if sample["condition"]!=condition or sample["presentation_order"]!=order: continue
            x,y=variant[a],variant[b]
            grouped[family].append(y["correct"]-x["correct"])
            if x["valid_answer"] and y["valid_answer"]: flips[f'{x["answer"]}_to_{y["answer"]}']+=1
        contrasts[f"{condition}|{order}|{b}_minus_{a}"]={**cluster_interval([mean(v) for v in grouped.values()]),
                                                           "decision_flips":{k:flips.get(k,0) for k in ("0_to_1","1_to_0","0_to_0","1_to_1")}}
    for kind,condition,order in itertools.product(("ordinary","guided","neutral_guidance"),CONDITIONS,ORDERS):
        grouped=defaultdict(list);flips=Counter()
        for (family,_),variant in by_stem.items():
            y=variant[kind]
            if y["condition"]!=condition or y["presentation_order"]!=order: continue
            x=baseline[(family,y["base_id"])]
            grouped[family].append(y["correct"]-x["correct"])
            if x["valid_answer"] and y["valid_answer"]: flips[f'{x["answer"]}_to_{y["answer"]}']+=1
        contrasts[f"{condition}|{order}|{kind}_minus_randomized_only"]={**cluster_interval([mean(v) for v in grouped.values()]),
                                                                              "decision_flips":{k:flips.get(k,0) for k in ("0_to_1","1_to_0","0_to_0","1_to_1")}}
    for kind,condition in itertools.product(("ordinary","guided","neutral_guidance"),CONDITIONS):
        pairs_by_base=defaultdict(dict)
        for variant in by_stem.values():
            y=variant[kind]
            if y["condition"]==condition: pairs_by_base[(y["family_id"],y["base_id"])][y["presentation_order"]]=y
        grouped=defaultdict(list);flips=Counter()
        for (family,_),orders in pairs_by_base.items():
            x,y=orders[ORDERS[0]],orders[ORDERS[1]]
            grouped[family].append(y["correct"]-x["correct"])
            if x["valid_answer"] and y["valid_answer"]: flips[f'{x["answer"]}_to_{y["answer"]}']+=1
        contrasts[f"{condition}|{kind}|historical_minus_randomized_order"]={**cluster_interval([mean(v) for v in grouped.values()]),
                                                                             "decision_flips":{k:flips.get(k,0) for k in ("0_to_1","1_to_0","0_to_0","1_to_1")}}
    joint={}
    for kind in ("ordinary","guided","neutral_guidance"):
        for condition,order in itertools.product(CONDITIONS,ORDERS):
            counts=Counter()
            for variant in by_stem.values():
                decision=variant[kind]
                if decision["condition"]==condition and decision["presentation_order"]==order:
                    selection=variant["source_selection"]
                    counts[f'source_{"correct" if selection["correct"] else "incorrect"}|decision_{"correct" if decision["correct"] else "incorrect"}']+=1
            joint[f"{kind}|{condition}|{order}"]={k:counts.get(k,0) for k in (
                "source_correct|decision_correct","source_correct|decision_incorrect",
                "source_incorrect|decision_correct","source_incorrect|decision_incorrect")}
    return {"by_task_type":by_task,"two_source_strata":strata,"by_causal_direction":direction,
            "direct_identification_by_name_order":direct,
            "governing_selection_by_name_order":selection_by_name_order,
            "paired_contrasts":contrasts,
            "source_decision_joint_counts":joint,
            "limitations":["Eight families; cluster percentile intervals are coarse development diagnostics.",
                           "Joint patterns combine independent fresh-context requests and do not establish mediation.",
                           "Guidance changes the task; improvement is not unassisted causal competence."]}
