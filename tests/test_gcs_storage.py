"""Tests for the Google Cloud Storage adapter."""

from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import PreconditionFailed

from pipeline.io.gcs_storage import upload_raw_file


def test_upload_raw_file_success(tmp_path):
    """Verify a raw file is uploaded to GCS correctly."""

    local_file = tmp_path / "raw_data.parquet"
    local_file.write_bytes(b"test parquet content")

    with patch("pipeline.io.gcs_storage.storage.Client") as mock_client:
        mock_blob = MagicMock()
        mock_client.return_value.bucket.return_value.blob.return_value = mock_blob

        result = upload_raw_file(
            local_path=local_file,
            bucket_name="test-bucket",
            destination_blob="raw/source_a/raw_data.parquet",
        )

        assert result == "gs://test-bucket/raw/source_a/raw_data.parquet"

        mock_client.return_value.bucket.assert_called_once_with("test-bucket")
        mock_client.return_value.bucket.return_value.blob.assert_called_once_with(
            "raw/source_a/raw_data.parquet"
        )

        mock_blob.upload_from_filename.assert_called_once_with(
            str(local_file),
            if_generation_match=0,
        )


def test_upload_raw_file_missing_file(tmp_path):
    """Verify that a missing local file raises an error."""

    with pytest.raises(FileNotFoundError):
        upload_raw_file(
            local_path=tmp_path / "missing.parquet",
            bucket_name="test-bucket",
            destination_blob="raw/missing.parquet",
        )


def test_upload_raw_file_prevents_overwrite(tmp_path):
    """Verify an existing GCS object cannot be overwritten."""

    local_file = tmp_path / "raw_data.parquet"
    local_file.write_bytes(b"test content")

    with patch("pipeline.io.gcs_storage.storage.Client") as mock_client:
        mock_blob = mock_client.return_value.bucket.return_value.blob.return_value
        mock_blob.upload_from_filename.side_effect = PreconditionFailed(
            "Object already exists"
        )

        with pytest.raises(PreconditionFailed):
            upload_raw_file(
                local_path=local_file,
                bucket_name="test-bucket",
                destination_blob="raw/source_a/raw_data.parquet",
            )
