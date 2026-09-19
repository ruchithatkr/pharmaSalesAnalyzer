"""Generates synthetic demo data for the Pharma Sales & Field Force Analyzer.

Produces two files (no real HCP/rep data — purely synthetic, fixed seed for
reproducibility):
  - field_force_sample.csv : actual call/prescription records
  - target_panel.csv       : each rep's assigned HCP call-plan panel (the
                              "target list" reach/coverage are measured against)

Run: python sample_data/generate_sample.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

REGIONS = ["North", "South", "East", "West"]
TERRITORIES_PER_REGION = 3
PRODUCTS = ["Cardiavex", "Glucanorm", "Respiraline"]
OUTCOMES = ["Completed", "Sample Drop", "Discussion Completed", "No Show", "Rescheduled"]
QUALIFYING_OUTCOMES = {"Completed", "Sample Drop", "Discussion Completed"}

MONTHS = [date(2026, m, 1) for m in range(3, 9)]  # Mar-Aug 2026

FIRST_NAMES = ["Alex", "Jordan", "Priya", "Sam", "Morgan", "Taylor", "Chris",
               "Riley", "Nina", "Omar", "Lee", "Dana"]
LAST_NAMES = ["Reed", "Kapoor", "Chen", "Ortiz", "Novak", "Singh", "Brooks",
              "Fischer", "Adeyemi", "Cole", "Park", "Hughes"]


def build_reps():
    reps = []
    rep_idx = 1
    for region in REGIONS:
        for t in range(1, TERRITORIES_PER_REGION + 1):
            territory_id = f"{region[0]}{t:02d}"
            reps.append({
                "rep_id": f"R{rep_idx:03d}",
                "rep_name": f"{FIRST_NAMES[rep_idx - 1]} {LAST_NAMES[rep_idx - 1]}",
                "territory_id": territory_id,
                "region": region,
            })
            rep_idx += 1
    return reps


def build_panel(reps):
    rows = []
    for i, rep in enumerate(reps):
        # one rep (R012) gets an intentionally tiny panel -> low-confidence demo case
        panel_size = 6 if rep["rep_id"] == "R012" else random.randint(28, 45)
        for h in range(1, panel_size + 1):
            rows.append({
                **rep,
                "hcp_id": f"H-{rep['territory_id']}-{h:03d}",
            })
    return pd.DataFrame(rows)


def build_calls(panel_df):
    rows = []
    rep_ids = panel_df["rep_id"].unique()

    # per-rep "skill" multiplier drives call volume, outcome quality, and prescription volume
    rep_skill = {rid: random.uniform(0.55, 1.25) for rid in rep_ids}
    # independent "how generous was the target-setting" factor per rep, so
    # attainment isn't trivially ~100% for everyone and isn't driven by the
    # same skill draw that produced the actual volume
    rep_target_factor = {rid: random.uniform(0.75, 1.25) for rid in rep_ids}

    for rep_id, rep_panel in panel_df.groupby("rep_id"):
        rep_row = rep_panel.iloc[0]
        skill = rep_skill[rep_id]
        hcp_ids = rep_panel["hcp_id"].tolist()

        for month_idx, month in enumerate(MONTHS):
            # growth drift: skilled reps trend up slightly over the 6 months
            month_growth = 1 + (month_idx * 0.03 * (skill - 0.8))

            # rep R012 has almost no calls -> sparse-sample demo case
            if rep_id == "R012":
                n_calls_this_month = random.randint(0, 2)
            else:
                # not every panel HCP gets called every month
                coverage_fraction = min(0.95, skill * random.uniform(0.5, 0.9))
                n_calls_this_month = int(len(hcp_ids) * coverage_fraction)

            called_hcps = random.sample(hcp_ids, k=min(n_calls_this_month, len(hcp_ids)))

            month_calls = []
            for hcp_id in called_hcps:
                # some HCPs get multiple touches in the month
                touches = 1 if random.random() > 0.35 else 2
                for _ in range(touches):
                    call_day = random.randint(1, 27)
                    call_date = month + timedelta(days=call_day - 1)
                    outcome_roll = random.random()
                    if outcome_roll < 0.55 * skill:
                        outcome = random.choice(["Completed", "Sample Drop", "Discussion Completed"])
                    elif outcome_roll < 0.8:
                        outcome = "Rescheduled"
                    else:
                        outcome = "No Show"

                    product = random.choice(PRODUCTS)
                    base_volume = random.uniform(4, 20) * skill * month_growth
                    prescription_volume = round(base_volume if outcome in QUALIFYING_OUTCOMES else base_volume * 0.3, 1)

                    month_calls.append({
                        "rep_id": rep_row["rep_id"],
                        "rep_name": rep_row["rep_name"],
                        "territory_id": rep_row["territory_id"],
                        "region": rep_row["region"],
                        "hcp_id": hcp_id,
                        "product": product,
                        "call_date": call_date.isoformat(),
                        "call_outcome": outcome,
                        "prescription_volume": prescription_volume,
                    })

            # target is a single monthly figure for the rep, set commensurate
            # with the volume actually achievable this month (independent
            # target_factor + small jitter) — NOT a flat per-call constant,
            # so it's directly comparable to the summed actual volume.
            month_actual_total = sum(c["prescription_volume"] for c in month_calls)
            target_volume = round(
                max(month_actual_total, 1) * rep_target_factor[rep_id] * random.uniform(0.95, 1.05), 1
            )
            for c in month_calls:
                c["target_volume"] = target_volume
            rows.extend(month_calls)

    calls_df = pd.DataFrame(rows)

    # inject a handful of exact-duplicate rows and one bad territory code,
    # so the Data Quality tab has something real to flag
    dupes = calls_df.sample(n=6, random_state=7)
    calls_df = pd.concat([calls_df, dupes], ignore_index=True)
    bad_code_idx = calls_df.sample(n=3, random_state=11).index
    calls_df.loc[bad_code_idx, "territory_id"] = "UNK"

    return calls_df.sort_values(["call_date", "rep_id"]).reset_index(drop=True)


def main():
    out_dir = Path(__file__).parent
    reps = build_reps()
    panel_df = build_panel(reps)
    calls_df = build_calls(panel_df)

    panel_df.to_csv(out_dir / "target_panel.csv", index=False)
    calls_df.to_csv(out_dir / "field_force_sample.csv", index=False)
    print(f"Wrote {len(panel_df)} panel rows -> target_panel.csv")
    print(f"Wrote {len(calls_df)} call rows -> field_force_sample.csv")


if __name__ == "__main__":
    main()
