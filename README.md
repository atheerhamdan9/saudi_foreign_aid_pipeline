# Saudi Foreign Aid Data Pipeline

A local data engineering pipeline for exploring Saudi foreign aid project
data through standardized records and stakeholder-facing metrics.

## Current pipeline

1. Read the source CSV snapshots from the local raw-data directory.
2. Normalize Arabic source column names to standardized English names.
3. Clean records and convert project costs to numeric values.
4. Remove exact duplicate records within each snapshot.
5. Load raw and cleaned records into DuckDB.
6. Build analytical metrics by snapshot and dimension.
7. Export the metrics to a CSV file and cleaned records to Parquet.

## Source snapshots

The current dataset contains three snapshots:

| Snapshot | Raw records | Cleaned records |
|---|---:|---:|
| October 2025 | 8,371 | 7,700 |
| December 2025 | 8,415 | 7,721 |
| March 2026 | 8,802 | 8,001 |
| Total | 25,588 | 23,422 |

The files are kept locally under
`data/raw/source_a/ingest_date=YYYY-MM-DD/`.

The ingestion date identifies when the files were added to the local project.
The `snapshot_month` field identifies the original source snapshot.

## Run the pipeline

Install the project and development dependencies:

`python -m pip install -e ".[dev]"`

Run the pipeline for an ingestion date:

`make run RUN_DATE=2026-10-11`

Run tests and lint:

`make test`

`make lint`

## Local outputs

- `data/processed/dev.duckdb`: local DuckDB warehouse.
- `data/processed/cleaned_source_a.parquet`: cleaned records.
- `data/output/fct_records_daily.csv`: analytical metrics.

The metrics summarize record counts and reported costs by snapshot, beneficiary
country, project sector, project donor, and project status.

## Data handling

Raw CSV files, DuckDB databases, Parquet files, and generated metrics are local
data artifacts and should not be committed to GitHub. Small test fixtures are
kept in the repository so tests can run without the original dataset.

The current implementation reads locally staged CSV files. Automated fetching
from a public API has not yet been implemented. The definitive source business
key and analytical aggregation rules remain subject to team review.


## Sequential record numbering

The pipeline assigns a sequential `record` number to every source row
after reading the CSV snapshots and before removing duplicates.

Snapshots are processed chronologically:
- October 2025: records 1–8,371
- December 2025: records 8,372–16,786
- March 2026: records 16,787–25,588

The numbering includes duplicate rows in the raw data. During cleaning,
exact duplicates are identified using the seven standardized source
columns, not the `record` number. The retained row keeps its original
record number, so gaps in the cleaned record sequence are expected.

The `record` column is a sequential source-row reference, not a unique
identifier for an aid project across snapshots.
