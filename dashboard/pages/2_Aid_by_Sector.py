from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt
from theme import DARK_GREEN

from queries import get_aid_by_sector
from styles import apply_dashboard_styles


apply_dashboard_styles()

st.title("Aid by Sector")
st.write("Explore reported Saudi foreign aid by project sector.")

with st.container(key="filter_snapshot", border=True):
    st.markdown(":material/calendar_month: **Select Snapshot**")
    snapshot = st.selectbox(
        "Select Snapshot",
        ["2025-10", "2025-12", "2026-03"],
        index=2,
        label_visibility="collapsed",
    )

try:
    df = get_aid_by_sector(snapshot)
except Exception:
    st.error(
        "Unable to load sector data from BigQuery. "
        "Please check the connection and try again."
    )
    st.stop()

# Load English sector names from the reference CSV
csv_path = Path(__file__).resolve().parents[1] / "sector_names.csv"

sector_reference = pd.read_csv(csv_path)

# Map original Arabic sector names to English
sector_names = dict(
    zip(
        sector_reference["arabic_name"],
        sector_reference["english_name"],
    )
)

df["sector_name"] = df["project_sector"].map(sector_names)

# Stop if any sector is missing from the reference file
missing = df.loc[df["sector_name"].isna(), "project_sector"].tolist()

if missing:
    st.error(f"Missing sector name mappings: {missing}")
    st.stop()
df["total_cost_usd"] = pd.to_numeric(
    df["total_cost_usd"], errors="coerce"
)

with st.container(key="kpi_countries"):
    st.metric("Sector Categories", len(df))

st.subheader("Top Sectors by Reported Aid Value")

# Dropdown list for sectors
sector_options = ["All Sectors"] + sorted(
    df["sector_name"].dropna().unique().tolist()
)

with st.container(key="filter_sector", border=True):
    selected_sector = st.selectbox(
        "Select a sector",
        sector_options,
    )

# Disable number selector when a specific sector is selected
with st.container(key="filter_country_limit", border=True):
    top_n = st.selectbox(
        "Number of sectors to display",
        [10, 20, 30],
        index=0,
        disabled=(selected_sector != "All Sectors"),
    )

# Filter data
chart_df = df.copy()

if selected_sector != "All Sectors":
    chart_df = chart_df[
        chart_df["sector_name"] == selected_sector
    ]

# Sort by total cost
chart_df = chart_df.sort_values(
    "total_cost_usd", ascending=False
)

# Apply Top N only when all sectors are selected
if selected_sector == "All Sectors":
    chart_df = chart_df.head(top_n)

# Convert to billions
chart_df["aid_billions"] = (
    chart_df["total_cost_usd"] / 1_000_000_000
)

# Create horizontal bar chart
chart = (
    alt.Chart(chart_df)
    .mark_bar(
        color=DARK_GREEN,
        cornerRadiusEnd=5,
        size=24,
    )
    .encode(
        x=alt.X(
            "aid_billions:Q",
            title="Reported Aid (USD Billions)",
        ),
        y=alt.Y(
            "sector_name:N",
            sort=chart_df["sector_name"].tolist(),
            title="Project Sector",
        ),
        tooltip=[
            alt.Tooltip(
                "sector_name:N",
                title="Project Sector",
            ),
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
            "labelFontSize": 13,
            "titleFontSize": 13,
            "labelColor": "#171717",
            "titleColor": "#171717",
            "gridColor": "#E8EEE9",
        },
    )
)

with st.container(key="sector_chart", border=True):
    st.altair_chart(chart, use_container_width=True)

st.subheader("All Project Sectors")

with st.container(key="beneficiary_table", border=True):
    st.dataframe(
        df[["sector_name", "record_count", "total_cost_usd"]].rename(
            columns={
                "sector_name": "Project Sector",
                "record_count": "Project Records",
                "total_cost_usd": "Reported Aid (USD)",
            }
        ),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Project Sector": st.column_config.TextColumn(
                "Project Sector"
            ),
            "Project Records": st.column_config.NumberColumn(
                "Project Records",
                format="%d",
            ),
            "Reported Aid (USD)": st.column_config.NumberColumn(
                "Reported Aid (USD)",
                format="dollar",
            ),
        },
    )

st.caption(
    "Source: BigQuery mart. Values represent reported project costs "
    "within the selected snapshot, not confirmed disbursements."
)