# Interleaved presentation order

Cohort 008 found a 9/32 F16 conflict-accuracy drop when historical evidence appeared first. Its two orders were collected in different sessions. This cohort tests the same items with both line orders in a single run per format, using the same 3B F16 and Q4_K_M CPU settings.

Each of the 64 original items appears twice. Both versions use opaque task IDs, share an evaluator-only pair key, and differ only in which evidence source appears first. Within each family, two of the four base items are assigned randomized-first execution and two historical-first execution. The runner interleaves all twins using its frozen run seed. Both model formats receive the same schedule. The conflict accuracy order contrast is primary. Model format by order is secondary. Score a complete single fenced JSON object with the preexisting sensitivity rule. Invalid answers count as incorrect. Resample the 16 families, not the duplicated responses.

The model sees only the prompt. The paired keys and order metadata remain in the evaluator records. This within-session assignment removes the cohort 008 collection-date difference. It does not remove all wording, repeated-item or task-family limitations.

The local source fixture is cohort 005's exact evidence tables. The frozen F16 schedule selects the 16 families. Create the generated fixture with python3 tools/make_interleaved_source_order.py --source PATH_TO_SOURCE_SELECTION --schedule experiments/cohort_005/run_001_f16/schedule.json --out NEW_DATA_DIRECTORY --seed 20261112.
