"""Upload validation — mirrors the sales-data-profiler agent and CLAUDE.md
section 10's hook list. Runs before any KPI is computed. Never silently drops
or "fixes" data; every issue is reported for a human/downstream decision.
"""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "rep_id", "rep_name", "territory_id", "region", "hcp_id", "product",
    "call_date", "call_outcome", "prescription_volume", "target_volume",
]


def profile_upload(calls_df: pd.DataFrame, known_territory_ids: set[str] | None = None) -> dict:
    checks = []

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in calls_df.columns]
    checks.append({
        "name": "Schema: required columns present",
        "passed": not missing_cols,
        "detail": "All required columns present." if not missing_cols
                   else f"Missing columns: {missing_cols}",
    })
    if missing_cols:
        return {
            "checks": checks,
            "recommendation": "block",
            "summary": "Upload is missing required columns — cannot proceed.",
        }

    dupe_mask = calls_df.duplicated(
        subset=["rep_id", "hcp_id", "product", "call_date", "call_outcome"], keep=False
    )
    n_dupes = int(dupe_mask.sum())
    checks.append({
        "name": "Duplicate call records",
        "passed": n_dupes == 0,
        "detail": "No duplicate call rows found." if n_dupes == 0
                   else f"{n_dupes} rows appear to be exact-duplicate calls (same rep/HCP/product/date/outcome).",
    })

    missing_target = calls_df["target_volume"].isna() | (calls_df["target_volume"] <= 0)
    n_missing_target = int(missing_target.sum())
    checks.append({
        "name": "Missing or zero targets",
        "passed": n_missing_target == 0,
        "detail": "All rows have a positive target." if n_missing_target == 0
                   else f"{n_missing_target} rows have a missing or zero target_volume.",
    })

    if known_territory_ids:
        bad_codes = sorted(set(calls_df["territory_id"].dropna().unique()) - set(known_territory_ids))
    else:
        bad_codes = []
    checks.append({
        "name": "Inconsistent territory codes",
        "passed": not bad_codes,
        "detail": "All territory codes recognized." if not bad_codes
                   else f"Unrecognized territory codes: {bad_codes}",
    })

    calls_per_rep = calls_df.groupby("rep_id").size()
    sparse_reps = calls_per_rep[calls_per_rep < 10].index.tolist()
    checks.append({
        "name": "Sparse-sample reps",
        "passed": not sparse_reps,
        "detail": "No reps below the minimum call-volume threshold." if not sparse_reps
                   else f"Reps with fewer than 10 calls in range (low-confidence for ranking): {sparse_reps}",
    })

    hard_failures = [c for c in checks if not c["passed"] and c["name"] in
                      ("Schema: required columns present",)]
    soft_failures = [c for c in checks if not c["passed"] and c not in hard_failures]

    if hard_failures:
        recommendation = "block"
        summary = "Upload blocked — fix schema issues before proceeding."
    elif soft_failures:
        recommendation = "proceed_with_exclusions"
        summary = (
            f"Upload usable with {len(soft_failures)} flagged issue(s) — affected rows/reps should be "
            "excluded or treated as low-confidence rather than taken at face value."
        )
    else:
        recommendation = "proceed"
        summary = "No data-quality issues found."

    return {"checks": checks, "recommendation": recommendation, "summary": summary}
