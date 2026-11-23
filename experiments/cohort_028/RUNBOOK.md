# Cohort 028 execution runbook

Status (23 November 2026): tokenizer preflight complete; development `llama8b` paused at 1030/1280 saved responses. No cohort 028 process is running. Two pinned F16 checkpoints, Llama-3.1-8B then Qwen2.5-7B, run sequentially. Both 16-family development blocks finish before any validation decision. A model reaches the fresh 32-family validation block only if its assisted system passes all required gates on both forms. The calculator is deterministic replay of the structured response, not a new model request.

## Launch

From `/home/i242514/Desktop/project-causalfade`:

```bash
PYTHONPATH=. .venv/bin/python tools/cohort028_prepare.py verify
PYTHONPATH=tools:. .venv/bin/python -c 'from cohort028_run_hourly import verify_amendment; verify_amendment(); print("hourly checkpoint amendment verified")'
set -o pipefail
PYTHONUNBUFFERED=1 PYTHONPATH=. .venv/bin/python tools/cohort028_run_hourly.py run-all 2>&1 | tee -a experiments/cohort_028/live.log
```

The tokenizer preflight has already passed. It loads each pinned tokenizer, checks maximum rendered prompts for each form/condition/representation, and generates no answer. `run-all` performs it automatically if absent. The full schedule has 2,560 development model requests (A and B), of which 1,030 are saved, and at most 5,120 conditional validation requests. C is replayed locally without model inference.

To leave it running after terminal closure:

```bash
nohup bash -lc 'cd /home/i242514/Desktop/project-causalfade; set -o pipefail; PYTHONUNBUFFERED=1 PYTHONPATH=. .venv/bin/python tools/cohort028_run_hourly.py run-all 2>&1 | tee -a experiments/cohort_028/live.log' >/dev/null 2>&1 & echo $!
```

To stream the complete task-by-task output in another terminal:

```bash
tail -n +1 -F /home/i242514/Desktop/project-causalfade/experiments/cohort_028/live.log
```

To inspect a compact snapshot:

```bash
cd /home/i242514/Desktop/project-causalfade
PYTHONPATH=. .venv/bin/python tools/cohort028_status.py
```

Repeating `run-all` through `cohort028_run_hourly.py` resumes interrupted work. The original frozen runner still invokes its local progress checkpoint every 20 completed requests, but the amendment commits and pushes only when an hour has elapsed since the previous Git checkpoint or after a model arm finishes and its analysis is saved. A final terminal pipeline-status commit may follow the last model arm. Startup and interruption status are saved locally without an immediate Git commit. The hour clock begins when the resumed process starts; it does not count time while the cohort is paused. See [the dated amendment](amendments/hourly_checkpoint_2026-11-23.json) and [deviation log](DEVIATIONS.md). Use this launcher for future resumes; direct use of the pinned `cohort028_run.py` retains the old 20-response Git cadence.

Every completed response is appended with `fsync` to `attempts.jsonl` and one `results.jsonl` row. A response persisted just before a crash is recovered from the attempt log instead of queried again. An incomplete final JSONL write is archived and truncated to the previous complete newline. A wrong or noncompliant completed response is never retried. Transport errors receive at most two retries; unresolved errors remain scheduled failures. Server startup receives at most three bounded attempts. A push failure leaves the local commit intact; run `git push` after connectivity returns.

The runner checks frozen file, source, model and server hashes and saved configuration on resume. Calculator input contains only the public numeric payload and the model-selected allowlisted rule. Neither hidden truth nor graph metadata enters the replay. Structured schema invalidity makes C a scheduled failure. Validation does not run for a development-failed model. No quantized arm or confirmatory inference is in this cohort.
