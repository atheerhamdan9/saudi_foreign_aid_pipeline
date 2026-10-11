
"""Load raw Parquet files from GCS into BigQuery."""

from google.cloud import bigquery


def load_raw_parquet(
    gcs_uri: str,
    project_id: str,
    dataset_id: str,
    table_id: str,
) -> int:
    """Load a Parquet file from GCS into an empty BigQuery table."""

    client = bigquery.Client(project=project_id)

    destination = f"{project_id}.{dataset_id}.{table_id}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
    )

    load_job = client.load_table_from_uri(
        gcs_uri,
        destination,
        job_config=job_config,
        location="europe-west1",
    )

    load_job.result()

    table = client.get_table(destination)
    return table.num_rows
