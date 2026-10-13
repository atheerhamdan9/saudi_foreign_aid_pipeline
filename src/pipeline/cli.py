"""Command-line entry point for the Saudi Foreign Aid pipeline."""

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from pipeline.config import (
    CONTRACTS_DIR,
    SOURCE_A_DIR,
    WAREHOUSE_PATH,
)
from pipeline.contracts import load_contract
from pipeline.io.warehouse import load, read_table, upsert_snapshots
from pipeline.metrics import write_metrics
from pipeline.quarantine import split_valid_and_quarantined
from pipeline.sources.saudi_aid_projects import extract
from pipeline.sources.source_a import read_source_a
from pipeline.transform import (
    SOURCE_COLUMNS,
    build_metrics,
    clean_records,
    transform_records,
)

OUTPUT_COLUMNS = SOURCE_COLUMNS
SNAPSHOT_PATTERN = re.compile(r"(?<!\d)(\d{2})M(\d{2})(?!\d)")


def _snapshot_month_from_filename(path: Path) -> str:
    """Get the original snapshot month from a filename such as 25M10."""
    match = SNAPSHOT_PATTERN.search(path.stem)
    if match is None:
        raise ValueError(
            f"Cannot determine snapshot month from filename: {path.name}"
        )

    year = 2000 + int(match.group(1))
    month = int(match.group(2))

    if not 1 <= month <= 12:
        raise ValueError(f"Invalid snapshot month in filename: {path.name}")

    return date(year, month, 1).strftime("%Y-%m")

def _needs_record_schema_migration(
    table: str,
    incoming: pd.DataFrame,
    db_path: Path,
) -> bool:
    """Check whether an existing table needs the new record column."""
    try:
        existing = read_table(table, db_path=db_path)
    except (FileNotFoundError, ValueError):
        return False

    if "record" not in incoming.columns or "record" in existing.columns:
        return False

    existing_months = set(existing["snapshot_month"].dropna().astype(str))
    incoming_months = set(incoming["snapshot_month"].dropna().astype(str))

    if not existing_months.issubset(incoming_months):
        raise ValueError(
            f"Cannot safely migrate {table!r} to the record schema. "
            f"Existing snapshots: {sorted(existing_months)}; "
            f"incoming snapshots: {sorted(incoming_months)}. "
            "Include all existing snapshots in the input directory."
        )

    return True


def run_local_pipeline(
    input_path: str | Path,
    output_path: str | Path,
) -> int:
    """Keep the initial CSV-to-CSV pipeline available for existing tests."""
    records = read_source_a(input_path)
    transformed_records = transform_records(records)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(transformed_records)

    return len(transformed_records)



