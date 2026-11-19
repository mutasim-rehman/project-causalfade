# Cohort 026 development screen

Status: second frozen F16 lineage in progress. The development fixture contains eight new SCM families, two independently worded forms and 112 requests per lineage. Validation and confirmation families have not been queried. The first Qwen run was invalidated after discovering an arithmetic-control oracle and prompt-order defect; its complete raw output and invalidation note remain archived. Fixture v2 was frozen before either valid development arm.

## Corrected Qwen F16 result

The corrected Qwen arm completed 112/112 strict-valid requests. On each form, it answered 8/16 graph-switch decisions correctly and achieved 0/8 paired switch fidelity. It selected `X=1` for all 16 switch items per form, so it was correct on 8/8 positive-action items and 0/8 negative-action items. Direct-form graph reading was 16/16 and arithmetic 8/8; decision-form graph reading was 13/16 and arithmetic 4/8. No-change accuracy was 8/16 per form. Both forms failed the frozen qualification gates. These are eight-family development results, not confirmation.

The fixed Llama F16 arm is running. Its complete result will determine whether either lineage/form qualifies. If neither does, the frozen stopping rule ends this assay without validation, confirmation or a precision contrast.

## Initial form result and final bounded revision

Llama F16 completed 112/112 requests but only 48/112 were strict-valid. It returned `X=1.` (with a period) on all 64 action tasks, making every switch and no-change decision invalid under the frozen exact-output rule. Graph reading was 32/32 valid and correct; arithmetic was 12/16 correct. This is a response-contract failure in addition to the apparent action bias. The exact raw texts are retained in `runs/llama8b_f16_v2`.

The one allowed wording revision now supplies the graph-dependent weighting rule without giving the numeric intervention answer, and explicitly requests a bare answer token. It is applied to both forms and both fixed lineages on the same eight development families. All gate thresholds and scheduled denominators remain unchanged. This is the final permitted revision; no further prompt or model search will follow if it fails.
