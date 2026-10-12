
from pathlib import Path

import pandas as pd
import streamlit as st

from queries import get_top_beneficiary_countries


st.set_page_config(
    page_title="Saudi Foreign Aid Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.title("Saudi Foreign Aid Dashboard")

st.write(
    "Explore reported Saudi foreign aid by beneficiary country."
)

snapshot = st.selectbox(
    "Select Snapshot",
    ["2025-10", "2025-12", "2026-03"],
    index=2,
)

# Load English country names
csv_path = Path(__file__).resolve().parent / "country_names.csv"

country_reference = pd.read_csv(csv_path)

country_names = dict(
    zip(
        country_reference["arabic_name"],
        country_reference["english_name"],
    )
)

# Get data from BigQuery
df = get_top_beneficiary_countries(snapshot)

# Translate country names
df["beneficiary_country"] = df["dimension_value"].map(
    country_names
)

missing = df.loc[
    df["beneficiary_country"].isna(),
    "dimension_value",
].tolist()

if missing:
    st.error(f"Missing country name mappings: {missing}")
    st.stop()

# Convert reported cost to numeric
df["total_cost_usd"] = pd.to_numeric(
    df["total_cost_usd"],
    errors="coerce",
)

# KPI
total_aid = df["total_cost_usd"].sum()

st.metric(
    label="Total Reported Aid (USD)",
    value=f"${total_aid:,.0f}",
)

# Top 10 beneficiary country categories
st.subheader(
    "Top 10 Beneficiary Countries by Reported Aid Value"
)

top_10 = (
    df.sort_values(
        "total_cost_usd",
        ascending=False,
    )
    .head(10)
    .copy()
)

top_10["aid_billions"] = (
    top_10["total_cost_usd"] / 1_000_000_000
)

st.bar_chart(
    top_10,
    x="beneficiary_country",
    y="aid_billions",
    horizontal=True,
    x_label="Beneficiary Country",
    y_label="Reported Aid (USD Billions)",
    height=450,
)

st.caption(
    "Source: BigQuery mart. "
    "Each snapshot is analyzed independently. "
    "Reported project costs are not confirmed disbursements. "
    "'Multiple Countries' is a geographic category, not a single country."
)
