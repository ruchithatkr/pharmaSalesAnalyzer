---
name: sales-kpi-design
description: Use when designing, validating, or modifying reach/frequency/coverage/call-productivity/target-attainment calculations for this project — e.g. adding a new KPI, changing a formula, or reviewing whether a proposed metric is sound. Not for one-off KPI number lookups (that's the coverage-kpi-agent's job).
---

# Sales KPI Design

Use this skill when a KPI formula in [analytics/](../../../analytics/) is being added,
changed, or reviewed.

## Rules

1. Every KPI must have a single canonical definition recorded in root
   [CLAUDE.md](../../../CLAUDE.md#2-approved-metrics-canonical-definitions) before
   it's implemented. If a request implies a new metric or a formula change, update
   that section first and get it acknowledged as the source of truth — don't let two
   different formulas for "coverage" exist in code and docs simultaneously.
2. Formulas must be deterministic and reproducible from raw data — no LLM judgment in
   the calculation itself.
3. Define the denominator carefully: state exactly what "total" means (all target
   HCPs? all called HCPs? per period or cumulative?). Most KPI bugs are denominator
   ambiguity.
4. Every KPI must specify a minimum sample size below which the value should be
   flagged low-confidence rather than suppressed or presented as-is.
5. Write the formula, an example calculation with sample numbers, and the edge cases
   (zero denominator, missing target, mid-period rep transfer) before implementing.
6. Add/update a unit test in [tests/](../../../tests/) for every formula change.
