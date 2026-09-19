"""Territory and prescriber (HCP) trend analysis, built on top of already
validated call data. See CLAUDE.md sections 2 (metric definitions) and 12
(context isolation — HCP-level output here should only reach roles authorized
for it).
"""
from __future__ import annotations

import pandas as pd

MIN_TREND_POINTS = 3


def territory_trend(calls_df: pd.DataFrame, period: str = "M") -> pd.DataFrame:
    """Monthly volume and call count per territory, for a trend line chart."""
    df = calls_df.copy()
    df["period"] = pd.to_datetime(df["call_date"]).dt.to_period(period).astype(str)
    out = (
        df.groupby(["territory_id", "region", "period"])
        .agg(total_calls=("hcp_id", "size"), volume=("prescription_volume", "sum"))
        .reset_index()
        .sort_values(["territory_id", "period"])
    )
    out["prior_volume"] = out.groupby("territory_id")["volume"].shift(1)
    out["growth"] = (
        (out["volume"] - out["prior_volume"]) / out["prior_volume"]
    ).where(out["prior_volume"] > 0)
    return out


def prescriber_trend(calls_df: pd.DataFrame, period: str = "M", window: int = MIN_TREND_POINTS) -> pd.DataFrame:
    """Rolling HCP-level engagement trend: call count and prescription volume
    per HCP per period, with a flag when an HCP has fewer than `window` periods
    of data (too little history for a reliable trend read).
    """
    df = calls_df.copy()
    df["period"] = pd.to_datetime(df["call_date"]).dt.to_period(period).astype(str)
    by_hcp_period = (
        df.groupby(["hcp_id", "territory_id", "period"])
        .agg(calls=("call_date", "size"), volume=("prescription_volume", "sum"))
        .reset_index()
        .sort_values(["hcp_id", "period"])
    )
    n_periods = by_hcp_period.groupby("hcp_id")["period"].transform("nunique")
    by_hcp_period["insufficient_history"] = n_periods < window
    by_hcp_period["rolling_volume"] = (
        by_hcp_period.groupby("hcp_id")["volume"]
        .transform(lambda s: s.rolling(window, min_periods=1).mean())
    )
    return by_hcp_period
