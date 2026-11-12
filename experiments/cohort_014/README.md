# Strict-output prompt-clarity feasibility screen

Cohort 013 found that the causal-context frame produced a complete leading action object followed by explanation on every response; all 64 reached the 160-token cap. The minimal frame produced valid fenced objects but failed the conflict-competence gate. Cohort 014 repeats the paired minimal/causal-context comparison on eight new matched-strength families with a stronger response contract and 48-token output budget.

Every prompt now requires exactly one bare JSON object with only the `activate` key, gives two valid one-line examples, and forbids fences or explanation. The same instruction is applied to both frames. The cap is 48 tokens, over three times the 14-token completion length observed for the short previous outputs; long explanations are not part of the target answer. Run 7B F16 only. Score strict JSON as primary and single-fence output as a separately labeled sensitivity.

Assess each prompt frame independently against the same reference thresholds: at least 56/64 valid actions, 44/64 correct overall, and 9/16 conflict correct in each evidence order. This is an exploratory development screen. Even a passing frame needs a separate confirmatory protocol and untouched families before any precision claim.
