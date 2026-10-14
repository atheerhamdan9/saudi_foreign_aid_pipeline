
from pathlib import Path
import altair as alt
from theme import DARK_GREEN
import pandas as pd
import streamlit as st

from queries import get_top_beneficiary_countries
from styles import apply_dashboard_styles


apply_dashboard_styles()

st.title("All Beneficiary Countries")

st.write("Explore all beneficiary countries by snapshot.")

with st.container(key="filter_snapshot", border=True):
    st.markdown(
        ":material/calendar_month: **Select Snapshot**"
    )
    snapshot = st.selectbox(
        "Select Snapshot",
        ["2025-10", "2025-12", "2026-03"],
        index=2,
        format_func=lambda value: value,
        label_visibility="collapsed",
    )

with st.container(key="filter_country", border=True):
    search = st.text_input(
        "Search for a country",
        placeholder="Enter country name...",
        icon=":material/search:",
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

if df.empty:
    st.warning("No data available for the selected snapshot.")
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

if search:
    df = df[
        df["country_name"]
        .str.contains(search, case=False, na=False, regex=False)
    ]

# Prepare KPI values
df["record_count"] = pd.to_numeric(
    df["record_count"], errors="coerce"
).fillna(0)

df["total_cost_usd"] = pd.to_numeric(
    df["total_cost_usd"], errors="coerce"
).fillna(0)

country_count = len(df)
total_records = int(df["record_count"].sum())
total_aid = df["total_cost_usd"].sum()

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    with st.container(key="kpi_total", border=True):
        st.metric(
            "Matching Countries" if search.strip() else "Beneficiary Countries",
            f"{country_count:,}",
        )

with col2:
    with st.container(key="kpi_categories", border=True):
        st.metric(
            "Project Records",
            f"{total_records:,}",
        )

with col3:
    with st.container(key="kpi_top", border=True):
        st.metric(
            "Reported Aid (USD)",
            f"${total_aid / 1_000_000_000:,.2f}B",
        )

# Display all countries in English
with st.container(key="beneficiary_table", border=True):
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
        column_config={
            "Beneficiary Country": st.column_config.TextColumn(
                "Beneficiary Country"
            ),
            "Project Records": st.column_config.NumberColumn(
                "Project Records",
                format="%d",
            ),
            "Reported Aid (USD)": st.column_config.NumberColumn(
                "Reported Aid (USD)",
                format="$%,.2f",
            ),
        },
    )

st.caption(
    "Data source: BigQuery mart. "
    "Each snapshot is displayed independently. "
    "Reported costs are not confirmed disbursements."
)

with st.container(key="filter_country_limit", border=True):
    top_n = st.selectbox(
        "Number of countries to display",
        [10, 20, 30],
        index=0,
        disabled=bool(search.strip()),
    )

st.subheader("Top Beneficiary Countries")

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

# Create horizontal bar chart
chart = (
    alt.Chart(chart_df)
    .mark_bar(color=DARK_GREEN, cornerRadiusEnd=5, size=24)
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
        height=max(180, len(chart_df) * 36 + 80),
    )
    .configure_view(strokeWidth=0)
    .configure(
        font="Inter",
        axis={
            "labelFont": "Inter",
            "titleFont": "Inter",
            "labelFontSize": 12,
            "titleFontSize": 13,
            "labelColor": "#171717",
            "titleColor": "#171717",
            "gridColor": "#E8EEE9",
        },
    )
)

with st.container(key="beneficiary_chart", border=True):
    st.altair_chart(chart, use_container_width=True)