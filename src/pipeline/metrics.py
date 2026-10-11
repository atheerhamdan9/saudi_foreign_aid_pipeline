"""Export stakeholder metrics to a local CSV file."""

from pathlib import Path

import pandas as pd

from pipeline.config import OUTPUT_DIR
from pipeline.transform import METRIC_COLUMNS

DEFAULT_METRICS_PATH = OUTPUT_DIR / "fct_records_daily.csv"


def write_metrics(
    metrics: pd.DataFrame,
    output_path: str | Path | None = None,
) -> Path:
    """Validate and export metrics to a UTF-8 CSV file."""
    if not isinstance(metrics, pd.DataFrame):
        raise TypeError("metrics must be a pandas DataFrame")

    if not metrics.columns.is_unique:
        raise ValueError("Metric column names must be unique")

    missing = set(METRIC_COLUMNS) - set(metrics.columns)
    if missing:
        raise ValueError(f"Missing metric columns: {sorted(missing)}")

    result = metrics.loc[:, METRIC_COLUMNS].copy()

    if result.isna().any().any():
        raise ValueError("Metrics contain missing values")

    allowed_dimensions = {
        "beneficiary_country",
        "project_sector",
        "project_donor",
        "project_status",
    }
    if not result["dimension_type"].isin(allowed_dimensions).all():
        raise ValueError("Metrics contain an unsupported dimension_type")

    destination = Path(output_path or DEFAULT_METRICS_PATH)
    destination.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(destination, index=False, encoding="utf-8-sig")

    return destination
