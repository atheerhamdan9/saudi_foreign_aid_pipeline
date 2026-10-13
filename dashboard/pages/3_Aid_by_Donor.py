from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt
from theme import DARK_GREEN, LIGHT_GREEN
from queries import get_aid_by_donor


st.title("Aid by Donor")
st.write("Explore reported Saudi foreign aid by donor entity.")

snapshot = st.selectbox(
    "Select Snapshot",
    ["2025-10", "2025-12", "2026-03"],
    index=2,
)

try:
    df = get_aid_by_donor(snapshot)
except Exception:
    st.error(
        "Unable to load donor data from BigQuery. "
        "Please check the connection and try again."
    )
    st.stop()

# Load donor names from the reference CSV
csv_path = Path(__file__).resolve().parents[1] / "donor_names.csv"

donor_reference = pd.read_csv(csv_path)

# Match the original Arabic names with their English equivalents
donor_names = dict(
    zip(
        donor_reference["arabic_name"],
        donor_reference["official_english_name"],
    )
)

df["donor_name"] = df["project_donor"].map(donor_names)

# Detect missing translations instead of silently showing Arabic names
missing = df.loc[df["donor_name"].isna(), "project_donor"].tolist()

if missing:
    st.error(f"Missing donor name mappings: {missing}")
    st.stop()

df["total_cost_usd"] = pd.to_numeric(
    df["total_cost_usd"],
    errors="coerce",
)

st.metric("Donor Categories", len(df))

st.subheader("Top Donors by Reported Aid Value")

# Dropdown list for donors
donor_options = ["All Donors"] + sorted(
    df["donor_name"].dropna().unique().tolist()
)

selected_donor = st.selectbox(
    "Select a donor",
    donor_options,
)

top_n = st.selectbox(
    "Number of donors to display",
    [5, 10, 20],
    index=1,
    disabled=(selected_donor != "All Donors"),
)

# Copy data
chart_df = df.copy()

# Filter by selected donor
if selected_donor != "All Donors":
    chart_df = chart_df[
        chart_df["donor_name"] == selected_donor
    ]

# Sort by total cost
chart_df = chart_df.sort_values(
    "total_cost_usd",
    ascending=False
)

# Apply Top N only for all donors
if selected_donor == "All Donors":
    chart_df = chart_df.head(top_n)

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
            "donor_name:N",
            sort=chart_df["donor_name"].tolist(),
            title="Donor Entity",
        ),
        color=alt.Color(
            "bar_color:N",
            scale=None,
            legend=None,
        ),
        tooltip=[
            alt.Tooltip(
                "donor_name:N",
                title="Donor Entity",
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

st.subheader("All Donor Entities")

st.dataframe(
    df[["donor_name", "record_count", "total_cost_usd"]].rename(
        columns={
            "donor_name": "Donor Entity",
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