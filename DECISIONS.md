# Research decisions

## 2026-11-10 13:10 PKT

Use the local CAUSALFADE folder for input weights and fixtures, and this repository for run artifacts. Start with the provisional 3B F16/Q2_K contrast on exact evidence. The known graph, exact probabilities and matched families remove sampling error in the evidence and make failures easier to interpret. Reserve the remaining model sizes and formats for later development decisions.

Use the official llama.cpp b12176 Ubuntu CPU build for both arms. The machine has an RTX 4000 Ada using nouveau, and a working CUDA setup has not been established. CPU execution avoids driver changes during the lab session and keeps the execution policy common. Eight threads and one model process at a time limit resource pressure. Validate via recorded startup, timing and complete task blocks.
