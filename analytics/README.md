# analytics

Deterministic KPI engine. This is the source of truth for every number the app
surfaces — no LLM in this repo should compute or restate these values independently.

- Upload validation (schema check on rep/HCP/territory/product/date/outcome/volume/
  target fields)
- HCP/territory normalization (canonical IDs/codes, inconsistent-code detection)
- Duplicate-call detection/deduplication
- KPI computation: reach, frequency, coverage, call productivity, target attainment,
  territory growth, HCP engagement trend — definitions in root
  [CLAUDE.md](../CLAUDE.md#2-approved-metrics-canonical-definitions)
- Aggregation reconciliation (aggregates must reconcile against source-level sums)
- Minimum-sample-threshold flagging for low-volume reps/territories

Any ML component (e.g., engagement-trend forecasting) lives here or alongside this
layer, clearly separated from the rule-based KPI calculations.
