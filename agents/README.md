# agents

Orchestration code for the analytical agent pipeline (distinct from the Claude Code
subagent *definitions* in [.claude/agents/](../.claude/agents/) — this folder is the
application-level code that invokes them and wires their outputs together).

Pipeline: Sales Data Profiler → Coverage KPI Agent → Territory Analyst → Prescriber
Trend Agent → Ranking/Recommendation Agent → QA/Test Agent.

- Delegation/orchestration logic: route a request to the KPI, Territory, Prescriber
  Trend, or Ranking/Recommendation agent based on intent
- QA/Test Agent gate: validates calculations and evidence links before an executive
  summary or ranking is presented as final
- Context isolation: each agent receives only the territory/product/time-range slice
  and metric definitions it needs (see root
  [CLAUDE.md](../CLAUDE.md#12-context-isolation))

See root [CLAUDE.md](../CLAUDE.md#11-agent-design) for the full agent design.
