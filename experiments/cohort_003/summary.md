# Q2_K repacking diagnostic results

We tested whether disabling CPU weight repacking restored valid output from the 3B Q2_K file. The two arms used the same weight digest and 16 exact-evidence prompts across four complete families. Only the repacking flag changed. The default arm reproduced the original text on all 16 overlapping items from cohort 001. These repeats check operational reproducibility and add no independent families.

| Arm | Requests completed | Length caps | Valid actions under either parser | Median seconds |
| --- | ---: | ---: | ---: | ---: |
| [Default](run_001_default/) | 16/16 | 16/16 | 0/16 | 7.33 |
| [Disabled](run_002_no_repack/) | 16/16 | 16/16 | 0/16 | 7.31 |

The generated text changed on all 16 matched tasks when repacking was disabled, but both arms exhausted the budget and yielded zero valid actions. An always-activate policy would score 8/16, and the analytic backdoor rule 16/16. Repacking changes the generations in this CPU build but disabling it does not rescue the tested file on this task. Other backend, quantizer or calibration changes remain untested.

[Machine-readable comparison](default_vs_no_repack.json) and [response agreement](response_agreement.json).
