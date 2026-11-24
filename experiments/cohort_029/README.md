# Cohort 029 · CF-TP1

## Status

The policy audit records both the literal gate and the proposed clarification.
The literal rule rejects constant predictions because they can only err under one
gold action. The [policy clarification](policy-clarification.md) applies the
constant-output gate only to declared constants and mathematically constant
threshold boundaries. The lab PI signs the clarification before freeze.

The transfer wording used by the mock is a test fixture. Formal preparation
requires the independent author's wording. Freeze requires blinded review and gate
evidence. The PI separately authorizes a specific manifest, deployment, path and
response cap.

## Run a mock and view progress

Run from the repository root. A compatible local Python works for mock preparation.
Use a fresh output directory per mock.

```bash
C29=experiments/cohort_029
mkdir -p "$C29/mock"
.venv/bin/python -m tools.cohort029_prepare --mock --out "$C29/mock/fixture"
.venv/bin/python -m tools.analyze_target_transport mock-run \
  --candidate "$C29/mock/fixture" --out "$C29/mock/run"
.venv/bin/python -m tools.run_target_transport stream --out "$C29/mock/run" --once
.venv/bin/python -m tools.analyze_target_transport calibrate-intervals \
  --out "$C29/mock/coverage.json"
```

Mock preparation reports the original literal failures and saves both tie audits for inspection.
The mock runner exercises an interrupted intent and then replays 4,096 deterministic
responses through terminal scoring. The expected Delta is 0.78125 percentage points.

## Formal preflight and freeze

Use the same Python 3.13 patch for candidate generation, token preflight and
collection. See the [independent review handoff](lab-handoff.md) for wording and review instructions.
The transfer input is a JSON object with single-paragraph
`context` and `arithmetic` strings. The renderer supplies the common message,
numerical layout and response contract. The implementation uses Python's standard
library and the archived llama.cpp binaries and GGUF.

```bash
C29=experiments/cohort_029
python3.13 -m tools.cohort029_prepare --transfer "$C29/lab/transfer.json" \
  --out "$C29/candidate"
python3.13 -m tools.cohort029_runtime --candidate "$C29/candidate" \
  --out "$C29/preflight"
ssh-keygen -Y sign -n causalfade-cohort029 -f /path/to/pi-key \
  "$C29/policy-clarification.md"
python3.13 -m tools.freeze_target_transport --candidate "$C29/candidate" \
  --preflight "$C29/preflight" --evidence "$C29/lab/evidence" \
  --protocol /home/i242514/Downloads/cohorts_29.md --out "$C29/freeze" \
  --policy-approval "$C29/policy-clarification.md.sig" --trust "$C29/lab/allowed_signers"
```

The token audit only calls chat template
and tokenization endpoints. It records the rendered chat and token sequence hashes
and enforces the 2,048-token budget with 48 tokens reserved for completion.

Prepare `lab/evidence/gates.json` with keys `"1"` through `"7"`. Each record supplies
`owner`, `verifier`, `artifact` relative to the evidence directory, `sha256`,
`predicate`, `observed`, `timestamp` and the Boolean `pass`. Also supply
`mock_recovery.json`, `coverage.json`, `form_review.md` and `deviations.json`.
The review documents names, dates, commits, form authorship, exposure declarations,
the eight blinded quartets and the four worked cases. Retain failed candidate evidence
when resolving any deficiency. Authorization is gate eight.

After freeze, six reviewers sign the exact `manifest.json` bytes with
`ssh-keygen -Y sign -n causalfade-cohort029 -f /path/to/lab-key manifest.json`.
Store signatures as `pi.sig`, `causal-lead.sig`, `statistician.sig`,
`benchmark-engineer.sig`, `independent-reviewer.sig` and `transfer-author.sig` in
`lab/signatures/`. The lab supplies a trusted `allowed_signers` file mapping these
principals to their approved public keys. The PI separately signs
`lab/authorization.json` in the same namespace and places the detached signature
at `lab/authorization.json.sig`. The signed JSON contains `authorized: true`,
`authorized_responses: 4096`, `manifest_sha256`, `model_sha256`, `server_sha256`
and the relative `run_path` shown below.

The following command prepares the unsigned PI authorization payload directly from
the frozen files. The PI reviews the payload and signs it with the same namespace.

```bash
python3.13 - <<'PY_AUTH'
from pathlib import Path
from tools.cohort029_prepare import write
from tools.cohort029_runtime import load, sha

base = Path("experiments/cohort_029")
freeze = base / "freeze"
manifest = freeze / "manifest.json"
deployment = load(freeze / "deployment/inventory.json")
write(base / "lab/authorization.json", {
    "authorized": True,
    "authorized_responses": load(manifest)["response_cap"],
    "manifest_sha256": sha(manifest),
    "model_sha256": deployment["model_sha256"],
    "server_sha256": deployment["server_sha256"],
    "run_path": str(base / "runs/confirmatory"),
})
PY_AUTH
ssh-keygen -Y sign -n causalfade-cohort029 -f /path/to/pi-key "$C29/lab/authorization.json"
```


## Start and stream the authorized run

First verify the signed launch files in the foreground. This check does not
start the model server. It lists missing files and exits nonzero.

```bash
python3.13 -m tools.run_target_transport check-ready
```

Wait for a successful check before starting the background job.

```bash
C29=experiments/cohort_029
RUN="$C29/runs/confirmatory"
mkdir -p "$C29/runs"
nohup python3.13 -u -m tools.run_target_transport run \
  --freeze "$C29/freeze" --signatures "$C29/lab/signatures" \
  --authorization "$C29/lab/authorization.json" \
  --trust "$C29/lab/allowed_signers" --out "$RUN" \
  >>"$C29/runs/confirmatory.console.log" 2>&1 </dev/null &
```

```bash
.venv/bin/python -m tools.run_target_transport stream \
  --out experiments/cohort_029/runs/confirmatory

# Includes startup, server retry and Git checkpoint messages.
tail -n 30 -F experiments/cohort_029/runs/confirmatory.console.log
```

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
