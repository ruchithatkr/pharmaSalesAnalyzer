---
name: recommendation-writing
description: Use when drafting recommendation narratives or executive-summary text for reps/territories/managers based on computed KPIs and rankings — e.g. "write up recommendations for the underperforming territories" or drafting chatbot response text. Not for computing the underlying numbers.
---

# Recommendation Writing

Use this skill when drafting the natural-language recommendation or chatbot
narrative that sits on top of already-computed KPIs/rankings (from
[analytics/](../../../analytics/) and [recommendation/](../../../recommendation/)).

## Rules

1. Every sentence that states a fact must cite the metric, time range, and
   territory/rep it came from. If you can't point to where a claim came from, cut it
   or mark it as needing verification — don't smooth it into confident prose.
2. No off-label, unsupported, or promotional product claims — ever, even implied
   ones (e.g., don't suggest a call should happen "because Product X works well for
   condition Y" unless that's from approved labeling and even then, this tool doesn't
   generate promotional content). See root
   [CLAUDE.md](../../../CLAUDE.md#4-compliant-language--guardrails).
3. When the underlying data is sparse or below the minimum sample threshold, say so
   explicitly and soften the recommendation to a descriptive observation instead of
   an actionable directive.
4. Keep recommendations actionable and specific (what, where, by when) rather than
   generic ("improve coverage") — but never more specific than the evidence supports.
5. Anything that could affect a rep's compensation, standing, or employment must be
   flagged for mandatory human review in the output itself, not just in a footnote a
   manager might skip (root CLAUDE.md section 6).
6. Route the draft through the qa-test-agent before it's presented as final.
