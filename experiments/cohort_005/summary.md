# Evidence-source selection results

Both 3B formats completed the same 64 prompts across 16 development families. The task supplied randomized and historical success rates and requested only the action. Every response stopped normally and contained one JSON fence. Strict accuracy was 0/64 for both formats. The table uses the declared single-fence score.

| Arm | Overall correct | Aligned correct | Conflict correct | Activate |
| --- | ---: | ---: | ---: | ---: |
| [F16](run_001_f16/) | 39/64 | 28/32 | 11/32 | 47/64 |
| [Q4_K_M](run_001_q4_k_m/) | 35/64 | 19/32 | 16/32 | 61/64 |

Always activating scores 32/64. Always choosing the direction favored by randomized evidence scores 64/64. Following historical evidence alone scores 32/64, with zero correct conflict choices. F16 followed the historical direction on 21/32 conflict items, compared with 16/32 for Q4_K_M. Q4_K_M minus F16 changed the conflict penalty by −43.75 points (paired 16-family percentile interval −65.63 to −21.88). It lost nine aligned choices and gained five conflict choices, while moving closer to an always-activate policy. Overall accuracy fell by 6.25 points (−12.50 to −1.56). A smaller conflict penalty here does not establish improved evidence use.

In the exploratory presentation-order split, F16 chose the historical direction on all 10 conflicting items when historical rates were listed first. When randomized rates were first, it activated on all 22 conflicting items, scoring 11/22. Since order was assigned at the family level and different families occupy each order, this split motivates reversing the order within the same items.

The proposed homogeneous processing tree requires activation probabilities to satisfy `p11 - p10 - p01 + p00 = 0`. F16's observed residual was −43.75 points (descriptive paired family interval −68.75 to −18.75). Q4_K_M's residual was −18.75 points (−37.50 to 0). The F16 cell pattern is difficult to reconcile with a homogeneous tree. These checks are post hoc and do not identify a latent mechanism. The original generator also makes the observational signal stronger in aligned items, with mean absolute gaps of 57.10 versus 38.04 points despite a matched causal magnitude of 9.53 points.

[Matched comparison](f16_vs_q4_k_m_source_selection.json) · [Source-order and additivity diagnostics](source_and_tree_diagnostics.json)
