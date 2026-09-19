# backend

API layer for the Pharma Sales & Field Force Performance Analyzer.

- Ingest endpoints for uploaded call/prescription/CRM data
- Request routing to [analytics/](../analytics/), [recommendation/](../recommendation/),
  and [agents/](../agents/)
- RBAC enforcement (territory/region scoping) delegated to
  [governance/](../governance/) policy
- Audit logging of data access/export actions

All KPI/ranking values returned by the API must originate from the deterministic
analytics engine — the backend must never let an LLM call substitute for a computed
value. See root [CLAUDE.md](../CLAUDE.md).
