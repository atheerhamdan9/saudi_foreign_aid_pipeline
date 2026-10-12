
"""Cloud smoke test for GCS and BigQuery."""

import os
from datetime import date
from uuid import uuid4

import pandas as pd
import pytest
from google.cloud import bigquery, storage

from pipeline.io.bigquery_loader import load_raw_parquet
from pipeline.io.gcs_storage import upload_raw_file


@pytest.mark.cloud
def test_cloud_smoke(tmp_path):
    """Upload one date to GCS and load it into BigQuery."""

    if os.getenv("RUN_CLOUD_TESTS") != "1":
        pytest.skip("Set RUN_CLOUD_TESTS=1 to run cloud tests")

    project_id = os.environ["GCP_PROJECT_ID"]
    bucket_name = os.environ["GCS_BUCKET_NAME"]
    dataset_id = os.environ["BQ_DATASET_ID"]

    run_id = uuid4().hex
    ingest_date = date(2026, 10, 11).isoformat()

    table_id = f"cloud_smoke_{run_id}"
    destination_blob = (
        f"tests/cloud_smoke/ingest_date={ingest_date}/"
        f"{run_id}.parquet"
    )

    local_path = tmp_path / "raw_source_a.parquet"

    # Small test dataset for one ingestion date.
    records = pd.DataFrame(
        {
            "record": [1, 2],
            "project_title": ["Project A", "Project B"],
            "snapshot_month": ["2025-10", "2025-10"],
        }
    )
    records.to_parquet(local_path, index=False)

    gcs_uri = None
    bq_client = bigquery.Client(project=project_id)
    gcs_client = storage.Client(project=project_id)

    try:
        # Upload raw Parquet to GCS.
        gcs_uri = upload_raw_file(
            local_path,
            bucket_name,
            destination_blob,
        )

        blob = gcs_client.bucket(bucket_name).blob(destination_blob)
        assert blob.exists()

        # Load GCS Parquet into a separate BigQuery table.
        loaded_rows = load_raw_parquet(
            gcs_uri,
            project_id,
            dataset_id,
            table_id,
        )

        assert loaded_rows == len(records)

        table = bq_client.get_table(
            f"{project_id}.{dataset_id}.{table_id}"
        )
        assert table.num_rows == 2

    finally:
        # Remove temporary cloud test resources.
        bq_client.delete_table(
            f"{project_id}.{dataset_id}.{table_id}",
            not_found_ok=True,
        )

        if gcs_uri is not None:
            gcs_client.bucket(bucket_name).blob(
                destination_blob
            ).delete()
