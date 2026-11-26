"""Offline CF-TP1 scoring, calibration, terminal archive and mock replay."""

import argparse
import base64
import collections
import fcntl
import itertools
import json
import math
import random
import statistics
from pathlib import Path

from causalfade.target_transport import TOTAL, digest, encode, task_id
from tools.cohort029_prepare import write
from tools.cohort029_runtime import load, rows, sha
from tools.run_target_transport import JOURNAL, Ledger, load_schedule

HALF = math.sqrt(2*math.log(40)/128)


class JSONObject(list):
    """Preserve the object boundary and duplicate keys."""


def score(raw):
    try:
        reply = json.loads(raw.decode("utf-8"))
        choices = reply["choices"]
        if len(choices) != 1:
            return None, "choice_count"
        choice = choices[0]
        if choice["finish_reason"] != "stop":
            return None, "non_stop"
        content = choice["message"]["content"]
        if not isinstance(content, str) or not content.lstrip(" \t\r\n").startswith("{"):
            return None, "invalid_content"
        content.encode("utf-8")
        value = json.loads(content, object_pairs_hook=JSONObject)
        if type(value) is not JSONObject or len(value) != 1 or value[0][0] != "activate":
            return None, "invalid_keys"
        action = value[0][1]
        if type(action) is int and action in (0, 1):
            return action, "valid"
        return None, "invalid_action"
    except UnicodeError:
        return None, "invalid_utf8"
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError):
        return None, "malformed"


def moments(groups):
    if len(groups) != 8 or any(len(g) != 16 for g in groups):
        raise ValueError("The family analysis needs eight strata of 16")
    estimate = statistics.mean(map(statistics.mean, groups))
    terms = [statistics.variance(g)/1024 for g in groups]
    var = sum(terms)
    return estimate, math.sqrt(var), var**2/(sum(t*t for t in terms)/15) if var else None


def t_cdf(x, df):
    # Composite Simpson over the positive half of the symmetric t density.
    x = min(abs(x), 12)
    n = 128
    step = x/n
    values = [(1+(i*step)**2/df)**(-(df+1)/2) for i in range(n+1)]
    integral = step/3 * (values[0]+values[-1]+4*sum(values[1:n:2])+2*sum(values[2:n:2]))
    normalizer = math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
    return 0.5 + normalizer*integral


def bounded(mean):
    return [max(-1, mean-HALF), min(1, mean+HALF)]


def intervals(groups):
    mean, se, df = moments(groups)
    approx = None
    if df is not None:
        lo, hi = 0., 4.
        for _ in range(42):
            mid = (lo+hi)/2
            if t_cdf(mid, df) < .975:
                lo = mid
            else:
                hi = mid
        width = (lo+hi)/2*se
        approx = [mean-width, mean+width]
    return dict(delta=mean, se=se, welch_df=df, interval_t=approx, interval_bounded=bounded(mean))


def calibrate(out):
    rng = random.Random(290433)
    scenarios = {
        "constant": ([0]*8, 0., False),
        "rare": ([.02]*8, .02, False),
        "balanced_extremes": ([.5]*8, 0., True),
        "heterogeneous": ([(i+1)/10*(-1)**i for i in range(8)], -.05, False),
    }
    results = {}
    for name, (rates, truth, extremes) in scenarios.items():
        raw, available, fallback, covered, bound = 0, 0, 0, 0, 0
        for _ in range(10000):
            groups = []
            for p in rates:
                n = sum(rng.random() < abs(p) for _ in range(16))
                groups.append([1 if p >= 0 else -1]*n + [-int(extremes)]*(16-n))
            # Only successes and signed values enter the family-level statistics.
            mean, se, df = moments(groups)
            bounded_ok = abs(mean-truth) <= HALF
            bound += bounded_ok
            if df is None:
                fallback += bounded_ok
                covered += bounded_ok
            else:
                available += 1
                ok = abs(mean-truth)/se <= 1.95 or t_cdf(abs(mean-truth)/se, df) <= .975
                raw += ok
                covered += ok
        rate = covered/10000
        results[name] = dict(replications=10000, true_mean=truth, reporting_coverage=rate,
                             mcse=math.sqrt(rate*(1-rate)/10000), t_available=available,
                             t_conditional_coverage=raw/available if available else None,
                             t_suppressed=10000-available, bounded_coverage=bound/10000,
                             fallback_coverage=fallback/(10000-available) if available < 10000 else None)
    write(out, dict(seed=290433, scenarios=results,
                    coverage_primary="bounded" if min(r["reporting_coverage"] for r in results.values()) < .94 else "t"))


