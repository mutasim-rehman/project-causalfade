"""Frozen-style cohort 024 fixture and strict response scoring."""
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory

from . import measurement_audit as prior
from .sensitivity import digest, read_jsonl, write_json, write_jsonl

VERSION = "matrix024-v1"
SEED = 20261120


def render(row):
    base = prior.render(row)
    if row["contract"] == "semantic" or row["task_type"] in ("source_selection", "numerical_control"):
        return base
    old = prior.alternatives(row)
    options = ['{"choice":"X=1"}', '{"choice":"X=0"}']
    if row["answer_order"] == "reversed":
        options.reverse()
    return base.replace(old, " or ".join(options))


def prepare(directory, seed=SEED):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError(directory)
    with TemporaryDirectory() as tmp:
        prior.generate(Path(tmp) / "input", seed)
        old = read_jsonl(Path(tmp) / "input/oracle_truth.jsonl")
    truth, public = [], []
    for item in old:
        contracts = ("semantic", "neutral") if item["task_type"] in ("decision", "noncausal_control", "randomized_only") else ("semantic",)
        for contract in contracts:
            row = {**item, "contract": contract}
            row["task_id"] = hashlib.sha256(json.dumps([VERSION, item["task_id"], contract]).encode()).hexdigest()[:24]
            truth.append(row)
            public.append({"task_id": row["task_id"], "family_id": row["family_id"], "prompt": render(row)})
    # Keep the prior complete shuffle, with contract twins adjacent only before this new shuffle.
    import random
    random.Random(seed + 1).shuffle(public)
    directory.mkdir(parents=True)
    write_jsonl(directory / "public_tasks.jsonl", public)
    write_jsonl(directory / "oracle_truth.jsonl", truth)
    manifest = {"version": VERSION, "classification": "development_only", "seed": seed,
                "families": 8, "tasks": len(truth), "per_arm": len(truth),
                "file_sha256": {name: digest(directory / name) for name in ("public_tasks.jsonl", "oracle_truth.jsonl")}}
    write_json(directory / "manifest.json", manifest)
    validate(directory)
    return manifest


def validate(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["version"] != VERSION or manifest["families"] != 8 or manifest["tasks"] != 1472:
        raise ValueError("Unexpected matrix fixture specification")
    for name, expected in manifest["file_sha256"].items():
        if digest(directory / name) != expected:
            raise ValueError("Fixture file hash mismatch: " + name)
    truth = read_jsonl(directory / "oracle_truth.jsonl")
    public = read_jsonl(directory / "public_tasks.jsonl")
    if len(truth) != 1472 or len(public) != 1472:
        raise ValueError("Incomplete fixture")
    lookup = {p["task_id"]: p for p in public}
    if len(lookup) != len(public) or len({r["task_id"] for r in truth}) != len(truth):
        raise ValueError("Duplicate task IDs")
    counts = {}
    for row in truth:
        p = lookup.get(row["task_id"])
        if p != {"task_id": row["task_id"], "family_id": row["family_id"], "prompt": render(row)}:
            raise ValueError("Prompt/truth mismatch")
        kind, contract = row["task_type"], row["contract"]
        if contract == "neutral" and kind not in ("decision", "noncausal_control", "randomized_only"):
            raise ValueError("Invalid contract cell")
        world = prior.World(row["family_id"], row["causal_positive"], row["association_positive"],
                            prior.STRENGTH, row["severity_gap"], row["assignment_strength"])
        expected = world.truth()
        for key, value in expected.items():
            if key in ("do_success_x0", "do_success_x1"):
                value += row["rate_offset"]
            observed = row[key]
            if not (math.isclose(observed, value, rel_tol=0, abs_tol=1e-12) if isinstance(value, float) else observed == value):
                raise ValueError("SCM oracle mismatch")
        for actual, target in ((row["randomized_rates"], world.do_means + row["rate_offset"]),
                               (row["historical_rates"], world.observational_means + row["rate_offset"])):
            if any(not math.isclose(a, float(b), rel_tol=0, abs_tol=1e-12) for a, b in zip(actual, target)):
                raise ValueError("Displayed rate mismatch")
        key = (row["family_id"], kind, contract, row["causal_positive"], row["answer_order"])
        counts[key] = counts.get(key, 0) + 1
    expected = {"decision": 8, "noncausal_control": 8, "source_selection": 8,
                "randomized_only": 2, "numerical_control": 2}
    for family in {r["family_id"] for r in truth}:
        for kind, n in expected.items():
            for contract in (("semantic", "neutral") if kind in ("decision", "noncausal_control", "randomized_only") else ("semantic",)):
                for direction in (0, 1):
                    for order in ("canonical", "reversed"):
                        if counts.get((family, kind, contract, direction, order)) != n:
                            raise ValueError("Unbalanced cell")
    return {"valid": True, "tasks": len(truth), "families": 8, "manifest_sha256": digest(directory / "manifest.json")}


def score(truth, raw):
    ids = {r["task_id"] for r in truth}
    records = {}
    for record in raw:
        task_id = record["task_id"]
        if task_id not in ids or task_id in records:
            raise ValueError("Unknown or duplicate raw task ID")
        records[task_id] = record
    rows = []
    for row in truth:
        record = records.get(row["task_id"])
        answer = None
        finish = None
        if record and not record.get("execution_error"):
            try:
                choice = record["response"]["choices"][0]
                finish = choice["finish_reason"]
                if finish == "stop":
                    def unique(pairs):
                        out = {}
                        for key, value in pairs:
                            if key in out:
                                raise ValueError("Duplicate key")
                            out[key] = value
                        return out
                    obj = json.loads(choice["message"]["content"], object_pairs_hook=unique)
                    key = "governing_study" if row["task_type"] == "source_selection" else "larger" if row["task_type"] == "numerical_control" else "choice" if row["contract"] == "neutral" else "decision"
                    allowed = ("A", "B") if key == "governing_study" else ("X=0", "X=1") if key in ("larger", "choice") else ("activate", "leave_off")
                    if isinstance(obj, dict) and set(obj) == {key} and type(obj[key]) is str and obj[key] in allowed:
                        answer = obj[key]
            except (KeyError, IndexError, TypeError, ValueError):
                pass
        target = row["randomized_name"] if row["task_type"] == "source_selection" else ("X=1" if row["causal_positive"] else "X=0") if row["task_type"] == "numerical_control" or row["contract"] == "neutral" else ("activate" if row["optimal_action"] else "leave_off")
        rows.append({**row, "completed": record is not None, "finish_reason": finish,
                     "valid_answer": answer is not None, "answer": answer, "correct": int(answer == target)})
    return rows
