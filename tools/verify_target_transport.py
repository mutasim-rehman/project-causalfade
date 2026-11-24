"""Public message oracle. This module has no private fixture dependencies."""

import re
from fractions import Fraction


def parse(messages):
    if [m["role"] for m in messages] != ["system", "user"]:
        raise ValueError("Unexpected public message structure")
    sections = messages[1]["content"].split("\n\n")
    if len(sections) != 5:
        raise ValueError("Unexpected blocks in public prompt")
    _, mixture, *blocks, options = sections
    match = re.fullmatch(r"Target mix: Amber ([0-9]{1,3})%, Blue ([0-9]{1,3})%", mixture)
    if not match:
        raise ValueError("Invalid target mixture")
    weights = dict(zip(("Amber", "Blue"), (Fraction(x)/100 for x in match.groups())))
    if sum(weights.values()) != 1 or any(not 0 < x < 1 for x in weights.values()):
        raise ValueError("Invalid target probabilities")
    tables, tags = {}, {}
    for block in blocks:
        header, *cells = block.splitlines()
        info = re.fullmatch(r"Source ([AB]) \(([^()]+)\)", header)
        if not info or info[1] in tables or len(cells) != 2:
            raise ValueError("Missing or ambiguous source")
        name, tag = info.groups()
        tables[name], tags[name] = {}, tag
        for line in cells:
            cell = re.fullmatch(r"(Amber|Blue): off ([0-9]{1,3}\.[05])%, on ([0-9]{1,3}\.[05])%", line)
            if not cell or cell[1] in tables[name]:
                raise ValueError("Missing or invalid stratum")
            rates = tuple(Fraction(x)/100 for x in cell.groups()[1:])
            if any(not 0 < x < 1 for x in rates):
                raise ValueError("Invalid displayed rate")
            tables[name][cell[1]] = rates
    descriptors = set(tags.values())
    if descriptors == {"randomized study", "historical study"}:
        governing = "randomized study"
    elif descriptors == {"designated scorecard", "other scorecard"}:
        governing = "designated scorecard"
    else:
        raise ValueError("Ambiguous source designation")
    source = next(name for name, tag in tags.items() if tag == governing)
    option_order = re.findall(r'\{"activate":([01])\}', options)
    if sorted(option_order) != ["0", "1"]:
        raise ValueError("Invalid action alternatives")
    scores = tuple(sum(weights[group]*rates[a] for group, rates in tables[source].items())
                   for a in range(2))
    if scores[0] == scores[1]:
        raise ValueError("Zero target contrast")
    for left, right in (("A", "B"), ("B", "A")):
        for group in weights:
            for r, h in zip(tables[left][group], tables[right][group]):
                if not 0 < 2*h-r < 1 or not 0 < 3*r-2*h < 1:
                    raise ValueError("Infeasible source assignment")
    return {"source": source, "weights": weights, "tables": tables,
            "scores": scores, "action": int(scores[1] > scores[0]),
            "options": list(map(int, option_order)), "tags": tags}
