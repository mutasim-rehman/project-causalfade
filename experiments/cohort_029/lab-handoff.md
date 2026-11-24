# Cohort 029 transfer form and review notes

## Transfer form

Provide `experiments/cohort_029/lab/transfer.json` with two
single-paragraph strings called `context` and `arithmetic`. For an independent submission, write from the scientific specification before inspecting archive or mock wording. The
renderer adds the system message, group names, target mix, two source blocks and
JSON response contract. The source blocks identify the randomized and historical
studies in the causal task, and the designated and other scorecards in the
arithmetic task.

The causal introduction should explain the randomized assignment and historical
operator selection, possible unmeasured risk, pre-treatment groups, transport of
group effects, and the goal of maximizing target success. Keep the calculation
implicit. The arithmetic introduction should explicitly instruct the reader to
weight the designated scorecard's on and off scores by the target mix and choose
the higher total. Use the noncausal scorecard setting. Do not include examples or
fixture-specific data in either paragraph.

Record the author and date, actual independence status and outcome exposure,
and the SHA-256 of the submitted file. Use the lab installation for formal
preparation and token preflight with Python 3.13. The mock wording is not an
independent transfer submission.

## Review and provenance

Use the candidate's blind_review.json for the eight transfer quartets and review the four worked cases. If someone performs an independent blinded review, record their actual exposure, answers before seeing the key, and reconciliation. Describe a solo review as such. Record missing independent authorship or review as a limitation in freeze provenance and the manuscript. Stop for ambiguous or scientifically incorrect instructions. Follow the [single-researcher runbook](README.md) to validate, freeze and launch explicitly.
