"""Grounded chatbot. Enforces CLAUDE.md's hard rules at the prompt level:
never fabricate a number, never generate off-label/promotional claims, always
disclose sparse/low-confidence data, and only use the role/territory-scoped
context handed to it — never raw HCP-identifiable rows unless explicitly
included by the caller for an authorized role (see CLAUDE.md section 12).
"""
from __future__ import annotations

import os

import pandas as pd

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are a commercial sales-operations assistant for a pharma \
field-force analytics tool. You answer questions ONLY using the KPI/ranking/trend \
tables provided below as context for this turn — never invent a number, rep, \
territory, or trend that isn't in that context.

Hard rules:
1. Never state a KPI, ranking, or trend figure that is not present in the provided \
context. If the answer isn't in the context, say so and suggest what data/filter \
would answer it, rather than guessing.
2. Never generate or imply off-label, unsupported, or promotional claims about any \
product's efficacy or safety. You may discuss call activity and prescribing \
*volume* patterns, never causally link them to a clinical claim.
3. If the context marks a rep/territory/HCP as low-confidence or below the minimum \
sample threshold, disclose that explicitly rather than presenting the number with \
confidence it doesn't have.
4. Every factual claim in your answer should reference the specific metric, time \
period, and territory/rep it came from.
5. You are not authorized to recommend or imply compensation, disciplinary, or \
employment actions — flag that a human manager must make those calls.
6. Stay within the role/territory scope described in the context — do not speculate \
about data outside that scope.
"""


def _context_to_text(context_tables: dict[str, pd.DataFrame]) -> str:
    parts = []
    for name, df in context_tables.items():
        if df is None or df.empty:
            parts.append(f"### {name}\n(no rows in current scope)")
            continue
        parts.append(f"### {name}\n{df.to_csv(index=False)}")
    return "\n\n".join(parts)


def ask(
    question: str,
    context_tables: dict[str, pd.DataFrame],
    role: str,
    territory_scope: str,
) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return (
            "Chatbot is disabled: no ANTHROPIC_API_KEY configured. "
            "Set it in your `.env` file to enable grounded Q&A. "
            "All other tabs (KPIs, trends, ranking) work without it."
        )

    try:
        import anthropic
    except ImportError:
        return "The `anthropic` package is not installed. Run `pip install -r requirements.txt`."

    client = anthropic.Anthropic(api_key=api_key)
    scope_note = f"Current viewer role: {role}. Territory/region scope: {territory_scope}."
    context_text = _context_to_text(context_tables)

    message = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{scope_note}\n\nContext tables (already scoped to this viewer — "
                    f"treat as ground truth, do not extrapolate beyond them):\n\n{context_text}"
                    f"\n\nQuestion: {question}"
                ),
            }
        ],
    )
    return "".join(block.text for block in message.content if block.type == "text")
