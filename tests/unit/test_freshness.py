"""Unit tests for source and ingestion freshness checks."""

from datetime import UTC, date, datetime, timedelta

import pytest

from pipeline.freshness import check_freshness


@pytest.fixture
def contract():
    """Freshness thresholds for Saudi Aid snapshots."""
    return {
        "freshness": {
            "source": {
                "field": "release_date",
                "warn_after_days": 180,
                "error_after_days": None,
            },
            "ingestion": {
                "field": "ingested_at",
                "warn_after_hours": 24,
                "error_after_hours": 48,
            },
        }
    }


def test_freshness_pass(contract):
    """Recent source and ingestion should pass."""
    now = datetime(2026, 3, 15, 12, 0, tzinfo=UTC)

    result = check_freshness(
        latest_release_date=date(2026, 3, 14),
        latest_ingested_at=now - timedelta(hours=2),
        contract=contract,
        now=now,
    )

    assert result["source"]["status"] == "pass"
    assert result["ingestion"]["status"] == "pass"


def test_old_snapshot_returns_warning(contract):
    """An old snapshot should warn without failing."""
    now = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)

    result = check_freshness(
        latest_release_date=date(2026, 3, 1),
        latest_ingested_at=now - timedelta(hours=2),
        contract=contract,
        now=now,
    )

    assert result["source"]["status"] == "warning"
    assert result["source"]["age_days"] > 180


def test_old_ingestion_returns_error(contract):
    """Ingestion older than 48 hours should fail."""
    now = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)

    result = check_freshness(
        latest_release_date=date(2026, 10, 1),
        latest_ingested_at=now - timedelta(hours=72),
        contract=contract,
        now=now,
    )

    assert result["ingestion"]["status"] == "error"


def test_null_source_error_threshold(contract):
    """A null source error threshold should not cause an exception."""
    now = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)

    result = check_freshness(
        latest_release_date=date(2025, 10, 1),
        latest_ingested_at=now - timedelta(hours=1),
        contract=contract,
        now=now,
    )

    assert result["source"]["status"] == "warning"
