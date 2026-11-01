# Synthetic validation results

**These results contain no LLM responses and no quantized-model measurements.**

Seed: 20261101. Independent simulation repetitions per scenario/sample-size: 200. Bootstrap replicates per diagnostic: 500.

## Parameter recovery

Each n is the number of simulated responses per cell (four cells per repetition). Bias and RMSE use only finite, converged estimates; exclusions and used counts are disclosed in the JSON. Near-boundary exclusions can themselves bias the retained summaries, so these are diagnostics rather than proof of uniform recovery.

- **interior, n=50**: C bias 0.0003, RMSE 0.0506; A bias 0.0054, RMSE 0.1407; B bias 0.0146, RMSE 0.1527. Nonconverged: 0; near-boundary fits: 3.
- **interior, n=200**: C bias -0.0032, RMSE 0.0252; A bias -0.0007, RMSE 0.0703; B bias -0.0033, RMSE 0.0699. Nonconverged: 0; near-boundary fits: 0.
- **interior, n=1000**: C bias 0.0002, RMSE 0.0108; A bias -0.0016, RMSE 0.0277; B bias -0.0023, RMSE 0.0273. Nonconverged: 0; near-boundary fits: 0.
- **lower_causal_sensitivity, n=50**: C bias -0.0092, RMSE 0.0649; A bias -0.0052, RMSE 0.0925; B bias -0.0101, RMSE 0.0871. Nonconverged: 0; near-boundary fits: 0.
- **lower_causal_sensitivity, n=200**: C bias 0.0005, RMSE 0.0324; A bias 0.0031, RMSE 0.0482; B bias 0.0005, RMSE 0.0426. Nonconverged: 0; near-boundary fits: 0.
- **lower_causal_sensitivity, n=1000**: C bias 0.0002, RMSE 0.0136; A bias -0.0001, RMSE 0.0213; B bias 0.0001, RMSE 0.0193. Nonconverged: 0; near-boundary fits: 0.
- **higher_conditional_association, n=50**: C bias -0.0041, RMSE 0.0515; A bias -0.0057, RMSE 0.1136; B bias -0.0184, RMSE 0.2728. Nonconverged: 0; near-boundary fits: 44.
- **higher_conditional_association, n=200**: C bias -0.0002, RMSE 0.0267; A bias 0.0019, RMSE 0.0529; B bias 0.0142, RMSE 0.1102. Nonconverged: 0; near-boundary fits: 0.
- **higher_conditional_association, n=1000**: C bias 0.0000, RMSE 0.0110; A bias -0.0009, RMSE 0.0258; B bias -0.0023, RMSE 0.0508. Nonconverged: 0; near-boundary fits: 0.
- **action_bias, n=50**: C bias -0.0139, RMSE 0.0535; A bias 0.0039, RMSE 0.1202; B bias 0.0146, RMSE 0.1192. Nonconverged: 0; near-boundary fits: 31.
- **action_bias, n=200**: C bias 0.0013, RMSE 0.0254; A bias -0.0034, RMSE 0.0672; B bias 0.0005, RMSE 0.0568. Nonconverged: 0; near-boundary fits: 0.
- **action_bias, n=1000**: C bias 0.0002, RMSE 0.0108; A bias 0.0003, RMSE 0.0298; B bias -0.0003, RMSE 0.0242. Nonconverged: 0; near-boundary fits: 0.
- **near_causal_boundary, n=50**: C bias 0.0006, RMSE 0.0138; A bias -0.0082, RMSE 0.3540; B bias -0.0488, RMSE 0.4753. Nonconverged: 13; near-boundary fits: 181.
- **near_causal_boundary, n=200**: C bias -0.0007, RMSE 0.0068; A bias 0.0327, RMSE 0.2967; B bias 0.0306, RMSE 0.3623. Nonconverged: 3; near-boundary fits: 122.
- **near_causal_boundary, n=1000**: C bias -0.0002, RMSE 0.0031; A bias 0.0044, RMSE 0.1405; B bias -0.0061, RMSE 0.1406. Nonconverged: 0; near-boundary fits: 1.
- **near_association_boundary, n=50**: C bias -0.0036, RMSE 0.0465; A bias 0.0009, RMSE 0.0259; B bias 0.0451, RMSE 0.4402. Nonconverged: 0; near-boundary fits: 180.
- **near_association_boundary, n=200**: C bias 0.0010, RMSE 0.0247; A bias 0.0014, RMSE 0.0120; B bias 0.0324, RMSE 0.3638. Nonconverged: 0; near-boundary fits: 107.
- **near_association_boundary, n=1000**: C bias -0.0004, RMSE 0.0111; A bias 0.0001, RMSE 0.0057; B bias -0.0233, RMSE 0.1415. Nonconverged: 0; near-boundary fits: 0.

## Deliberate model misspecification

Binomial parametric-bootstrap goodness-of-fit tests compare tree predictions against four unrestricted cell probabilities. An initial symmetric logistic generator was found to be observationally equivalent to the tree and is retained explicitly. The asymmetric incompatible generator was added after that diagnostic finding. These demonstrations are exploratory, not preregistered tests or estimates of test size or power.

- **tree_generated**: deviance 0.471; bootstrap p=0.5070; held-out negative log loss: tree 0.4417, logistic 0.4417. Bootstrap nonconverged: 0.
- **observationally_equivalent_logistic**: deviance 0.688; bootstrap p=0.4331; held-out negative log loss: tree 0.4444, logistic 0.4444. Bootstrap nonconverged: 0.
- **incompatible_logistic**: deviance 702.746; bootstrap p=0.0020; held-out negative log loss: tree 0.3973, logistic 0.3497. Bootstrap nonconverged: 0.

## What this establishes

The implementation can be checked against known generating parameters and a competing response generator. Boundary diagnostics determine where interpretation is fragile. Recovery under the assumed tree does not establish that LLMs use that tree.

The observationally equivalent logistic generator is deliberately retained: a passing fit test cannot distinguish those response mechanisms from these four cells alone. The asymmetric generator checks whether a detectable violation can be rejected. Neither result proves test calibration.

See [the methodology](../../docs/RESEARCH_METHODOLOGY.md) for the proposed LLM experiment and the distinction between implemented validation and planned inferential analyses.
