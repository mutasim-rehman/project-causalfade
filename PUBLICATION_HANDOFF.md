# Project CausalFade — Cohort 029 publication handoff

## Immutable scientific release reference

- **Release tag:** `cohort-029-v1.0.0` (annotated; do not move it).
- **Tagged scientific commit:** `76206c259caa488668a7556ce1bc53cb35d220da`.
- **Public release:** https://github.com/mutasim-rehman/project-causalfade/releases/tag/cohort-029-v1.0.0
- **Repository:** https://github.com/mutasim-rehman/project-causalfade
- **Scope:** Original Cohort 029 freeze and journal, plus later offline analysis and verification. This handoff was added as a subsequent administrative commit; the tag fixes the scientific artifact set.

No new LLM inference was run for this release. The original 4,096 model responses
are retained byte for byte from the completed lab run.

## Integrity and exact locations

| Evidence | Tagged path | SHA-256 or status |
| --- | --- | --- |
| CF-TP1 v1.0 protocol | `experiments/cohort_029/freeze/protocol.md` | Original frozen copy |
| Scientific amendment | `experiments/cohort_029/freeze/policy-clarification.md` | Original frozen copy |
| Production manifest | `experiments/cohort_029/freeze/manifest.json` | `5252f69d30a0a5bb65a5efa669458e325c0531f25ab55f768531c7ca29f4c766` |
| Original journal | `experiments/cohort_029/runs/confirmatory/events.jsonl` | `673eb723637614dc8b94875f2e8c4e9e20234c1d179c992791853797875977bd` |
| Exact transfer submission | `experiments/cohort_029/lab/transfer.json` | `48bb313e7d02fcfe5f17b99739fb33f84c1803e6127e6add6488115f0e8123c5` |
| Final prompts and request hashes | `experiments/cohort_029/freeze/fixture/tasks.jsonl` | 4,096 messages; all reconstructed |
| Numerical families, oracle and schedule | `experiments/cohort_029/freeze/fixture/` | 128 families; 4,096 task IDs |
| Model, server, tokenizer preflight | `experiments/cohort_029/freeze/deployment/` | Original hashes and counts; binaries excluded |
| Completion, scoring, analysis | `experiments/cohort_029/runs/confirmatory/terminal.json`, `analysis/` | Created offline after collection |
| Deterministic replay | `experiments/cohort_029/runs/confirmatory/reproduction/` | Byte-identical six-file replay |
| Independent verification | `experiments/cohort_029/release/verification.json` | PASS, 50/50 checks |
| Validation timing | `experiments/cohort_029/release/validation_record.json` | Distinguishes frozen checks from post-run reruns |

The tagged repository contains all required computational inputs. `candidate/`,
`preflight/`, `mock/`, raw server logs, model weights and runtime binaries are
not needed to reproduce the published analysis. The original frozen
deployment files, rather than a later tokenizer preflight, are the authority
for the actual run. No original terminal or analysis outputs were present at
the start of release work; the published versions were computed from the
original journal after collection.

## Verified results

| Prespecified measure | Saved-response result |
| --- | ---: |
| Scheduled and strict-valid responses | 4,096/4,096 |
| Causal transfer target-pair fidelity | 128/512 (25.00%) |
| Arithmetic transfer target-pair fidelity | 146/512 (28.515625%) |
| Family-standardized difference, causal minus arithmetic | −3.515625 percentage points |
| Approximate 95% t interval | −7.7713 to +0.7400 points |
| Conservative bounded interval | −27.5237 to +20.4924 points |
| Causal transfer activation | 995/1,024 |
| Correct causal target reversals | 3/256 |
| Arithmetic action changes, target reversals | 46/256 |
| Arithmetic action changes, target invariance | 45/256 |

The full source-role, target-switch, display-order, action-direction,
invalidity and secondary cell counts are in
[RESULTS.md](experiments/cohort_029/release/RESULTS.md) and
[`secondary.json`](experiments/cohort_029/runs/confirmatory/analysis/secondary.json).
The [pair](experiments/cohort_029/runs/confirmatory/analysis/pair_scores.jsonl),
[family](experiments/cohort_029/runs/confirmatory/analysis/family_scores.jsonl),
and [row](experiments/cohort_029/runs/confirmatory/analysis/row_scores.jsonl)
records support independent tables. Exact figure data and the two SVG plots
are in [figures](experiments/cohort_029/release/figures/).

