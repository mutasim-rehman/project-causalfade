# Fresh-family formula replication results

Both 3B formats completed 48 requests on the same 12 fresh families. The frozen fixture seed and full input are archived in this cohort. Task IDs and family parameter draws are disjoint from the initial fixture. Every response stopped normally and used a single JSON fence, so strict scores were 0/48. The declared sign analysis accepts one fence and retains every scheduled item.

| Arm | Correct estimate sign | Aligned sign | Conflict sign | Explicit action correct | Action disagrees with sign |
| --- | ---: | ---: | ---: | ---: | ---: |
| [F16](run_001_f16/) | 46/48 | 23/24 | 23/24 | 24/48 | 22/48 |
| [Q4_K_M](run_001_q4_k_m/) | 31/48 | 14/24 | 17/24 | 28/48 | 37/48 |

Q4_K_M lost 31.25 points of sign accuracy relative to F16 (12-family paired percentile interval −41.67 to −20.83). Seventeen items worsened and two improved. This repeats the direction of the earlier 25-point gap on 16 different families. The fresh difference in sign-based conflict penalties was −12.5 points (−29.17 to +4.17). Accuracy fell in both conditions. The analytic formula solves all 48, and always declining scores 24/48.

Explicit action and estimate sign again told different stories. F16 declined on all 48, and Q4_K_M scored four more correct actions despite a substantially worse sign score. The estimates and action fields frequently disagreed. This is independent-family replication of a configuration difference under the supplied arithmetic rule. It uses one checkpoint, one prompt family and one CPU runtime. It supplies a focused target for later evaluation, separate from selective causal degradation or performance of an unconstrained agent.

[Paired sign comparison](paired_estimate_sign.json) · [Paired explicit action comparison](paired_explicit_action.json)
