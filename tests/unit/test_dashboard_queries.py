"""Unit tests for dashboard BigQuery error handling."""

import sys
from datetime import UTC
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import ServiceUnavailable
from google.auth.exceptions import DefaultCredentialsError

# Allow importing queries.py from the dashboard directory.
DASHBOARD_DIR = Path(__file__).resolve().parents[2] / "dashboard"
sys.path.insert(0, str(DASHBOARD_DIR))


import queries  # noqa: E402


def test_bigquery_client_handles_missing_credentials():
    """Missing credentials should produce a clear RuntimeError."""

    with patch(
        "queries.bigquery.Client",
        side_effect=DefaultCredentialsError("Missing credentials"),
    ):
        with pytest.raises(
            RuntimeError,
            match="Unable to connect to BigQuery",
        ):
            queries.get_bigquery_client()


@pytest.mark.parametrize(
    "query_function",
    [
        queries.get_top_beneficiary_countries,
        queries.get_aid_by_sector,
        queries.get_aid_by_donor,
        queries.get_project_status,
    ],
)
def test_bigquery_query_failure(query_function):
    """All dashboard queries should handle BigQuery service failures."""

    mock_client = MagicMock()
    mock_client.query.side_effect = ServiceUnavailable(
        "BigQuery temporarily unavailable"
    )

    with patch(
        "queries.get_bigquery_client",
        return_value=mock_client,
    ):
        with pytest.raises(RuntimeError, match="Unable to load"):
            query_function("2026-03")


@pytest.mark.parametrize(
    "query_function",
    [
        queries.get_top_beneficiary_countries,
        queries.get_aid_by_sector,
        queries.get_aid_by_donor,
        queries.get_project_status,
    ],
)
def test_queries_filter_selected_snapshot(query_function):
    """Queries must filter by snapshot using a parameter."""

    mock_client = MagicMock()
    mock_client.query.return_value.result.return_value = []

    with patch(
        "queries.get_bigquery_client",
        return_value=mock_client,
    ):
        query_function("2026-03")

    args, kwargs = mock_client.query.call_args
    sql = args[0]
    job_config = kwargs["job_config"]

    assert "snapshot_month = @snapshot_month" in sql
    assert job_config.query_parameters[0].value == "2026-03"
    
def test_get_data_last_updated():
    from datetime import datetime
    from unittest.mock import MagicMock, patch

    from queries import get_data_last_updated

    expected_time = datetime(
        2026, 10, 13, 12, 0, tzinfo=UTC
    )

    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_table.modified = expected_time
    mock_client.get_table.return_value = mock_table

    with patch(
        "queries.get_bigquery_client",
        return_value=mock_client,
    ):
        result = get_data_last_updated()

    assert result == expected_time
    mock_client.get_table.assert_called_once()
    
def test_get_data_last_updated_failure():
    from unittest.mock import MagicMock, patch

    import pytest
    from google.api_core.exceptions import ServiceUnavailable
    from queries import get_data_last_updated

    mock_client = MagicMock()
    mock_client.get_table.side_effect = ServiceUnavailable(
        "BigQuery temporarily unavailable"
    )

    with patch(
        "queries.get_bigquery_client",
        return_value=mock_client,
    ):
        with pytest.raises(
            RuntimeError,
            match="Unable to retrieve the BigQuery table update time",
        ):
            get_data_last_updated()