# Cohort 017: exploratory 14B follow-up

## Completion and analysis recovery

Both Qwen2.5-14B-Instruct Q8_0 and Q4_K_M arms completed 768/768 responses on the existing cohort 016 schedule. All responses stopped normally and were strict-valid. The unattended controller failed at analysis because its Python environment lacked NumPy. That original status and failure log are preserved.

On 13 November 2026, paired analysis was recovered locally from the archived records with Python 3.13.5 and NumPy 2.3.5. A zero-variance guard was added to the follow-up analyzer: degenerate family contrasts receive descriptive means and null t-test quantities, rather than infinite statistics. This is a disclosed post-collection analysis repair, not a new frozen test or a change to cohort 016. See [analysis.json](analysis.json) and [analysis_recovery.json](analysis_recovery.json).

## Findings

- Q8_0: 488/768 correct overall (63.5%). Conflict accuracy was 104/192 randomized-first (54.2%) and 96/192 historical-first (50.0%). Historical-first minus randomized-first was −4.17 percentage points; exploratory 95% family t interval −6.98 to −1.35.
- Q4_K_M: 440/768 correct overall (57.3%). Conflict accuracy was 96/192 (50.0%) in both orders, with activation on every conflict item. The order contrast is zero with no empirical family variation; no t inference is reported.
- The Q4-minus-Q8 conflict order interaction was +4.17 points (95% paired family percentile interval +1.56 to +7.29). This is exploratory, not a fresh confirmation of the 7B interaction.
- Aligned randomized-first accuracy was 192/192 for Q8_0 and 152/192 for Q4_K_M. Historical-first aligned accuracy was 96/192 for both; both activated on all 192 items in that condition.

## Interpretation

The large positive 7B conflict-order effect does not reproduce in these 14B outputs. A strong presentation-related action shift remains on aligned items, while conflict behavior is dominated by activation bias. Larger size cannot be described as restoring causal competence, and a zero Q4 order contrast does not establish robustness or equivalence.

Q8_0 is quantized, not a full-precision reference. These 96 families were already used at 7B, the study uses one model lineage and a scaffolded direct-response task, and exploratory intervals do not establish model-population effects. No latent causal-route or autonomous-discovery claim follows.
