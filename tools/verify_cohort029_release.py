"""Offline, model-free verification of the original Cohort 029 lab release.

This reads the frozen production files and saved response journal. It never
starts the runner or contacts the inference server. The output is an audit
report, not a replacement for the original freeze or response journal.
"""

import argparse
import base64
import collections
import hashlib
import json
import math
import statistics
from fractions import Fraction
from pathlib import Path

from causalfade.target_forms import render
from causalfade.target_transport import task_id
from tools.verify_target_transport import parse


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/cohort_029"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def read(path):
    return json.loads(path.read_bytes())


def lines(path):
    with path.open("rb") as source:
        return [json.loads(line) for line in source]


def fraction(value):
    return Fraction(value["numerator"], value["denominator"])


def strict_action(raw):
    class ObjectPairs(list):
        pass

    envelope = json.loads(raw)
    assert len(envelope["choices"]) == 1
    choice = envelope["choices"][0]
    assert choice["finish_reason"] == "stop"
    content = choice["message"]["content"]
    assert isinstance(content, str) and content.lstrip().startswith("{")
    value = json.loads(content, object_pairs_hook=ObjectPairs)
    assert type(value) is ObjectPairs and len(value) == 1
    assert value[0][0] == "activate" and type(value[0][1]) is int
    assert value[0][1] in (0, 1)
    return value[0][1]


