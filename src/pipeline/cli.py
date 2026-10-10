
"""Command-line entry point and local pipeline functions."""

import csv
from pathlib import Path

from pipeline.config import CONTRACTS_DIR
from pipeline.contracts import load_contract
from pipeline.sources.source_a import read_source_a
from pipeline.transform import transform_records

OUTPUT_COLUMNS = [
    "project_title",
    "project_status",
    "project_sector",
    "project_location",
    "total_cost_usd",
    "project_donor",
    "beneficiary_country",
]


def run_local_pipeline(
    input_path: str | Path,
    output_path: str | Path,
) -> int:
    """Read a source CSV, transform records, and write a local CSV."""
    records = read_source_a(input_path)
    transformed_records = transform_records(records)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(transformed_records)

    return len(transformed_records)


def main() -> int:
    """Validate the project's data contracts."""
    contract_files = [
        CONTRACTS_DIR / "source_a.yml",
        CONTRACTS_DIR / "fct_records_daily.yml",
    ]

    for path in contract_files:
        contract = load_contract(path)
        print(
            f"OK: {contract['dataset']} "
            f"({len(contract['columns'])} columns)"
        )

    print("Contract validation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())