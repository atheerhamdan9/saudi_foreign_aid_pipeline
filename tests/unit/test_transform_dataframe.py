import pandas as pd
import pytest

from pipeline.transform import build_metrics, clean_records


def sample_dataframe():
    return pd.DataFrame(
        [
            {
                "project_title": " Health Project ",
                "project_status": "Completed",
                "project_sector": "Health",
                "project_location": "Yemen",
                "total_cost_usd": "1,000",
                "project_donor": "Saudi Fund",
                "beneficiary_country": "Yemen",
            },
            {
                "project_title": "Education Project",
                "project_status": "In progress",
                "project_sector": "Education",
                "project_location": "Sudan",
                "total_cost_usd": "2500",
                "project_donor": "Saudi Fund",
                "beneficiary_country": "Sudan",
            },
            {
                "project_title": " Health Project ",
                "project_status": "Completed",
                "project_sector": "Health",
                "project_location": "Yemen",
                "total_cost_usd": "1,000",
                "project_donor": "Saudi Fund",
                "beneficiary_country": "Yemen",
            },
        ]
    )


def test_clean_records_normalizes_cost_and_snapshot():
    result = clean_records(sample_dataframe(), "2025-10")

    assert result.iloc[0]["project_title"] == "Health Project"
    assert result.iloc[0]["total_cost_usd"] == 1000
    assert result["snapshot_month"].eq("2025-10").all()
    assert len(result) == 2


def test_clean_records_rejects_invalid_cost():
    raw = sample_dataframe()
    raw.loc[0, "total_cost_usd"] = "unknown"

    with pytest.raises(ValueError, match="Invalid total_cost_usd"):
        clean_records(raw, "2025-10")


def test_clean_records_rejects_missing_column():
    raw = sample_dataframe().drop(columns=["project_sector"])

    with pytest.raises(ValueError, match="Missing expected columns"):
        clean_records(raw, "2025-10")


def test_same_record_is_preserved_in_different_snapshots():
    october = clean_records(sample_dataframe(), "2025-10")
    march = clean_records(sample_dataframe(), "2026-03")

    combined = pd.concat([october, march], ignore_index=True)

    assert len(october) == 2
    assert len(march) == 2
    assert len(combined) == 4
    assert set(combined["snapshot_month"]) == {"2025-10", "2026-03"}


def test_build_metrics_matches_contract_and_aggregates():
    cleaned = clean_records(sample_dataframe(), "2025-10")
    metrics = build_metrics(cleaned)

    assert list(metrics.columns) == [
        "snapshot_month",
        "dimension_type",
        "dimension_value",
        "record_count",
        "total_cost_usd",
    ]

    donor = metrics[
        (metrics["dimension_type"] == "project_donor")
        & (metrics["dimension_value"] == "Saudi Fund")
    ].iloc[0]

    assert donor["record_count"] == 2
    assert donor["total_cost_usd"] == 3500

    country = metrics[
        (metrics["dimension_type"] == "beneficiary_country")
        & (metrics["dimension_value"] == "Yemen")
    ].iloc[0]

    assert country["record_count"] == 1
    assert country["total_cost_usd"] == 1000


def test_build_metrics_returns_empty_result_with_expected_columns():
    empty = pd.DataFrame(
        columns=[
            "project_title",
            "project_status",
            "project_sector",
            "project_location",
            "total_cost_usd",
            "project_donor",
            "beneficiary_country",
            "snapshot_month",
        ]
    )

    result = build_metrics(empty)

    assert list(result.columns) == [
        "snapshot_month",
        "dimension_type",
        "dimension_value",
        "record_count",
        "total_cost_usd",
    ]
    assert result.empty
