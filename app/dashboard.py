"""
Streamlit dashboard for the SEC Risk Language vs. Volatility project.
Loads pre-computed results, no live scraping or model fitting happens here.
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Risk Language & Volatility", layout="wide")

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

try:
    comparisons = pd.read_csv(DATA_DIR / "dashboard_risk_volatility.csv")
    trajectory = pd.read_csv(DATA_DIR / "dashboard_company_trajectory.csv")
    with open(DATA_DIR / "dashboard_summary.json") as f:
        summary = json.load(f)
except FileNotFoundError as e:
    st.error(f"Could not find data files: {e}")
    st.stop()

# ---- Header ----
st.title("Does Risk Disclosure Language Predict Stock Volatility?")
st.markdown(
    "Testing whether changes in how retailers describe risk in their annual "
    "10-K filings predict how volatile their stock becomes afterward, using "
    "real filings pulled directly from SEC EDGAR."
)

# ---- Headline metrics ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("Companies Analyzed", summary["n_companies"])
col2.metric("Year-over-Year Comparisons", summary["n_comparisons"])
col3.metric("Correlation (word count)", f"{summary['correlation_word_count']:.3f}")
col4.metric("Statistical Significance", f"p = {summary['p_value']:.3f}")

st.divider()

# ---- Main scatter plot ----
st.subheader("Risk Language Change vs. Excess Volatility")

fig = px.scatter(
    comparisons,
    x="word_count_change_pct",
    y="excess_volatility",
    hover_data=["ticker", "year_from", "year_to"],
    labels={
        "word_count_change_pct": "Risk Section Word Count Change (%)",
        "excess_volatility": "Excess Volatility (company minus market)",
    },
    trendline="ols",
)
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(height=450)
st.plotly_chart(fig, width='stretch')

st.markdown(
    f"There's a **statistically significant but modest** relationship "
    f"(r = {summary['correlation_word_count']:.2f}, "
    f"R² = {summary['r_squared']:.3f}, p = {summary['p_value']:.3f}, "
    f"n = {summary['n_comparisons']}). Word count change explains roughly "
    f"{summary['r_squared']*100:.1f}% of the variation in excess volatility — "
    f"real, but not something to trade on alone."
)

st.divider()

# ---- Company explorer ----
st.subheader("Explore a Company's Risk Language & Volatility Over Time")

selected_ticker = st.selectbox("Choose a company", sorted(trajectory["ticker"].unique()))
company_data = trajectory[trajectory["ticker"] == selected_ticker].sort_values("filing_year")

col1, col2 = st.columns(2)

with col1:
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=company_data["filing_year"], y=company_data["risk_text_length"],
        mode="lines+markers", name="Risk Section Length"
    ))
    fig1.update_layout(title="Risk Section Length Over Time", height=350,
                        xaxis_title="Filing Year", yaxis_title="Characters")
    st.plotly_chart(fig1, width='stretch')

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=company_data["filing_year"], y=company_data["excess_volatility"],
        mode="lines+markers", name="Excess Volatility", line=dict(color="orange")
    ))
    fig2.add_hline(y=0, line_dash="dash", line_color="gray")
    fig2.update_layout(title="Excess Volatility Over Time", height=350,
                        xaxis_title="Filing Year", yaxis_title="Excess Volatility")
    st.plotly_chart(fig2, width='stretch')

if selected_ticker in summary["excluded_companies"]:
    st.warning(
        f"{selected_ticker} was later delisted, taken private, or went bankrupt, "
        f"and no accessible free data source retained historical volatility data "
        f"for it — so volatility isn't shown, though risk-language data is."
    )

st.divider()

# ---- Honest findings ----
st.subheader("Key Findings")
st.markdown(f"""
- **Risk-language change alone is a weak predictor of volatility** : the raw 
  correlation was close to zero ({0.0282:.3f}) before controlling for the market.
- **Controlling for market-wide volatility revealed a real but modest signal**: 
  after isolating company-specific volatility, word count change showed a 
  statistically significant relationship (p = {summary['p_value']:.3f}), though 
  it explains only about {summary['r_squared']*100:.1f}% of the variation.
- **Simple word-count change outperformed a more sophisticated wording-similarity 
  measure**, a reminder that more complex features don't always carry more signal.
- **4 companies were excluded from the volatility analysis** ({', '.join(summary['excluded_companies'])}) 
  due to being delisted, taken private, or bankrupt, with no accessible free 
  historical pricing data.
""")

st.caption(
    "Data source: SEC EDGAR (10-K filings, 2019-2023) and Yahoo Finance "
    "(stock price history). Volatility measured as annualized standard "
    "deviation of daily returns over the 60 trading days following each filing."
)