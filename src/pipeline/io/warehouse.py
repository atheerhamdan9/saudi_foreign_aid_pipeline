"""Load Pandas DataFrames into the local DuckDB warehouse."""

import re
from pathlib import Path
from typing import Literal

import duckdb
import pandas as pd

from pipeline.config import WAREHOUSE_PATH

_VALID_TABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load(
    table: str,
    df: pd.DataFrame,
    *,
    db_path: str | Path | None = None,
    if_exists: Literal["replace", "append"] = "replace",
) -> int:
    """Load a DataFrame into DuckDB and return the number of rows loaded.

    By default, the destination table is replaced to make repeated full
    loads predictable. Use if_exists="append" only when appending is intended.
    """
    if not _VALID_TABLE_NAME.fullmatch(table):
        raise ValueError(f"Invalid DuckDB table name: {table!r}")

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    if len(df.columns) == 0:
        raise ValueError("DataFrame must contain at least one column")

    if not df.columns.is_unique:
        raise ValueError("DataFrame column names must be unique")

    if if_exists not in ("replace", "append"):
        raise ValueError("if_exists must be 'replace' or 'append'")

    database_path = Path(db_path or WAREHOUSE_PATH)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(database_path))

    try:
        connection.register("_incoming_dataframe", df)

        existing_table = (
            connection.execute(
                """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_name = ?
            LIMIT 1
            """,
                [table],
            ).fetchone()
            is not None
        )

        quoted_table = f'"{table}"'

        if if_exists == "replace" or not existing_table:
            connection.execute(
                f"CREATE OR REPLACE TABLE {quoted_table} "
                "AS SELECT * FROM _incoming_dataframe"
            )
        else:
            connection.execute(
                f"INSERT INTO {quoted_table} SELECT * FROM _incoming_dataframe"
            )

        return len(df)
    finally:
        connection.unregister("_incoming_dataframe")
        connection.close()


def read_table(
    table: str,
    *,
    db_path: str | Path | None = None,
) -> pd.DataFrame:
    """Read a table from the local DuckDB warehouse as a DataFrame."""
    if not _VALID_TABLE_NAME.fullmatch(table):
        raise ValueError(f"Invalid DuckDB table name: {table!r}")

    database_path = Path(db_path or WAREHOUSE_PATH)
    if not database_path.is_file():
        raise FileNotFoundError(f"DuckDB database not found: {database_path}")

    connection = duckdb.connect(str(database_path), read_only=True)

    try:
        exists = connection.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_name = ?
            LIMIT 1
            """,
            [table],
        ).fetchone()

        if exists is None:
            raise ValueError(f"Table not found in DuckDB: {table}")

        return connection.execute(f'SELECT * FROM "{table}"').df()
    finally:
        connection.close()


def upsert_snapshots(
    table: str,
    df: pd.DataFrame,
    *,
    snapshot_column: str = "snapshot_month",
    db_path: str | Path | None = None,
) -> int:
    """Replace incoming snapshots while preserving other snapshots."""
    if not _VALID_TABLE_NAME.fullmatch(table):
        raise ValueError(f"Invalid DuckDB table name: {table!r}")

    if not _VALID_TABLE_NAME.fullmatch(snapshot_column):
        raise ValueError(f"Invalid snapshot column: {snapshot_column!r}")

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    if df.empty:
        raise ValueError("Cannot upsert an empty DataFrame")

    if not df.columns.is_unique:
        raise ValueError("DataFrame column names must be unique")

    if snapshot_column not in df.columns:
        raise ValueError(f"Missing snapshot column: {snapshot_column}")

    if df[snapshot_column].isna().any():
        raise ValueError("Snapshot values must not be null")

    if not all(isinstance(column, str) for column in df.columns):
        raise ValueError("DataFrame column names must be strings")

    database_path = Path(db_path or WAREHOUSE_PATH)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(database_path))

    try:
        connection.register("_incoming_snapshots", df)

        existing = connection.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'main' AND table_name = ?
            LIMIT 1
            """,
            [table],
        ).fetchone() is not None

        quoted_table = f'"{table}"'
        quoted_snapshot = f'"{snapshot_column}"'

        if not existing:
            connection.execute(
                f"CREATE TABLE {quoted_table} "
                "AS SELECT * FROM _incoming_snapshots"
            )
            return len(df)

        existing_columns = [
            row[0]
            for row in connection.execute(
                f"DESCRIBE {quoted_table}"
            ).fetchall()
        ]

        if existing_columns != list(df.columns):
            raise ValueError(
                f"Schema mismatch for table {table!r}. "
                f"Expected {existing_columns}, got {list(df.columns)}."
            )

        try:
            connection.execute("BEGIN TRANSACTION")
            connection.execute(
                f"DELETE FROM {quoted_table} "
                f"WHERE {quoted_snapshot} IN ("
                f"SELECT DISTINCT {quoted_snapshot} "
                "FROM _incoming_snapshots)"
            )
            connection.execute(
                f"INSERT INTO {quoted_table} "
                "SELECT * FROM _incoming_snapshots"
            )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise

        return len(df)
    finally:
        connection.unregister("_incoming_snapshots")
        connection.close()