def run_snapshot_pipeline(
    run_date: date,
    *,
    source_root: str | Path = SOURCE_A_DIR,
    db_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, int | Path]:
    """Load snapshots, number source rows, clean them, and export metrics."""
    ingest_dir = Path(source_root) / f"ingest_date={run_date.isoformat()}"

    if not ingest_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {ingest_dir}")

    # Sort by the actual snapshot date, not by file creation date.
    files = sorted(
        ingest_dir.glob("*.csv"),
        key=_snapshot_month_from_filename,
    )
    if not files:
        raise FileNotFoundError(f"No CSV files found in: {ingest_dir}")

    raw_frames = []
    cleaned_frames = []
    seen_months = set()
    records_read = 0
    records_cleaned = 0
    next_record = 1
    quarantine_frames = []

    # Read snapshots in chronological order and number rows before cleaning.
    for path in files:
        snapshot_month = _snapshot_month_from_filename(path)

        if snapshot_month in seen_months:
            raise ValueError(
                f"More than one input file for snapshot {snapshot_month}"
            )
        seen_months.add(snapshot_month)

        records = read_source_a(path)
        if not records:
            raise ValueError(f"Source file contains no records: {path.name}")

        raw = pd.DataFrame.from_records(
            records,
            columns=SOURCE_COLUMNS,
        )

        # The sequence includes every source row, including duplicates.
        raw.insert(
            0,
            "record",
            range(next_record, next_record + len(raw)),
        )
        next_record += len(raw)

        raw["snapshot_month"] = snapshot_month

        # Deduplicate on source fields while preserving the assigned record.
        #cleaned = clean_records(raw, snapshot_month)
        valid, quarantined = split_valid_and_quarantined(raw)
        #Collect rejected records for quarantine storage.
        quarantine_frames.append(quarantined)
        # Clean only valid records.
        cleaned = clean_records(valid, snapshot_month)

        raw_frames.append(raw)
        cleaned_frames.append(cleaned)
        records_read += len(raw)
        records_cleaned += len(cleaned)

    raw_batch = pd.concat(raw_frames, ignore_index=True)
    cleaned_batch = pd.concat(cleaned_frames, ignore_index=True)
    quarantine_batch = pd.concat(
        quarantine_frames,
        ignore_index=True,
    )

    database_path = Path(db_path or WAREHOUSE_PATH)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    # Land raw source records as Parquet, preserving all rows.
    raw_parquet_path = database_path.parent / "raw_source_a.parquet"
    raw_batch.to_parquet(raw_parquet_path, index=False)

    incoming_months = set(raw_batch["snapshot_month"].astype(str))
    incoming_batches = [
        ("raw_source_a_records", raw_batch),
        ("cleaned_source_a_records", cleaned_batch),
    ]

    # Inspect existing tables before changing either table.
    tables_to_rebuild = set()

    for table, batch in incoming_batches:
        try:
            existing = read_table(table, db_path=database_path)
        except (FileNotFoundError, ValueError):
            # The table does not exist yet.
            continue

        if "snapshot_month" not in existing.columns:
            raise ValueError(
                f"Cannot safely update {table!r}: "
                "the existing table has no snapshot_month column."
            )

        existing_months = set(
            existing["snapshot_month"].dropna().astype(str)
        )

        # Global record numbering requires the input batch to include
        # all snapshots already stored in the warehouse.
        if not existing_months.issubset(incoming_months):
            missing_months = sorted(existing_months - incoming_months)
            raise ValueError(
                "Global record numbering requires all existing snapshots "
                f"in the input directory. Missing snapshots: {missing_months}"
            )

        # Rebuild a legacy table when its columns differ from the new schema.
        if list(existing.columns) != list(batch.columns):
            tables_to_rebuild.add(table)

    # Upgrade the old schema if necessary; otherwise replace incoming months.
    """
    for table, batch in incoming_batches:
        if table in tables_to_rebuild:
            load(table, batch, db_path=database_path)
        else:
            upsert_snapshots(
                table,
                batch,
                db_path=database_path,
            )
    """
    for table, batch in incoming_batches:
        if table == "cleaned_source_a_records":
            load(table, batch, db_path=database_path)
        elif batch.empty or table in tables_to_rebuild:
            load(table, batch, db_path=database_path)
        else:
            upsert_snapshots(
                table,
                batch,
                db_path=database_path,
           )
    load(
        "quarantined_source_a_records",
        quarantine_batch,
        db_path=database_path,
    )

    # Export all cleaned snapshots currently in the warehouse.
    all_cleaned = read_table(
        "cleaned_source_a_records",
        db_path=database_path,
    )
    parquet_path = database_path.parent / "cleaned_source_a.parquet"
    all_cleaned.to_parquet(parquet_path, index=False)

    # Metrics remain aggregated; the row-level record ID is not a metric.
    """
    metrics_batch = build_metrics(all_cleaned)
    upsert_snapshots(
        "fct_records_daily",
        metrics_batch,
        db_path=database_path,
    )
    """
    metrics_batch = build_metrics(all_cleaned)
    if metrics_batch.empty:
        load(
            "fct_records_daily",
            metrics_batch,
            db_path=database_path,
        )
    else:
        upsert_snapshots(
            "fct_records_daily",
            metrics_batch,
            db_path=database_path,
        )

    all_metrics = read_table(
        "fct_records_daily",
        db_path=database_path,
    )
    metrics_path = write_metrics(all_metrics, output_path)

    return {
        "records_read": records_read,
        "records_cleaned": records_cleaned,
        "metric_rows": len(all_metrics),
        "warehouse_path": database_path,
        "parquet_path": parquet_path,
        "metrics_path": metrics_path,
    }


def _validate_contracts() -> None:
    """Load the project contracts before running the pipeline."""
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


def _parse_iso_date(value: str) -> date:
    """Parse a YYYY-MM-DD command-line date."""
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Date must use YYYY-MM-DD format."
        ) from exc

    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError(
            "Date must use YYYY-MM-DD format."
        )

    return parsed


def main(argv: list[str] | None = None) -> int:
    """Validate contracts by default or run a dated local pipeline."""
    args = sys.argv[1:] if argv is None else argv

    # Preserve the previous contract-validation behavior when no arguments
    # are passed.
    if not args:
        _validate_contracts()
        return 0

    parser = argparse.ArgumentParser(
        description="Saudi Foreign Aid local data pipeline"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Load a local ingestion-date partition and export metrics",
    )
    run_parser.add_argument(
        "--date",
        required=True,
        type=_parse_iso_date,
        help="Ingestion date, in YYYY-MM-DD format",
    )

    run_parser.add_argument(
        "--cloud",
        action="store_true",
        help="Upload the raw Parquet file to GCS",
    )

    parsed = parser.parse_args(args)
    _validate_contracts()

    if parsed.command == "run":
        result = run_snapshot_pipeline(parsed.date)
        if parsed.cloud:
            from pipeline.config import GCS_BUCKET_NAME
            if not GCS_BUCKET_NAME:
                parser.error("GCS_BUCKET_NAME is required when using --cloud")
            raw_parquet_path = result["warehouse_path"].parent / "raw_source_a.parquet"

            landed_uri = extract(
                run_date=parsed.date,
                local_path=raw_parquet_path,
                bucket_name=GCS_BUCKET_NAME,
            )

            print(f"Landed URI: {landed_uri}")
        print(f"Records read: {result['records_read']:,}")
        print(f"Records after cleaning: {result['records_cleaned']:,}")
        print(f"Metric rows: {result['metric_rows']:,}")
        print(f"DuckDB: {result['warehouse_path']}")
        print(f"Cleaned Parquet: {result['parquet_path']}")
        print(f"Metrics CSV: {result['metrics_path']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
