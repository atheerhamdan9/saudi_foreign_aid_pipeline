
"""Transform Saudi foreign aid source records for analysis."""

from decimal import Decimal, InvalidOperation
from typing import Any

EXPECTED_COLUMNS = {
    "project_title",
    "project_status",
    "project_sector",
    "project_location",
    "total_cost_usd",
    "project_donor",
    "beneficiary_country",
}


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
    """Clean source records, convert costs, and remove exact duplicates."""
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