# Fresh-family interleaved source-order replication

Cohort 009 found that F16 conflict accuracy fell by 21.875 percentage points when historical evidence appeared first in a balanced, same-session crossover on 16 reused families. This follow-up tests whether that effect persists on new generated families.

Generate 12 fresh SCM families with seed 20261113, derive their exact source-selection tasks, and include both source orders for each of 48 base items. The randomized first-order assignment is balanced within each family. Run F16 and Q4_K_M over the same shuffled task schedule, using the existing CPU inference settings and single-fence scoring.

The prespecified primary outcome is the within-family historical-first minus randomized-first change in F16 conflict accuracy. The F16 versus Q4_K_M interaction is secondary. Invalid actions count as errors. Use the 12 families as the bootstrap units. This is an exploratory independent-family replication chosen after viewing cohort 009. It concerns this source-selection task and does not establish generalization to other model families or causal tasks.

The source generator manifest, task fixture, prompts, evaluator truth and baselines are stored in this cohort. The generated source world seed and the order-assignment seed are distinct and recorded.
