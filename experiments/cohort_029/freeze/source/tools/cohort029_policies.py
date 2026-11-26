"""Behavior of fixed rival policies on the rendered CF-TP1 fixture."""

import gzip
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product

from tools.cohort029_prepare import encode, write


def predict(public, thresholds, tie):
    weights, tables, options = (public[k] for k in ("weights", "tables", "options"))
    sources = list(tables)[::1-2*tie]
    governing = tables[public["source"]]
    groups = list(governing)[::1-2*tie]
    diffs = {name: {g: cells[1]-cells[0] for g, cells in table.items()}
             for name, table in tables.items()}
    standardized = {name: sum(weights[g]*d for g, d in effects.items())
                    for name, effects in diffs.items()}
    def choose(d):
        return int(d > 0) if d else options[tie]

    majority = max(groups, key=weights.get)
    effects = diffs[public["source"]]
    action = choose(effects[majority])
    pick = max(groups, key=lambda g: abs(effects[g]))
    extreme = max(sources, key=lambda name: max(
        v for rates in tables[name].values() for v in rates))
    extreme_effect = max(sources, key=lambda name: max(map(abs, diffs[name].values())))
    highest = [max(pair[a] for pair in governing.values()) for a in range(2)]
    contribution = {a: sum(weights[g]*abs(d) for g, d in effects.items() if (d > 0) == a)
                    for a in (0, 1)}
    output = {
        "source_A": choose(standardized["A"]), "source_B": choose(standardized["B"]),
        "source_first": choose(standardized[list(tables)[0]]),
        "source_last": choose(standardized[list(tables)[-1]]),
        "source_min_effect": choose(standardized[min(sources, key=lambda n: abs(standardized[n]))]),
        "source_max_effect": choose(standardized[max(sources, key=lambda n: abs(standardized[n]))]),
        "source_extreme_rate": choose(standardized[extreme]),
        "source_extreme_effect": choose(standardized[extreme_effect]),
        "source_pool": choose(sum(standardized.values())),
        "target_equal": choose(sum(effects.values())),
        "target_amber": choose(effects["Amber"]), "target_blue": choose(effects["Blue"]),
        "target_majority": action, "target_largest_effect": choose(effects[pick]),
        "target_majority_treated": choose(governing[majority][1]-Fraction(1, 2)),
        "target_highest_rate": choose(highest[1]-highest[0]),
        "target_highest_treated": choose(max(row[1] for row in governing.values())-Fraction(1, 2)),
        "target_first_option": options[0], "target_last_option": options[-1],
        "target_constant_0": 0, "target_constant_1": 1,
        "role_invert_B": choose(standardized["A"]) ^ (public["source"] == "B"),
        "positive": choose(contribution[1]-contribution[0]),
    }
    for threshold, polarity, equality in product(thresholds, (0, 1), (0, 1)):
        share = weights[majority]
        above = int(share > threshold or (share == threshold and equality))
        key = f"{threshold}:{polarity}:{equality}"
        output["weight_only:" + key] = above ^ polarity
        output["weight_majority:" + key] = action ^ above ^ polarity
    return output


def audit(out, parsed, design, mock=False):
    thresholds = [Fraction(w, 100) for w in (*range(54, 63), *range(76, 85))]
    summary, failures, literal_failures = {}, [], []
    lookup = {tuple(row["indices"]): i for i, row in enumerate(design)}
    for tie in (0, 1):
        columns = defaultdict(bytearray)
        predicted_actions = defaultdict(set)
        with (out / f"policy_rows_tie_{tie}.jsonl.gz").open("xb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as records:
                for (key, public), row in zip(parsed, design, strict=True):
                    if key != row["task_id"]:
                        raise ValueError("Policy row ID mismatch")
                    predictions = predict(public, thresholds, tie)
                    records.write(encode(dict(task_id=key, predictions=predictions)) + b"\n")
                    for name, action in predictions.items():
                        columns[name].append(action == public["action"])
                        predicted_actions[name].add(action)
        target_pairs, role_pairs = [], []
        for i, row in enumerate(design):
            slot, f, t, o, r, k = row["indices"]
            if k == 0:
                target_pairs.append((i, lookup[(slot, f, t, o, r, 1)], row["p"]))
            if r == 0:
                role_pairs.append((i, lookup[(slot, f, t, o, 1, k)], row["g"]))
        report = {}
        for name, correct in columns.items():
            wrong = [(d, pub) for (_, pub), d, ok in zip(parsed, design, correct)
                     if not ok and d["indices"][1:3] == (1, 0)]
            families = len({d["indices"][0] for d, _ in wrong})
            actions = sorted({pub["action"] for _, pub in wrong})
            target = Counter((switch, correct[i]+correct[j]) for i, j, switch in target_pairs)
            role = Counter((switch, correct[i]+correct[j]) for i, j, switch in role_pairs)
            cells = Counter((tuple(d["indices"][1:]), d["h"], pub["options"][0], int(ok))
                            for (_, pub), d, ok in zip(parsed, design, correct))
            report[name] = dict(correct=sum(correct), total=len(correct),
                                disagreement_families=families, disagreement_items=len(wrong),
                                disagreement_actions=actions,
                                target_pairs=[[s, n, v] for (s, n), v in sorted(target.items())],
                                role_pairs=[[s, n, v] for (s, n), v in sorted(role.items())],
                                cells=[[factors, h, option, ok, count]
                                       for (factors, h, option, ok), count in sorted(cells.items())])
            # Only declared constants and mathematically constant threshold rules
            # qualify. A seemingly constant nondegenerate rival still faces the full gate.
            exempt = name in {"target_constant_0", "target_constant_1"}
            if name.startswith("weight_only:"):
                _, cutoff, _, inclusive = name.split(":")
                threshold = Fraction(cutoff)
                exempt = ((threshold == min(thresholds) and inclusive == "1") or
                          (threshold == max(thresholds) and inclusive == "0"))
            source_fail = name.startswith("source_") and (
                bool(role[1, 2]) or sum(correct)*4 > len(correct)*3)
            target_fail = name.startswith("target_") and (
                bool(target[1, 2]) or target[0, 2]*2 > len(target_pairs))
            if name == "positive":
                literal = clarified = sum(correct) != len(correct)
            else:
                core_fail = families < 16 or source_fail or target_fail
                literal = core_fail or actions != [0, 1]
                if exempt:
                    clarified = (core_fail or len(predicted_actions[name]) != 1 or
                                 sum(correct)*2 != len(correct) or bool(target[1, 2]))
                else:
                    clarified = literal
            report[name]["constant_rule_exception"] = exempt
            if literal:
                literal_failures.append((tie, name))
            if clarified:
                failures.append((tie, name))
        summary[str(tie)] = report
    write(out / "policy_audit.json", dict(ties=summary, failures=failures,
          literal_failures=literal_failures, policy_rule="constant-rivals-v1",
          forced_target_flip_wrong=sum(not switch for _, _, switch in target_pairs),
          forced_role_flip_wrong=sum(not switch for _, _, switch in role_pairs)))
    if literal_failures:
        print(f"Literal policy gate failures retained: {len(literal_failures)}", flush=True)
    if failures:
        print(f"Failures under policy clarification: {failures}", flush=True)
        if not mock:
            raise ValueError("Formal fixture failed the policy audit. See policy_audit.json.")
