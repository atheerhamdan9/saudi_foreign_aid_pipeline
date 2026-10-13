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
    quarantined = read_table(
        "quarantined_source_a_records",
        db_path=database_path,
    )
    assert quarantined.empty
    assert "rejection_reason" in quarantined.columns
    assert "quarantined_at" in quarantined.columns
    assert set(cleaned["snapshot_month"]) == {"2025-10"}

    with output_path.open(encoding="utf-8-sig", newline="") as file:
        metrics = list(csv.DictReader(file))

    assert len(metrics) == 7
    assert {row["snapshot_month"] for row in metrics} == {"2025-10"}

def test_record_numbers_continue_across_snapshots(tmp_path):
    import shutil
    from datetime import date

    from pipeline.cli import run_snapshot_pipeline
    from pipeline.io.warehouse import read_table

    source_root = tmp_path / "raw" / "source_a"
    ingest_dir = source_root / "ingest_date=2026-10-11"
    ingest_dir.mkdir(parents=True)

    filenames = [
        "Saudi foreign aid projects 25M10.csv",
        "Saudi foreign aid projects 25M12.csv",
        "Saudi foreign aid projects 26M03.csv",
    ]

    for filename in filenames:
        shutil.copyfile(FIXTURE_PATH, ingest_dir / filename)

    database_path = tmp_path / "processed" / "dev.duckdb"
    output_path = tmp_path / "output" / "fct_records_daily.csv"

    result = run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=output_path,
    )

    raw = read_table("raw_source_a_records", db_path=database_path)
    cleaned = read_table(
        "cleaned_source_a_records",
        db_path=database_path,
    )

    assert result["records_read"] == 9
    assert result["records_cleaned"] == 6

    # All source rows receive sequential numbers before deduplication.
    assert sorted(raw["record"].tolist()) == list(range(1, 10))

    # The duplicate rows are removed, but surviving numbers are preserved.
    assert sorted(cleaned["record"].tolist()) == [1, 2, 4, 5, 7, 8]

    assert set(cleaned["snapshot_month"]) == {
        "2025-10",
        "2025-12",
        "2026-03",
    }

    assert result["metric_rows"] == 21
        # Rerun the pipeline and verify snapshots are preserved.
    run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=output_path,
    )

    cleaned_after_rerun = read_table(
        "cleaned_source_a_records",
        db_path=database_path,
    )

    assert len(cleaned_after_rerun) == 6
    assert set(cleaned_after_rerun["snapshot_month"]) == {
        "2025-10",
        "2025-12",
        "2026-03",
    }
    assert sorted(cleaned_after_rerun["record"].tolist()) == [
        1, 2, 4, 5, 7, 8
    ]

def test_snapshot_pipeline_missing_directory(tmp_path):
    """Raise a clear error when the source directory is missing."""
    from datetime import date

    import pytest

    from pipeline.cli import run_snapshot_pipeline

    with pytest.raises(
        FileNotFoundError,
        match="Input directory not found",
    ):
        run_snapshot_pipeline(
            date(2026, 10, 11),
            source_root=tmp_path / "missing_source",
        )

def test_snapshot_pipeline_missing_csv_files(tmp_path):
    """Raise a clear error when the source directory has no CSV files."""
    from datetime import date

    import pytest

    from pipeline.cli import run_snapshot_pipeline

    source_root = tmp_path / "raw" / "source_a"
    ingest_dir = source_root / "ingest_date=2026-10-11"
    ingest_dir.mkdir(parents=True)

    with pytest.raises(
        FileNotFoundError,
        match="No CSV files found",
    ):
        run_snapshot_pipeline(
            date(2026, 10, 11),
            source_root=source_root,
        )

def test_pipeline_quarantines_invalid_cost(tmp_path):
    from datetime import date

    import pandas as pd

    from pipeline.cli import run_snapshot_pipeline
    from pipeline.io.warehouse import read_table

    source_root = tmp_path / "raw" / "source_a"
    ingest_dir = source_root / "ingest_date=2026-10-11"
    ingest_dir.mkdir(parents=True)

    records = pd.read_csv(FIXTURE_PATH)
    #records.loc[0, "total_cost_usd"] = "invalid"
    records.loc[0, "مجموع التكاليف $"] = "invalid"

    source_path = ingest_dir / "Saudi foreign aid projects 25M10.csv"
    records.to_csv(source_path, index=False)

    database_path = tmp_path / "processed" / "dev.duckdb"

    result = run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=tmp_path / "output" / "metrics.csv",
    )

    quarantined = read_table(
        "quarantined_source_a_records",
        db_path=database_path,
    )

    assert len(quarantined) == 1
    assert quarantined.iloc[0]["total_cost_usd"] == "invalid"
    assert "total_cost_usd" in quarantined.iloc[0]["rejection_reason"]
    assert result["records_cleaned"] < result["records_read"]

        # Rerun the same snapshot to verify idempotency.
    run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=tmp_path / "output" / "metrics.csv",
    )

    quarantined_after_rerun = read_table(
        "quarantined_source_a_records",
        db_path=database_path,
    )

    assert len(quarantined_after_rerun) == 1

def test_pipeline_all_invalid_records(tmp_path):
    from datetime import date

    import pandas as pd

    from pipeline.cli import run_snapshot_pipeline
    from pipeline.io.warehouse import read_table

    source_root = tmp_path / "raw" / "source_a"
    ingest_dir = source_root / "ingest_date=2026-10-11"
    ingest_dir.mkdir(parents=True)

    records = pd.read_csv(FIXTURE_PATH)
    records["مجموع التكاليف $"] = "invalid"

    records.to_csv(
        ingest_dir / "Saudi foreign aid projects 25M10.csv",
        index=False,
    )

    database_path = tmp_path / "processed" / "dev.duckdb"

    run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=tmp_path / "output" / "metrics.csv",
    )

    quarantined = read_table(
        "quarantined_source_a_records",
        db_path=database_path,
    )

    assert len(quarantined) == len(records)

def test_pipeline_removes_stale_cleaned_records(tmp_path):
    from datetime import date

    import pandas as pd

    from pipeline.cli import run_snapshot_pipeline
    from pipeline.io.warehouse import read_table

    source_root = tmp_path / "raw" / "source_a"
    ingest_dir = source_root / "ingest_date=2026-10-11"
    ingest_dir.mkdir(parents=True)

    source_path = ingest_dir / "Saudi foreign aid projects 25M10.csv"
    records = pd.read_csv(FIXTURE_PATH)
    records.to_csv(source_path, index=False)

    database_path = tmp_path / "processed" / "dev.duckdb"
    output_path = tmp_path / "output" / "metrics.csv"

    run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=output_path,
    )

    # Make all source records invalid.
    records["مجموع التكاليف $"] = "invalid"
    records.to_csv(source_path, index=False)

    run_snapshot_pipeline(
        date(2026, 10, 11),
        source_root=source_root,
        db_path=database_path,
        output_path=output_path,
    )

    cleaned = read_table(
        "cleaned_source_a_records",
        db_path=database_path,
    )
    quarantined = read_table(
        "quarantined_source_a_records",
        db_path=database_path,
    )

    assert cleaned.empty
    assert len(quarantined) == len(records)
