"""Validate source and ingestion freshness using contract thresholds."""

from datetime import UTC, date, datetime
from typing import Any


def check_freshness(
    latest_release_date: date,
    latest_ingested_at: datetime,
    contract: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Check freshness against thresholds defined in the data contract."""

    if now is None:
        now = datetime.now(UTC)

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")

    if latest_ingested_at.tzinfo is None or latest_ingested_at.utcoffset() is None:
        raise ValueError("latest_ingested_at must be timezone-aware")

    config = contract["freshness"]

    source_age_days = (now.date() - latest_release_date).days
    ingestion_age_hours = (
        now - latest_ingested_at
    ).total_seconds() / 3600

    def get_status(
        age: float,
        warn: float,
        error: float | None,
    ) -> str:
        if error is not None and age > error:
            return "error"
        if age > warn:
            return "warning"
        return "pass"

    source_status = get_status(
        source_age_days,
        config["source"]["warn_after_days"],
        config["source"]["error_after_days"],
    )

    ingestion_status = get_status(
        ingestion_age_hours,
        config["ingestion"]["warn_after_hours"],
        config["ingestion"]["error_after_hours"],
    )

    return {
        "source": {
            "status": source_status,
            "age_days": source_age_days,
        },
        "ingestion": {
            "status": ingestion_status,
            "age_hours": round(ingestion_age_hours, 2),
        },
    }
