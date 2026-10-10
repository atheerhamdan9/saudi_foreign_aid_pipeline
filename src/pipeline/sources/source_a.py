
import csv
from pathlib import Path

SOURCE_COLUMN_MAP = {
    "عنوان المشروع": "project_title",
    "حالة المشروع": "project_status",
    "قطاع المشروع": "project_sector",
    "موقع المشروع": "project_location",
    "الجهة المانحة للمشروع": "project_donor",
    "الدولة المستفيدة": "beneficiary_country",
}

EXPECTED_COLUMNS = {
    "project_title",
    "project_status",
    "project_sector",
    "project_location",
    "total_cost_usd",
    "project_donor",
    "beneficiary_country",
}


def _normalize_header(header: str) -> str:
    """Remove extra whitespace and a possible byte-order mark."""
    return " ".join(header.replace("\ufeff", "").strip().split())


def _map_source_columns(source_headers: list[str]) -> dict[str, str]:
    """Map Arabic source headers to standardized English column names."""
    mapping = {}

    for source_header in source_headers:
        header = _normalize_header(source_header)

        if not header:
            raise ValueError("The CSV contains an empty column name.")

        if header in SOURCE_COLUMN_MAP:
            target_name = SOURCE_COLUMN_MAP[header]
        elif any(term in header for term in ("تكاليف", "تكلفة", "تكلف")):
            # Allow variations in the Arabic cost-column heading.
            target_name = "total_cost_usd"
        else:
            raise ValueError(f"Unexpected source column: {source_header!r}")

        if target_name in mapping.values():
            raise ValueError(
                f"More than one source column maps to {target_name!r}."
            )

        mapping[source_header] = target_name

    missing = EXPECTED_COLUMNS - set(mapping.values())
    if missing:
        raise ValueError(f"Missing expected columns: {sorted(missing)}")

    return mapping


def _read_csv(path: Path, encoding: str) -> list[dict[str, str]]:
    """Read one CSV file and normalize its column names."""
    with path.open("r", encoding=encoding, newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(f"The CSV file has no header: {path}")

        column_mapping = _map_source_columns(reader.fieldnames)
        records = []

        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(
                    f"Unexpected extra fields at CSV line {line_number}."
                )

            record = {}

            for source_name, target_name in column_mapping.items():
                value = row.get(source_name)
                record[target_name] = value.strip() if value is not None else ""

            records.append(record)

        return records


def read_source_a(path: str | Path) -> list[dict[str, str]]:
    """Read the Saudi Foreign Aid CSV using UTF-8 or Windows Arabic encoding."""
    csv_path = Path(path)

    try:
        return _read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return _read_csv(csv_path, encoding="cp1256")