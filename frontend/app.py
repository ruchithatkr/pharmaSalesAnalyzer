"""Streamlit entrypoint — Pharma Sales & Field Force Performance Analyzer.

Build flow: Upload -> call-KPI/coverage analysis -> territory/prescriber
trends -> rep ranking -> recommendations -> chatbot. See root CLAUDE.md for
the governing rules this app must respect (approved metric definitions,
ranking rules, compliant language, data-access boundaries).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from analytics.data_profile import profile_upload
from analytics.kpi import compute_kpi_table
from analytics.trends import prescriber_trend, territory_trend
from backend.chatbot import ask as chatbot_ask
from recommendation.narrative import build_recommendation
from recommendation.ranking import rank_reps

load_dotenv()

# --- dataviz palette (validated default, see .claude/skills — do not reorder) ---
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
STATUS_GOOD = "#0ca30c"
STATUS_CRITICAL = "#d03b3b"
SEQUENTIAL_BLUE = [[0.0, "#cde2fb"], [0.5, "#3987e5"], [1.0, "#104281"]]

ROLE_SCOPE = {
    "Sales Head": "all",
    "Commercial Excellence": "all",
    "Analytics": "all",
    "Regional Manager": "region",
    "Territory Manager": "territory",
    "Field Representative": "territory",
}
# roles allowed to see individual HCP-identifiable trend detail rather than
# an aggregate-only summary (CLAUDE.md section 12 — context isolation)
HCP_DETAIL_ROLES = {"Territory Manager", "Field Representative"}


@st.cache_data
def load_default_data():
    calls = pd.read_csv(ROOT / "sample_data" / "field_force_sample.csv")
    panel = pd.read_csv(ROOT / "sample_data" / "target_panel.csv")
    return calls, panel


def apply_scope(calls: pd.DataFrame, panel: pd.DataFrame, role: str, region: str | None, territory: str | None):
    scope_kind = ROLE_SCOPE[role]
    if scope_kind == "all":
        return calls, panel, "All regions/territories"
    if scope_kind == "region":
        return (
            calls[calls["region"] == region],
            panel[panel["region"] == region],
            f"Region: {region}",
        )
    return (
        calls[calls["territory_id"] == territory],
        panel[panel["territory_id"] == territory],
        f"Territory: {territory}",
    )


def fmt_pct(x):
    return "—" if pd.isna(x) else f"{x:.0%}"


st.set_page_config(page_title="Pharma Sales & Field Force Analyzer", layout="wide")
st.title("Pharma Sales & Field Force Performance Analyzer")

with st.sidebar:
    st.header("Access scope")
    role = st.selectbox("Viewer role", list(ROLE_SCOPE.keys()))

    calls_default, panel_default = load_default_data()
    region = territory = None
    if ROLE_SCOPE[role] == "region":
        region = st.selectbox("Region", sorted(calls_default["region"].unique()))
    elif ROLE_SCOPE[role] == "territory":
        territory = st.selectbox("Territory", sorted(calls_default["territory_id"].unique()))

    st.divider()
    st.header("Data")
    uploaded = st.file_uploader("Upload call/prescription CSV", type="csv")
    st.caption(
        "No file? The bundled synthetic sample dataset is used automatically. "
        "The HCP target panel (call plan) is always the bundled reference file."
    )

calls_raw = pd.read_csv(uploaded) if uploaded is not None else calls_default
panel_raw = panel_default

calls, panel, scope_label = apply_scope(calls_raw, panel_raw, role, region, territory)
st.caption(f"Viewing as **{role}** — scope: **{scope_label}** · {len(calls)} call rows in scope")

tab_quality, tab_kpi, tab_territory, tab_prescriber, tab_ranking, tab_chat = st.tabs(
    ["Data Quality", "Call-KPI & Coverage", "Territory Trends", "Prescriber Trends",
     "Rep Ranking & Recommendations", "Chatbot"]
)

# ---------------------------------------------------------------- Data Quality
with tab_quality:
    st.subheader("Upload validation")
    report = profile_upload(calls_raw, known_territory_ids=set(panel_raw["territory_id"]))
    st.info(report["summary"])
    for check in report["checks"]:
        icon = "✅" if check["passed"] else "🛑"
        color = STATUS_GOOD if check["passed"] else STATUS_CRITICAL
        st.markdown(
            f"{icon} <span style='color:{color}'><b>{check['name']}</b></span> — {check['detail']}",
            unsafe_allow_html=True,
        )

# --------------------------------------------------------------- Call-KPI tab
with tab_kpi:
    st.subheader("Call-KPI & Coverage")
    group_cols = ["rep_id", "rep_name", "territory_id", "region"]
    kpi_table = compute_kpi_table(calls, panel, group_cols)

    if kpi_table.empty:
        st.warning("No call data in the current scope.")
    else:
        agg = kpi_table[~kpi_table["is_low_confidence"]]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Reach", fmt_pct(agg["reach"].mean()) if not agg.empty else "—")
        c2.metric("Frequency", f"{agg['frequency'].mean():.1f}" if not agg.empty else "—")
        c3.metric("Coverage", fmt_pct(agg["coverage"].mean()) if not agg.empty else "—")
        c4.metric("Call Productivity", fmt_pct(agg["call_productivity"].mean()) if not agg.empty else "—")
        c5.metric("Target Attainment", fmt_pct(agg["target_attainment"].mean()) if not agg.empty else "—")
        st.caption("Averages exclude reps flagged low-confidence (below minimum sample thresholds).")

        metrics = ["reach", "frequency_pct", "coverage", "call_productivity", "target_attainment"]
        chart_df = kpi_table.copy()
        chart_df["frequency_pct"] = chart_df["frequency"] / chart_df["frequency"].max() if chart_df["frequency"].max() else 0
        long_df = chart_df.melt(
            id_vars=["rep_name", "is_low_confidence"],
            value_vars=["reach", "coverage", "call_productivity", "target_attainment"],
            var_name="metric", value_name="value",
        )
        fig = px.bar(
            long_df, x="rep_name", y="value", color="metric", barmode="group",
            color_discrete_sequence=CATEGORICAL,
            labels={"value": "", "rep_name": "Rep", "metric": "Metric"},
            title="Reach / Coverage / Call Productivity / Target Attainment by rep",
        )
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)

        display_cols = group_cols + ["total_calls", "distinct_hcps_called", "target_hcps",
                                       "reach", "frequency", "coverage", "call_productivity",
                                       "target_attainment", "is_low_confidence"]
        st.dataframe(kpi_table[display_cols], use_container_width=True)

# ------------------------------------------------------------ Territory Trends
with tab_territory:
    st.subheader("Territory Trends")
    tt = territory_trend(calls)
    if tt.empty:
        st.warning("No call data in the current scope.")
    else:
        territories = sorted(tt["territory_id"].unique())[:8]  # cap categorical series per dataviz guidance
        plot_df = tt[tt["territory_id"].isin(territories)]
        color_map = {t: CATEGORICAL[i % len(CATEGORICAL)] for i, t in enumerate(territories)}
        fig = px.line(
            plot_df, x="period", y="volume", color="territory_id", markers=True,
            color_discrete_map=color_map,
            labels={"volume": "Prescription volume", "period": "Month", "territory_id": "Territory"},
            title="Monthly prescription volume by territory",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(tt, use_container_width=True)

# ----------------------------------------------------------- Prescriber Trends
with tab_prescriber:
    st.subheader("Prescriber (HCP) Trends")
    pt = prescriber_trend(calls)
    if pt.empty:
        st.warning("No call data in the current scope.")
    elif role in HCP_DETAIL_ROLES:
        hcps = sorted(pt["hcp_id"].unique())
        pick = st.multiselect("HCPs", hcps, default=hcps[:5])
        plot_df = pt[pt["hcp_id"].isin(pick)]
        color_map = {h: CATEGORICAL[i % len(CATEGORICAL)] for i, h in enumerate(pick)}
        fig = px.line(
            plot_df, x="period", y="rolling_volume", color="hcp_id", markers=True,
            color_discrete_map=color_map,
            labels={"rolling_volume": "Rolling avg. prescription volume", "period": "Month", "hcp_id": "HCP"},
            title="HCP engagement trend (rolling average)",
        )
        st.plotly_chart(fig, use_container_width=True)
        n_thin = int(pt.groupby("hcp_id")["insufficient_history"].first().sum())
        if n_thin:
            st.caption(f"{n_thin} HCP(s) have fewer than 3 months of history — trend not yet reliable.")
        st.dataframe(pt[pt["hcp_id"].isin(pick)], use_container_width=True)
    else:
        st.info(
            "Your role sees aggregate prescriber-trend insight only — individual HCP identifiers "
            "are withheld outside Territory Manager / Field Representative scope (CLAUDE.md section 12)."
        )
        agg = pt.groupby("period").agg(
            hcps_tracked=("hcp_id", "nunique"),
            avg_rolling_volume=("rolling_volume", "mean"),
        ).reset_index()
        fig = px.line(
            agg, x="period", y="avg_rolling_volume", markers=True,
            color_discrete_sequence=[CATEGORICAL[0]],
            labels={"avg_rolling_volume": "Avg. rolling prescription volume", "period": "Month"},
            title="Aggregate HCP engagement trend (de-identified)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(agg, use_container_width=True)

# ------------------------------------------------------ Ranking & Recommendations
with tab_ranking:
    st.subheader("Rep Ranking & Recommendations")
    group_cols = ["rep_id", "rep_name", "territory_id", "region"]
    kpi_table = compute_kpi_table(calls, panel, group_cols)
    period_label = "current scope/period"

    if kpi_table.empty:
        st.warning("No call data in the current scope.")
    else:
        result = rank_reps(kpi_table)
        ranked, insufficient = result["ranked"], result["insufficient_data"]

        if not ranked.empty:
            fig = px.bar(
                ranked.sort_values("score"), x="score", y="rep_name", orientation="h",
                color="score", color_continuous_scale=SEQUENTIAL_BLUE,
                labels={"score": "Weighted score", "rep_name": "Rep"},
                title="Rep ranking (weighted score — see CLAUDE.md section 3 for formula/tie-break)",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(
                ranked[["rank", "rep_name", "territory_id", "score", "reach", "coverage",
                        "call_productivity", "target_attainment"]],
                use_container_width=True,
            )
            st.markdown("#### Recommendations")
            for _, row in ranked.iterrows():
                st.markdown("- " + build_recommendation(row, len(ranked), period_label))

        if not insufficient.empty:
            st.markdown("#### Insufficient data (not ranked)")
            for _, row in insufficient.iterrows():
                st.markdown("- " + build_recommendation(row, len(ranked), period_label))

        st.caption(
            "Rankings and recommendations are decision support only — any action affecting "
            "compensation, standing, or employment requires manager review (CLAUDE.md section 6)."
        )

# --------------------------------------------------------------------- Chatbot
with tab_chat:
    st.subheader("Chatbot")
    st.caption("Answers are grounded in the computed tables for your current role/scope — nothing else.")

    group_cols = ["rep_id", "rep_name", "territory_id", "region"]
    kpi_table = compute_kpi_table(calls, panel, group_cols)
    result = rank_reps(kpi_table) if not kpi_table.empty else {"ranked": pd.DataFrame(), "insufficient_data": pd.DataFrame()}
    tt = territory_trend(calls)

    context = {
        "kpi_by_rep": kpi_table,
        "ranking": result["ranked"],
        "insufficient_data": result["insufficient_data"],
        "territory_trend": tt,
    }
    if role in HCP_DETAIL_ROLES:
        context["prescriber_trend"] = prescriber_trend(calls)

    question = st.text_input("Ask a question about the current scope's KPIs, trends, or ranking")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            answer = chatbot_ask(question, context, role=role, territory_scope=scope_label)
        st.markdown(answer)