def main(out):
    freeze = BASE / "freeze"
    fixture = freeze / "fixture"
    run = BASE / "runs/confirmatory"
    manifest = read(freeze / "manifest.json")
    schedule = read(fixture / "schedule.json")
    forms = read(fixture / "forms.json")
    worlds = {w["slot"]: w for w in lines(fixture / "worlds.jsonl")}
    tasks = {t["task_id"]: t for t in lines(fixture / "tasks.jsonl")}
    design = {d["task_id"]: d for d in lines(fixture / "design.jsonl")}
    gold = {g["task_id"]: g for g in lines(fixture / "gold.jsonl")}
    public = {p["task_id"]: p for p in lines(fixture / "public_oracle.jsonl")}
    inventory = read(freeze / "deployment/inventory.json")
    budget = read(freeze / "deployment/token_budget.json")
    journal = lines(run / "events.jsonl")
    checks = []

    def check(name, observed, expected):
        checks.append(dict(name=name, passed=observed == expected,
                           observed=observed, expected=expected))

    manifest_hash = sha(freeze / "manifest.json")
    check("manifest_sidecar_sha256", manifest_hash,
          (freeze / "manifest.sha256").read_text().strip())
    check("manifest_schema_protocol_cap", [manifest["schema"], manifest["protocol"], manifest["response_cap"]],
          [2, "CF-TP1", 4096])
    file_mismatches = []
    for name, item in manifest["files"].items():
        path = freeze / name
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
            file_mismatches.append(name)
    check("frozen_file_hash_mismatches", file_mismatches, [])
    source_mismatches = [name for name in manifest["files"] if name.startswith("source/")
                         and sha(ROOT / name.removeprefix("source/")) != manifest["files"][name]["sha256"]]
    check("frozen_source_hash_mismatches", source_mismatches, [])
    check("transfer_matches_original_lab_file", forms["transfer"], read(BASE / "lab/transfer.json"))
    check("transfer_matches_dated_submission", sha(BASE / "lab/transfer.json"),
          sha(BASE / "lab/intake/umar-asghar/2026-11-24-latest/transfer.json"))
    check("fixture_sizes", [len(worlds), len(schedule), len(tasks), len(design), len(gold), len(public)],
          [128, 4096, 4096, 4096, 4096, 4096])
    fixture_audit = read(fixture / "fixture_audit.json")
    check("fixture_audit_core", [fixture_audit["families"], fixture_audit["tasks"],
          fixture_audit["oracle_mismatches"], fixture_audit["worked_cases"],
          len(fixture_audit["dup_prompts"])], [128, 4096, 0, 4, 0])
    policy = read(fixture / "policy_audit.json")
    check("clarified_shortcut_policy_gate", [policy["policy_rule"], policy["failures"]],
          ["constant-rivals-v1", []])
    check("retained_literal_policy_failures", len(policy["literal_failures"]), 12)
    check("task_id_sets", all(set(x) == set(schedule) for x in (tasks, design, gold, public)), True)
    check("budget_task_set", set(budget["counts"]) == set(schedule), True)
    check("budget_input_hash", budget["tasks_sha256"], sha(fixture / "tasks.jsonl"))
    check("budget_runtime_hashes", [budget["model_sha256"], budget["server_sha256"]],
          [inventory["model_sha256"], inventory["server_sha256"]])
    check("tokenizer_template_sha256", hashlib.sha256(budget["template"].encode()).hexdigest(),
          budget["template_sha256"])
    check("token_budget_violations", sum(c["tokens"] + 48 > 2048 for c in budget["counts"].values()), 0)
    archive = ROOT / "experiments/cohort_016"
    archived_plan = read(archive / "frozen_run_plan.json")
    check("archived_model_sha256", inventory["model_sha256"], archived_plan["model_q4_k_m"]["sha256"])
    check("archived_runtime_sha256", inventory["server_sha256"], archived_plan["runtime_sha256"])
    check("frozen_sampling", inventory["sampling"],
          dict(temperature=0, seed=20261126, max_tokens=48, cache_prompt=False, stream=False))

    message_mismatches, request_hash_mismatches = [], []
    oracle_mismatches, direct_oracle_mismatches, id_mismatches = [], [], []
    for key in schedule:
        row = design[key]
        slot, form, task, order, role, target = row["indices"]
        world = worlds[slot]
        messages = render((forms["archive"], forms["transfer"])[form], task,
                          order, role, target, world["tables"], world["weights"], world["bits"])
        if messages != tasks[key]["messages"]:
            message_mismatches.append(key)
        if hashlib.sha256(encode(messages)).hexdigest() != tasks[key]["request_sha256"]:
            request_hash_mismatches.append(key)
        if task_id(tuple(row["indices"])) != key:
            id_mismatches.append(key)
        parsed = parse(messages)
        direct_scores = [sum(Fraction(weight, 100) * Fraction(world["tables"][role][s][action], 200)
                             for s, weight in enumerate((world["weights"][target],
                                                        100-world["weights"][target])))
                         for action in (0, 1)]
        if any(fraction(a) != b for a, b in zip(gold[key]["scores"], direct_scores)) or (
            gold[key]["action"] != int(direct_scores[1] > direct_scores[0])):
            direct_oracle_mismatches.append(key)
        if parsed["action"] != gold[key]["action"] or any(
            fraction(a) != b for a, b in zip(gold[key]["scores"], parsed["scores"])):
            oracle_mismatches.append(key)
        if parsed["action"] != public[key]["action"]:
            oracle_mismatches.append(key)
    check("reconstructed_message_mismatches", message_mismatches, [])
    check("reconstructed_request_hash_mismatches", request_hash_mismatches, [])
    check("task_id_mismatches", id_mismatches, [])
    check("public_private_oracle_mismatches", oracle_mismatches, [])
    check("independent_exact_oracle_mismatches", direct_oracle_mismatches, [])

    types = collections.Counter(e["type"] for e in journal)
    check("journal_event_counts", dict(types),
          dict(start=1, intent=4096, dispatch=4096, response=4096))
    check("journal_sequence_mismatches", [i for i, e in enumerate(journal)
          if e["sequence"] != i], [])
    binding = {"manifest_sha256": manifest_hash, "run_path": "experiments/cohort_029/runs/confirmatory"}
    check("journal_binding_mismatches", sum(e["binding"] != binding for e in journal), 0)
    responses, positions, corrupt = {}, [], []
    for event in journal:
        if event["type"] == "start":
            continue
        position = (event["sequence"] - 1) // 3
        key = schedule[position]
        if event["task_id"] != key or event["request_sha256"] != tasks[key]["request_sha256"]:
            positions.append(position)
        if event["type"] == "response":
            raw = base64.b64decode(event["response_b64"], validate=True)
            if event["http_status"] != 200 or hashlib.sha256(raw).hexdigest() != event["response_sha256"]:
                corrupt.append(position)
            responses[key] = strict_action(raw)
    check("journal_schedule_or_request_mismatches", positions, [])
    check("response_integrity_mismatches", corrupt, [])
    check("unique_completed_responses", len(responses), 4096)
    check("terminal_journal_sha256", read(run / "terminal.json")["journal_sha256"], sha(run / "events.jsonl"))
    check("terminal_complete", read(run / "terminal.json")["complete"], True)

    # Recalculate strict row and pair outcomes directly from saved response bytes.
    scored = {}
    for key in schedule:
        d = design[key]
        action = responses[key]
        scored[tuple(d["indices"])] = dict(**d, gold=gold[key]["action"], action=action,
                                            disposition="valid", correct=int(action == gold[key]["action"]),
                                            valid=True)
    saved_rows = {r["task_id"]: r for r in lines(run / "analysis/row_scores.jsonl")}
    check("independent_row_score_mismatches", [r["task_id"] for r in scored.values()
          if saved_rows.get(r["task_id"]) != r], [])
    pairs = []
    for dimension, kind in ((5, "target"), (4, "role"), (3, "physical_order")):
        for index, left in scored.items():
            if index[dimension]:
                continue
            right = scored[index[:dimension] + (1,) + index[dimension+1:]]
            count = left["correct"] + right["correct"]
            pairs.append(dict(kind=kind, indices=list(index), task_ids=[left["task_id"], right["task_id"]],
                              p=left["p"], g=left["g"], complete=True, valid_pair=True,
                              invalid_containing=False, action_invariant=left["action"] == right["action"],
                              correct_members=count, lower=int(count == 2), upper=int(count == 2)))
    saved_pairs = {(p["kind"], tuple(p["indices"])): p
                   for p in lines(run / "analysis/pair_scores.jsonl")}
    check("independent_pair_score_mismatches", [p["task_ids"] for p in pairs
          if saved_pairs.get((p["kind"], tuple(p["indices"]))) != p], [])
    transfer = [p for p in pairs if p["kind"] == "target" and p["indices"][1] == 1]
    by_arm = {t: [p for p in transfer if p["indices"][2] == t] for t in (0, 1)}
    primary = read(run / "analysis/primary.json")
    c, a = (sum(p["lower"] for p in by_arm[t]) for t in (0, 1))
    check("primary_fidelity_counts", [c, a],
          [primary["causal"]["both_correct"], primary["control"]["both_correct"]])
    check("reported_primary_fidelity_counts", [c, a], [128, 146])
    check("primary_difference", (c-a)/512, primary["delta"])
    check("reported_primary_difference_percentage_points", 100*(c-a)/512, -3.515625)
    family = collections.defaultdict(dict)
    for p in transfer:
        slot, _, task, _, _, _ = p["indices"]
        family[slot][task] = family[slot].get(task, 0) + p["lower"] / 4
    strata = [[family[s][0]-family[s][1] for s in range(16*h, 16*h+16)] for h in range(8)]
    mean = statistics.mean(statistics.mean(g) for g in strata)
    terms = [statistics.variance(g)/1024 for g in strata]
    se = math.sqrt(sum(terms))
    df = sum(terms)**2 / (sum(t*t for t in terms)/15)
    check("family_primary_mean_se_df", [mean, se, df],
          [primary["delta"], primary["se"], primary["welch_df"]])
    # A denser integration than the original analyzer checks its approximate
    # Student t interval without reusing the analyzer's numerical routine.
    def t_cdf(value):
        steps = 2048
        width = value / steps
        density = lambda x: (1+x*x/df)**(-(df+1)/2)
        area = width/3 * (density(0)+density(value)
               + 4*sum(density(i*width) for i in range(1, steps, 2))
               + 2*sum(density(i*width) for i in range(2, steps, 2)))
        norm = math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
        return 0.5 + norm*area

    lo, hi = 0., 4.
    for _ in range(55):
        mid = (lo+hi)/2
        if t_cdf(mid) < .975:
            lo = mid
        else:
            hi = mid
    width = (lo+hi)/2*se
    interval = [mean-width, mean+width]
    max_interval_error = max(abs(x-y) for x, y in zip(interval, primary["interval_t"]))
    checks.append(dict(name="independent_t_interval", passed=max_interval_error < 1e-8,
                       max_abs_difference=max_interval_error, tolerance=1e-8,
                       computed=interval, saved=primary["interval_t"]))
    half = math.sqrt(2*math.log(40)/128)
    check("independent_conservative_interval", [max(-1,mean-half), min(1,mean+half)],
          primary["interval_bounded"])
    check("reported_approximate_interval_rounded_pp", [round(100*x, 2) for x in interval],
          [-7.77, 0.74])
    secondary = read(run / "analysis/secondary.json")
    saved_cells = {tuple(x["key"]): x for x in secondary["pair_cells"]}
    cells = collections.defaultdict(collections.Counter)
    for p in pairs:
        _, form, task, *_ = p["indices"]
        switch = p["p"] if p["kind"] == "target" else p["g"] if p["kind"] == "role" else None
        cell = cells[p["kind"], form, task, switch]
        cell["scheduled"] += 1
        cell["valid_pair"] += 1
        cell["valid_pair_both_correct"] += p["correct_members"] == 2
        cell["action_invariant"] += p["action_invariant"]
        cell[f"correct_members_{p['correct_members']}"] += 1
    check("independent_secondary_pair_cell_mismatches", [list(k) for k, values in cells.items()
          if k not in saved_cells or {name: saved_cells[k].get(name, 0) for name in values} != dict(values)
          or saved_cells[k].get("missing_pair", 0) != 0
          or saved_cells[k].get("invalid_containing", 0) != 0], [])
    check("secondary_pair_cell_key_set", set(saved_cells) == set(cells), True)
    saved_rows_cells = {tuple(x["key"]): x for x in secondary["row_cells"]}
    row_cells = collections.defaultdict(collections.Counter)
    for r in scored.values():
        _, form, task, _, role, target = r["indices"]
        cell = row_cells[form, task, role, target, r["gold"]]
        cell["scheduled"] += 1
        cell["valid"] += 1
        cell["correct"] += r["correct"]
        cell["activated"] += r["action"]
    check("independent_secondary_row_cell_mismatches", [list(k) for k, values in row_cells.items()
          if k not in saved_rows_cells or {name: saved_rows_cells[k].get(name, 0) for name in values} != dict(values)], [])
    check("secondary_row_cell_key_set", set(saved_rows_cells) == set(row_cells), True)
    activation = sum(r["action"] for r in scored.values()
                     if r["indices"][1:3] == [1, 0])
    check("reported_causal_transfer_activation", activation, 995)
    def paircell(task, switch):
        return cells["target", 1, task, switch]
    check("reported_causal_reversal_both_correct", paircell(0, 1)["valid_pair_both_correct"], 3)
    check("reported_arithmetic_reversal_changes", 256-paircell(1, 1)["action_invariant"], 46)
    check("reported_arithmetic_invariant_changes", 256-paircell(1, 0)["action_invariant"], 45)

    report = dict(schema=1, mode="offline; no model inference", original_manifest_sha256=manifest_hash,
                  original_journal_sha256=sha(run / "events.jsonl"),
                  original_freeze= "experiments/cohort_029/freeze",
                  generated_analysis="experiments/cohort_029/runs/confirmatory/analysis",
                  checks=checks, passed=all(c["passed"] for c in checks),
                  counts=dict(families=128, tasks=4096, archive_messages=2048,
                              transfer_messages=2048, valid_responses=len(responses)),
                  primary=dict(causal_pair_fidelity=[c, 512], arithmetic_pair_fidelity=[a, 512],
                               difference_percentage_points=100*(c-a)/512,
                               approximate_interval_percentage_points=[100*x for x in primary["interval_t"]],
                               conservative_bounded_interval_percentage_points=[100*x for x in primary["interval_bounded"]]))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(encode(report) + b"\n")
    print(f"Cohort 029 offline verification: {'PASS' if report['passed'] else 'FAIL'}; "
          f"{sum(x['passed'] for x in checks)}/{len(checks)} checks")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", type=Path, default=BASE / "release/verification.json")
    main(cli.parse_args().out)
