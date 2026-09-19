import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics.kpi import compute_kpi_table, territory_growth


def make_calls():
    return pd.DataFrame([
        # rep R1: 2 HCPs, one called twice (covered), one called once
        {"rep_id": "R1", "rep_name": "Rep One", "territory_id": "T1", "region": "North",
         "hcp_id": "H1", "product": "P1", "call_date": "2026-01-05",
         "call_outcome": "Completed", "prescription_volume": 10, "target_volume": 20},
        {"rep_id": "R1", "rep_name": "Rep One", "territory_id": "T1", "region": "North",
         "hcp_id": "H1", "product": "P1", "call_date": "2026-01-15",
         "call_outcome": "Sample Drop", "prescription_volume": 5, "target_volume": 20},
        {"rep_id": "R1", "rep_name": "Rep One", "territory_id": "T1", "region": "North",
         "hcp_id": "H2", "product": "P1", "call_date": "2026-01-10",
         "call_outcome": "No Show", "prescription_volume": 0, "target_volume": 20},
    ])


def make_panel():
    return pd.DataFrame([
        {"rep_id": "R1", "rep_name": "Rep One", "territory_id": "T1", "region": "North", "hcp_id": "H1"},
        {"rep_id": "R1", "rep_name": "Rep One", "territory_id": "T1", "region": "North", "hcp_id": "H2"},
        {"rep_id": "R1", "rep_name": "Rep One", "territory_id": "T1", "region": "North", "hcp_id": "H3"},  # never called
    ])


def test_reach_and_frequency():
    calls, panel = make_calls(), make_panel()
    table = compute_kpi_table(calls, panel, ["rep_id", "rep_name", "territory_id", "region"],
                               min_sample_calls=0, min_sample_hcps=0)
    row = table.iloc[0]
    assert row["distinct_hcps_called"] == 2
    assert row["target_hcps"] == 3
    assert row["reach"] == 2 / 3
    assert row["total_calls"] == 3
    assert row["frequency"] == 3 / 2


def test_coverage_requires_min_frequency():
    calls, panel = make_calls(), make_panel()
    table = compute_kpi_table(calls, panel, ["rep_id", "rep_name", "territory_id", "region"],
                               min_required_frequency=2, min_sample_calls=0, min_sample_hcps=0)
    row = table.iloc[0]
    # only H1 was called >= 2 times -> covered_hcps = 1, target_hcps = 3
    assert row["coverage"] == 1 / 3


def test_call_productivity():
    calls, panel = make_calls(), make_panel()
    table = compute_kpi_table(calls, panel, ["rep_id", "rep_name", "territory_id", "region"],
                               min_sample_calls=0, min_sample_hcps=0)
    row = table.iloc[0]
    # 2 of 3 calls (Completed, Sample Drop) are qualifying
    assert row["call_productivity"] == 2 / 3


def test_low_confidence_flag():
    calls, panel = make_calls(), make_panel()
    table = compute_kpi_table(calls, panel, ["rep_id", "rep_name", "territory_id", "region"],
                               min_sample_calls=10, min_sample_hcps=5)
    assert table.iloc[0]["is_low_confidence"] is True or bool(table.iloc[0]["is_low_confidence"])


def test_zero_denominator_does_not_crash():
    empty_calls = pd.DataFrame(columns=[
        "rep_id", "rep_name", "territory_id", "region", "hcp_id", "product",
        "call_date", "call_outcome", "prescription_volume", "target_volume",
    ])
    panel = make_panel()
    table = compute_kpi_table(empty_calls, panel, ["rep_id", "rep_name", "territory_id", "region"])
    assert table.empty


def test_territory_growth():
    df = pd.DataFrame([
        {"territory_id": "T1", "call_date": "2026-01-05", "prescription_volume": 10},
        {"territory_id": "T1", "call_date": "2026-02-05", "prescription_volume": 15},
    ])
    growth = territory_growth(df)
    last = growth.iloc[-1]
    assert last["growth"] == (15 - 10) / 10
