
from pathlib import Path
import altair as alt
from theme import DARK_GREEN, LIGHT_GREEN
import pandas as pd
import streamlit as st

from queries import get_top_beneficiary_countries


st.title("All Beneficiary Countries")

st.write("Explore all beneficiary countries by snapshot.")

snapshot = st.selectbox(
    "Select Snapshot",
    ["2025-10", "2025-12", "2026-03"],
    index=2,
)

# Load English country names
csv_path = Path(__file__).resolve().parents[1] / "country_names.csv"

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
        "Unable to load beneficiary country data from BigQuery. "
        "Please check the connection and try again."
    )
    st.stop()

# Translate country names
df["country_name"] = df["dimension_value"].map(country_names)

# Check for missing translations
missing = df.loc[
    df["country_name"].isna(),
    "dimension_value",
].tolist()

if missing:
    st.error(f"Missing country name mappings: {missing}")
    st.stop()

# Search using English names
search = st.text_input("Search for a country")

if search:
    df = df[
        df["country_name"]
        .str.contains(search, case=False, na=False, regex=False)
    ]

st.metric("Country Categories", len(df))

# Display all countries in English
st.dataframe(
    df[
        ["country_name", "record_count", "total_cost_usd"]
    ].rename(
        columns={
            "country_name": "Beneficiary Country",
            "record_count": "Project Records",
            "total_cost_usd": "Reported Aid (USD)",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Data source: BigQuery mart. "
    "Each snapshot is displayed independently. "
    "Reported costs are not confirmed disbursements."
)

st.subheader("Top Beneficiary Countries")

top_n = st.selectbox(
    "Number of countries to display",
    [10, 20, 30],
    index=0,
    disabled=bool(search.strip()),
)

chart_df = df.copy()

chart_df["total_cost_usd"] = pd.to_numeric(
    chart_df["total_cost_usd"],
    errors="coerce",
)

chart_df = (
    chart_df
    .sort_values("total_cost_usd", ascending=False)
    .head(top_n)
    .copy()
)

chart_df["aid_billions"] = (
    chart_df["total_cost_usd"] / 1_000_000_000
)

# Alternate between dark and light green
chart_df["bar_color"] = [
    DARK_GREEN if i % 2 == 0 else LIGHT_GREEN
    for i in range(len(chart_df))
]

# Create horizontal bar chart
chart = (
    alt.Chart(chart_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "aid_billions:Q",
            title="Reported Aid (USD Billions)",
        ),
        y=alt.Y(
            "country_name:N",
            sort=chart_df["country_name"].tolist(),
            title="Beneficiary Country",
        ),
        color=alt.Color(
            "bar_color:N",
            scale=None,
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("country_name:N", title="Country"),
            alt.Tooltip(
                "aid_billions:Q",
                title="Reported Aid (USD Billions)",
                format=",.2f",
            ),
        ],
    )
    .properties(
        height=max(180, len(chart_df) * 40 + 100),
    )
)

st.altair_chart(chart, use_container_width=True)