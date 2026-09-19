# recommendation

Ranking and recommendation engine.

- Rep/territory ranking using transparent, reproducible scoring (inputs from
  [analytics/](../analytics/))
- Deterministic tie-handling rule (documented secondary sort key, never LLM
  discretion)
- Minimum-sample-threshold enforcement — insufficient-data reps/territories are
  flagged or tiered separately, not silently ranked
- Recommendation narrative generation: evidence-tied to the underlying metrics, no
  off-label/unsupported promotional language

See root [CLAUDE.md](../CLAUDE.md#3-ranking-rules) for ranking rules and
[#4-compliant-language--guardrails](../CLAUDE.md#4-compliant-language--guardrails)
for language constraints. Any output that could affect compensation or employment
decisions requires human review before use.
