# Saudi Aid Project — Data Profiling

## 1. Purpose

The purpose of this profiling is to assess the structure, quality, and reliability of the Saudi Foreign Aid Projects dataset before implementing the data pipeline.

The profiling focuses on identifying duplicate records, validating potential keys, checking missing values, understanding data coverage, verifying data types, and identifying data quality issues.

## 2. Data Source Overview

**Source:** Saudi Open Data Portal

**Dataset:** Saudi Foreign Aid Projects

**Format:** CSV

**Available Snapshots:**
- October 2025 — 25M10
- December 2025 — 25M12
- March 2026 — 26M03

Each snapshot is profiled independently to understand changes in the source data over time.

### Initial Dataset Structure

| Snapshot | Total Rows | Total Columns |
|---|---:|---:|
| October 2025 | 8,371 | 7 |
| December 2025 | 8,415 | 7 |
| March 2026 | 8,802 | 7 |

### Initial Finding

All three snapshots contain 7 columns, but column naming conventions differ across snapshots, particularly the Total Cost column.

Column names must be standardized during transformation.

## 3. Grain

The initial assumption is that each row represents a record associated with a Saudi foreign aid project.

However, repeated project titles and costs may indicate duplicate records or multiple records associated with the same project.

The final grain will be determined after examining repeated records and identifying a reliable unique identifier.

## 4. Keys

A potential composite key was evaluated using:

- Project Title
- Total Cost

### Composite Key Analysis

| Metric | October 2025 | December 2025 | March 2026 |
|---|---:|---:|---:|
| Total Rows | 8,371 | 8,415 | 8,802 |
| Unique Composite Keys | 7,549 | 7,570 | 7,842 |
| Extra Rows with Repeated Keys | 822 | 845 | 960 |
| Rows in Repeated Key Groups | 1,052 | 1,076 | 1,206 |

**Finding:** The combination of Project Title and Total Cost is not unique and cannot reliably identify every source record.

**Action:** Investigate repeated key groups and evaluate alternative identifiers before defining the final primary key.

## 5. Uniqueness

### Exact Duplicate Analysis

| Snapshot | Total Rows | Unique Rows | Exact Duplicates | Duplicate Rate |
|---|---:|---:|---:|---:|
| October 2025 | 8,371 | 7,700 | 671 | 8.02% |
| December 2025 | 8,415 | 7,721 | 694 | 8.25% |
| March 2026 | 8,802 | 8,001 | 801 | 9.10% |

**Finding:** Exact duplicate records were detected in all three snapshots. March 2026 has the highest duplicate rate.

**Action:** Preserve the original records in the raw layer and remove exact duplicates within each snapshot in the analytical layer.

## 6. Nulls

### Missing Values Results

- October 2025: 0% missing values (8,371 records).
- December 2025: 0% missing values (8,415 records).
- March 2026: 0% missing values (8,802 records).

**Finding:** No missing or blank values were detected across all 7 columns in the three snapshots.

**Note:** Placeholder values such as N/A or Unknown have not yet been evaluated.

## 7. Coverage

The profiling measures:

- Total records per snapshot.
- Number of distinct beneficiary countries.
- Number of distinct project sectors.
- Number of distinct donors.

### Coverage Analysis

| Metric | October 2025 | December 2025 | March 2026 |
|---|---:|---:|---:|
| Beneficiary Countries | 174 | 174 | 176 |
| Project Sectors | 36 | 36 | 36 |
| Project Donors | 21 | 21 | 22 |
| Project Statuses | 2 | 2 | 2 |

**Finding:** The March 2026 snapshot shows an increase in distinct beneficiary country values and donors, while the number of sectors and project statuses remains unchanged.

These counts represent distinct values in the source data and have not yet been validated for naming consistency.

## 8. Data Types

The expected analytical data types include:

| Field | Expected Type |
|---|---|
| Project Title | String |
| Beneficiary Country | String |
| Project Sector | String |
| Total Cost | Numeric |
| Project Donor | String |
| Project Status | String |
| Project Location | String |

**Action:** Validate the actual source types and identify columns requiring conversion.

## 9. Surprises & Data Quality Issues

### Findings

- **Schema Inconsistency:** Column naming conventions differ across snapshots, particularly the Total Cost column.
- **Duplicate Records:** Exact duplicate rows were identified in all three snapshots.
- **Key Uniqueness:** The combination of Project Title and Total Cost is not unique.
- **Data Standardization:** Arabic categorical values may require translation and standardization during transformation.

**Action:** Address confirmed data quality issues in the transformation layer while preserving the original raw datasets.

## 10. Initial Data Quality Decisions

- Keep raw CSV files unchanged.
- Profile each snapshot independently.
- Do not combine snapshot funding totals without accounting for repeated records.
- Standardize column names and relevant categorical values into English.
- Apply data cleaning and validation rules in the transformation layer.
- Document any unresolved data quality issues.
