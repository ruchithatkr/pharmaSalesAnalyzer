# frontend

Dashboard UI and chatbot interface for the Pharma Sales & Field Force Performance
Analyzer.

- Upload flow for rep call/prescription data (CSV/XLSX)
- KPI and coverage dashboards (reach, frequency, coverage, productivity, attainment)
- Territory/prescriber trend views
- Rep ranking views (with evidence/inputs visible, not just the score)
- Chatbot panel — answers must render the underlying metric/time range/territory the
  answer is grounded in

Role-based views: what a user sees is scoped to their authorized territory/region per
[governance/](../governance/) RBAC policy. See root [CLAUDE.md](../CLAUDE.md) for
approved metric definitions and compliant-language rules that apply to any rendered
chatbot/recommendation text.
