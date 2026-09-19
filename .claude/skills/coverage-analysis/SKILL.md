---
name: coverage-analysis
description: Use when analyzing HCP call-plan-vs-actual coverage — e.g. "which HCPs are under-covered", "compare planned vs actual call frequency", building or reviewing a coverage report or dashboard view. Distinct from raw KPI computation; this is about interpreting coverage gaps.
---

# Coverage Analysis

Use this skill for call-plan-vs-actual coverage analysis, building on KPI outputs
from [analytics/](../../../analytics/) (reach, frequency, coverage — canonical
definitions in root [CLAUDE.md](../../../CLAUDE.md#2-approved-metrics-canonical-definitions)).

## Approach

1. Start from computed coverage/reach/frequency — never estimate these from
   unaggregated call logs directly in a chat response.
2. Segment coverage gaps meaningfully: distinguish "never called" HCPs from
   "under-frequency" HCPs (called, but below the required cadence) — they need
   different corrective actions.
3. Always state the target-list definition and time window used — coverage numbers
   are meaningless without them.
4. Flag HCPs/territories below the minimum sample threshold as low-confidence rather
   than including them in headline coverage stats.
5. When presenting gaps to a manager, tie each gap back to a specific, actionable
   territory/rep/HCP-segment — vague "coverage is low" statements aren't useful.
6. Never let a coverage gap analysis imply an HCP should be called *because of* a
   product claim — that crosses into promotional/off-label territory (root
   CLAUDE.md section 4).
