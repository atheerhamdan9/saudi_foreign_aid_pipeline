import pandas as pd
import streamlit as st
import plotly.express as px
from theme import DARK_GREEN, LIGHT_GREEN
from queries import get_project_status


st.title("Project Status")
st.write("Explore the distribution of aid project records by status.")

snapshot = st.selectbox(
    "Select Snapshot",
    ["2025-10", "2025-12", "2026-03"],
    index=2,
)

df = get_project_status(snapshot)

status_names = {
    "منتهي": "Completed",
    "تحت التنفيذ": "In Progress",
}

df["status"] = df["project_status"].replace(status_names)

df["record_count"] = pd.to_numeric(df["record_count"])
df["total_cost_usd"] = pd.to_numeric(df["total_cost_usd"])

total_records = int(df["record_count"].sum())

df["percentage"] = (
    df["record_count"] / total_records * 100
    if total_records > 0
    else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Project Records", f"{total_records:,}")

col2.metric(
    "Completed Records",
    f"{df.loc[df['status'] == 'Completed', 'record_count'].sum():,.0f}",
)

col3.metric(
    "In Progress Records",
    f"{df.loc[df['status'] == 'In Progress', 'record_count'].sum():,.0f}",
)

filtered_df = df.copy()

st.subheader("Project Status Distribution")

st.subheader("Project Status Distribution")

fig = px.pie(
    filtered_df,
    names="status",
    values="record_count",
    hole=0.5,
    color="status",
    color_discrete_map={
    "Completed": DARK_GREEN,
    "In Progress": LIGHT_GREEN,
    },
)

fig.update_traces(
    textposition="inside",
    textinfo="percent+label",
)

fig.update_layout(
    height=400,
    showlegend=True,
    margin=dict(t=20, b=20, l=20, r=20),
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Status Breakdown")

st.dataframe(
    filtered_df[
    ["status", "record_count", "percentage", "total_cost_usd"]
    ].rename(
        columns={
            "status": "Project Status",
            "record_count": "Project Records",
            "percentage": "Percentage (%)",
            "total_cost_usd": "Reported Aid (USD)",
        }
    ),
    hide_index=True,
    use_container_width=True,
)

st.caption(
    "Percentages are based on project records, not unique projects. "
    "Reported costs do not represent confirmed disbursements."
)