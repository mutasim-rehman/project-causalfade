# Matched observational-strength source-selection development pilot

Both formats completed the frozen 128-prompt schedule over 64 paired items and 16 new families. Every output was a single fenced JSON object that stopped normally. Strict action scoring therefore found 0 valid responses in each arm; single-fence scoring is reported as the prespecified sensitivity. The two runs used identical prompt schedules and the PC-local Qwen2.5 3B F16 and Q4_K_M GGUF files.

## Source-order crossover

| Format | Condition | Randomized evidence first | Historical evidence first | Change |
| --- | --- | ---: | ---: | ---: |
| F16 | Aligned | 18/32 | 32/32 | +43.75 points (95% family interval +34.375 to +50) |
| F16 | Conflict | 16/32 | 8/32 | −25 points (−37.5 to −12.5) |
| Q4_K_M | Aligned | 16/32 | 17/32 | +3.125 points (0 to +9.375) |
| Q4_K_M | Conflict | 16/32 | 16/32 | 0 points (0 to 0) |

F16 again changed its conflict choices with evidence order: accuracy fell by 25 points when historical evidence was first. This matches the effect size in fresh-family cohort 010 and is consistent with cohort 009. The aligned result moved in the opposite direction, rising by 43.75 points with historical evidence first. Q4_K_M had no conflict-order effect and scored at the always-activate baseline in the balanced conflict cells.

## Format comparison

After collapsing over presentation order, F16 scored 50/64 aligned and 24/64 conflict; Q4_K_M scored 33/64 and 32/64. The aligned-minus-conflict penalty was 40.625 points for F16 and 1.563 points for Q4_K_M, for a Q4_K_M-minus-F16 penalty difference of −39.063 points (95% family interval −45.313 to −32.813). Q4_K_M lost 26.563 points of aligned accuracy relative to F16 (interval −31.25 to −21.875) and gained 12.5 points of conflict accuracy (interval +6.25 to +18.75). This smaller conflict penalty reflects near-chance performance and an almost universal activate response (63/64 aligned, 64/64 conflict), not preserved causal reasoning.

## Interpretation and limits

The matched-strength fixture passed its mathematical audit: randomized contrasts retained the causal signs, observational contrasts retained the association signs, and aligned/conflict observational magnitudes matched within each family. The target historical magnitude overlaps the earlier conflict-signal range. Thus, this cohort removes the original generator's aligned-versus-conflict signal-strength imbalance for the supplied rates.

This is a development cohort selected after earlier outcomes, not confirmatory evidence. It reuses one prompt frame, one synthetic population family, one model family and a small number of SCM families. The F16 order effect repeats, but low conflict competence and the striking aligned-order shift limit mechanistic interpretation. Q4_K_M's apparent smaller conflict penalty is driven by a near-constant action policy. No general quantization claim follows.

The single-fence action outcomes and paired family bootstrap are in [format analysis](format_analysis.json) and [order analysis](source_order_analysis.json). The original version of the order analysis, which undercounted displayed correct/activate totals by a factor of two while leaving paired effects and intervals unchanged, is preserved as [v1](source_order_analysis_v1_undercounted_counts.json). Both model runs, raw outputs, logs, hashes and schedules are archived under `run_001_f16/` and `run_001_q4_k_m/`.
