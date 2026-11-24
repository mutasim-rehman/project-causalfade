"""Prepare and audit a candidate without model inference."""

import argparse
import itertools
import json
import random
import re
from copy import deepcopy
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from causalfade.target_forms import ARCHIVE, MOCK_TRANSFER, render
from causalfade.target_transport import (
    DESIGN, TOTAL, aliases, digest, encode, enumerate_world, rational, sample, task_id,
)
from tools.verify_target_transport import parse


def write(path, value, rows=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as out:
        if rows:
            for row in value:
                out.write(encode(row) + b"\n")
        else:
            out.write(encode(value) + b"\n")


def unpack(value):
    if isinstance(value, Fraction):
        return rational(value)
    if isinstance(value, dict):
        return {k: unpack(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [unpack(v) for v in value]
    return value


def worked_cases():
    left_switch, left_stable = ((106, 88), (112, 94))
    cases = ((left_switch, (91, 116), ((0, 1), (1, 0))),
             (left_stable, (90, 104), ((1, 1), (0, 0))),
             (left_stable, (110, 96), ((1, 1), (1, 1))),
             (left_switch, (107, 88), ((0, 1), (0, 1))))
    for left, right, expected in cases:
        tables = tuple(tuple((100, rate) for rate in source) for source in (left, right))
        for role, target, task in itertools.product(range(2), repeat=3):
            _, _, scores = enumerate_world(tables, (55, 80), role)
            public = parse(render(ARCHIVE, task, 0, role, target, tables, (55, 80), (0,)*4))
            if public["action"] != expected[role][target] or public["scores"] != scores[target]:
                raise ValueError("Worked case mismatch")
    return len(cases)


def projections(tables, weights, bits, target, role):
    names = ("A", "B")[::1-2*bits[0]]
    groups = ("Amber", "Blue")[::1-2*bits[1]]
    w = weights[target]
    return (names[role], dict(zip(groups, [Fraction(w, 100), Fraction(100-w, 100)])),
            {name: dict(zip(groups, (tuple(Fraction(v, 200) for v in row) for row in table)))
             for name, table in zip(names, tables)})


def verify_join(public, expected):
    if any(public[key] != value for key, value in expected.items()):
        raise ValueError("Public/private oracle mismatch")


def structural_audit(out, prompts, parsed, design):
    records = {tuple(d["indices"]): (p["messages"], public)
               for d, p, (_, public) in zip(design, prompts, parsed, strict=True)}
    checks = Counter()
    for idx, (messages, public) in records.items():
        context, mix, first, second, options = messages[1]["content"].split("\n\n")
        if re.search(r"CF-TP1|family-[0-9]+|target [01]\b|[a-f0-9]{64}",
                     messages[1]["content"], re.IGNORECASE):
            raise ValueError("Private fixture metadata leaked into public text")
        for dimension, name in ((2, "task"), (3, "order"), (4, "role"), (5, "target")):
            if idx[dimension]:
                continue
            other, partner = records[idx[:dimension]+(1,)+idx[dimension+1:]]
            new_context, new_mix, new_first, new_second, new_options = other[1]["content"].split("\n\n")
            strip = lambda block: re.sub(r" \([^\n]+\)", "", block, count=1)
            ok = other[0] == messages[0] and options == new_options
            if name == "target":
                ok &= (context, first, second) == (new_context, new_first, new_second) and mix != new_mix
            elif name == "order":
                ok &= (context, mix, first, second) == (new_context, new_mix, new_second, new_first)
                ok &= public["action"] == partner["action"]
            else:
                ok &= mix == new_mix and [strip(first), strip(second)] == [strip(new_first), strip(new_second)]
                if name == "task":
                    ok &= public["source"] == partner["source"] and public["scores"] == partner["scores"]
                else:
                    ok &= context == new_context and public["source"] != partner["source"]
            if not ok:
                raise ValueError(f"Structural difference violates {name} contract at {idx}")
            checks[name] += 1
    write(out / "structural_diffs.json", dict(checks=checks, mismatches=0))



def blind_review_packet(out, prompts, design):
    """Use the first slot of each stratum and alternate physical source order."""
    packets = [[] for _ in DESIGN]
    for prompt, row in zip(prompts, design, strict=True):
        slot, form, task, order, _, _ = row["indices"]
        h = row["h"]
        if slot == h*16 and form == 1 and task == 0 and order == h % 2:
            packets[h].append({k: prompt[k] for k in ("task_id", "messages")})
    if any(len(packet) != 4 for packet in packets):
        raise ValueError("Blinded review requires eight complete quartets")
    rng = random.Random(290434)
    rng.shuffle(packets)
    for packet in packets:
        rng.shuffle(packet)
    write(out / "blind_review.json", packets)



def prepare(out, transfer, mock):
    if not mock and sys.version_info[:2] != (3, 13):
        raise ValueError("Formal preparation requires Python 3.13")
    form = MOCK_TRANSFER if mock else json.loads(transfer.read_text())
    if set(form) != {"context", "arithmetic"} or any(
        not isinstance(v, str) or not v.strip() or "\n" in v for v in form.values()
    ):
        raise ValueError("Transfer form requires two single-paragraph strings")
    out.mkdir(parents=True, exist_ok=False)
    write(out / "forms.json", {"archive": ARCHIVE, "transfer": form, "mock": mock,
                               "python": sys.version.split()[0], "schema": 1})
    worlds, prompts, design, truth, parsed, expected, signatures = [], [], [], [], [], {}, []
    for slot, h, bits, stream, proposals, tables, weights, scm in sample():
        p, g, b = DESIGN[h]
        corners = [[scores[1] - scores[0] for scores in entry[2]] for entry in scm]
        if any(b*(-1)**(g*r+p*k)*corners[r][k] < Fraction(1, 200)
               for r, k in itertools.product(range(2), repeat=2)):
            raise ValueError("Gold corner violates margin")
        worlds.append(unpack(dict(slot=slot, family_id=f"family-{slot:03}", h=h,
                                  p=p, g=g, b=b, bits=bits, stream=f"{stream:064x}",
                                  proposals=proposals, tables=tables, weights=weights,
                                  scm=scm, corners=corners)))
        transformed = [tuple(int(v*2) for v in key) for key in aliases(tables, weights)]
        signatures.append((transformed[0], min(transformed), transformed))
        for f, t, order, role, target in itertools.product(range(2), repeat=5):
            indices = (slot, f, t, order, role, target)
            key = task_id(indices)
            messages = render((ARCHIVE, form)[f], t, order, role, target, tables, weights, bits)
            prompts.append(dict(task_id=key, messages=messages, request_sha256=digest(encode(messages))))
            design.append(dict(task_id=key, indices=indices, h=h, p=p, g=g, b=b, bits=bits,
                               family_id=f"family-{slot:03}"))
            scores = scm[role][2][target]
            action = int(scores[1] > scores[0])
            truth.append(unpack(dict(task_id=key, scores=scores, contrast=scores[1]-scores[0], action=action)))
            source, mixture, rates = projections(tables, weights, bits, target, role)
            expected[key] = dict(source=source, weights=mixture, tables=rates, scores=scores, action=action)
    for prompt in prompts:
        parsed.append((prompt["task_id"], parse(prompt["messages"])))
    write(out / "public_oracle.jsonl", (unpack(dict(task_id=k, **v)) for k, v in parsed), rows=True)
    for key, public in parsed:
        verify_join(public, expected[key])
    first = prompts[0]["messages"]
    for mutation in (lambda s: s.replace("randomized study)", "X)").replace(
            "historical study)", "randomized study)").replace("X)", "historical study)"),
            lambda s: re.sub(r"off (\d+)\.([05])%", lambda m:
                f"off {int(m[1])+(m[2]=='5')}.{5 if m[2]=='0' else 0}%", s, count=1)):
        changed = deepcopy(first)
        changed[1]["content"] = mutation(first[1]["content"])
        try:
            verify_join(parse(changed), expected[prompts[0]["task_id"]])
        except ValueError:
            pass
        else:
            raise ValueError("Oracle mutation went undetected")
    if len(signatures) != 128 or len({sig[1] for sig in signatures}) != 128:
        raise ValueError("Duplicate or mirrored family")
    near = []
    for i, (base, _, _) in enumerate(signatures):
        distance, neighbor = min(
            (min(max(abs(a-b) for a, b in zip(base, alias)) for alias in keys), j)
            for j, (_, _, keys) in enumerate(signatures) if i != j)
        near.append(dict(slot=i, neighbor=neighbor, distance_pp=distance/2, flagged=distance <= 2))
    ids = sorted(expected)
    if len(ids) != TOTAL or len(prompts) != TOTAL:
        raise ValueError("Task crossing count mismatch")
    random.Random(290432).shuffle(ids)
    seen = {}
    for prompt in prompts:
        key = prompt["request_sha256"]
        action = expected[prompt["task_id"]]["action"]
        if key in seen and seen[key][0] != action:
            raise ValueError("Duplicate messages have inconsistent actions")
        seen.setdefault(key, (action, []))[1].append(prompt["task_id"])
    nuisance = Counter((tuple(d["bits"]), expected[d["task_id"]]["action"]) for d in design)
    balance = Counter((tuple(d["indices"][1:]), expected[d["task_id"]]["action"]) for d in design)
    if any(nuisance[(bits, 0)] != nuisance[(bits, 1)] for bits, _ in nuisance) or any(
        balance[(factors, 0)] != balance[(factors, 1)] for factors, _ in balance
    ):
        raise ValueError("Unexpected public action imbalance")
    for name, data in (("worlds", worlds), ("tasks", prompts), ("design", design), ("gold", truth)):
        write(out / (name + ".jsonl"), data, rows=True)
    write(out / "schedule.json", ids)
    write(out / "fixture_audit.json", dict(families=len(worlds), tasks=len(ids),
          proposal_counts=[w["proposals"] for w in worlds], near_neighbors=near,
          dup_prompts=[v[1] for v in seen.values() if len(v[1]) > 1],
          worked_cases=worked_cases(), oracle_mismatches=0, mutation_checks=2))
    structural_audit(out, prompts, parsed, design)
    blind_review_packet(out, prompts, design)
    from tools.cohort029_policies import audit
    audit(out, parsed, design, mock=mock)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", type=Path, required=True)
    form = cli.add_mutually_exclusive_group(required=True)
    form.add_argument("--transfer", type=Path)
    form.add_argument("--mock", action="store_true")
    args = cli.parse_args()
    prepare(args.out, args.transfer, args.mock)
