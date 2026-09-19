"""Rule-based, evidence-tied recommendation text. Deliberately not an LLM call —
this is the compliance-critical path (CLAUDE.md section 4: every claim must
cite the metric/time range/scope it came from; no off-label/promotional
language is possible here because nothing beyond the template is generated).
"""
from __future__ import annotations

import pandas as pd

from analytics.kpi import MIN_REQUIRED_FREQUENCY


def build_recommendation(row: pd.Series, total_ranked: int, period_label: str) -> str:
    """`row` is one row from ranking.rank_reps()["ranked"] or ["insufficient_data"]."""
    if row.get("is_low_confidence"):
        return (
            f"**{row['rep_name']}** ({row['territory_id']}) — insufficient data to rank "
            f"reliably for {period_label}: only {int(row['total_calls'])} calls to "
            f"{int(row['distinct_hcps_called'])} distinct HCPs (minimum sample thresholds "
            f"not met). Showing descriptive metrics only, no rank or recommendation asserted."
        )

    gaps = []
    if pd.notna(row.get("coverage")) and row["coverage"] < 0.7:
        gaps.append(
            f"coverage is {row['coverage']:.0%} (target HCPs reached at ≥{MIN_REQUIRED_FREQUENCY} "
            f"calls/period) — below the 70% healthy-coverage line"
        )
    if pd.notna(row.get("target_attainment")) and row["target_attainment"] < 0.9:
        gaps.append(f"target attainment is {row['target_attainment']:.0%}, trailing plan")
    if pd.notna(row.get("call_productivity")) and row["call_productivity"] < 0.6:
        gaps.append(f"call productivity is {row['call_productivity']:.0%} (share of calls with a qualifying outcome)")

    headline = (
        f"**{row['rep_name']}** ({row['territory_id']}) ranks #{int(row['rank'])} of {total_ranked} "
        f"for {period_label}, score {row['score']:.2f} — "
        f"reach {row['reach']:.0%}, coverage {row['coverage']:.0%}, "
        f"call productivity {row['call_productivity']:.0%}, target attainment {row['target_attainment']:.0%}."
    )

    if gaps:
        return headline + " Gap(s) to review: " + "; ".join(gaps) + "."
    return headline + " No material gaps against the metrics above for this period."
