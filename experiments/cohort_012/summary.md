# 7B F16 reference-competence feasibility screen

The F16 arm completed all 64 scheduled prompts across eight development families. Its schedule exactly matched the pre-frozen family sample and task order. Every response was a single fenced JSON object and stopped normally, so strict action scoring was 0/64; after the prespecified single-fence handling, 64/64 actions were valid.

The model scored 47/64 overall (73.4%), meeting the 44/64 overall threshold. It scored 32/32 aligned and 15/32 conflict. Conflict accuracy was 8/16 with randomized evidence first and 7/16 with historical evidence first. Both per-order conflict criteria required at least 9/16, so the reference gate failed despite adequate output validity and overall accuracy.

The frozen stopping rule says not to launch 7B Q4_K_M after a failed F16 reference gate. No quantized arm was run. This result indicates that the simplified matched-strength task remains difficult for the 7B full-precision reference on conflict cases. It is a small, exploratory screen on families already used by cohort 011, and it cannot estimate a precision effect or serve as confirmatory evidence.

The exact thresholds and frozen schedule are in [the run plan](frozen_run_plan.json) and [schedule](frozen_schedule.json). The raw responses, logs, model hash, metrics, and gate result are in [the F16 run](run_001_7b_f16/). The complete [gate analysis](gate_analysis.json) documents why collection stopped.
