# Cohort 029 — CF-TP1 single-researcher runbook

**Collection completed on 25 November 2026.** All 4,096 scheduled responses
are saved. This document preserves the historical launch procedure; use the
[offline release guide](release/REPRODUCE.md) to verify and analyze the
completed experiment without model inference.

The original [CF-TP1 scientific specification](CF-TP1-v1.0.md) is archived verbatim. This workflow supersedes its signing and committee administration. It retains the generator, two forms, numerical and public-text oracles, rival policies, matched controls, model configuration, 128 families, 4,096 scheduled responses and statistical endpoints. Offline verification from previous versions is historical evidence.

## 1. Prepare and validate

On the lab PC, place the actual final two-paragraph JSON form at the path below. See the [form requirements](lab-handoff.md). Review the wording against the scientific question and record actual limitations. Use one Python 3.13 patch throughout. Use new output directories; preserve failed attempts and follow the protocol's one-repair limit.

~~~bash
cd /home/i242514/Desktop/project-causalfade
C29=experiments/cohort_029
python3.13 -m tools.cohort029_prepare --transfer "$C29/lab/transfer.json" --out "$C29/candidate"
python3.13 -m unittest discover -s tests -p 'test_target_transport*.py' -v
python3.13 -m tools.cohort029_runtime --candidate "$C29/candidate" --out "$C29/preflight"
~~~

Preparation verifies SCM feasibility, paired truth and margins, public-text agreement, prompt changes, balance and scientific rival-policy gates. The runtime preflight uses the pinned local server and model for chat formatting and tokenization only. Check the forms, review packet, fixture audit, literal and clarified rival-policy results, and tokenizer budget. Numerical oracle agreement cannot certify the meaning of the prose.

## 2. Freeze and check readiness

~~~bash
python3.13 -m tools.freeze_target_transport --candidate "$C29/candidate" --preflight "$C29/preflight" --out "$C29/freeze"
python3.13 -m tools.run_target_transport check-ready
~~~

Optional freeze arguments --authorship "..." and --review "..." record the actual author, exposure, review work, and/or lack of independence. Omission records independence as undocumented, which limits transfer claims. Keep original supporting records with the release. Automated oracle agreement does not establish independent human review.

Freeze regenerates the formal fixture, compares its files byte-for-byte with the candidate, checks the tokenizer evidence, exercises mock interruption/recovery and scoring, and runs the prespecified interval calibration. It publishes the results, protocol, implementation snapshot, provenance, manifest and checksum into a new directory only after success. Save the printed manifest SHA-256 in your research log. The sidecar detects accidental changes; the log provides an external reference. Readiness rechecks frozen files, source and the local deployment inventory without issuing a completion. Investigate and disclose failed checks.

## 3. Explicitly start collection

Execute the following only when ready for real responses. The formal run path is fixed.

~~~bash
python3.13 -m tools.run_target_transport run
~~~

Monitor from a second terminal. After an interruption use resume with the same freeze and journal.

~~~bash
python3.13 -m tools.run_target_transport stream --out experiments/cohort_029/runs/confirmatory
python3.13 -m tools.run_target_transport resume
~~~

The stream shows saved responses out of 4,096, percentage, remaining calls, ETA,
connection failures and ambiguous dispatches. Keep the PC awake. The runner retries
connection failures before dispatch with backoff and can restart a failed server
before dispatch. A response that may have been generated stops collection and
requires lab reconciliation. A persisted malformed or capped reply consumes its
scheduled call. For a clean interruption, repeat the launch command with `resume`.
The journal and lock must remain on the same persistent filesystem. Restoring only a
Git snapshot after disk loss cannot resolve requests made after that snapshot.

The runner commits the journal and progress snapshot every five minutes when it
returns from a request, and on completion or controlled exit. It pushes
`origin/codex/cohort-029-checkpoints` without altering the working branch or index.
Set up noninteractive Git authentication before launch. A failed push leaves a local
commit and is attempted again at the next checkpoint. Resume after a push failure
at completion to retry the push without dispatching any calls. The two Git paths
contain response envelopes and progress. Use the lab's authorized remote.

## Close, score and reproduce offline

```bash
C29=experiments/cohort_029
RUN="$C29/runs/confirmatory"
python3.13 -m tools.analyze_target_transport close \
  --fixture "$C29/freeze/fixture" --run "$RUN" --out "$RUN/terminal.json"
python3.13 -m tools.analyze_target_transport analyze \
  --fixture "$C29/freeze/fixture" --run "$RUN" \
  --terminal "$RUN/terminal.json" --out "$RUN/analysis"
python3.13 -m tools.analyze_target_transport reproduce \
  --fixture "$C29/freeze/fixture" --run "$RUN" --terminal "$RUN/terminal.json" \
  --reference "$RUN/analysis" --out "$RUN/reproduction"
```

Explicit abandonment uses `close --abandon`, records all outstanding IDs and closes
the run to resume. Missing primary rows yield identification bounds. The analysis
outputs link scored rows, target/role/order pairs, families, strata and summary
results to archive hashes. Formal manuscript figures and the publication release
require the lab's reproduction and release review.
