# November 10, 2026 research session

The session started at revision `ef0fa4e` with local inputs in `/home/i242514/Desktop/CAUSALFADE`. Prior work consists of synthetic design validation and prepared weights. Cohort 001 will assess feasibility of the paired 3B F16/Q2_K direct-response comparison using the existing fixtures.

The CPU runtime is llama.cpp b12176 (commit 8820b088d) on the Ubuntu lab machine. The durable runner was pushed as `aec9fd2`. The exploratory fence sensitivity and arithmetic-control generator were pushed as `da4507b`. All 26 repository tests passed after these changes. Cohort 001 is executing F16 followed by Q2_K, with 64 scheduled responses each. Initial F16 output exposed a strict JSON compliance issue. Both unmodified strict scoring and a separately labeled fence-only sensitivity will be reported.

F16 completed 64 of 64 responses, and its weight SHA-256 matched the historical manifest. All outputs were single fenced JSON objects, so strict action accuracy was 0/64. The fence-only sensitivity produced 33/64 correct actions, with activation on 63/64 and the correct adjustment set on 0/64. This establishes a reference-competence issue independent of JSON fencing.

Q2_K completed 64 requests with matching weight provenance. All 64 were length-capped and failed both parsers. The strict contrast has a complete accuracy floor. Fence-only accuracy is 51.6% for F16 and 0% for Q2_K. The +3.125-point conflict-penalty contrast arises because the weak F16 arm was one answer better in the conflict cells, while Q2_K failed in all cells. It does not show selective susceptibility. Q4_K_M is running as a post hoc intermediate-format comparator.

Q4_K_M completed the same 64 prompts. All outputs were fenced JSON and stopped normally. Fence-only accuracy was 34/64, with activation on 62/64 and correct adjustment on 0/64. Cohort 001 established a Q2_K output failure and a weak 3B direct-response reference. See the [paired pilot summary](experiments/cohort_001/summary.md).
