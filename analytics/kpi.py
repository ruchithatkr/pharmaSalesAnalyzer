"""Canonical KPI formulas. Definitions must match CLAUDE.md section 2 exactly —
this module is the single source of truth; no other code should recompute or
restate these numbers independently.

All functions are pure (no I/O) and operate on already-validated/normalized
call-level DataFrames with columns:
  rep_id, rep_name, territory_id, region, hcp_id, product, call_date,
  call_outcome, prescription_volume, target_volume

`target_df` (the assigned HCP panel / call plan) has columns:
  rep_id, territory_id, region, hcp_id
"""
from __future__ import annotations

import pandas as pd

QUALIFYING_OUTCOMES = {"Completed", "Sample Drop", "Discussion Completed"}

MIN_SAMPLE_CALLS = 10
MIN_SAMPLE_HCPS = 5
MIN_REQUIRED_FREQUENCY = 2  # calls/HCP/period required to count as "covered"


def _panel_size(target_df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    return (
        target_df.groupby(group_cols)["hcp_id"]
        .nunique()
        .rename("target_hcps")
        .reset_index()
    )


def compute_kpi_table(
    calls_df: pd.DataFrame,
    target_df: pd.DataFrame,
    group_cols: list[str],
    min_sample_calls: int = MIN_SAMPLE_CALLS,
    min_sample_hcps: int = MIN_SAMPLE_HCPS,
    min_required_frequency: int = MIN_REQUIRED_FREQUENCY,
) -> pd.DataFrame:
    """One row per group (e.g. per rep, or per territory) with every approved KPI.

    Reach            = distinct HCPs called / distinct HCPs in target panel
    Frequency        = total calls / distinct HCPs reached
    Coverage         = target HCPs reached >= min_required_frequency / total target HCPs
    Call Productivity = calls with a qualifying outcome / total calls
    Target Attainment = actual prescription volume / target volume
    """
    if calls_df.empty:
        return pd.DataFrame(columns=group_cols + [
            "total_calls", "distinct_hcps_called", "target_hcps", "reach",
            "frequency", "coverage", "call_productivity", "target_attainment",
            "is_low_confidence",
        ])

    total_calls = calls_df.groupby(group_cols).size().rename("total_calls")

    distinct_hcps_called = (
        calls_df.groupby(group_cols)["hcp_id"].nunique().rename("distinct_hcps_called")
    )

    qualifying_calls = (
        calls_df.assign(is_qualifying=calls_df["call_outcome"].isin(QUALIFYING_OUTCOMES))
        .groupby(group_cols)["is_qualifying"]
        .sum()
        .rename("qualifying_calls")
    )

    calls_per_hcp = (
        calls_df.groupby(group_cols + ["hcp_id"]).size().rename("calls").reset_index()
    )
    covered_hcps = (
        calls_per_hcp[calls_per_hcp["calls"] >= min_required_frequency]
        .groupby(group_cols)["hcp_id"]
        .nunique()
        .rename("covered_hcps")
    )

    actual_volume = calls_df.groupby(group_cols)["prescription_volume"].sum().rename("actual_volume")

    # target_volume is a single figure per group per period (repeated across
    # every row in that period) — take one value per period, then sum across
    # periods present in scope, so it's comparable to actual_volume summed
    # over the same periods.
    period_df = calls_df.copy()
    period_df["_period"] = pd.to_datetime(period_df["call_date"]).dt.to_period("M")
    target_volume = (
        period_df.groupby(group_cols + ["_period"])["target_volume"].first()
        .groupby(level=list(range(len(group_cols))))
        .sum()
        .rename("target_total")
    )

    panel = _panel_size(target_df, group_cols)

    table = (
        total_calls.to_frame()
        .join(distinct_hcps_called)
        .join(qualifying_calls)
        .join(covered_hcps)
        .join(actual_volume)
        .join(target_volume)
        .reset_index()
        .merge(panel, on=group_cols, how="left")
    )

    table["covered_hcps"] = table["covered_hcps"].fillna(0)
    table["target_hcps"] = table["target_hcps"].fillna(0)

    table["reach"] = (table["distinct_hcps_called"] / table["target_hcps"]).where(table["target_hcps"] > 0)
    table["frequency"] = (table["total_calls"] / table["distinct_hcps_called"]).where(table["distinct_hcps_called"] > 0)
    table["coverage"] = (table["covered_hcps"] / table["target_hcps"]).where(table["target_hcps"] > 0)
    table["call_productivity"] = (table["qualifying_calls"] / table["total_calls"]).where(table["total_calls"] > 0)
    table["target_attainment"] = (table["actual_volume"] / table["target_total"]).where(table["target_total"] > 0)

    table["is_low_confidence"] = (
        (table["total_calls"] < min_sample_calls) | (table["distinct_hcps_called"] < min_sample_hcps)
    )

    return table.drop(columns=["qualifying_calls", "covered_hcps", "target_total"])


def territory_growth(calls_df: pd.DataFrame, period: str = "M") -> pd.DataFrame:
    """(current period volume - prior period volume) / prior period volume, per territory."""
    df = calls_df.copy()
    df["period"] = pd.to_datetime(df["call_date"]).dt.to_period(period)
    by_period = (
        df.groupby(["territory_id", "period"])["prescription_volume"].sum().reset_index()
        .sort_values(["territory_id", "period"])
    )
    by_period["prior_volume"] = by_period.groupby("territory_id")["prescription_volume"].shift(1)
    by_period["growth"] = (
        (by_period["prescription_volume"] - by_period["prior_volume"]) / by_period["prior_volume"]
    ).where(by_period["prior_volume"] > 0)
    return by_period
