"""Google Cloud Storage adapter for raw data files."""

from pathlib import Path

from google.cloud import storage


def upload_raw_file(
    local_path: str | Path,
    bucket_name: str,
    destination_blob: str,
) -> str:
    """Upload a raw file to GCS without overwriting existing files."""

    file_path = Path(local_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not bucket_name:
        raise ValueError("Bucket name is required.")

    if not destination_blob or destination_blob.startswith("/"):
        raise ValueError("A relative destination blob path is required.")

    if ".." in Path(destination_blob).parts:
        raise ValueError("Destination blob cannot contain '..'.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)

    blob.upload_from_filename(
        str(file_path),
        if_generation_match=0,
    )

    return f"gs://{bucket_name}/{destination_blob}"
