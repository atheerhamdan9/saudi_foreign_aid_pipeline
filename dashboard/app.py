
from pathlib import Path
import altair as alt
from theme import CHART_COLORS
import pandas as pd
import streamlit as st

from queries import (
    get_top_beneficiary_countries,
    get_data_last_updated,
)

from styles import apply_dashboard_styles

st.set_page_config(
    page_title="Saudi Foreign Aid Dashboard",
    page_icon="🌍",
    layout="wide",
)

apply_dashboard_styles()

st.markdown(
    """
    <style>
    .st-key-kpi_total,
    .st-key-kpi_categories,
    .st-key-kpi_top {
        padding: 14px 18px;
        border-radius: 12px;
        border: 1px solid #E2E8E3;
        min-height: 100px;
    }

    /* KPI values */
    .st-key-kpi_total [data-testid="stMetricValue"],
    .st-key-kpi_categories [data-testid="stMetricValue"],
    .st-key-kpi_top [data-testid="stMetricValue"] {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #171717 !important;
    }

    .st-key-kpi_total {
        background-color: #EAF5EE;
        border-bottom: 3px solid #00843D;
    }

    .st-key-kpi_categories {
        background-color: #FBF4E5;
        border-bottom: 3px solid #C5A45D;
    }

    .st-key-kpi_top {
        background-color: #F0F5F1;
        border-bottom: 3px solid #8CC9A3;
    }

    .st-key-kpi_total [data-testid="stMetricLabel"],
    .st-key-kpi_categories [data-testid="stMetricLabel"],
    .st-key-kpi_top [data-testid="stMetricLabel"],
    .st-key-kpi_total [data-testid="stMetricValue"],
    .st-key-kpi_categories [data-testid="stMetricValue"],
    .st-key-kpi_top [data-testid="stMetricValue"] {
        color: #171717 !important;
    }
    /* Reduce top whitespace */
    [data-testid="stMainBlockContainer"] {
        padding-top: 1.5rem !important;
    }
    /* Main dashboard title */
    h1 {
        font-size: 34px !important;
        font-weight: 650 !important;
        line-height: 1.3 !important;
    }
    /* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #F8F5EF !important;
}

/* Sidebar navigation text */
[data-testid="stSidebar"] a {
    color: #171717 !important;
}

/* Active navigation item */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #EDE3CE !important;
    border-left: 3px solid #C5A45D;
    border-radius: 6px;
}
    </style>
    """,
    unsafe_allow_html=True,
)
# Display KSrelief logo
logo_path = Path(__file__).resolve().parent / "assets" / "ksrelief_logo.svg"

header_logo, header_title = st.columns(
    [1.5, 5],
    gap="small",
    vertical_alignment="center",
)

with header_logo:
    st.image(str(logo_path), width=210)

with header_title:
    st.title("Saudi Foreign Aid Dashboard")
    st.markdown(
        "Explore reported Saudi foreign aid allocations "
        "across beneficiary countries and reporting snapshots."
    )

st.markdown(
    """
    <div style="
        background-color: #F8F5EF;
        border-left: 3px solid #C5A45D;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 10px 0 18px 0;
        color: #171717;
        font-family: Inter, sans-serif;
        font-size: 13px;
        line-height: 1.6;
    ">
        <div style="font-weight: 600; margin-bottom: 3px;">
            ⓘ Important Notice
        </div>
        Independent educational data analytics project.
        Not an official KSrelief platform.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

with st.container(key="filter_snapshot", border=True):
    st.markdown(":material/calendar_month: **Select Snapshot**")
    snapshot = st.selectbox(
        "Select Snapshot",
        ["2025-10", "2025-12", "2026-03"],
        index=2,
        label_visibility="collapsed",
    )

# Display the last modification time of the BigQuery mart.
try:
    last_updated = get_data_last_updated()

    if last_updated is not None:
        st.caption(
            "BigQuery mart last updated: "
            f"{last_updated:%Y-%m-%d %H:%M} UTC"
        )
    else:
        st.caption("BigQuery mart update time unavailable.")

except RuntimeError:
    st.warning(
        "Unable to retrieve the BigQuery mart update time."
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

# KPI Summary
st.subheader("Snapshot Overview")

total_aid = df["total_cost_usd"].sum()
beneficiary_count = df["beneficiary_country"].nunique()

top_beneficiary = (
    df.sort_values("total_cost_usd", ascending=False)
    ["beneficiary_country"]
    .iloc[0]
    if not df.empty
    else "N/A"
)

kpi1, kpi2, kpi3 = st.columns(3, gap="medium")

with kpi1:
    with st.container(key="kpi_total"):
        st.metric(
            "Total Reported Aid",
            f"${total_aid / 1_000_000_000:,.2f}B",
        )

with kpi2:
    with st.container(key="kpi_categories"):
        st.metric(
            "Beneficiary Categories",
            f"{beneficiary_count:,}",
        )

with kpi3:
    with st.container(key="kpi_top"):
        st.metric(
            "Top Beneficiary",
            top_beneficiary,
        )

st.divider()

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

chart = (
    alt.Chart(top_10)
    .mark_bar(
        color=CHART_COLORS[0],
        cornerRadiusEnd=5,
        size=24,
    )
    .encode(
        x=alt.X(
            "aid_billions:Q",
            title="Reported Aid (USD Billions)",
            axis=alt.Axis(
                format=",.1f",
                grid=True,
                gridColor="#E8EEE9",
                labelFontSize=12,
                titleFontSize=13,
            ),
        ),
        y=alt.Y(
            "beneficiary_country:N",
            sort="-x",
            title=None,
            axis=alt.Axis(
                labelLimit=220,
                labelFontSize=13,
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "beneficiary_country:N",
                title="Beneficiary",
            ),
            alt.Tooltip(
                "total_cost_usd:Q",
                title="Reported Aid (USD)",
                format="$,.0f",
            ),
        ],
    )
    .properties(
        height=450,
    )
    .configure(
        font="Inter",
        title={
            "font": "Inter",
            "fontSize": 16,
            "fontWeight": "normal",
            "color": "#171717",
        },
        axis={
            "labelFont": "Inter",
            "titleFont": "Inter",
            "labelColor": "#171717",
            "titleColor": "#171717",
        },
    )
)

with st.container(key="home_chart", border=True):
    st.altair_chart(chart, use_container_width=True)


st.caption(
    "Source: BigQuery mart. "
    "Each snapshot is analyzed independently. "
    "Reported project costs are not confirmed disbursements. "
    "'Multiple Countries' is a geographic category, not a single country."
)