def mock_response(action):
    return encode({"choices": [{"finish_reason": "stop",
                                "message": {"content": json.dumps({"activate": action})}}]})


def mock_run(candidate, out):
    out.mkdir(parents=True, exist_ok=False)
    schedule, tasks = load_schedule(candidate)
    gold = {x["task_id"]: x["action"] for x in rows(candidate / "gold.jsonl")}
    design = {x["task_id"]: x for x in rows(candidate / "design.jsonl")}
    binding = {"mode": "mock"}
    file = out / JOURNAL
    journal = Ledger(file, schedule, tasks, binding)
    journal.event("start")
    journal.event("intent")
    journal = Ledger(file, schedule, tasks, binding)
    journal.recover()
    for key in schedule:
        journal.event("intent")
        journal.event("dispatch")
        slot, form, arm, *_ = design[key]["indices"]
        flipped = form == 1 and ((arm == 0 and slot == 0) or (arm == 1 and slot in (16, 17)))
        raw = mock_response(gold[key] ^ flipped)
        journal.event("response", http_status=200, response_b64=base64.b64encode(raw).decode(),
                      response_sha256=digest(raw), duration_seconds=0)
    final = Ledger(file, schedule, tasks, binding)
    if len(final.done) != TOTAL or final.failures != 1:
        raise ValueError("Mock resume reconciliation failed")
    from tools.run_target_transport import progress
    import time
    progress(out, final, "mock_complete", time.monotonic(), TOTAL)
    close(candidate, out, out / "terminal.json", False)
    result = analyze(candidate, out, out / "terminal.json", out / "analysis")
    if result["delta"] != 1/128:
        raise ValueError("Known mock signed family effect failed")
    write(out / "mock_recovery.json", dict(passed=True, completed=TOTAL, pre_dispatch_recovered=1,
         expected_delta=1/128, observed_delta=result["delta"]))


def archived(fixture, run):
    schedule, tasks = load_schedule(fixture)
    path = run / JOURNAL
    with path.open("rb") as src:
        first = json.loads(src.readline())
    return Ledger(path, schedule, tasks, first["binding"])


def close(fixture, run, out, abandon):
    if out.resolve() != (run / "terminal.json").resolve():
        raise ValueError("Use terminal.json inside the run directory")
    with (run / "runner.local.lock").open("ab") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        seal_terminal(fixture, run, out, abandon)


def seal_terminal(fixture, run, out, abandon):
    ledger = archived(fixture, run)
    complete = len(ledger.done) == TOTAL
    if not complete and not abandon:
        raise ValueError("Missing responses. Explicit abandonment is required to close.")
    write(out, dict(schema=1, complete=complete, disposition="complete" if complete else "abandoned",
          journal_sha256=sha(run / JOURNAL), schedule_sha256=sha(fixture / "schedule.json"),
          tasks_sha256=sha(fixture / "tasks.jsonl"), binding=ledger.binding,
          outstanding=[dict(task_id=k, reason=("ambiguous_dispatch" if i == 0 and ledger.open
                         and ledger.open[1] != "intent" else "uncollected"))
                       for i, k in enumerate(ledger.schedule[len(ledger.done):])]))


def unique(path, keys):
    records = rows(path)
    by_id = {v["task_id"]: v for v in records}
    if len(by_id) != len(records) or set(by_id) != set(keys):
        raise ValueError(f"Invalid unique join: {path}")
    return by_id


