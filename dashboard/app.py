
from pathlib import Path

import altair as alt
from theme import CHART_COLORS
import pandas as pd
import streamlit as st

from queries import get_top_beneficiary_countries, get_mart_last_modified


st.set_page_config(
    page_title="Saudi Foreign Aid Dashboard",
    page_icon="🌍",
    layout="wide",
)

# Display KSrelief logo
logo_path = Path(__file__).resolve().parent / "assets" / "ksrelief_logo.svg"

st.image(str(logo_path), width=180)

st.title("Saudi Foreign Aid Dashboard")

st.caption(
    "Independent educational data analytics project. "
    "Not an official KSrelief platform."
)

# Display the last modification time of the BigQuery analytical mart.
last_modified = get_mart_last_modified()

if last_modified is not None:
    st.caption(
        "Data last updated (BigQuery mart): "
        f"{last_modified.strftime('%Y-%m-%d %H:%M UTC')}"
    )
else:
    st.caption("Data last updated: Not available")


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

try:
    df = get_top_beneficiary_countries(snapshot)
except Exception:
    st.error(
        "Unable to load data from BigQuery. "
        "Please check the connection and try again."
    )
    st.stop()

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

top_10["bar_color"] = [
    CHART_COLORS[i % len(CHART_COLORS)]
    for i in range(len(top_10))
]

chart = (
    alt.Chart(top_10)
    .mark_bar()
    .encode(
        x=alt.X(
            "aid_billions:Q",
            title="Reported Aid (USD Billions)",
        ),
        y=alt.Y(
            "beneficiary_country:N",
            sort="-x",
            title="Beneficiary Country",
        ),
        color=alt.Color(
            "bar_color:N",
            scale=None,
            legend=None,
        ),
        tooltip=[
            alt.Tooltip(
                "beneficiary_country:N",
                title="Country",
            ),
            alt.Tooltip(
                "aid_billions:Q",
                title="Aid (USD Billions)",
                format=",.2f",
            ),
        ],
    )
    .properties(height=450)
)

st.altair_chart(chart, use_container_width=True)

st.caption(
    "Source: BigQuery mart. "
    "Each snapshot is analyzed independently. "
    "Reported project costs are not confirmed disbursements. "
    "'Multiple Countries' is a geographic category, not a single country."
)
