
"""Idempotent extraction and landing of Saudi Aid data in GCS."""

from datetime import date
from pathlib import Path
from time import sleep

from google.api_core.exceptions import (
    InternalServerError,
    PreconditionFailed,
    ServiceUnavailable,
    TooManyRequests,
)
from google.cloud import storage

from pipeline.io.gcs_storage import upload_raw_file


RETRYABLE_ERRORS = (
    ServiceUnavailable,
    TooManyRequests,
    InternalServerError,
)


def extract(
    run_date: date,
    local_path: str | Path,
    bucket_name: str,
    max_attempts: int = 3,
) -> str:
    """Land one date in GCS and return its URI."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    file_path = Path(local_path)

    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    destination_blob = (
        f"raw/source_a/ingest_date={run_date.isoformat()}/"
        f"{file_path.name}"
    )
    landed_uri = f"gs://{bucket_name}/{destination_blob}"

    client = storage.Client()
    blob = client.bucket(bucket_name).blob(destination_blob)

    for attempt in range(max_attempts):
        try:
            if blob.exists():
                return landed_uri

            return upload_raw_file(
                local_path=file_path,
                bucket_name=bucket_name,
                destination_blob=destination_blob,
            )

        except PreconditionFailed:
            # Another run may have created the same object.
            if blob.exists():
                return landed_uri
            raise

        except RETRYABLE_ERRORS:
            if attempt == max_attempts - 1:
                raise

            sleep(2**attempt)

    raise RuntimeError("Extraction failed")