def analyze(fixture, run, terminal, out):
    ledger = archived(fixture, run)
    closure = load(terminal)
    if (closure["journal_sha256"] != sha(run / JOURNAL) or closure["binding"] != ledger.binding or
        closure["schedule_sha256"] != sha(fixture / "schedule.json") or
        closure["tasks_sha256"] != sha(fixture / "tasks.jsonl") or
        closure["complete"] != (len(ledger.done) == TOTAL)):
        raise ValueError("Terminal record no longer matches the archive")
    manifest_path = fixture.parent / "manifest.json"
    coverage_primary = None
    if ledger.binding.get("mode") != "mock":
        manifest = load(manifest_path)
        if sha(manifest_path) != ledger.binding["manifest_sha256"]:
            raise ValueError("Analysis fixture differs from frozen manifest")
        for name in ("design.jsonl", "gold.jsonl"):
            if sha(fixture / name) != manifest["files"][f"fixture/{name}"]["sha256"]:
                raise ValueError(f"Frozen analysis file changed: {name}")
        coverage_primary = manifest["coverage_primary"]
    design = unique(fixture / "design.jsonl", ledger.schedule)
    gold = unique(fixture / "gold.jsonl", ledger.schedule)
    lookup, scored = {}, []
    for key in ledger.schedule:
        d, expected = design[key], gold[key]["action"]
        idx = tuple(d["indices"])
        if task_id(idx) != key or idx[0]//16 != d["h"] or idx in lookup or expected not in (0, 1):
            raise ValueError("Invalid design map or oracle join")
        if key in ledger.done:
            action, disposition = score(base64.b64decode(ledger.done[key]["response_b64"]))
            correct = int(action == expected)
        else:
            action, disposition, correct = None, "missing", None
        row = dict(**d, gold=expected, action=action, disposition=disposition,
                   correct=correct, valid=disposition == "valid")
        scored.append(row)
        lookup[idx] = row
    pairs = []
    slots = collections.defaultdict(list)
    for dimension, kind in ((5, "target"), (4, "role"), (3, "physical_order")):
        for idx, row in lookup.items():
            if idx[dimension]:
                continue
            other = lookup[idx[:dimension] + (1,) + idx[dimension+1:]]
            values = row["correct"], other["correct"]
            valid = row["valid"] and other["valid"]
            known = None not in values
            a, b = row["action"], other["action"]
            record = dict(kind=kind, indices=idx, task_ids=[row["task_id"], other["task_id"]],
                          p=row["p"], g=row["g"], complete=known, valid_pair=valid,
                          invalid_containing=any(x["correct"] is not None and not x["valid"]
                                                 for x in (row, other)),
                          action_invariant=(a == b if valid else None),
                          correct_members=sum(values) if known else None,
                          lower=int(all(values)),
                          upper=int(all(v != 0 for v in values)))
            pairs.append(record)
            if kind == "target":
                slots[idx[:3]].append(record)
    families = []
    for slot, form in itertools.product(range(128), range(2)):
        causal, control = (slots[slot, form, t] for t in range(2))
        c0, c1 = (sum(r[b] for r in causal)/4 for b in ("lower", "upper"))
        a0, a1 = (sum(r[b] for r in control)/4 for b in ("lower", "upper"))
        families.append(dict(slot=slot, h=slot//16, form=form, causal_lower=c0, causal_upper=c1,
                             control_lower=a0, control_upper=a1,
                             delta_lower=c0-a1, delta_upper=c1-a0))
    transfer = [f for f in families if f["form"] == 1]
    complete = closure["complete"]
    primary_complete = all(p["complete"] for p in pairs if p["kind"] == "target" and p["indices"][1] == 1)
    strata = [[f["delta_lower"] for f in transfer if f["h"] == h] for h in range(8)]
    primary = dict(complete_fixture=complete, complete_primary=primary_complete, unit="proportion",
                   identification_bounds=[statistics.mean(f[b] for f in transfer) for b in
                                          ("delta_lower", "delta_upper")],
                   coverage_primary=coverage_primary,
                   scheduled_pairs_per_transfer_task=512)
    if primary_complete:
        primary.update(intervals(strata))
        primary["delta_percentage_points"] = 100*primary["delta"]
        for t, arm in enumerate(("causal", "control")):
            n = sum(f[f"{arm}_lower"]*4 for f in transfer)
            primary[arm] = dict(both_correct=int(n), scheduled=512, fidelity=n/512)
    pair_cells = collections.defaultdict(collections.Counter)
    for p in pairs:
        _, form, task, *_ = p["indices"]
        switch = p["p"] if p["kind"] == "target" else p["g"] if p["kind"] == "role" else None
        cell = pair_cells[p["kind"], form, task, switch]
        cell["scheduled"] += 1
        cell["missing_pair"] += not p["complete"]
        cell["valid_pair"] += p["valid_pair"]
        cell["valid_pair_both_correct"] += p["valid_pair"] and p["correct_members"] == 2
        cell["invalid_containing"] += p["invalid_containing"]
        cell["action_invariant"] += p["action_invariant"] is True
        if p["complete"]:
            cell[f"correct_members_{p['correct_members']}"] += 1
    row_cells = collections.defaultdict(collections.Counter)
    for r in scored:
        _, form, task, _, role, target = r["indices"]
        cell = row_cells[form, task, role, target, r["gold"]]
        cell["scheduled"] += 1
        cell[r["disposition"]] += 1
        cell["correct"] += r["correct"] == 1
        cell["activated"] += r["action"] == 1
    secondary = dict(pair_cells=[dict(key=k, **c) for k, c in pair_cells.items()],
                     row_cells=[dict(key=k, **c) for k, c in row_cells.items()],
                     transfer_minus_archive=(statistics.mean(f["delta_lower"] for f in transfer) -
                         statistics.mean(f["delta_lower"] for f in families if f["form"] == 0)) if complete else None)
    out.mkdir(parents=True, exist_ok=False)
    for name, records in (("row_scores", scored), ("pair_scores", pairs), ("family_scores", families)):
        write(out / (name + ".jsonl"), records, rows=True)
    write(out / "stratum_scores.json", [
        dict(h=h, family_count=len(g), mean_delta=statistics.mean(g) if primary_complete else None)
        for h, g in enumerate(strata)])
    write(out / "primary.json", primary)
    write(out / "secondary.json", secondary)
    write(out / "analysis_manifest.json", dict(terminal_sha256=sha(terminal), schema=1,
          inputs={name: sha(fixture / name) for name in ("schedule.json", "design.jsonl", "gold.jsonl")},
          journal_sha256=sha(run / JOURNAL), analyzer_sha256=sha(Path(__file__)),
          outputs={p.name: sha(p) for p in sorted(out.iterdir())}))
    print(json.dumps(primary, indent=2))
    return primary


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    for name, flags in (("mock-run", ("candidate", "out")), ("calibrate-intervals", ("out",)),
                        ("close", ("fixture", "run", "out")),
                        ("analyze", ("fixture", "run", "terminal", "out")),
                        ("reproduce", ("fixture", "run", "terminal", "out", "reference"))):
        cmd = sub.add_parser(name)
        for f in flags:
            cmd.add_argument("--" + f, type=Path, required=True)
        if name == "close":
            cmd.add_argument("--abandon", action="store_true")
    args = vars(cli.parse_args())
    op = args.pop("command")
    if op == "reproduce":
        reference = args.pop("reference")
        analyze(**args)
        outputs = load(reference / "analysis_manifest.json")["outputs"]
        changed = [name for name, digest_value in outputs.items()
                   if sha(args["out"] / name) != digest_value]
        write(args["out"] / "reproduction_report.json", dict(passed=not changed, changed=changed))
        if changed:
            raise ValueError(f"Replay differs: {changed}")
        return
    {"mock-run": mock_run, "calibrate-intervals": calibrate, "close": close, "analyze": analyze}[op](**args)


if __name__ == "__main__":
    main()
