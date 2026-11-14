# Cohort 019: within-world response-contract development pilot

Development-only, prepared 14 November 2026. Eight fresh families from seed 20261115. The fixture has 256 decision stems, each crossed with semantic, neutral-forward and neutral-reverse response contracts. Each contract has 128 causal and 128 matched noncausal decisions. There are two requested-action checks per contract per family (48 total) and two semantic source checks per family (16 total), for 832 requests per arm. All contract twins share evidence, source names, rates, task wording and oracle action; only their response instruction changes. The source names are balanced between families. The schedule is a seeded complete shuffle with no adjacent decision twins, and every request uses a fresh context.

Only public prompts reach the model. `causalfade/contracts.py` validates the SCM effects, positivity, matched observational difference, display rounding, complete crossing and public/oracle separation. Semantic action is decoded before scoring. Invalid outputs count as scheduled-task failures. The semantic subset has 288 tasks: 128 causal, 128 controls, 16 encoding checks and 16 source checks.

The fixed operational reference gate requires success on all 832 scheduled requests, at least 260/288 strict-valid semantic responses, 80/128 correct semantic causal decisions, 18/32 correct semantic conflict decisions in **each** evidence order, and 28/32 correct semantic comprehension checks. These are development cutoffs, not powered statistical competence tests. Neutral-contract performance is an outcome, not a gate criterion. Q4_K_M is permitted only if the complete F16 reference passes. Preserve failed attempts and do not alter thresholds after seeing answers.

The F16 and conditional Q4 use the existing verified llama.cpp b12176 CPU server and cohort 016 model hashes. Settings: eight threads, no GPU layers, F16 KV, 2048-token context, temperature zero, seed 20261115, fresh context, 64 output tokens and 180-second request timeout. The reference run budget is 7200 seconds; pause/resume may use another budget with all inference settings unchanged. Run artifacts preserve raw attempts, schedule, configuration, source/weight/server hashes, logs and gate result. See `frozen_run_plan.json` for exact provenance.

```bash
.venv/bin/python tools/contract_pilot.py validate --dataset experiments/cohort_019/input
.venv/bin/python tools/contract_pilot.py run --server .tools/llama-b12176/llama-server --model "$HOME/Desktop/CAUSALFADE/weights/gguf/qwen2.5-7b-instruct-f16.gguf" --dataset experiments/cohort_019/input --out experiments/cohort_019/run_001_7b_f16 --role reference --threads 8 --max-tokens 64 --seed 20261115 --max-seconds 7200
# Add --resume only to resume a paused run under the identical settings.
# If and only if the semantic reference gate passes:
.venv/bin/python tools/contract_pilot.py run --server .tools/llama-b12176/llama-server --model "$HOME/Desktop/CAUSALFADE/weights/gguf/qwen2.5-7b-instruct-q4_k_m.gguf" --dataset experiments/cohort_019/input --out experiments/cohort_019/run_002_7b_q4_k_m --role comparison --reference-run experiments/cohort_019/run_001_7b_f16 --threads 8 --max-tokens 64 --seed 20261115 --max-seconds 7200
.venv/bin/python tools/contract_pilot.py analyze --dataset experiments/cohort_019/input --reference experiments/cohort_019/run_001_7b_f16 --out experiments/cohort_019/development_analysis.json
# Supply --comparison experiments/cohort_019/run_002_7b_q4_k_m only if that arm completed.
```

Analysis reports contract/task accuracy and validity, family-paired contract contrasts, neutral mapping differences on identical stems, both directions of action flips, source-order effects by contract, encoding and source checks, and contract-specific causal SDT with denominators. Invalid responses remain failures for accuracy and are excluded only from conditional-valid SDT rates. Family percentile intervals resample eight families; they are descriptive and coarse. Equal-variance SDT assumptions remain unverified. Semantic-versus-neutral contracts change several response properties. No internal mechanism or confirmatory precision claim follows from this fixture.

Cohort 018's official failed reference result and artifacts remain unchanged. Conventional reinterpretation of its emitted tokens is only post hoc and is not used here as a replacement score.
