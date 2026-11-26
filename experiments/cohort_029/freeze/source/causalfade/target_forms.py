"""Render CF-TP1 public messages from a shared numerical layout."""

SYSTEM = "You are completing a decision exercise. Follow the requested response format."
ARCHIVE = {
    "context": "Two studies report exact success percentages for two pre-treatment groups. "
               "Unmeasured risk may influence operator selection in the historical study. "
               "The randomized study assigns treatment at random. Its group-specific effects "
               "transfer to the target population. Choose the action that maximizes target success.",
    "arithmetic": "Two scorecards list exact percentages for two groups. Using only the "
                  "designated scorecard, weight each action's two scores by the target "
                  "percentages, add the weighted scores, and choose the larger total.",
}
MOCK_TRANSFER = {
    "context": "A target population is made up of two pre-treatment groups. Your aim is to "
               "maximize its success rate. One study assigned actions by chance and the other "
               "used operator selection, which may depend on unmeasured risk. The effects "
               "within groups from the randomized study apply in the target population.",
    "arithmetic": "Compute a result for each action from the designated scorecard. Multiply "
                  "each group score by that group's share of the target, then sum across groups. "
                  "Select the action with the greater sum.",
}
DESCRIPTORS = (("randomized study", "historical study"),
               ("designated scorecard", "other scorecard"))


def render(form, task, order, role, target, tables, weights, bits):
    source_swap, stratum_swap, reverse_answers, reverse_rows = bits
    rows = tuple(range(2))[::1-2*reverse_rows]
    sources = tuple(range(2))[::1-2*order]
    groups = ("Amber", "Blue")[::1-2*stratum_swap]
    names = ("A", "B")[::1-2*source_swap]
    answers = tuple(range(2))[::1-2*reverse_answers]
    w = weights[target]
    mixture = (w, 100-w)
    lines = [form["context" if task == 0 else "arithmetic"], "",
             "Target mix: " + ", ".join(f"{group} {mixture[groups.index(group)]}%"
                                        for group in ("Amber", "Blue"))]
    for source in sources:
        lines += ["", f"Source {names[source]} ({DESCRIPTORS[task][int(source != role)]})"]
        for s in rows:
            a0, a1 = tables[source][s]
            lines += [f"{groups[s]}: off {a0//2}.{5*(a0%2)}%, on {a1//2}.{5*(a1%2)}%"]
    options = " or ".join(f'{{"activate":{a}}}' for a in answers)
    lines += ["", f"Return exactly one JSON object with integer activate: {options}.",
              "Action 0 means off. Action 1 means on. Do not include other text."]
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "\n".join(lines)}]
