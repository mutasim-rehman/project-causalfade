# Cohort 024 lab runbook (Ubuntu)

## Unattended handoff

After the preparation-only checkpoint is committed, one command can resume pinned F16 downloads, verify publisher LFS SHA-256 hashes and Meta Instruct authorization, build/reuse all six quantizations per lineage, write ignored local inventories, freeze and push the 21-arm plan, then run all 30,912 requests. It resumes clean two-hour arm budget pauses and commits/pushes audited completed arms. A failed push or failed task stops visibly. The command does not run repository tests. Keep the terminal or a persistent `tmux` session alive:

```bash
cd "$HOME/Desktop/project-causalfade"
.venv/bin/python -u tools/cohort024_unattended.py start 2>&1 | tee -a experiments/cohort_024/bootstrap.log
```

In another terminal, stream aggregate progress:

```bash
cd "$HOME/Desktop/project-causalfade"
.venv/bin/python -u tools/cohort024_unattended.py progress --interval 20
```

The launcher reads `HF_TOKEN` from the environment or the ignored `.env` file; the token is never printed or passed on a command line. It checks authorized access to the pinned official Meta Instruct source before using the pinned Llama F16 GGUF derivative. F16 GGUF files are downloaded from pinned `second-state` revisions with publisher LFS hashes; the publisher's original conversion command is not independently verified. The existing Qwen F16 must match its archived SHA-256. No 12–14B arm is included. The three model lineages are distinct from the fixture's eight SCM world families. A roughly **26–45 hour** inference window is plausible on this CPU, excluding downloads and quantization; the 7200-second per-session budget means some F16 arms will pause and resume automatically. This is a development measurement screen, not a confirmatory quantization result.

The code and fixture are committed before inference. Start from a clean checkout. Keep model GGUF files and quantized outputs **outside Git**. No Codex agent is required. Commands stop on missing files, changed hashes, failed attempts or changed settings. They do not silently retry a failed request.

## 1. Pull and verify

```bash
cd "$HOME/Desktop/project-causalfade"
git pull --ff-only origin main
source .venv/bin/activate
python -m unittest discover -s tests -q
python tools/cohort024.py validate --dataset experiments/cohort_024/input
git status --short
```

Keep the pre-existing untracked publication assessment separate from model/run artifacts if present.

## 2. Prepare three F16 source files

Acquire or convert **F16 GGUF** files for Qwen2.5-7B-Instruct, Mistral-7B-Instruct-v0.3 and Llama-3.1-8B-Instruct. Verify each model's license and pinned source revision. Llama access may require accepting Meta's terms. Use the same pinned source revision for every quantized variant of a lineage. The existing Qwen F16 file may be reused if its SHA-256 matches prior cohorts. Do not substitute the cohort 022 Mistral Q4 file as an F16 source.

Copy `experiments/cohort_024/sources.example.json` to `experiments/cohort_024/sources.local.json`, replace all three **absolute** paths and revision strings, and add the exact SHA-256, source repository, revision, license and conversion provenance for each F16 file. These fields are required. The example paths are placeholders and will fail closed. Keep `sources.local.json` untracked.

## 3. Build model formats and freeze the lab plan

```bash
python tools/cohort024.py build-models \
  --sources experiments/cohort_024/sources.local.json \
  --quantizer .tools/llama-b12176/llama-quantize \
  --out "$HOME/Desktop/CAUSALFADE/weights/cohort_024_quantized" \
  --models-out experiments/cohort_024/models.local.json

python tools/cohort024.py freeze \
  --dataset experiments/cohort_024/input \
  --models experiments/cohort_024/models.local.json \
  --server .tools/llama-b12176/llama-server \
  --plan experiments/cohort_024/frozen_lab_plan.json \
  --threads 8

git add experiments/cohort_024/frozen_lab_plan.json
git commit -m "protocol: freeze cohort 024 lab model matrix"
git push origin main
```

The model builder writes a provenance sidecar and SHA-256 for every quant. On interruption, rerun the same command: verified completed files are reused. If a partial target lacks valid provenance, stop and inspect it; do not overwrite it without recording the failed conversion. The `freeze` command checks all model files, source revisions, fixture/source hashes and server hash. It does not overwrite an existing plan. For a smaller *predeclared* matrix, specify `--levels Q8_0,Q4_K_M` at build time and freeze that set; do not drop arms after observing outcomes.

## 4. Run all arms with live output

```bash
set -o pipefail
python -u tools/cohort024.py run-all \
  --plan experiments/cohort_024/frozen_lab_plan.json \
  --out experiments/cohort_024/runs \
  --max-seconds 7200 --progress-every 20 \
  2>&1 | tee -a experiments/cohort_024/live.log
```

The CLI prints `LIVE model_id completed/1472` every 20 requests and `END model_id status` after each arm. F16 arms run first. In another terminal, inspect progress:

Each arm archives the server's `/props` response before sending task prompts. Inspect `server_props.json` and `stderr.log` if a chat-template or model-load problem is suspected.

```bash
python tools/cohort024.py status --plan experiments/cohort_024/frozen_lab_plan.json --runs experiments/cohort_024/runs
tail -f experiments/cohort_024/live.log
```

Exit 0 means all listed arms completed. Exit 2 means the current arm paused, was interrupted or failed. Check `status.json`, `stderr.log`, the last raw attempt and the lock before any restart. A budget pause or clean interruption can resume with **the identical** `run-all` command; completed arms are audited and skipped. An infrastructure-failed attempt is retained and requires a separately documented amendment/new run, not an implicit retry. Do not delete a `.lock` until verifying its process is gone. Do not edit code, models, plan or settings mid-matrix.

At a natural completed-arm checkpoint, archive/push outputs if feasible:

```bash
python tools/cohort024.py checkpoint --plan experiments/cohort_024/frozen_lab_plan.json --runs experiments/cohort_024/runs
```

Avoid staging GGUF weights or `sources.local.json`/`models.local.json`. The checkpoint command stages only audited completed-arm directories and exits visibly on push failure. It rejects unrelated staged files. It never stages live.log, GGUF weights, credentials, local manifests or unrelated untracked files. The raw logs may be large; ensure Git storage is available before starting.

## 5. Analyze and push closure

```bash
python tools/cohort024.py analyze \
  --plan experiments/cohort_024/frozen_lab_plan.json \
  --runs experiments/cohort_024/runs \
  --out experiments/cohort_024/development_analysis.json
git add experiments/cohort_024/runs experiments/cohort_024/live.log experiments/cohort_024/development_analysis.json
git commit -m "results: close cohort 024 development matrix"
git push origin main
```

Only after the raw and control results are reviewed should a separate untouched-family confirmation and power plan be frozen. The analysis file is deliberately development-only.
