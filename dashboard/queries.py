import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "saudi-foreign-aid-data"

MART_TABLE = (
    "saudi-foreign-aid-data."
    "saudi_aid_dbt_dev."
    "fct_records_by_snapshot"
)


def get_top_beneficiary_countries(snapshot_month: str) -> pd.DataFrame:
    """Return beneficiary countries ranked by reported aid value."""

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            snapshot_month,
            dimension_type,
            dimension_value,
            record_count,
            total_cost_usd
        FROM `{MART_TABLE}`
        WHERE snapshot_month = @snapshot_month
          AND dimension_type = 'beneficiary_country'
        ORDER BY total_cost_usd DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "snapshot_month",
                "STRING",
                snapshot_month,
            )
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    return pd.DataFrame(
        [dict(row.items()) for row in rows],
        columns=[
            "snapshot_month",
            "dimension_type",
            "dimension_value",
            "record_count",
            "total_cost_usd",
        ],
    )
    
def get_aid_by_sector(snapshot_month: str) -> pd.DataFrame:
    """Return aid sectors ranked by reported aid value."""

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            snapshot_month,
            dimension_value AS project_sector,
            record_count,
            total_cost_usd
        FROM `{MART_TABLE}`
        WHERE snapshot_month = @snapshot_month
          AND dimension_type = 'project_sector'
        ORDER BY total_cost_usd DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "snapshot_month",
                "STRING",
                snapshot_month,
            )
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    return pd.DataFrame(
        [dict(row.items()) for row in rows],
        columns=[
            "snapshot_month",
            "project_sector",
            "record_count",
            "total_cost_usd",
        ],
    )
    
def get_aid_by_donor(snapshot_month: str) -> pd.DataFrame:
    """Return donor entities ranked by reported aid value."""

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            snapshot_month,
            dimension_value AS project_donor,
            record_count,
            total_cost_usd
        FROM `{MART_TABLE}`
        WHERE snapshot_month = @snapshot_month
          AND dimension_type = 'project_donor'
        ORDER BY total_cost_usd DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "snapshot_month", "STRING", snapshot_month
            )
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    return pd.DataFrame(
        [dict(row.items()) for row in rows],
        columns=[
            "snapshot_month",
            "project_donor",
            "record_count",
            "total_cost_usd",
        ],
    )
    
def get_project_status(snapshot_month: str) -> pd.DataFrame:
    """Return project status distribution for a snapshot."""

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            snapshot_month,
            dimension_value AS project_status,
            record_count,
            total_cost_usd
        FROM `{MART_TABLE}`
        WHERE snapshot_month = @snapshot_month
          AND dimension_type = 'project_status'
        ORDER BY record_count DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "snapshot_month", "STRING", snapshot_month
            )
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    return pd.DataFrame(
        [dict(row.items()) for row in rows],
        columns=[
            "snapshot_month",
            "project_status",
            "record_count",
            "total_cost_usd",
        ],
    )