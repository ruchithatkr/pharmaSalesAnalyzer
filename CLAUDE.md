# Pharma Sales & Field Force Performance Analyzer

## Style
Commercial / Sales Operations analytics application.

## Build Flow
Upload rep call/prescription data → call-KPI and coverage analysis → territory/prescriber trends → rep ranking → recommendations → chatbot.

## Problem Statement
Commercial teams need consolidated, fair, and compliant insight into field-force
effectiveness, HCP (Health Care Provider) coverage, territory trends, and actionable
performance gaps.

## Users & Stakeholders
Sales Head, Commercial Excellence, Regional Managers, Territory Managers, Field
Representatives, Analytics, Compliance, and Brand Teams.

## Business KPIs / Success Metrics
Reach, frequency, coverage, call productivity, target attainment, territory growth,
HCP engagement trends, recommendation adoption, and time saved.

---

## 1. Scope

This repo implements a deterministic-analytics-first sales operations tool. LLM use
is limited to explanation, summarization, and recommendation drafting — **never** as
the source of truth for a KPI, ranking, or clinical/product claim.

**In scope:** call/prescription data ingestion, KPI computation, territory and HCP
trend analysis, rep ranking, recommendation generation, and a chatbot that answers
questions grounded in computed metrics.

**Out of scope:** clinical decision support, patient-level data, off-label or
unsupported product/promotional claims, and any output that determines compensation,
termination, or disciplinary action without human review.

## 2. Approved Metrics (canonical definitions)

All agents, tools, and the chatbot must use these definitions — do not let an LLM
invent an alternate formula.

| Metric | Definition |
|---|---|
| **Reach** | Distinct HCPs called ÷ Distinct HCPs in target list, per period/territory |
| **Frequency** | Total calls ÷ Distinct HCPs reached, per period |
| **Coverage** | Target HCPs reached at or above the minimum required frequency ÷ Total target HCPs |
| **Call Productivity** | Calls resulting in a qualifying outcome (e.g., sample drop, discussion completed) ÷ Total calls |
| **Target Attainment** | Actual volume/value ÷ Target volume/value, per rep/territory/product |
| **Territory Growth** | (Current period volume − Prior period volume) ÷ Prior period volume |
| **HCP Engagement Trend** | Rolling trend of an HCP's call responsiveness and prescription behavior over time |

Any new metric must be added here with a definition and owner (Commercial Excellence)
before agents or dashboards may reference it.

## 3. Ranking Rules

- Rankings must be **transparent and reproducible**: the formula and inputs used for
  any rep/territory rank must be inspectable, not a black-box LLM judgment.
- **Minimum sample thresholds** apply — a rep/territory with insufficient call volume
  or HCP count must be flagged as "insufficient data" rather than ranked outright, or
  ranked in a clearly separated low-confidence tier.
- **Tie handling** must use a documented, deterministic rule (e.g., secondary sort key
  such as coverage, then attainment); never break ties arbitrarily or via LLM
  discretion.
- Rankings must exclude factors correlated with protected characteristics or
  territory assignment inequities (e.g., legacy territory size/potential) unless
  explicitly normalized for.
- Every ranking output must carry the inputs/evidence used, so a manager can audit
  *why* a rep ranked where they did.

## 4. Compliant Language & Guardrails

- **No off-label or unsupported promotional claims** — the assistant must never
  generate, suggest, or imply drug efficacy/safety claims outside approved labeling.
- Chatbot and recommendation text must be **evidence-tied**: every claim must cite the
  underlying computed metric/time range/territory it came from. If the assistant
  cannot ground a statement in computed data, it must say so rather than infer.
  Statements should read as "descriptive analytics with recommendations," not medical
  or promotional advice.
  When data is sparse or a metric is below the minimum sample threshold, the assistant
  discloses this explicitly and falls back to descriptive statements only — no
  ranking or recommendation is asserted with confidence it doesn't have.
- No agent or skill may generate content intended for external/patient/HCP-facing
  distribution — outputs are for internal commercial team use only.

## 5. Data Access Boundaries

