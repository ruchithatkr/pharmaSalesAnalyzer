# governance

Compliance, access-control, and guardrail configuration.

- Role-based territory/region access policy (Sales Head, Commercial Excellence,
  Regional Manager, Territory Manager, Field Rep, Analytics, Compliance, Brand)
- Audit trail for data access/export actions
- Minimum sample-size thresholds for ranking eligibility
- Off-label/unsupported promotional claim prohibition — enforced as a guardrail on
  any LLM-generated text (recommendation narratives, chatbot responses)
- Evidence-check policy: no recommendation/chatbot response ships without a traceable
  link to the metric(s) it's grounded in

See root [CLAUDE.md](../CLAUDE.md#5-data-access-boundaries) and
[#6-human-in-the-loop](../CLAUDE.md#6-human-in-the-loop).
