"""Transparent, reproducible rep ranking. See CLAUDE.md section 3 — the
formula and every input must be inspectable, ties must break deterministically,
and low-confidence rows must never be ranked at full confidence.
"""
from __future__ import annotations

import pandas as pd

DEFAULT_WEIGHTS = {
    "reach": 0.2,
    "coverage": 0.3,
    "call_productivity": 0.2,
    "target_attainment": 0.3,
}

DEFAULT_TIE_BREAK_KEYS = ["coverage", "target_attainment", "reach"]


def _min_max_normalize(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return series.fillna(0) * 0
    return (series - lo) / (hi - lo)


def rank_reps(
    kpi_table: pd.DataFrame,
    weights: dict[str, float] | None = None,
    tie_break_keys: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Returns {"ranked": df, "insufficient_data": df}.

    `ranked` is sorted by a documented weighted score (metrics min-max
    normalized within the ranked population, then combined per `weights`),
    with ties broken by `tie_break_keys` in order, and rep_id as the final
    deterministic tie-break. Rows flagged `is_low_confidence` are excluded
    from `ranked` and returned separately in `insufficient_data`.
    """
    weights = weights or DEFAULT_WEIGHTS
    tie_break_keys = tie_break_keys or DEFAULT_TIE_BREAK_KEYS

    eligible = kpi_table[~kpi_table["is_low_confidence"]].copy()
    insufficient = kpi_table[kpi_table["is_low_confidence"]].copy()

    if eligible.empty:
        return {"ranked": eligible, "insufficient_data": insufficient}

    score = pd.Series(0.0, index=eligible.index)
    for metric, weight in weights.items():
        score = score + weight * _min_max_normalize(eligible[metric])
    eligible["score"] = score

    sort_cols = ["score"] + tie_break_keys + ["rep_id"]
    sort_ascending = [False] + [False] * len(tie_break_keys) + [True]
    eligible = eligible.sort_values(sort_cols, ascending=sort_ascending).reset_index(drop=True)
    eligible["rank"] = eligible.index + 1

    return {"ranked": eligible, "insufficient_data": insufficient}
