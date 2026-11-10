# 7B reference feasibility results

The [7B F16 run](run_001_f16/) completed all 32 prompts across eight development families. The local weight hash matched the conversion manifest. Every response stopped normally and used a single JSON fence. Strict action accuracy was 0/32. With fence handling, 32/32 actions were valid, 17/32 were correct, and 9/16 conflict actions were correct. Always activating scores 16/32 and the analytic backdoor policy scores 32/32.

The model chose activation on 31/32 and the correct adjustment set on 32/32. It agreed with the sign of its own estimate on all 32, but the estimates themselves had mean absolute error about 0.506. Naming the right adjustment variable did not yield a usable decision baseline. Median wall time was 24.09 seconds per request.

The prespecified session gate required at least 28 valid, 22 correct overall and 9 correct conflict actions. The overall criterion failed. No 7B Q2_K arm was launched. This screen uses overlapping development families from the same generator and does not identify a general effect of checkpoint size.

[Machine-readable gate and cell results](reference_feasibility.json).
