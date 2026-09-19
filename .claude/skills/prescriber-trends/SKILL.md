---
name: prescriber-trends
description: Use when analyzing HCP/prescriber-level engagement or prescription trend patterns over time — e.g. "which HCPs are becoming less responsive", "identify emerging high-potential prescribers". Involves HCP-identifiable data; use narrowly.
---

# Prescriber Trend Analysis

Use this skill for HCP-level engagement/prescription trend analysis, in conjunction
with the prescriber-trend-agent.

## Approach

1. This is the only analysis type in this project that legitimately needs
   HCP-identifiable (not just aggregate) data. Confirm the requester's role is
   authorized for HCP-level data (root [CLAUDE.md](../../../CLAUDE.md#5-data-access-boundaries))
   before proceeding; if not, produce an aggregate/territory-level view instead.
2. Use rolling-window trend logic (e.g., trailing 3/6-period comparison) with a
   stated window — a single-period swing is noise, not a trend.
3. Flag HCPs with too few data points for a reliable trend read rather than reporting
   a trend direction anyway.
4. Never frame a trend finding as, or adjacent to, a clinical/efficacy/off-label
   claim about why an HCP's prescribing changed (root CLAUDE.md section 4) — describe
   the observed pattern only (e.g., "call responsiveness declined 20% over the last
   two quarters"), not a causal or promotional narrative.
5. When trend output feeds into a territory or rep-facing summary, aggregate/
   de-identify before handing off — don't let HCP-identifiable detail leak into a
   context that only needs the aggregate insight.
