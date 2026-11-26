# Cohort 029 offline reproduction

This release contains the **original production freeze** from the lab PC and
the complete saved response journal. It is the CF-TP1 v1.0 experiment, not a
mock or a later prompt reconstruction. The journal was already published at
Git commit `d90909798e7f1f2fbab9abbf34f4c2b27be526de`; this release adds
the freeze and deterministic analyses. No model call is needed for any command
below. Do not run `tools.run_target_transport run` or `resume` for reproduction.

## Inputs and provenance

| Artifact | Path | Role |
| --- | --- | --- |
| Protocol | `freeze/protocol.md` | Original CF-TP1 v1.0 protocol |
| Amendment | `freeze/policy-clarification.md` | Constant-rival clarification |
| Manifest and checksum | `freeze/manifest.json`, `freeze/manifest.sha256` | Original frozen file inventory |
| Exact two-form wording | `freeze/fixture/forms.json` | Archive-compatible and final transfer form |
| Original transfer submission | `lab/transfer.json` | Exact submitted JSON bytes |
| Authorship and review evidence | `lab/evidence/transfer-authorship.md`, `lab/review/umar-48bb313e/` | Original declarations, answers and signed attestation; qualification in provenance note |
| Final serialized prompts | `freeze/fixture/tasks.jsonl` | 4,096 system/user message pairs and request hashes |
| Families and private worlds | `freeze/fixture/worlds.jsonl` | 128 numerical families and both SCM worlds |
| Gold and public oracles | `freeze/fixture/gold.jsonl`, `freeze/fixture/public_oracle.jsonl` | Strict answer key and public-text check |
| Schedule and design | `freeze/fixture/schedule.json`, `freeze/fixture/design.jsonl` | Exact task IDs, factors and dispatch order |
| Deployment | `freeze/deployment/` | Pinned model/server digests and tokenizer preflight |
| Original journal | `runs/confirmatory/events.jsonl` | All 4,096 saved response envelopes |
| Completion record | `runs/confirmatory/terminal.json` | Generated offline from the original journal |
| Original-code analysis | `runs/confirmatory/analysis/` | Strict row, pair, family, primary and secondary outputs |
| Replay | `runs/confirmatory/reproduction/` | Byte-identical deterministic analysis replay |
| Independent checks | `release/verification.json` | Prompt, oracle, journal and score verification |
| Validation timing | `release/validation_record.json` | Frozen pre-inference evidence versus post-collection reruns |
| Figures | `release/figures/` | SVG figures and exact JSON figure data |
| Readable results | `release/RESULTS.md` | Primary and prespecified secondary counts |

`candidate/`, `preflight/`, and `mock/` on the original PC
contain development or supporting records. They are not substitutes for the
production freeze. The `release/` directory contains later verification and
presentation files; its contents are not claimed to be pre-inference records.

## Environment

Use Python **3.13.18**, the patch recorded in the frozen forms and inventory.
The offline Cohort 029 tools use only the Python standard library. A 7B model,
llama.cpp, GPU, network connection, and model weights are not required. The
repository's general `requirements.txt` belongs to other project utilities.

Clone the exact release and run from the repository root:

```bash
git clone https://github.com/mutasim-rehman/project-causalfade.git
cd project-causalfade
git checkout cohort-029-v1.0.0
C29=experiments/cohort_029
RUN="$C29/runs/confirmatory"
```

The manifest sidecar contains only the hash, so check it from its directory:

```bash
(cd "$C29/freeze" && sha256sum -c <(sed 's/$/  manifest.json/' manifest.sha256))
sha256sum "$RUN/events.jsonl"
python3.13 -m tools.verify_cohort029_release --out /tmp/cohort029-verification.json
python3.13 -m unittest discover -s tests -p 'test_target_transport*.py' -v
```

The verifier checks every frozen file against the original manifest, rebuilds
all 4,096 rendered messages from the frozen worlds and forms, recomputes all
request hashes, joins every journal event to its task and schedule position,
checks raw response hashes, independently recalculates the exact action oracle,
and compares strict row, pair and secondary-cell scores. `passed: true` in the
generated JSON is the computational reproduction criterion. The checked-in
`release/verification.json` is the lab-side report, not an input trusted by the
verifier.

To rebuild all generated fixture files without model inference:

```bash
TMP=$(mktemp -d)
python3.13 -m tools.cohort029_prepare \
  --transfer "$C29/lab/transfer.json" --out "$TMP/fixture"
diff -qr "$TMP/fixture" "$C29/freeze/fixture"
```

An empty `diff` is byte-for-byte agreement. This was rerun after collection;
the original freeze had already performed the same deterministic comparison
before publication of its manifest. The freeze also contains the original
tokenizer counts; reproducing those counts would require the pinned 7B model
and server and is outside model-free reproduction.

To regenerate the strict analysis in a **new output directory**, without
touching the raw journal or committed analysis:

```bash
python3.13 -m tools.analyze_target_transport reproduce \
  --fixture "$C29/freeze/fixture" --run "$RUN" \
  --terminal "$RUN/terminal.json" --reference "$RUN/analysis" \
  --out "$TMP/reproduction"
cat "$TMP/reproduction/reproduction_report.json"
```

`"passed":true` means the six original-code output files matched the archived
analysis byte for byte. The separate release verifier checks the numerical
oracle and row/pair/cell scores through another implementation. To regenerate
the two SVG figures and `figure_data.json`, run
`python3.13 -m tools.plot_cohort029_release` in a writable checkout. It reads
the saved primary analysis only and makes no model calls.

## Exact primary result

The transfer form's causal target-pair fidelity was **128/512 (25.00%)** and
the arithmetic control was **146/512 (28.515625%)**. The family-standardized
causal-minus-arithmetic difference was **−3.515625 percentage points**.
The approximate 95% t interval was **[−7.7713, +0.7400] points**; the
conservative bounded interval was **[−27.5237, +20.4924] points**. The
approximate interval crosses zero and does not establish equivalence. The
family-level standard error was 2.1323975 points and Welch degrees of freedom
were 67.5285. The frozen coverage calibration designated the approximate t
interval as primary for coverage reporting; the bounded interval remains
separately reported.

See [RESULTS.md](RESULTS.md), [secondary.json](../runs/confirmatory/analysis/secondary.json),
[pair_scores.jsonl](../runs/confirmatory/analysis/pair_scores.jsonl), and
[row_scores.jsonl](../runs/confirmatory/analysis/row_scores.jsonl) for every
prespecified secondary cell. All 4,096 saved responses were strict-valid.
The causal transfer condition activated in 995/1,024 responses. On target
reversal pairs, the causal form changed action in 8/256 pairs and got both
answers correct in 3/256; the arithmetic form changed action in 46/256.
On target-invariant pairs, the arithmetic form changed action in 45/256.

## Interpretation and limits

This is a deployment-specific observation about intervention-decision
behavior and evaluation reliability. It does not establish a selective
quantization effect, internal causal-reasoning mechanism, or equivalence of
causal and arithmetic performance. The release preserves the negative and
inconclusive outcomes. See [PROVENANCE_AND_LIMITATIONS.md](PROVENANCE_AND_LIMITATIONS.md) for authorship,
review, license, and validation timing.
