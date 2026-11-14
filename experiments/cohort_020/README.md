# Cohort 020: staged component diagnostic (development only)

**Pre-generation design, 14 November 2026.** Use eight fresh SCM families and seed 20261116. Within each family, cross two causal directions and two effect magnitudes (0.04, 0.12), giving four base stems. Each stem has one randomized-only intervention decision, one aligned two-source decision in each physical block order, and one conflicting two-source decision in each order: 4 × 5 = 20 decision prompts/family, or 160 total. The same four stems each have one single-pair number comparison on their randomized rates: 32 total. Each family also has four direct source-identification checks crossing randomized study name A/B and actual block order first/second: 32 total. **Total: 224 prompts.**

Each decision stem keeps its randomized rates and correct semantic action fixed across randomized-only, aligned and conflict variants. Historical differences have matched absolute magnitude 0.36 and opposite signs in aligned/conflict. Neutral names A/B are balanced across the four stems within family. The two-source task shows genuinely numbered blocks with method and rates in physical order. The source check uses the same block presentation but asks directly for the randomized study identifier; it does not use an action response. All prompts are sent in fresh contexts in a seeded shuffled schedule.

Responses are strict one-key JSON: number comparisons use `{"larger":"X=0"}` or `{"larger":"X=1"}`; intervention decisions use `{"decision":"activate"}` or `{"decision":"leave_off"}`; source identification uses `{"randomized_study":"A"}` or `{"randomized_study":"B"}`. Additional text/fields, duplicate keys, malformed or length-capped outputs are invalid scheduled-task failures. Evaluator fields are never sent.

Planned analysis: scheduled accuracy/validity by task type, direction, strength and source order; family-paired random-only minus number comparison (diagnostic task-demand contrast), aligned/conflict additions against the same randomized-only stem, and physical order reversal within identical two-source evidence. Report action flips, activation rates, source identification by name/order, and eight-family percentile intervals. Comparisons do not uniquely identify an internal processing stage. No Q4 or confirmatory collection is authorized for this cohort.

## Execution and reproduction

The existing verified llama.cpp b12176 server and Qwen2.5-7B F16 checkpoint are used on CPU only: eight threads, zero GPU layers, 2048-token context, F16 KV, temperature zero, seed 20261116, fresh contexts, 64 output tokens and 180-second request timeout. The 7200-second session budget can be renewed only by an identical `--resume` command after a budget pause. The runner records append-only, fsynced attempts, a complete schedule, source/model/server hashes and an exclusive lock. Failed infrastructure attempts are not silently replaced. No Q4 arm is permitted by this runner. Exact hashes and contrasts are in `frozen_run_plan.json`.

```bash
.venv/bin/python tools/component_pilot.py validate --dataset experiments/cohort_020/input
.venv/bin/python tools/component_pilot.py run --server .tools/llama-b12176/llama-server --model "$HOME/Desktop/CAUSALFADE/weights/gguf/qwen2.5-7b-instruct-f16.gguf" --dataset experiments/cohort_020/input --out experiments/cohort_020/run_001_7b_f16 --role reference --threads 8 --max-tokens 64 --seed 20261116 --max-seconds 7200
.venv/bin/python tools/component_pilot.py analyze --dataset experiments/cohort_020/input --reference experiments/cohort_020/run_001_7b_f16 --out experiments/cohort_020/development_analysis.json
```
