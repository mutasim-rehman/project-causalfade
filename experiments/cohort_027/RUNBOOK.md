# Cohort 027 execution runbook

This runbook starts the prepared scientific workflow. Preparation and tests have not issued model generation requests. The frozen fixture has eight development and sixteen validation families. The 14B F16 source is present but excluded before outcomes because its 29.55 GB file cannot leave the required 4 GB host headroom plus runtime buffers on this 32 GB RAM machine. Four F16 references remain: Qwen 3B, Qwen 7B, Mistral 7B and Llama 8B. The protocol's cross-family condition remains feasible.

## Preflight and launch

From `/home/i242514/Desktop/project-causalfade`:

```bash
PYTHONPATH=. .venv/bin/python tools/cohort027_prepare.py verify
PYTHONPATH=. .venv/bin/python tools/cohort027_tokencheck.py
set -o pipefail
PYTHONUNBUFFERED=1 PYTHONPATH=. .venv/bin/python tools/cohort027_run.py run-all 2>&1 | tee -a experiments/cohort_027/live.log
```

The tokenizer preflight loads each eligible tokenizer and checks the longest rendered prompt in each form/task class against the 4096 context and 64-token output cap. It generates no model answers. `run-all` also performs this preflight if it has not been done separately. It runs eligible F16 development arms sequentially in the frozen randomized model order. Only F16 references passing both forms receive validation. Only references passing validation receive six same-source quantized development arms. If none qualifies, the workflow stops at the corresponding gate. No confirmation collection is part of this cohort.

To keep the run alive after closing the terminal, launch it with `nohup` and use the stream command in another terminal:

```bash
nohup bash -lc 'cd /home/i242514/Desktop/project-causalfade; set -o pipefail; PYTHONUNBUFFERED=1 PYTHONPATH=. .venv/bin/python tools/cohort027_run.py run-all 2>&1 | tee -a experiments/cohort_027/live.log' >/dev/null 2>&1 & echo $!
tail -n +1 -F /home/i242514/Desktop/project-causalfade/experiments/cohort_027/live.log
```

A read-only snapshot is available with:

```bash
PYTHONPATH=. .venv/bin/python tools/cohort027_status.py
```

Run the same `run-all` command to resume after interruption. The runner checks the frozen manifest, source files, model hash and saved arm configuration. It resumes from durable task IDs, recovers a response written to the attempts log just before a crash, and preserves any torn final JSONL bytes before truncating to the last complete record. It never retries a completed noncompliant or wrong answer. Transport failures receive at most two retries; unresolved failures remain scheduled failures. Server startup has three bounded attempts. A failed server or Git operation leaves existing task records intact.

Each scientific task writes its full response and timing to `attempts.jsonl`, then one result row to `results.jsonl`, with `fsync` before proceeding. Progress and event files update as tasks finish. Every 14 completed tasks, the arm is committed and pushed. A push failure is logged and does not erase the local commit; run `git push` after network access returns. The pipeline status is also committed. No concurrent model servers are used, so the optional throughput benchmark is unnecessary. Quantized models are built only for validated F16 references, from the pinned F16 source and quantizer, with per-format provenance.

After a successful stage C, compile the descriptive paired report:

```bash
PYTHONPATH=. .venv/bin/python tools/cohort027_report.py
```

This report is exploratory. The development families have already selected qualifying references; no confirmatory precision inference or independent transfer claim follows from this workflow.
