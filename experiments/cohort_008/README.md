# Within-item evidence presentation reversal

Cohort 005 associated historical-first presentation with greater historical-direction agreement in F16 on conflict items. Because presentation order varied across families, the original split alone cannot separate order from family characteristics. Reverse the two evidence lines on every prompt and rerun the same two 3B formats on all 64 matched tasks. Preserve table values, wording, item IDs, schedules and settings. Reuse the original arms as the complementary order for each item.

The primary exploratory contrast is the change in correct conflict decisions from randomized-first to historical-first within each format under single-fence scoring. We expect lower F16 conflict accuracy when historical rates appear first. Report both formats and the format difference in the order contrast, using family blocks for uncertainty. Invalid decisions count as wrong. This manipulation checks sensitivity to line order on these prompts. Presentation order remains partly coupled to run timing because the complementary order was collected later.

Generate with `python3 tools/make_arithmetic_control.py --variant source-selection-reversed --source PATH_TO_DESIGN_VALIDATION --out NEW_DATA_DIRECTORY`.
