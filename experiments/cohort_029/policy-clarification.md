# CF-TP1 policy clarification · constant-rivals-v1

The solo workflow freezes the exact bytes of this clarification with the fixture.
It clarifies the rival policy gates in section 6 and the lab validation matrix.

The requirement to disagree under both gold actions applies to nonconstant rival
policies. For a declared constant-action policy, or a weight-only threshold that
is mathematically constant on the entire prespecified public weight grid, apply
the constant-output gate. Its item accuracy must equal 50%, it must be wrong in
at least 16 transfer-causal families, and it must get zero target-switch pairs
both correct. Preserve item and family disagreements by gold action.

For the weight-only family, the exception applies only at the minimum threshold
with inclusive comparison and at the maximum threshold with strict comparison,
in either polarity. Every other threshold is subject to the two-gold-action gate
even if its predictions happen to be constant in one candidate fixture.

Retain the original literal-gate results beside the clarified results. Keep the
same generator, prompt design, schedule, model, scoring, estimand and response cap.
Collection starts only through the explicit runner command.
