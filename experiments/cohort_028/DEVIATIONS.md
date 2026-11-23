# Cohort 028 deviation log

## 23 November 2026 — Git checkpoint cadence

Development `llama8b` had saved 1030/1280 responses when the user paused the run for PC shutdown. The original runner commits and pushes every 20 responses and at pipeline status changes. In response to the user's request, the versioned [operational amendment](amendments/hourly_checkpoint_2026-11-23.json) uses [a separate launcher](../../tools/cohort028_run_hourly.py) to save local progress at the same checkpoints while committing and pushing only hourly or on model-arm completion. The final model completion commit includes terminal pipeline status. No inference was launched to prepare or verify this amendment. The frozen plan, fixture, parser, calculator, analysis, qualification gates and original runner source are unchanged. Results already saved remain valid and are resumed by task ID. Future runs must use the amended launcher to get the new cadence.

Record any future departure from the frozen fixture, model/runtime plan, schedule, parser, calculator, retry policy or gate here before interpreting results. Preserve original artifacts and give the reason, timestamp and affected arm.
