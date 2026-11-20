# Cohort 028 execution runbook

Status: code and frozen fixture prepared; no cohort 028 generation requested. Two pinned F16 checkpoints, Qwen2.5-7B and Llama-3.1-8B, run sequentially. The 16-family development block is complete for both models before any validation decision. A model reaches the fresh 32-family validation block only if its assisted system passes all required gates on both forms. The calculator is deterministic replay of the structured response, not a new model request.

## Launch

From `/home/i242514/Desktop/project-causalfade`:

```bash
PYTHONPATH=. .venv/bin/python tools/cohort028_prepare.py verify
PYTHONPATH=. .venv/bin/python tools/cohort028_tokencheck.py
set -o pipefail
PYTHONUNBUFFERED=1 PYTHONPATH=. .venv/bin/python tools/cohort028_run.py run-all 2>&1 | tee -a experiments/cohort_028/live.log
```

The tokenizer preflight loads each pinned tokenizer, checks maximum rendered prompts for each form/condition/representation, and generates no answer. `run-all` performs that preflight automatically if absent. It performs 2,560 development model requests (A and B) and at most 5,120 conditional validation requests. C is replayed locally without model inference.

To leave it running after terminal closure:

```bash
nohup bash -lc 'cd /home/i242514/Desktop/project-causalfade; set -o pipefail; PYTHONUNBUFFERED=1 PYTHONPATH=. .venv/bin/python tools/cohort028_run.py run-all 2>&1 | tee -a experiments/cohort_028/live.log' >/dev/null 2>&1 & echo $!
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

Repeating `run-all` resumes interrupted work. Every completed response is appended with `fsync` to `attempts.jsonl` and one `results.jsonl` row. A response persisted just before a crash is recovered from the attempt log instead of queried again. An incomplete final JSONL write is archived and truncated to the previous complete newline. A wrong or noncompliant completed response is never retried. Transport errors receive at most two retries; unresolved errors remain scheduled failures. Server startup receives at most three bounded attempts. Each arm commits and pushes a checkpoint every 20 completed requests, including config, raw attempts, results, progress and events. A push failure leaves the local commit intact; run `git push` after connectivity returns.

The runner checks frozen file, source, model and server hashes and saved configuration on resume. Calculator input contains only the public numeric payload and the model-selected allowlisted rule. Neither hidden truth nor graph metadata enters the replay. Structured schema invalidity makes C a scheduled failure. Validation does not run for a development-failed model. No quantized arm or confirmatory inference is in this cohort.
