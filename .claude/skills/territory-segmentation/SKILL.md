---
name: territory-segmentation
description: Use when comparing territories, building territory segments/tiers, or analyzing territory growth trends. Use for "which territories are underperforming", "segment territories by growth/coverage", or territory comparison dashboard logic.
---

# Territory Segmentation

Use this skill for territory-vs-territory comparison and segmentation logic, building
on outputs from [analytics/](../../../analytics/) and the territory-analyst agent.

## Approach

1. Segment on approved metrics only (reach, coverage, attainment, growth — root
   [CLAUDE.md](../../../CLAUDE.md#2-approved-metrics-canonical-definitions)). Don't
   introduce an ad hoc composite score without documenting its formula first (see
   sales-kpi-design skill).
2. Normalize for structural differences before comparing territories head-to-head —
   e.g., territory size, HCP-target-list size, historical potential — otherwise
   "underperforming" may just mean "smaller/harder territory."
3. Use clear, reproducible segment boundaries (e.g., quartiles, or fixed thresholds
   agreed with Commercial Excellence) — not subjective judgment calls that would
   differ between runs.
4. Respect the requester's authorized territory/region scope (root CLAUDE.md
   sections 5, 12) — never surface territories outside it.
5. Present segmentation as descriptive input to a ranking/recommendation, not as a
   final judgment on rep performance — territory outcome and rep performance are not
   the same thing.
