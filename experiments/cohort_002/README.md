# Formula-given arithmetic control

Hypothesis: explicitly supplying the adjustment arithmetic will improve action accuracy if difficulty selecting or applying the adjustment drives errors in the direct task. Precision differences that persist with a supplied formula can also reflect arithmetic, instruction following, output format, or other general failures.

This exploratory comparison uses the same exact table, item IDs, order, world-family sample and output keys as cohort 001. The prompt replaces the causal problem with an explicit arithmetic rule using the same target score and decision threshold. It supplies the computation but leaves the numeric calculation and action to the model. Prompt wording and length change, so this control does not isolate a single cognitive operation. Report strict and single-fence scores separately. The source dataset and local control dataset are identified by their digests; the full rendered prompts are preserved in each run schedule.

Generate the control with `python3 tools/make_arithmetic_control.py --source PATH_TO_DESIGN_VALIDATION --out NEW_DATA_DIRECTORY`. Apply identical model/runtime settings and the same family and order seed.