## Offline reproduction commands

Use Python **3.13.18**. From a new clone, no 7B model, inference server,
credentials or GPU is required:

```bash
git clone https://github.com/mutasim-rehman/project-causalfade.git
cd project-causalfade
git checkout cohort-029-v1.0.0
C29=experiments/cohort_029
RUN="$C29/runs/confirmatory"

(cd "$C29/freeze" && sha256sum -c <(sed 's/$/  manifest.json/' manifest.sha256))
python3.13 -m tools.verify_cohort029_release --out /tmp/cohort029-verification.json
python3.13 -m unittest discover -s tests -p 'test_target_transport*.py' -v

TMP=$(mktemp -d)
python3.13 -m tools.cohort029_prepare \
  --transfer "$C29/lab/transfer.json" --out "$TMP/fixture"
diff -qr "$TMP/fixture" "$C29/freeze/fixture"
python3.13 -m tools.analyze_target_transport reproduce \
  --fixture "$C29/freeze/fixture" --run "$RUN" \
  --terminal "$RUN/terminal.json" --reference "$RUN/analysis" \
  --out "$TMP/reproduction"
cat "$TMP/reproduction/reproduction_report.json"
python3.13 -m tools.plot_cohort029_release
```

The exact procedure and interpretation limits are in the
[reproduction guide](experiments/cohort_029/release/REPRODUCE.md). Never use
`tools.run_target_transport run` or `resume` for this offline task.

## Provenance, deviations and scope

The pre-inference freeze rebuilt the formal fixture, verified the oracle and
prompt structure, exercised mock recovery, ran tokenizer preflight and
prespecified interval calibration. It preserved 12 **literal** shortcut
policy failures and the `constant-rivals-v1` clarification; the clarified
policy gate passed. The 12 unit tests, fresh fixture rebuild, calibration
replay, release verifier and clean-checkout analysis replay were run **after**
collection. Their timing is recorded in the validation record.

The selected transfer text matches a dated lab submission. A human authorship
declaration and blinded review records were recovered and published under the
existing `lab/` paths. The authorship signature validates bytes but did not
match the available trusted signer list. The review attestation validates with
the available `Raza` key and hash-binds the production packet, but the
reviewer identity is abbreviated and the freeze itself recorded independent
authorship and review as **undocumented**. Do not describe either as a
certified pre-inference independent gate. See the full
[provenance note](experiments/cohort_029/release/PROVENANCE_AND_LIMITATIONS.md).

The approximate interval crosses zero. This is a deployment-specific
intervention-decision and evaluation-reliability result. It does not establish
equivalence, selective quantization damage, or a neural causal mechanism.
Cohort 028's development runs completed and stopped at its frozen gate; no
later arms ran. The project should preserve negative and inconclusive findings.

## Reproduction status and remaining publication work

- **PASS — offline computational reproduction:** a clean checkout of the
  tagged commit reconstructed all 4,096 prompts and request hashes, checked
  journal order and raw response hashes, reproduced the exact oracle and
  strict scores, and regenerated the original-code analysis byte for byte.
- **FAIL — external independent reproduction completion criterion:** no separate
  reviewer or laptop has yet executed the tagged commands. This is a remaining
  action, not a failure of the available computational checks.

The manuscript agent should use the protocol and amendment, manifest,
`release/verification.json`, `release/validation_record.json`,
`release/RESULTS.md`, `analysis/primary.json`, `analysis/secondary.json`,
pair/family/row scores, figure data, and the provenance note. An external
researcher should run the commands above and archive their output. A DOI
archive has not been minted. The transfer author's downstream reuse license
is not documented; [LICENSES.md](LICENSES.md) explains the scoped software
and numerical-data licenses and exclusions. Resolve that permission before
relicensing the transfer prose in a manuscript or derivative benchmark.
