# Pharma Sales & Field Force Performance Analyzer

Working prototype. See [CLAUDE.md](CLAUDE.md) for the full scope, approved KPI
definitions, ranking rules, and governance this app follows.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # optional — only needed for the Chatbot tab
# edit .env and set ANTHROPIC_API_KEY=...
```

The bundled synthetic sample dataset already exists at
`sample_data/field_force_sample.csv` / `sample_data/target_panel.csv`. To
regenerate it (e.g. after changing the generator):

```bash
python sample_data/generate_sample.py
```

## Run

```bash
streamlit run frontend/app.py
```

Opens in your browser. Pick a viewer role in the sidebar (simulates
role-based territory access — see CLAUDE.md section 5), optionally upload
your own call/prescription CSV (falls back to the bundled sample data if you
don't), and walk through the tabs in build-flow order: Data Quality →
Call-KPI & Coverage → Territory Trends → Prescriber Trends → Rep Ranking &
Recommendations → Chatbot.

The Chatbot tab works without `ANTHROPIC_API_KEY` set — it just tells you
it's disabled instead of failing. Every other tab works with no API key.

## Test

```bash
pytest tests/
```

## Known gaps in this prototype (see CLAUDE.md for the target state)

- RBAC is simulated via a sidebar role selector, not enforced by a real
  authentication/authorization layer — fine for local exploration, not for
  production use.
- No deployment yet — this runs locally only. See CLAUDE.md sections 26-27
  for the intended pilot/production rollout path.
- The `.claude/agents/` subagents describe how a Claude Code session should
  work on *this repository*; the running app itself implements the
  analytics/ranking/chatbot logic directly rather than invoking them at
  runtime.