- **Role-based territory access**: Territory Managers and Reps see only their own
  territory/team; Regional Managers see their region; Sales Head/Commercial
  Excellence/Analytics may see cross-region aggregates per their role.
- Individual HCP-identifiable data must be excluded from any context/prompt that only
  requires aggregate insights (see Context Isolation, section 12 in the design notes
  below).
- All data access and export actions are logged to an audit trail (who, what
  territory/product/time range, when).
- HCP and rep personal data handling must follow applicable privacy regulation (e.g.,
  HIPAA-adjacent sensitivity for prescriber data, local data protection law) —
  treat prescriber and rep-identifiable records as sensitive by default.

## 6. Human-in-the-Loop

Human review is **mandatory** wherever an output could materially affect:
- patient safety
- regulatory/compliance standing
- product release or pricing
- a rep's compensation, standing, or employment

Rankings and recommendations are decision *support*, not decision *automation*.
Managers review before any consequential action is taken.

## 7. Architecture

```
CRM/files → validation & normalization → KPI engine → territory/HCP analytics
          → ranking/recommendation engine → Claude assistant → dashboard/chat
```

- Deterministic analytics compute all KPIs, coverage, and ranking scores.
- ML is used only where prediction is justified (e.g., HCP engagement trend
  forecasting) — not as a substitute for the deterministic KPI engine.
- LLM (Claude) usage is limited to: explaining computed results, drafting
  recommendation narratives, and answering chatbot questions — always grounded in
  tool output, never inventing figures.
- Avoid unnecessary multi-agent complexity — use the smallest number of agents that
  cleanly separates concerns (see `.claude/agents/`).

## 8. Repository Structure

| Folder | Purpose |
|---|---|
| [frontend/](frontend/) | Dashboard UI and chatbot interface |
| [backend/](backend/) | API layer, request routing, auth/RBAC enforcement |
| [analytics/](analytics/) | KPI engine, coverage/reach/frequency calculations, aggregation |
| [recommendation/](recommendation/) | Ranking logic, tie-handling, recommendation generation |
| [agents/](agents/) | Agent orchestration code (profiler, KPI, territory, trend, ranking, QA) |
| [governance/](governance/) | RBAC policy, audit logging, compliance/guardrail configuration |
| [tests/](tests/) | Unit and integration tests |
| [evals/](evals/) | Golden datasets and LLM/agent evaluation harnesses |
| [deployment/](deployment/) | CI/CD, environment configuration, deployment manifests |
| [monitoring/](monitoring/) | Observability: traces, metrics, feedback capture |
| [.claude/agents/](.claude/agents/) | Claude Code subagent definitions for this project |
| [.claude/skills/](.claude/skills/) | Claude Code skills for KPI design, coverage, segmentation, trends, recommendations |

Standard Git workflow: feature branches off `main`, PR review before merge, no direct
pushes to `main` for anything beyond initial scaffolding.

## 9. Skills

Defined under `.claude/skills/`:
- **sales-kpi-design** — designing/validating reach, frequency, coverage, and
  attainment calculations
- **coverage-analysis** — HCP coverage and call-plan-vs-actual analysis
- **territory-segmentation** — territory comparison, segmentation, and growth analysis
- **prescriber-trends** — HCP-level engagement and prescription trend analysis
- **recommendation-writing** — compliant, evidence-tied recommendation drafting

## 10. Hooks / Validation Gates

These are process gates the pipeline must enforce before analytics/rankings are
produced (implemented in `analytics/` and `governance/`, not necessarily Claude Code
hooks):
1. **Upload validation** — schema check on rep/HCP/territory/product/date/outcome/
   volume/target fields.
2. **HCP/territory normalization** — canonicalize IDs, names, and codes; flag
   inconsistent territory codes.
3. **Duplicate-call check** — detect and deduplicate repeated call records.
4. **Aggregation reconciliation** — recomputed aggregates must reconcile against
   source-level sums before being surfaced.
5. **Tie handling** — deterministic secondary-sort rule applied consistently.
6. **Evidence check** — no chatbot/recommendation response ships without a traceable
   link to the metric(s) it's grounded in.

## 11. Agent Design

Defined under `.claude/agents/`:
1. **Sales Data Profiler** — profiles uploaded data, flags quality issues (duplicates,
   missing targets, inconsistent codes, sparse samples).
