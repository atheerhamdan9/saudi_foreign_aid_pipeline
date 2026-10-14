"""Separate valid source records from quarantined records."""

from datetime import UTC, datetime

import pandas as pd

from pipeline.transform import TEXT_COLUMNS, _parse_cost


def split_valid_and_quarantined(
    raw: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separate invalid records while preserving original values."""

    valid_indices = []
    rejected = []
    seen_records = set()

    for index, row in raw.iterrows():
        reasons = []
        if "record" in raw.columns:
            record_number = pd.to_numeric(
                pd.Series([row["record"]]), errors="coerce"
            ).iloc[0]
            if (
                pd.isna(record_number)
                or not float(record_number).is_integer()
                or record_number < 1
            ):
                reasons.append("record: must be a positive integer")

        if "record" in raw.columns and pd.notna(record_number):
            if record_number in seen_records:
                reasons.append("record: duplicate record number")
            else:
                seen_records.add(record_number)

        for column in TEXT_COLUMNS:
            value = row[column]
            if pd.isna(value) or (
                isinstance(value, str) and not value.strip()
            ):
                reasons.append(f"{column}: missing or blank")

        try:
            _parse_cost(row["total_cost_usd"])
        except (ValueError, TypeError):
            reasons.append("total_cost_usd: invalid value")

        if reasons:
            rejected_row = row.to_dict()
            rejected_row["rejection_reason"] = "; ".join(reasons)
            rejected_row["quarantined_at"] = datetime.now(UTC)
            rejected.append(rejected_row)
        else:
            valid_indices.append(index)

    valid = raw.loc[valid_indices].copy()

    quarantine_columns = (
        list(raw.columns)
        + ["rejection_reason", "quarantined_at"]
    )

    quarantined = pd.DataFrame(
        rejected,
        columns=quarantine_columns,
    )

    return valid, quarantined
