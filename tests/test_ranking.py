import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from recommendation.ranking import rank_reps


def make_kpi_table():
    return pd.DataFrame([
        {"rep_id": "R1", "rep_name": "A", "reach": 0.9, "coverage": 0.8,
         "call_productivity": 0.7, "target_attainment": 0.9, "is_low_confidence": False},
        {"rep_id": "R2", "rep_name": "B", "reach": 0.5, "coverage": 0.5,
         "call_productivity": 0.5, "target_attainment": 0.5, "is_low_confidence": False},
        # tie with R2 on every ranked metric except rep_id -> deterministic tie-break by rep_id
        {"rep_id": "R3", "rep_name": "C", "reach": 0.5, "coverage": 0.5,
         "call_productivity": 0.5, "target_attainment": 0.5, "is_low_confidence": False},
        {"rep_id": "R4", "rep_name": "D", "reach": 0.1, "coverage": 0.1,
         "call_productivity": 0.1, "target_attainment": 0.1, "is_low_confidence": True},
    ])


def test_low_confidence_excluded_from_ranking():
    result = rank_reps(make_kpi_table())
    assert "R4" not in result["ranked"]["rep_id"].tolist()
    assert "R4" in result["insufficient_data"]["rep_id"].tolist()


def test_ranking_order_by_score():
    result = rank_reps(make_kpi_table())
    ranked = result["ranked"]
    assert ranked.iloc[0]["rep_id"] == "R1"  # clearly best on every metric


def test_deterministic_tie_break():
    result = rank_reps(make_kpi_table())
    ranked = result["ranked"]
    tied = ranked[ranked["rep_id"].isin(["R2", "R3"])].sort_values("rank")
    # identical metrics -> tie-break falls through to rep_id ascending
    assert tied.iloc[0]["rep_id"] == "R2"
    assert tied.iloc[1]["rep_id"] == "R3"


def test_rank_is_contiguous_and_reproducible():
    result_a = rank_reps(make_kpi_table())["ranked"]
    result_b = rank_reps(make_kpi_table())["ranked"]
    assert result_a["rep_id"].tolist() == result_b["rep_id"].tolist()
    assert result_a["rank"].tolist() == list(range(1, len(result_a) + 1))
