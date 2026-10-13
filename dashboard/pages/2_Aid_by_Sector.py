from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt
from theme import DARK_GREEN, LIGHT_GREEN

from queries import get_aid_by_sector


st.title("Aid by Sector")
st.write("Explore reported Saudi foreign aid by project sector.")

snapshot = st.selectbox(
    "Select Snapshot",
    ["2025-10", "2025-12", "2026-03"],
    index=2,
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

st.metric("Sector Categories", len(df))

st.subheader("Top Sectors by Reported Aid Value")

# Dropdown list for sectors
sector_options = ["All Sectors"] + sorted(
    df["sector_name"].dropna().unique().tolist()
)

selected_sector = st.selectbox(
    "Select a sector",
    sector_options,
)

# Disable number selector when a specific sector is selected
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

# Alternate between dark and light green
chart_df = chart_df.copy()

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
            "sector_name:N",
            sort=chart_df["sector_name"].tolist(),
            title="Project Sector",
        ),
        color=alt.Color(
            "bar_color:N",
            scale=None,
            legend=None,
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
        height=max(180, len(chart_df) * 40 + 100),
    )
)

st.altair_chart(chart, use_container_width=True)

st.subheader("All Project Sectors")

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
)

st.caption(
    "Source: BigQuery mart. Values represent reported project costs "
    "within the selected snapshot, not confirmed disbursements."
)