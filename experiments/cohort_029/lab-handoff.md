# Cohort 29 independent review handoff

## Transfer author

Provide `experiments/cohort_029/lab/transfer.json` with two independently written
single-paragraph strings called `context` and `arithmetic`. Write from the
scientific specification before inspecting the archive and mock wording. The
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

Record the author and date, a declaration of independence and outcome exposure,
and the SHA-256 of the submitted file. The benchmark engineer runs formal
preparation and token preflight with Python 3.13. The mock wording is not an
independent transfer submission.

## Independent reviewer and gate owners

Solve the eight blinded transfer-form causal role-by-target quartets in the
formal candidate's `blind_review.json` plus the four worked cases. Record decisions before accessing the
private oracle and reconcile them afterwards. Document any ambiguity and review
the independence of the public verifier. Sign the review alongside the transfer
authorship record in `form_review.md`.

Copy or regenerate the mock recovery and coverage reports into `lab/evidence/`.
Record gate evidence for the formal candidate in `gates.json` and record the
clarification and any prior formal failures in `deviations.json`. The
[runbook](README.md) specifies the evidence fields and signing commands.
The PI signs the clarification separately from the manifest and the final run
authorization.
