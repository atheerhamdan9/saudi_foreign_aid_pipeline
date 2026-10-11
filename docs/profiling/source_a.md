# Source A — Data Profiling

## 1. Source overview

Source A consists of three CSV snapshots of Saudi foreign aid project records. Each file represents a source release from a different month.

| Source file                            | Snapshot month | Original rows | Exact duplicates removed | Rows after deduplication |
| -------------------------------------- | -------------- | ------------: | -----------------------: | -----------------------: |
| `Saudi foreign aid projects 25M10.csv` | `2025-10`      |         8,371 |                      671 |                    7,700 |
| `Saudi foreign aid projects 25M12.csv` | `2025-12`      |         8,415 |                      694 |                    7,721 |
| `Saudi foreign aid projects 26M03.csv` | `2026-03`      |         8,802 |                      801 |                    8,001 |
| **Total**                              |                |    **25,588** |                **2,166** |               **23,422** |

The pipeline standardizes the source headers into seven canonical English columns.

## 2. Standardized schema

| Column                | Description                               |
| --------------------- | ----------------------------------------- |
| `project_title`       | Title of the aid project                  |
| `project_status`      | Reported project status                   |
| `project_sector`      | Sector associated with the project        |
| `project_location`    | Project location                          |
| `total_cost_usd`      | Reported total project cost in US dollars |
| `project_donor`       | Donor entity                              |
| `beneficiary_country` | Country receiving the aid                 |

The source reader handles variations in Arabic column headers and maps them to the standardized English column names.

## 3. Data quality findings

* All seven required fields were found to have no missing values in the three snapshots.
* No missing or invalid project cost values were identified during the initial checks.
* Exact duplicate rows were found in each source snapshot and are removed during cleaning.
* Deduplication is performed separately within each snapshot.
* Records from different snapshots are retained even when their project information is identical, because each snapshot represents a separate source release.

After within-snapshot deduplication, the pipeline retains **23,422 records** from the original 25,588 rows.

## 4. Snapshot handling

The pipeline derives `snapshot_month` from the source filename:

* `25M10` → `2025-10`
* `25M12` → `2025-12`
* `26M03` → `2026-03`

`snapshot_month` identifies the source release represented by a file. It is different from `ingest_date`, which records when the file is brought into the pipeline.

Reprocessing a snapshot should replace that snapshot's records without deleting records belonging to other snapshots.

## 5. Initial dimensional profiling

The following distinct-value counts were observed after cleaning:

| Dimension             | `2025-10` | `2025-12` | `2026-03` |
| --------------------- | --------: | --------: | --------: |
| Beneficiary countries |       174 |       174 |       176 |
| Donor entities        |        21 |        21 |        22 |
| Project sectors       |        36 |        36 |        36 |
| Project statuses      |         2 |         2 |         2 |

These counts describe the available categories in each snapshot; they do not imply that project identities are unique across snapshots.

## 6. Grain and key considerations

The appropriate analytical grain is **one project record in one source snapshot**.

A project title and total cost alone have not been established as a reliable unique key. Project details may change between snapshots, and different records may share the same title or cost. Therefore, the pipeline removes exact duplicate rows within each snapshot instead of assuming that a title-cost combination uniquely identifies a project across the full dataset.

## 7. Analytical use

The cleaned dataset supports descriptive analysis of reported project records and costs by:

* Beneficiary country
* Project sector
* Donor entity
* Project status
* Source snapshot

The current objective is to make the source data more accessible, structured, and analysis-ready. This profiling work does not attempt to measure the economic or social impact of foreign aid.
