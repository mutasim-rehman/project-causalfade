# Lab handoff: prepared sensitivity/bias pilot

**Later development work:** Cohort 018's F16 reference completed and failed its competence gate. Its commands and artifacts below remain the historical handoff. For the separate within-world response-contract experiment, use [cohort 019's frozen plan and reproduction commands](../experiments/cohort_019/README.md). Do not rerun cohort 018 or use a post hoc token reinterpretation as its official score.

**14 November 2026 session.** Most implementation and archived 14B analysis are already prepared. The lab agent should verify the environment, run the committed development fixture, inspect competence and analyze completed outputs. Read [cohort 018](../experiments/cohort_018/README.md) and the [study specification](INTERDISCIPLINARY_FOLLOWUP.md) first.

## 1. Sync and environment (approximately 30–60 minutes)

Inspect `git status` and preserve local work before updating from the branch/commit supplied in the handoff. Do not discard changes or force-pull. Commands below assume the checkout root. Use an existing compatible local environment or create one:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c 'import sys, numpy; print(sys.version); print(numpy.__version__)'
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/sensitivity_pilot.py validate --dataset experiments/cohort_018/input
```

The archived 14B paired report is now [complete](../experiments/cohort_017/summary.md). Its original automation failure is historical, not a requirement to rerun inference. Reproduce its analysis to a separate path only if necessary:

```bash
.venv/bin/python tools/analyze_14b_followup.py --q8 experiments/cohort_017/run_001_14b_q8_0 --q4 experiments/cohort_017/run_002_14b_q4_k_m --truth experiments/cohort_016/input/oracle_truth.jsonl --out /tmp/causalfade-14b-analysis-check.json
```

Verify the existing llama.cpp b12176 CPU server and the model files from cohort 016. No new model downloads or quantization are needed. The new runner records model/server hashes, CPU/KV settings, source hashes, decoding and schedule. Paths below match the historical lab layout; inspect and adjust only if the installation moved.

## 2. Run the development reference (budget approximately two hours)

```bash
.venv/bin/python tools/sensitivity_pilot.py run \
  --server .tools/llama-b12176/llama-server \
  --model "$HOME/Desktop/CAUSALFADE/weights/gguf/qwen2.5-7b-instruct-f16.gguf" \
  --dataset experiments/cohort_018/input \
  --out experiments/cohort_018/run_001_7b_f16 \
  --role reference --threads 8 --max-tokens 64 --max-seconds 7200
```

This starts a loopback-only CPU server and sends only each public prompt. There are 288 requests. Inspect `status.json` for progress; do not launch a duplicate writer against the same directory. The runner acquires an exclusive run lock and refuses concurrent execution. `gate_analysis.json` is authoritative only after successful completion. A failed competence gate is a valid development outcome, not a reason to remove tasks or loosen cutoffs.

The time budget pauses before starting another request when less than its timeout remains. Exit code 2 means paused/interrupted/failed: inspect status, not just the exit code. A budget pause can resume by repeating the identical command with `--resume`, optionally changing only `--max-seconds` to allocate another session budget. The schedule, weights, source hashes and inference settings must match. Do not update the code mid-run.

Attempts are append-only and fsynced. An infrastructure-failed attempt is preserved as a failure and never automatically replaced. After repairing such a failure, finish or archive the run and explicitly document a new attempt/run policy; do not silently obtain a replacement answer. A malformed or length-capped model response remains invalid. A normal-output competence failure cannot be fixed through retries.

## 3. Run the conditional Q4 comparison (budget approximately two hours)

Only proceed if the complete reference passes the stored gate. The command enforces this and verifies the same fixture/provenance:

```bash
.venv/bin/python tools/sensitivity_pilot.py run \
  --server .tools/llama-b12176/llama-server \
  --model "$HOME/Desktop/CAUSALFADE/weights/gguf/qwen2.5-7b-instruct-q4_k_m.gguf" \
  --dataset experiments/cohort_018/input \
  --out experiments/cohort_018/run_002_7b_q4_k_m \
  --role comparison --reference-run experiments/cohort_018/run_001_7b_f16 \
  --threads 8 --max-tokens 64 --max-seconds 7200
```

Both roles use the same complete shuffled task order and default decoding seed. A failed reference gate blocks Q4 before its output directory/server is created. CPU runtime can vary; reserve analysis time rather than expanding the family count. Do not start large confirmation during this session.

## 4. Analyze and interpret (approximately one to two hours)

After both runs complete:

```bash
.venv/bin/python tools/sensitivity_pilot.py analyze \
  --dataset experiments/cohort_018/input \
  --reference experiments/cohort_018/run_001_7b_f16 \
  --comparison experiments/cohort_018/run_002_7b_q4_k_m \
  --out experiments/cohort_018/development_analysis.json
```

If reference competence fails, omit `--comparison` and analyze the completed reference alone. The JSON includes numerical details and a sibling Markdown report is generated. Existing reports are not overwritten; choose a new path for an amended analysis. Analysis reconstructs semantic actions from raw responses, rather than trusting saved parsed predictions.

Inspect validity, balanced-direction accuracy, hits/false alarms, action propensity, strength/order strata, matched controls and administration breakdowns. Do not equate fixed-strategy agreement with identified mechanism. Eight families support development decisions, not precise general claims. SDT uses a disclosed boundary correction and unverified equal-variance assumptions. The controls share numbers but differ in instruction semantics.

## 5. Final session deliverable (remaining time)

Write a short cohort summary, update `EXPERIMENTS.md`, `DECISIONS.md` and `SESSION_REPORT.md`, and preserve raw/config/schedule/session records. State whether to retain or revise the task, which explanations remain plausible, runtime cost and one candidate primary contrast/endpoint for the later study. Preserve the fixed fixture and operational gate; revised tasks receive a new directory/version and remain development-only.

Power/coverage simulations, formal psychometric invariance, full rival-model fitting and independent model-family replication remain prospective. No new confirmatory endpoint is registered by this pilot. Commit results according to repository conventions; keep weights/binaries outside Git and back up irreplaceable records.
