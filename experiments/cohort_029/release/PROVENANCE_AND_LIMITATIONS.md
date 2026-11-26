# Production provenance and limits

## Original versus later files

The lab PC held the original `freeze/` directory, created on 25 November 2026
before the first journal event. Its manifest SHA-256 is
`5252f69d30a0a5bb65a5efa669458e325c0531f25ab55f768531c7ca29f4c766`.
The first journal event records 2026-11-25 08:15:14 UTC, and every event binds
that exact manifest hash. The 4,096-response journal SHA-256 is
`673eb723637614dc8b94875f2e8c4e9e20234c1d179c992791853797875977bd`.
Neither the freeze nor the journal was regenerated for this release. The
release's `terminal.json`, analyses, verification report and figures were
created **after** collection from saved data. They are later derived files,
not pre-inference evidence. The journal itself was committed at `d909097`.

The frozen files include the original `inventory.json` and
`token_budget.json`, which document the pinned Qwen2.5-7B-Instruct Q4_K_M
checkpoint, archived llama.cpp server build, 2,048-token context, 48-token
completion cap, temperature zero, seed 20261126, no prompt caching and no
response streaming. The model and server binaries are not redistributed.
The tokenizer preflight covered all 4,096 tasks. The freeze also contains
the generator, renderer, scorer, protocol, amendment, and pre-inference mock
recovery and interval-calibration evidence. The later release verifier checks
their hashes and deterministic behavior without loading the model.

## Transfer form and human review

`lab/transfer.json` exactly matches the transfer text in the freeze and the
dated 24 November submission in the original lab intake. Its SHA-256 is
`48bb313e7d02fcfe5f17b99739fb33f84c1803e6127e6add6488115f0e8123c5`.
The lab also holds an authorship declaration attributed to Umar Asghar. It
declares that Claude drafted the two paragraphs from his brief and that he
did not open the mock wording. The declaration's detached SSH signature
validates the file bytes cryptographically, but its key was **not** in the
available trusted signer list, so signer identity could not be authenticated
from that list.

A separate blinded review packet and answer sheet exist. Their hashes match
the production freeze's `blind_review.json` and `tasks.jsonl`. The lab's
reconciliation reports 32/32 scheduled decisions and 16/16 worked decisions
matching, with no source or reported-effect mismatch. A later review
attestation verifies with the available `Raza` public key in the
`causalfade-cohort029` SSH namespace. The submitted reviewer label is
abbreviated, and the old reconciliation file still states that identity,
candidate binding and signature were pending. The signed attestation supplies
candidate hashes, but there is no amended freeze provenance recording an
independence determination before collection. The frozen provenance therefore
remains exactly as executed: **independent authorship undocumented; independent
review undocumented**. These recovered records support a more detailed
historical account but do not retroactively change the frozen declaration.

The original authorship declaration, detached signature, blinded review
packet, answer sheet, signed review attestation, and available trusted public
key list are included under their existing `lab/` paths. The draft gate
documents remain on the lab PC and are not presented as production gate
passes. These records do not prove a fully independently authored or reviewed
instrument. The transfer form is included to permit exact prompt
reproduction; its author's downstream licensing permission has not been
documented.

## Validation timing

Before inference, the freeze rebuilt the candidate byte for byte, checked
the public and private oracles, fixture balance, prompt differences, shortcut
policies, tokenizer budget, mock recovery and interval calibration. The
frozen `evidence/` files document those checks. The literal policy audit
retained 12 failed constant/weight-only rival gates, documented in the
constant-rival clarification; the clarified gate passed. These failures are
not erased from the release.

After inference, the lab reran all 12 Cohort 029 unit tests and a fresh
full fixture rebuild. The rebuild matched the frozen fixture byte for byte.
It also ran the release's 50-check offline verifier and the original-code
analysis replay. These later checks support reproduction but are **not**
represented as preregistered pre-run checks.

## Scientific and licensing scope

The primary approximate t interval crosses zero. It is a failure to detect a
reliable advantage in this one deployment, not an equivalence result.
Performance cannot identify an internal causal-reasoning mechanism. The
original selective quantization hypothesis is not established by Cohort 029.
The family sample and task framing limit generalization.

The repository contains third-party research papers and model references;
their own licenses control reuse. Model weights and llama.cpp binaries are
not part of this release. The project has no blanket prior open-source license.
The numerical data, code, manuscript text and transfer wording therefore
need rights review before a later redistribution license is asserted. Public
GitHub access and exact offline reproduction are available now; public access
does not itself grant permission to republish third-party or contributor text.
