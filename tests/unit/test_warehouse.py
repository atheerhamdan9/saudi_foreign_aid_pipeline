import duckdb
import pandas as pd
import pytest

from pipeline.io.warehouse import load, read_table, upsert_snapshots


def test_load_creates_table(tmp_path):
    db_path = tmp_path / "test.duckdb"
    df = pd.DataFrame(
        {
            "snapshot_month": ["2025-10", "2025-12"],
            "project_title": ["Project A", "Project B"],
        }
    )

    loaded = load("raw_source_a", df, db_path=db_path)

    assert loaded == 2

    with duckdb.connect(str(db_path), read_only=True) as connection:
        rows = connection.execute(
            "SELECT snapshot_month, project_title "
            "FROM raw_source_a ORDER BY snapshot_month"
        ).fetchall()

    assert rows == [
        ("2025-10", "Project A"),
        ("2025-12", "Project B"),
    ]


def test_load_replaces_table_by_default(tmp_path):
    db_path = tmp_path / "test.duckdb"

    load("raw_source_a", pd.DataFrame({"value": [1, 2]}), db_path=db_path)
    load("raw_source_a", pd.DataFrame({"value": [3]}), db_path=db_path)

    with duckdb.connect(str(db_path), read_only=True) as connection:
        rows = connection.execute("SELECT value FROM raw_source_a").fetchall()

    assert rows == [(3,)]


def test_load_can_append_explicitly(tmp_path):
    db_path = tmp_path / "test.duckdb"

    load("raw_source_a", pd.DataFrame({"value": [1]}), db_path=db_path)
    load(
        "raw_source_a",
        pd.DataFrame({"value": [2]}),
        db_path=db_path,
        if_exists="append",
    )

    with duckdb.connect(str(db_path), read_only=True) as connection:
        count = connection.execute("SELECT COUNT(*) FROM raw_source_a").fetchone()[0]

    assert count == 2


def test_load_rejects_invalid_table_name(tmp_path):
    with pytest.raises(ValueError, match="Invalid DuckDB table name"):
        load(
            "raw; DROP TABLE users",
            pd.DataFrame({"value": [1]}),
            db_path=tmp_path / "test.duckdb",
        )



def test_read_table_returns_dataframe(tmp_path):
    db_path = tmp_path / "test.duckdb"
    original = pd.DataFrame(
        {
            "snapshot_month": ["2025-10"],
            "total_cost_usd": [1000],
        }
    )

    load("source_records", original, db_path=db_path)
    result = read_table("source_records", db_path=db_path)

    assert result.to_dict("records") == original.to_dict("records")



def test_upsert_snapshots_preserves_other_snapshots(tmp_path):
    db_path = tmp_path / "test.duckdb"

    october = pd.DataFrame(
        {"snapshot_month": ["2025-10"], "value": [1]}
    )
    december = pd.DataFrame(
        {"snapshot_month": ["2025-12"], "value": [2]}
    )
    updated_october = pd.DataFrame(
        {"snapshot_month": ["2025-10"], "value": [3]}
    )

    upsert_snapshots("snapshot_records", october, db_path=db_path)
    upsert_snapshots("snapshot_records", december, db_path=db_path)
    upsert_snapshots(
        "snapshot_records", updated_october, db_path=db_path
    )

    result = read_table(
        "snapshot_records", db_path=db_path
    ).sort_values("snapshot_month")

    assert result.to_dict("records") == [
        {"snapshot_month": "2025-10", "value": 3},
        {"snapshot_month": "2025-12", "value": 2},
    ]
