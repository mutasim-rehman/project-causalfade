# 7B F16 reference-competence feasibility screen

This is an exploratory reference screen using the matched observational-strength source-selection fixture from cohort 011. It samples eight of the same 16 development families with runner seed 20261112, giving 64 prompts (both evidence orders for four source-selection cells per family). These families were already used by the 3B pilot and are not confirmatory or independent; reusing them makes the screen a direct task-level feasibility check for the larger reference.

Before inference, the task schedule, 7B F16 weight digest, CPU settings and decision gate are frozen in `frozen_run_plan.json`. The prior 7B screen's fence-only criteria are carried forward as rates: at least 56/64 valid actions, at least 44/64 correct overall, and at least 9/16 correct in conflict under each evidence order. The stricter per-order conflict requirement checks that competence is not concentrated in one evidence order. If the F16 reference fails the gate, do not launch the quantized arm. If it passes, run a matched 7B Q4_K_M arm on the identical schedule as a developmental format comparison.

Score strict JSON and single-fence sensitivity separately. Keep the eight families as bootstrap units. No outcome from this screen can qualify as confirmatory evidence.
