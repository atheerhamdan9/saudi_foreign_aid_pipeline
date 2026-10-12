
"""Tests for the Saudi Aid cloud extraction."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import PreconditionFailed, ServiceUnavailable

from pipeline.sources.saudi_aid_projects import extract


RUN_DATE = date(2026, 10, 11)
BUCKET = "test-bucket"


@pytest.fixture
def local_file(tmp_path):
    path = tmp_path / "raw_source_a.parquet"
    path.write_bytes(b"test data")
    return path


@patch("pipeline.sources.saudi_aid_projects.storage.Client")
@patch("pipeline.sources.saudi_aid_projects.upload_raw_file")
def test_extract_returns_landed_uri(mock_upload, mock_client, local_file):
    """Successful extraction returns the GCS URI."""
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_client.return_value.bucket.return_value.blob.return_value = mock_blob

    expected_uri = (
        "gs://test-bucket/raw/source_a/"
        "ingest_date=2026-10-11/raw_source_a.parquet"
    )
    mock_upload.return_value = expected_uri

    result = extract(RUN_DATE, local_file, BUCKET)

    assert result == expected_uri
    mock_upload.assert_called_once()


@patch("pipeline.sources.saudi_aid_projects.storage.Client")
@patch("pipeline.sources.saudi_aid_projects.upload_raw_file")
def test_extract_is_idempotent(mock_upload, mock_client, local_file):
    """An existing date partition is not uploaded again."""
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_client.return_value.bucket.return_value.blob.return_value = mock_blob

    result = extract(RUN_DATE, local_file, BUCKET)

    assert result.endswith(
        "ingest_date=2026-10-11/raw_source_a.parquet"
    )
    mock_upload.assert_not_called()


@patch("pipeline.sources.saudi_aid_projects.sleep")
@patch("pipeline.sources.saudi_aid_projects.storage.Client")
@patch("pipeline.sources.saudi_aid_projects.upload_raw_file")
def test_extract_retries_with_backoff(
    mock_upload, mock_client, mock_sleep, local_file
):
    """Temporary failures trigger exponential backoff."""
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_client.return_value.bucket.return_value.blob.return_value = mock_blob

    expected_uri = (
        "gs://test-bucket/raw/source_a/"
        "ingest_date=2026-10-11/raw_source_a.parquet"
    )
    mock_upload.side_effect = [
        ServiceUnavailable("Temporary failure"),
        ServiceUnavailable("Temporary failure"),
        expected_uri,
    ]

    result = extract(RUN_DATE, local_file, BUCKET)

    assert result == expected_uri
    assert mock_upload.call_count == 3
    assert mock_sleep.call_count == 2
    assert [call.args[0] for call in mock_sleep.call_args_list] == [1, 2]


@patch("pipeline.sources.saudi_aid_projects.sleep")
@patch("pipeline.sources.saudi_aid_projects.storage.Client")
@patch("pipeline.sources.saudi_aid_projects.upload_raw_file")
def test_extract_stops_after_max_attempts(
    mock_upload, mock_client, mock_sleep, local_file
):
    """Extraction stops after the maximum retry attempts."""
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_client.return_value.bucket.return_value.blob.return_value = mock_blob
    mock_upload.side_effect = ServiceUnavailable("GCS unavailable")

    with pytest.raises(ServiceUnavailable):
        extract(RUN_DATE, local_file, BUCKET, max_attempts=3)

    assert mock_upload.call_count == 3
    assert [call.args[0] for call in mock_sleep.call_args_list] == [1, 2]


def test_extract_missing_file(tmp_path):
    """Extraction raises an error if the local file is missing."""
    missing_file = tmp_path / "missing.parquet"

    with pytest.raises(FileNotFoundError):
        extract(RUN_DATE, missing_file, BUCKET)


@patch("pipeline.sources.saudi_aid_projects.storage.Client")
@patch("pipeline.sources.saudi_aid_projects.upload_raw_file")
def test_extract_handles_concurrent_upload(
    mock_upload, mock_client, local_file
):
    """Handle another process uploading the same object first."""
    mock_blob = MagicMock()
    mock_blob.exists.side_effect = [False, True]
    mock_client.return_value.bucket.return_value.blob.return_value = mock_blob
    mock_upload.side_effect = PreconditionFailed("Object already exists")

    result = extract(RUN_DATE, local_file, BUCKET)

    expected_uri = (
        "gs://test-bucket/raw/source_a/"
        "ingest_date=2026-10-11/raw_source_a.parquet"
    )

    assert result == expected_uri
    mock_upload.assert_called_once()
    assert mock_blob.exists.call_count == 2


@patch("pipeline.sources.saudi_aid_projects.storage.Client")
@patch("pipeline.sources.saudi_aid_projects.upload_raw_file")
def test_extract_repeated_run(mock_upload, mock_client, local_file):
    """Running extraction twice uploads the file only once."""
    mock_blob = MagicMock()
    mock_blob.exists.side_effect = [False, True]
    mock_client.return_value.bucket.return_value.blob.return_value = mock_blob

    expected_uri = (
        "gs://test-bucket/raw/source_a/"
        "ingest_date=2026-10-11/raw_source_a.parquet"
    )
    mock_upload.return_value = expected_uri

    first_result = extract(RUN_DATE, local_file, BUCKET)
    second_result = extract(RUN_DATE, local_file, BUCKET)

    assert first_result == second_result == expected_uri
    mock_upload.assert_called_once()
