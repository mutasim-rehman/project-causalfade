# Invalidated pilot run

This complete 112-response Qwen F16 pilot used fixture v1. The arithmetic-control oracle hardcoded `yes` despite reversed-outcome families requiring `no`, and the control prompt included an intervention question before the control question. The resulting analysis is retained for audit only; its qualification checks must not be interpreted. Fixture v2 fixes both issues and requires fresh runs.
