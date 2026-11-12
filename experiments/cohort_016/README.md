# Cohort 016: fresh-family evidence-order replication

## Purpose

Cohort 015 found a large Q4_K_M order contrast on conflict prompts, along with order changes on aligned prompts where the two sources agree. Cohort 016 is a prospective replication on 96 newly generated matched-strength SCM families. Cohort 015 and all earlier cohorts remain development data and are excluded from this analysis.

Both 7B F16 and Q4_K_M receive the same 768 strict-JSON prompts on the causal-context frame. Each family has two aligned and two conflict base tasks; every task is paired across randomized-first and historical-first line order. Within every family, the randomized in-family first-position assignment is balanced two tasks per side. The generation, order-assignment and response-shuffle seeds are fixed in the frozen plan.

## Primary outcome and test

For each family, calculate the mean strict action accuracy on the two Q4_K_M conflict items with historical evidence first minus the mean accuracy on those same items with randomized evidence first. Invalid JSON or invalid actions count as incorrect. The primary estimate is the mean of the 96 family-level differences. Test the two-sided null that this mean is zero at alpha 0.05 using a one-sample t statistic over families; report its 95% t interval and family-bootstrap interval. There is one primary outcome. Format-by-order interaction, F16 order effects and aligned-item outcomes are secondary and descriptive.

## Sample-size plan

The prespecified smallest effect of interest is 20 percentage points. A Monte Carlo power analysis simulated two paired binary differences per family using a Gaussian copula, 100,000 replicates per design cell, and a two-sided family-level t test. Ninety-six families gives approximately 81% power when pair discordance is 70% and within-family correlation is 0.50. This discordance is slightly above the 65.6% observed in cohort 015. Power is about 71% under the more extreme 90% discordance and 0.50 correlation scenario. Assumptions and sensitivity cells are in [power_analysis.json](power_analysis.json); this planning simulation is not model evidence.

## Execution

Run both formats with llama.cpp b12176 on CPU, eight threads, context 2048, one parallel sequence, F16 KV cache, temperature zero, a 48-token cap, and prompt caching disabled. Use the same exact schedule for both formats. Model and runtime hashes, dataset checksums, response schedule, seeds and analysis are frozen in [frozen_run_plan.json](frozen_run_plan.json). There are no outcome-based exclusions or interim stopping rules.

Model files are read from `/home/i242514/Desktop/CAUSALFADE/weights/gguf/`; this cohort uses no external SSD.
