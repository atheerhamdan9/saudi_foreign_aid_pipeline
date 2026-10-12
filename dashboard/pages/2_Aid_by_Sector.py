from pathlib import Path
import pandas as pd
import streamlit as st

from queries import get_aid_by_sector


st.title("Aid by Sector")
st.write("Explore reported Saudi foreign aid by project sector.")

snapshot = st.selectbox(
    "Select Snapshot",
    ["2025-10", "2025-12", "2026-03"],
    index=2,
)

df = get_aid_by_sector(snapshot)

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

top_n = st.selectbox(
    "Number of sectors to display",
    [10, 20, 30],
    index=0,
)

chart_df = df.sort_values(
    "total_cost_usd", ascending=False
).head(top_n).copy()

chart_df["aid_billions"] = (
    chart_df["total_cost_usd"] / 1_000_000_000
)

st.bar_chart(
    chart_df,
    x="sector_name",
    y="aid_billions",
    horizontal=True,
    x_label="Project Sector",
    y_label="Reported Aid (USD Billions)",
    height=max(450, top_n * 35),
)

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