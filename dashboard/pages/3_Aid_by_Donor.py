from pathlib import Path
import pandas as pd
import streamlit as st

from queries import get_aid_by_donor


st.title("Aid by Donor")
st.write("Explore reported Saudi foreign aid by donor entity.")

snapshot = st.selectbox(
    "Select Snapshot",
    ["2025-10", "2025-12", "2026-03"],
    index=2,
)

df = get_aid_by_donor(snapshot)

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

top_n = st.selectbox(
    "Number of donors to display",
    [5, 10, 20],
    index=1,
)

chart_df = (
    df.sort_values("total_cost_usd", ascending=False)
    .head(top_n)
    .copy()
)

chart_df["aid_billions"] = (
    chart_df["total_cost_usd"] / 1_000_000_000
)

st.bar_chart(
    chart_df,
    x="donor_name",
    y="aid_billions",
    horizontal=True,
    x_label="Donor Entity",
    y_label="Reported Aid (USD Billions)",
    height=max(450, top_n * 40),
)

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