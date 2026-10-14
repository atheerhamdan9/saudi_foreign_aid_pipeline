import streamlit as st


def apply_dashboard_styles():
    st.markdown(
        """
        <style>

        /* White main page background */
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background-color: #FFFFFF !important;
        }

        /* Beige sidebar */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
            background-color: #F8F5EF !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 1.5rem !important;
        }

        h1 {
            font-size: 34px !important;
            font-weight: 650 !important;
            line-height: 1.3 !important;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
            background-color: #F8F5EF !important;
        }

        [data-testid="stSidebar"] a {
            color: #171717 !important;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #EDE3CE !important;
            border-left: 3px solid #C5A45D;
            border-radius: 6px;
        }

        .st-key-kpi_total,
        .st-key-kpi_categories,
        .st-key-kpi_top,
        .st-key-kpi_countries {
            padding: 14px 18px;
            border-radius: 12px;
            border: 1px solid #E2E8E3;
            min-height: 100px;
        }

        .st-key-kpi_total,
        .st-key-kpi_countries {
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

        [class*="st-key-kpi_"] [data-testid="stMetricValue"] {
            font-size: 20px !important;
            font-weight: 600 !important;
            color: #171717 !important;
        }

        [class*="st-key-kpi_"] [data-testid="stMetricLabel"] {
            color: #171717 !important;
        }

        /* Force white main content background */
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        [data-testid="stHeader"] {
            background-color: #FFFFFF !important;
        }

        /* Keep sidebar beige */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
            background-color: #F8F5EF !important;
        }



        /* Country filters container */
        .st-key-country_filters {
            background-color: #F8F9FA !important;
            border: 1px solid #E2E5E3 !important;
            border-radius: 12px !important;
            padding: 18px 22px !important;
        }
        /* Filter fields: visible background and border */
        div[data-testid="stSelectbox"] [data-baseweb="select"],
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
        div[data-testid="stTextInput"] [data-baseweb="base-input"],
        div[data-testid="stTextInput"] [data-baseweb="input"] {
            background: #F1F3F6 !important;
            border: 1px solid #D5DBE1 !important;
            border-radius: 12px !important;
            min-height: 50px !important;
            box-shadow: none !important;
        }

        /* Input text */
        div[data-testid="stTextInput"] input {
            background: transparent !important;
        }

        /* Green focus */
        div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
        div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
        border-color: #00843D !important;
        box-shadow: 0 0 0 1px #00843D !important;
    }

        /* Hover effect */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
        [data-testid="stTextInput"] div[data-baseweb="input"]:hover {
            background-color: #E9EDF1 !important;
            border-color: #AAB7AE !important;
        }

        /* Green border when selected */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
        [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }

        /* Input background */
        [data-testid="stTextInput"] input {
            background-color: transparent !important;
        }

        /* Professional filter cards */
        .st-key-filter_snapshot,
        .st-key-filter_country {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E6E4 !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            margin-bottom: 16px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        }


        /* Input fields inside filter cards */
        .st-key-filter_snapshot [data-baseweb="select"] > div,
        .st-key-filter_country [data-baseweb="base-input"] {
            background-color: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
        }

        /* Green focus indicator */
        .st-key-filter_snapshot [data-baseweb="select"]:focus-within > div,
        .st-key-filter_country [data-baseweb="base-input"]:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }


        /* Refined filter input styling */
        .st-key-filter_snapshot [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        .st-key-filter_country [data-testid="stTextInput"] [data-baseweb="input"] {
            background: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
            min-height: 44px !important;
        }

        .st-key-filter_country [data-testid="stTextInput"] input {
            background: transparent !important;
        }

        .st-key-filter_snapshot [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div,
        .st-key-filter_country [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
            border-color: #00843D !important;
        }


        /* Streamlit 1.65 React Aria selectbox */
        .st-key-filter_snapshot .react-aria-ComboBox [role="group"] {
            background-color: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
            min-height: 48px !important;
            padding: 0 12px !important;
            box-shadow: none !important;
        }

        .st-key-filter_snapshot .react-aria-ComboBox input {
            background-color: transparent !important;
            color: #171717 !important;
        }

        .st-key-filter_snapshot .react-aria-ComboBox [role="group"]:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }



        /* Country search field - inner input only */
        .st-key-filter_country [data-testid="stTextInput"] > div > div {
            background-color: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
            min-height: 48px !important;
        }

        .st-key-filter_country [data-testid="stTextInput"] input {
            background-color: transparent !important;
        }

        .st-key-filter_country [data-testid="stTextInput"] > div > div:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }


        /* Number of countries filter */
        .st-key-filter_country_limit {
            background: #FFFFFF !important;
            border: 1px solid #E2E6E4 !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            margin-bottom: 12px !important;
        }

        .st-key-filter_country_limit .react-aria-ComboBox [role="group"] {
            background-color: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
            min-height: 48px !important;
            padding: 0 12px !important;
        }

        .st-key-filter_country_limit .react-aria-ComboBox input {
            background-color: transparent !important;
            color: #171717 !important;
        }

        .st-key-filter_country_limit .react-aria-ComboBox [role="group"]:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }


        /* Beneficiary countries data table */
        .st-key-sector_chart, .st-key-beneficiary_table {
            background: #FFFFFF !important;
            border: 1px solid #E2E6E4 !important;
            border-radius: 12px !important;
            padding: 16px !important;
            overflow: hidden;
        }

        .st-key-sector_chart, .st-key-beneficiary_table [data-testid="stDataFrame"] {
            border-radius: 8px !important;
            overflow: hidden;
        }

        .st-key-sector_chart, .st-key-beneficiary_table [data-testid="stDataFrame"] canvas {
            border-radius: 8px !important;
        }


        /* Sector selection filter */
        .st-key-filter_sector {
            background: #FFFFFF !important;
            border: 1px solid #E2E6E4 !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        }

        .st-key-filter_sector .react-aria-ComboBox [role="group"] {
            background-color: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
            min-height: 48px !important;
            padding: 0 12px !important;
            box-shadow: none !important;
        }

        .st-key-filter_sector .react-aria-ComboBox input {
            background-color: transparent !important;
            color: #171717 !important;
        }

        .st-key-filter_sector .react-aria-ComboBox [role="group"]:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }


        /* Sector selectbox direct styling */
        [data-testid="stSelectbox"]:has(input[aria-label="Select a sector"])
        .react-aria-ComboBox [role="group"] {
            background: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
            min-height: 48px !important;
            padding: 0 12px !important;
        }

        [data-testid="stSelectbox"]:has(input[aria-label="Select a sector"])
        .react-aria-ComboBox input {
            background: transparent !important;
        }

        [data-testid="stSelectbox"]:has(input[aria-label="Select a sector"])
        .react-aria-ComboBox [role="group"]:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }


        /* Unified selectbox styling */
        [data-testid="stSelectbox"] .react-aria-ComboBox [role="group"] {
            background-color: #F5F6F7 !important;
            border: 1px solid #D9DEE2 !important;
            border-radius: 8px !important;
            min-height: 48px !important;
            padding: 0 12px !important;
            box-shadow: none !important;
        }

        [data-testid="stSelectbox"] .react-aria-ComboBox input {
            background-color: transparent !important;
            color: #171717 !important;
        }

        [data-testid="stSelectbox"] .react-aria-ComboBox [role="group"]:focus-within {
            border-color: #00843D !important;
            box-shadow: 0 0 0 1px #00843D !important;
        }

        
        /* Shared chart and table cards */
        .st-key-home_chart,
.st-key-beneficiary_chart,
.st-key-donor_chart,
.st-key-donor_table,
.st-key-status_chart,
.st-key-status_table {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E5E3 !important;
            border-radius: 12px !important;
            padding: 18px 22px !important;
        }


        /* Donor Categories KPI */
        .st-key-kpi_donor_categories {
            background-color: #EAF5EE !important;
            border: 1px solid #E2E8E3 !important;
            border-bottom: 3px solid #00843D !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            min-height: 100px;
        }

</style>
        """,
        unsafe_allow_html=True,
    )
