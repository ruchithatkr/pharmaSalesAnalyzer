# evals

Golden dataset and LLM/agent/RAG evaluation harnesses.

- Synthetic sales records with known-correct KPIs/rankings for regression testing
- Reconciliation accuracy measurement (computed vs. expected aggregates)
- Recommendation relevance/compliance scoring (evidence-linked, no off-label claims)
- Agent task completion and latency measurement across the pipeline
- Security/red-team scenarios: HCP-data extraction attempts, unauthorized territory
  access, ranking manipulation, off-label prompt injection, unsupported-claim
  elicitation, tool misuse

Run as part of continuous evaluation on each release — see
[deployment/](../deployment/).