2. **Coverage KPI Agent** — computes reach/frequency/coverage/productivity/attainment.
3. **Territory Analyst** — compares territories, computes growth, surfaces trends.
4. **Prescriber Trend Agent** — analyzes HCP-level engagement/prescription trends
   (aggregate only, no patient data).
5. **Ranking/Recommendation Agent** — produces transparent rep/territory rankings and
   compliant recommendation narratives.
6. **QA/Test Agent** — validates calculations, reconciliation, and evidence links
   before any executive summary is finalized.

## 12. Context Isolation

- Managers/agents are limited to their authorized territories/products; cross-territory
  aggregation is only exposed to roles authorized for it.
- Individual HCP-identifiable data is excluded from any agent context that only
  requires aggregate insight (e.g., Territory Analyst gets aggregates, not raw HCP
  rows, unless the task specifically requires HCP-level trend analysis).

## 13. Delegation / Orchestration

Requests route to the KPI, Territory, Prescriber Trend, or Ranking/Recommendation
agent based on intent. The QA/Test Agent validates calculations and evidence before
any executive summary or ranking is presented as final.

## 14. Context Engineering & Memory

Provide agents only: the relevant territory/product/time-range slice, the approved
metric definitions (section 2), a summary of prior analytical steps in the session,
and the specific tool outputs needed for the current question — not the full raw
dataset or unrelated territories.

## 15. Tools

CSV/XLSX parsers, Pandas-based analytics, charting, SQL/CRM API access, code review
tooling, and optional enterprise BI integration.

## 16–18. RAG / MCP / Custom MCP

Architecture decisions, not mandatory features:
- **RAG** — optional, for commercial policy docs, approved product information, and
  field-force SOPs; not needed for purely numerical dashboard analysis.
- **MCP** — use only when a governed connection to CRM, data warehouse, document
  repository, or workflow system is required.
- **Custom MCP** — optional "Commercial Analytics MCP" for reusable, governed access
  to approved KPI data/services across multiple agents/apps.

## 19–21. Testing & Evaluation

- **Unit/integration** (`tests/`): reach/frequency/coverage formulas, filters,
  aggregations, rankings, tie handling, recommendations, role restrictions, file
  ingestion, chatbot evidence-linking.
- **Golden dataset / eval** (`evals/`): synthetic sales records with known-correct
  KPIs/rankings; measure reconciliation accuracy, recommendation relevance/compliance,
  agent task completion, and latency.
- **Security / red-team**: attempt HCP-data extraction, unauthorized territory
  access, ranking manipulation, off-label prompt injection, unsupported claims, and
  tool misuse. Track results in `evals/`.

## 22–24. Observability, Load & Cost

Capture (in `monitoring/`): data-processing events, KPI outputs, recommendation
evidence, agent/tool traces, token usage, latency, errors, and user feedback. Load-test
with large field-force datasets and concurrent regional users; track model usage cost
per analytical session.

## 25. Fallbacks

Recommendations must disclose missing/sparse data and fall back to descriptive
analytics (no ranking/recommendation asserted) when confidence is insufficient.

## 26–29. Pilot, Deployment, Monitoring, Improvement

Pilot with one brand/region against existing commercial reports, with manager/
compliance sign-off before wider rollout. Deploy to an approved commercial analytics
environment with enterprise auth, auditability, and secure data access. Track data
freshness, ranking stability, recommendation usefulness, compliance exceptions,
adoption, and feedback; improve segmentation/prompts/recommendation logic/UX based on
measured outcomes.

---

## Hard Rules for Any Agent Working in This Repo

1. Never fabricate a KPI, ranking, or trend number — always compute or call the tool
   that computes it.
2. Never generate off-label, unsupported, or promotional product claims.
3. Never expose HCP- or rep-identifiable data outside its authorized role/context.
4. Never let an LLM override a deterministic ranking/tie-handling rule.
5. Always disclose when data is sparse/below threshold rather than presenting false
   confidence.
6. Flag any output that could affect compensation, employment, pricing, or regulatory
   standing for mandatory human review before use.
