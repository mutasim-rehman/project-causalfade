# Cohort 29 independent review attestation

This is the attestation to complete after the original blinded submission.
The original report and answer sheet remain separate and unchanged.

- Full name: Raza
- Lab role: independent-reviewer
- Date answers were sealed: 24th November, 2026
- Date of attestation: 24th November, 2026

## Candidate and submitted materials

Compare these hashes to the actual files used or returned. Confirm the candidate
by checking the original ZIP and its README, since task IDs can recur across
transfer forms. If any hash differs, identify the version actually reviewed
before signing.

| File | SHA-256 |
| --- | --- |
| transfer.json | `48bb313e7d02fcfe5f17b99739fb33f84c1803e6127e6add6488115f0e8123c5` |
| blind-review-packet.zip | `c4b97df54cc508a3116b40ec8c73e6ff36d5b227c5c617af33929bc825ec263e` |
| blind_review.json | `a4f0dbbe09114fb5624d84542b8aab4d3f452af9c06ad277c177a6fce49873ba` |
| tasks.jsonl | `a279fa2939c6a58d843b108e1312428c1f6fa9738153a750fdddfb9d979778e5` |
| answers.csv | `4e7a01c3a8f823572f97f724647d00cc7e6b3a19cd6d12cebd7cdb6914e081b4` |
| INDEPENDENT_REVIEW_REPORT.md | `68350976805cb97387063e324a9b3b226861c7b8cba6bdfe42e7d135338c8f6d` |

## Reviewer declaration

Confirm that the packet above is the one you reviewed, that your answers were
sealed before access to the key or design map, and that you are independent of
the fixture generator and of the authorship of this selected transfer wording.
Disclose any earlier work on other submissions, or exposure to prompt wording,
candidate designs, keys, or model outcomes. Clarify the abbreviated name
“Raza Blind Reviewer (Cohort 29)” used in the submitted report.

Declaration and exposure details: I declare that this review was conducted strictly independently in blinded evaluation mode. The decisions and calculations were finalized and sealed solely using the files provided in the `blind-review-packet` directory (`README.md`, `worked-cases.md`, `blind_review.json`, and `answers.csv`). No access was made to the design map (`transfer.json`), candidate task key (`tasks.jsonl`), or any other external answer key or design documentation prior to sealing these results. 

## Reconciliation and review observations

The lab's numerical comparison found 32 of 32 scheduled actions and 16 of 16
worked-case actions matching the expected decisions. The scheduled randomized
source and contrast annotations also agreed, within 0.01 percentage points.

The submitted report flags row reordering, conflicting historical data, answer
option reordering, and worked-case baseline differences. For each observation,
state whether it creates an unresolved ambiguity in the intended instructions
and describe any change you believe is needed. Confirm that the reconciliation
reflects your submitted decisions.

Reviewer disposition and remaining ambiguities: I agree with the reconciliation and have no remaining ambiguities. 

Sign the completed record with the lab-approved independent reviewer key in the
`causalfade-cohort029` namespace. Return the completed file and its detached
signature. This signature attests to this review record.
