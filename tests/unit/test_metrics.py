import pandas as pd
import pytest

from pipeline.metrics import write_metrics


def test_write_metrics_creates_csv(tmp_path):
    output_path = tmp_path / "output" / "metrics.csv"
    metrics = pd.DataFrame(
        [
            {
                "snapshot_month": "2025-10",
                "dimension_type": "beneficiary_country",
                "dimension_value": "Yemen",
                "record_count": 10,
                "total_cost_usd": 1500,
            }
        ]
    )

    result_path = write_metrics(metrics, output_path)

    assert result_path == output_path
    assert output_path.is_file()

    saved = pd.read_csv(output_path)
    assert list(saved.columns) == [
        "snapshot_month",
        "dimension_type",
        "dimension_value",
        "record_count",
        "total_cost_usd",
    ]
    assert saved.loc[0, "dimension_value"] == "Yemen"
    assert saved.loc[0, "total_cost_usd"] == 1500


def test_write_metrics_rejects_missing_columns(tmp_path):
    metrics = pd.DataFrame({"dimension_value": ["Yemen"]})

    with pytest.raises(ValueError, match="Missing metric columns"):
        write_metrics(metrics, tmp_path / "metrics.csv")
