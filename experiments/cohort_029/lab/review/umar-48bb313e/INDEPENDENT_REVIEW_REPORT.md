# Independent Blind Review Report · Cohort 29

**Reviewer Name:** Raza Blind Reviewer (Cohort 29)  
**Review Date:** November 24, 2026  
**Declaration of Independence and Exposure:**  
This review was conducted strictly independently in blinded evaluation mode. The decisions and calculations were finalized and sealed solely using the files provided in the `blind-review-packet` directory (`README.md`, `worked-cases.md`, `blind_review.json`, and `answers.csv`). No access was made to the design map (`transfer.json`), candidate task key (`tasks.jsonl`), or any other external answer key or design documentation prior to sealing these results.

---

## 1. Summary of Methodology & Analysis

### Identification of Evidence
Each prompt in `blind_review.json` presents evidence from two sources:
- **Randomized study:** Treatment assigned purely at random, guaranteeing unconfounded conditional stratum-specific effects.
- **Historical observational study:** Treatment chosen by operators, subject to unmeasured confounding and potential Simpson's paradox bias.

In accordance with causal inference principles and the prompt's explicit guidance, all causal recommendations are derived exclusively from the **randomized study**, while treating observational discrepancies as confounding artifacts.

### Transportability Assumption
It is assumed that the stratum-specific potential outcome risk rates (or conditional average treatment effects) transfer directly to the target population:
- For target strata weights $w_{\text{Amber}}$ and $w_{\text{Blue}} = 1 - w_{\text{Amber}}$:
  - Target On rate = $w_{\text{Amber}} \cdot P(Y=1 \mid \text{on}, \text{Amber}) + w_{\text{Blue}} \cdot P(Y=1 \mid \text{on}, \text{Blue})$
  - Target Off rate = $w_{\text{Amber}} \cdot P(Y=1 \mid \text{off}, \text{Amber}) + w_{\text{Blue}} \cdot P(Y=1 \mid \text{off}, \text{Blue})$
  - Target Effect $\Delta$ = Target On rate - Target Off rate
- Action is set to **1** (on) if $\Delta > 0$ and **0** (off) if $\Delta < 0$.

---

## 2. Unclear Instructions, Ambiguities & Missing Assumptions Flagged

1. **Inverted Stratum Order in Sources (Groups 1, 4, 7 / Tasks 4–7, 16–19, 28–31):**
   In the Target mix specification, Amber is listed first and Blue second (e.g. `Amber 42%, Blue 58%`). However, in Source A and Source B tables, Blue is listed first and Amber second. Readers or automated parsers assuming positional alignment will cross-multiply rates incorrectly.
2. **Confounding Conflict in Historical Data (Groups 2, 3, 5, 7 / Tasks 8–15, 20–23, 28–31):**
   In 16 of the 32 tasks, the historical observational study yields a target treatment effect with the opposite sign of the randomized study (Simpson's paradox / confounding bias). Without an explicit causal rule to favor the randomized study over the observational study, non-causal evaluators could make opposite decisions.
3. **Response Schema Ordering Variation (Tasks 8–15, 20–23):**
   The prompt JSON instructions invert the presentation order of the activate options: `{"activate":0} or {"activate":1}` instead of `{"activate":1} or {"activate":0}`.
4. **Baseline Off-Rate Differences:**
   In `worked-cases.md`, off-rates are fixed at exactly 50% across all strata ($S=1, S=0$). In `blind_review.json`, baseline off-rates differ across strata within the study.

---

## 3. Arithmetic Control Verification (Worked Cases)
All four worked cases across all four randomized-source and target-mix combinations were evaluated and verified against the designated source arithmetic control:
- **Case 1:** (L, low) -> 0; (L, high) -> 1; (R, low) -> 1; (R, high) -> 0
- **Case 2:** (L, low) -> 1; (L, high) -> 1; (R, low) -> 0; (R, high) -> 0
- **Case 3:** (L, low) -> 1; (L, high) -> 1; (R, low) -> 1; (R, high) -> 1
- **Case 4:** (L, low) -> 0; (L, high) -> 1; (R, low) -> 0; (R, high) -> 1

The designated table arithmetic control yields identical totals and choices in 100% of cases.
