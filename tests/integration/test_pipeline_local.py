import csv
from pathlib import Path

from pipeline.cli import run_local_pipeline

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "source_a_sample.csv"
)


def test_local_pipeline_reads_transforms_and_writes_output(tmp_path):
    """The local pipeline should transform a CSV and write the results."""
    output_path = tmp_path / "processed" / "aid_projects.csv"

    record_count = run_local_pipeline(
        input_path=FIXTURE_PATH,
        output_path=output_path,
    )

    assert output_path.exists()
    assert record_count == 2

    with output_path.open("r", encoding="utf-8", newline="") as file:
        records = list(csv.DictReader(file))

    assert len(records) == 2
    assert records[0]["project_title"] == "مشروع صحة"
    assert records[0]["total_cost_usd"] == "1000"

    expected_columns = {
        "project_title",
        "project_status",
        "project_sector",
        "project_location",
        "total_cost_usd",
        "project_donor",
        "beneficiary_country",
    }
    assert set(records[0]) == expected_columns


def test_full_pipeline_loads_duckdb_and_exports_metrics(tmp_path):
    import csv
    import shutil
    from datetime import date

    from pipeline.cli import run_snapshot_pipeline
    from pipeline.io.warehouse import read_table

    source_root = tmp_path / "raw" / "source_a"
    ingest_dir = source_root / "ingest_date=2026-10-11"
    ingest_dir.mkdir(parents=True)

    shutil.copyfile(
        FIXTURE_PATH,
        ingest_dir / "Saudi foreign aid projects 25M10.csv",
    )

    database_path = tmp_path / "processed" / "dev.duckdb"
    output_path = tmp_path / "output" / "fct_records_daily.csv"

    result = run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=output_path,
    )

    assert result["records_read"] == 3
    assert result["records_cleaned"] == 2
    assert database_path.is_file()
    assert result["parquet_path"].is_file()
    assert output_path.is_file()

    raw = read_table("raw_source_a_records", db_path=database_path)
    cleaned = read_table("cleaned_source_a_records", db_path=database_path)
    assert len(raw) == 3
    assert len(cleaned) == 2
    assert set(cleaned["snapshot_month"]) == {"2025-10"}

    with output_path.open(encoding="utf-8-sig", newline="") as file:
        metrics = list(csv.DictReader(file))

    assert len(metrics) == 7
    assert {row["snapshot_month"] for row in metrics} == {"2025-10"}
