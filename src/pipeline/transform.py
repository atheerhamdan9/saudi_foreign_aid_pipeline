"""Pure transformations for Saudi Foreign Aid source data."""

import math
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

SOURCE_COLUMNS = [
    "project_title",
    "project_status",
    "project_sector",
    "project_location",
    "total_cost_usd",
    "project_donor",
    "beneficiary_country",
]

TEXT_COLUMNS = [
    "project_title",
    "project_status",
    "project_sector",
    "project_location",
    "project_donor",
    "beneficiary_country",
]

DIMENSION_COLUMNS = [
    "beneficiary_country",
    "project_sector",
    "project_donor",
    "project_status",
]

METRIC_COLUMNS = [
    "snapshot_month",
    "dimension_type",
    "dimension_value",
    "record_count",
    "total_cost_usd",
]

EXPECTED_COLUMNS = set(SOURCE_COLUMNS)


def _parse_cost(value: Any) -> int | float:
    """Convert a cost string, such as '1,000', into a number."""
    if value is None:
        raise ValueError("total_cost_usd must not be empty.")

    normalized = str(value).strip().replace(",", "").replace("$", "")

    if not normalized:
        raise ValueError("total_cost_usd must not be empty.")

    try:
        cost = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(
            f"Invalid total_cost_usd value: {value!r}"
        ) from exc

    if not cost.is_finite():
        raise ValueError(f"Invalid total_cost_usd value: {value!r}")

    if cost == cost.to_integral_value():
        return int(cost)

    return float(cost)


def transform_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Legacy list-based transformation retained for compatibility."""
    transformed = []
    seen = set()

    for record in records:
        missing = EXPECTED_COLUMNS - set(record)
        if missing:
            raise ValueError(
                f"Missing expected columns: {sorted(missing)}"
            )

        cleaned = {
            key: value.strip() if isinstance(value, str) else value
            for key, value in record.items()
        }
        cleaned["total_cost_usd"] = _parse_cost(
            cleaned["total_cost_usd"]
        )

        signature = tuple(
            (key, cleaned[key]) for key in sorted(cleaned)
        )
        if signature not in seen:
            seen.add(signature)
            transformed.append(cleaned)

    return transformed


def clean_records(
    raw: pd.DataFrame,
    snapshot_month: str,
) -> pd.DataFrame:
    """Clean one source snapshot and preserve its identity.

    Exact duplicates are removed only within this snapshot. Call this
    function separately for each source file.
    """
    if not isinstance(raw, pd.DataFrame):
        raise TypeError("raw must be a pandas DataFrame")

    if not raw.columns.is_unique:
        raise ValueError("Source column names must be unique")

    missing = EXPECTED_COLUMNS - set(raw.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {sorted(missing)}")

    try:
        parsed_month = datetime.strptime(snapshot_month, "%Y-%m")
    except ValueError as exc:
        raise ValueError(
            "snapshot_month must use YYYY-MM format"
        ) from exc

    if parsed_month.strftime("%Y-%m") != snapshot_month:
        raise ValueError("snapshot_month must use YYYY-MM format")

    cleaned = raw.loc[:, SOURCE_COLUMNS].copy()

    for column in TEXT_COLUMNS:
        cleaned[column] = cleaned[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        blank_mask = cleaned[column].isna() | cleaned[column].map(
            lambda value: isinstance(value, str) and not value
        )
        if blank_mask.any():
            raise ValueError(f"{column} contains missing or blank values")

    cost_text = (
        cleaned["total_cost_usd"]
        .astype("string")
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
    )
    costs = pd.to_numeric(cost_text, errors="coerce")
    finite_mask = costs.map(
        lambda value: math.isfinite(value) if pd.notna(value) else False
    )

    if not finite_mask.all():
        bad_rows = costs.index[~finite_mask].tolist()[:5]
        raise ValueError(
            f"Invalid total_cost_usd values at row indexes: {bad_rows}"
        )

    cleaned["total_cost_usd"] = costs

    # Normalize first, then deduplicate inside this snapshot only.
    cleaned = cleaned.drop_duplicates(
        subset=SOURCE_COLUMNS
    ).reset_index(drop=True)

    cleaned["snapshot_month"] = snapshot_month
    return cleaned[SOURCE_COLUMNS + ["snapshot_month"]]


def build_metrics(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Aggregate cleaned records to the fct_records_daily contract grain."""
    required = EXPECTED_COLUMNS | {"snapshot_month"}
    missing = required - set(cleaned.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {sorted(missing)}")

    if cleaned.empty:
        return pd.DataFrame(columns=METRIC_COLUMNS)

    metric_frames = []

    for dimension in DIMENSION_COLUMNS:
        summary = (
            cleaned.groupby(
                ["snapshot_month", dimension],
                as_index=False,
                sort=True,
            )
            .agg(
                record_count=("project_title", "size"),
                total_cost_usd=("total_cost_usd", "sum"),
            )
            .rename(columns={dimension: "dimension_value"})
        )
        summary.insert(1, "dimension_type", dimension)
        metric_frames.append(summary[METRIC_COLUMNS])

    return (
        pd.concat(metric_frames, ignore_index=True)
        .sort_values(
            ["snapshot_month", "dimension_type", "dimension_value"]
        )
        .reset_index(drop=True)
    )
