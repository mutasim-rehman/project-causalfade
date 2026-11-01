# Task, response and scoring contract

## Public task

One UTF-8 JSON object per JSONL line:

```json
{
  "task_id": "opaque deterministic identifier",
  "family_id": "world-0000",
  "evidence_mode": "exact",
  "prompt": "Complete self-contained task text"
}
```

`evidence_mode` is `exact` or `sampled`. `family_id` is a blocking key for the evaluator. Send only `prompt` into a fresh model context. Public task IDs should be used to join responses, not as an additional semantic input. A family has four cells per evidence layer. Keep all family variants on the same side of any split.

Exact evidence contains conditional success probabilities and joint population probabilities for Z,X. Sample evidence contains `z`, `x`, `n`, `successes` for each stratum. Population weights for Z and the known causal graph are stated in the prompt. Sample summaries represent an observational dataset, not randomized treatment assignment.

## Oracle truth

`oracle_truth.jsonl` adds `causal_positive`, `association_positive`, `effect_size`, `severity_gap`, `assignment_strength`, `ate`, `observational_difference`, `do_success_x0`, `do_success_x1`, `optimal_action` and `conflict`. These fields are evaluator-only. Their presence in the repository is not permission to expose them to an agent runner.

## Parsed prediction

```json
{
  "task_id": "matching public identifier",
  "activate": 1,
  "ate_estimate": 0.1,
  "adjustment_set": ["Z"]
}
```

The JSON above specifies the shape, not a real task answer. `activate` must be an integer 0 or 1; booleans, strings and floats are invalid. Effect estimates must be finite JSON numbers. A missing or invalid field does not remove the task from the accuracy denominator. Numeric estimation and minimal-adjustment validity are checked separately from action validity. `adjustment_set` must be exactly one entry Z for the current minimal-set contract.

The scorer expects parsed task records. A future runner must retain raw model text and parser status and produce an invalid parsed record for a failed response. The scorer does not execute model-generated code, implement tool calls or validate arbitrary reasoning traces. Duplicate prediction IDs and unknown IDs stop scoring, since their interpretation is ambiguous. Missing task IDs generate explicit missing-response records.

## Provenance

The scorer requires checkpoint, precision, quantizer, seed and evidence_source in a separate provenance JSON. Do not put tokens, API keys or private credentials in it. Add exact weight revision/hash, prompt hash, calibration details, activation/cache precision, backend and hardware, chat template, decoding, budget and tools before actual research collection. A nonempty provenance object does not independently verify these claims.

One scored file represents one configuration/run. For repeated runs, analyze the dependence explicitly rather than concatenating duplicate task IDs into the single-run analysis utility.

## Scored record and missingness

Each row contains the task/family keys, conditions, valid_action, missing_prediction, correct, numeric_estimate_valid, ate_error, adjustment_valid and regret. Invalid/missing action means correct=0 and regret=null. Invalid/nonfinite numeric output means ate_error=null. These null outcomes require a stated denominator and missingness report in downstream numeric summaries.

Do not fit the binary processing model by recoding invalid activation as decline. Its input is the actual yes/no response. A joint invalid-response model or a separately labeled valid-response sensitivity analysis is needed when invalidity is appreciable. The primary correctness analysis already retains invalid actions as failures.
