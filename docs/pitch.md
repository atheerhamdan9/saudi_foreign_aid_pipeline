# Saudi Foreign Aid Data Analytics Platform

## Decision

Saudi foreign aid analysts and decision makers need a reliable way to understand where reported Saudi foreign aid is allocated across beneficiary countries, sectors, donor entities, and project statuses using consistent, snapshot-aware data across published releases.

## Ranked Key Questions

1. Which beneficiary countries receive the highest reported aid value?
2. Which sectors receive the largest reported aid allocations?
3. Which donor entities contribute the most reported aid?

Project status is used as a supporting analytical dimension.

---

## Problem

Saudi foreign aid data is publicly available, but it is not fully analysis-ready.

The published data spans multiple overlapping releases and contains differences in column naming, formatting, and source representation.

The source also contains repeated records and does not provide a reliable unique project identifier.

These issues make it difficult to produce consistent and trustworthy analysis across releases.

---

## Problem Statement

Transform raw Saudi foreign aid open data into clean, standardized, validated, reusable, snapshot-aware, and analysis-ready datasets.

---

## Stakeholders

- Aid policy analysts
- Decision makers
- Data analysts
- Researchers

---

## Solution

Build a data platform that:

1. Ingests Saudi foreign aid CSV snapshots.
2. Preserves the original raw source records for traceability.
3. Standardizes inconsistent Arabic source schemas.
4. Validates source structure and record quality.
5. Assigns stable sequential source-record numbers before cleaning.
6. Separates invalid records into a quarantine layer.
7. Converts reported project costs into numeric values.
8. Removes standardized exact duplicates only within the same snapshot.
9. Preserves identical records appearing in different snapshots as historical observations.
10. Produces reusable dbt analytical models.
11. Loads analytical data into BigQuery for downstream serving.
12. Provides a Streamlit dashboard for stakeholder analysis.

---

## Rabbit Holes

The following areas could increase project complexity and are intentionally limited or avoided:

- Attempting to identify the same project across releases without a reliable project ID.
- Translating thousands of individual project titles.
- Performing fuzzy entity resolution across snapshots.
- Attempting to measure the economic or social impact of aid.
- Adding large external datasets that are not required for the core analytical questions.
- Automatically deleting duplicate-looking records whose identity cannot be verified.

---

## No-Gos

The project does not include:

- Real-time streaming.
- Machine-learning prediction.
- Economic or social impact measurement.
- Political analysis.
- Comparison of Saudi aid with other donor countries.
- Mobile application development.
- Cross-release project identity matching.

---

## Snapshot Strategy

The available source releases represent overlapping historical snapshots:

| Source Release | Snapshot Month |
|---|---|
| `25M10` | `2025-10` |
| `25M12` | `2025-12` |
| `26M03` | `2026-03` |

All analytical metrics are calculated within an individual `snapshot_month`.

The releases must not be summed together as if each snapshot represented independent aid activity.

---

## Duplicate Handling

The source does not provide a reliable unique project identifier.

The project therefore uses a conservative deduplication strategy.

During cleaning:

1. Text fields are standardized.
2. Reported project costs are converted to numeric values.
3. Duplicate comparison uses the seven standardized source fields.
4. Deduplication is scoped to a single `snapshot_month`.
5. The earliest assigned source `record` number is retained.
6. Identical records appearing in different snapshots remain separate historical observations.

The raw layer remains unchanged for traceability.

---

## Backwards Trace

The analytical questions were traced backwards from each stakeholder question to the metric, analytical mart fields, and original source fields.

The primary analytical mart is:

`fct_records_by_snapshot`

Its grain is:

`snapshot_month + dimension_type + dimension_value`

| Priority | Stakeholder Question | Metric | Mart Fields | Source Fields | Calculation |
|---|---|---|---|---|---|
| 1 | Which beneficiary countries receive the highest reported aid value? | Total reported aid value by beneficiary country | `snapshot_month`, `dimension_type`, `dimension_value`, `total_cost_usd` | `beneficiary_country`, `total_cost_usd` | Filter to one `snapshot_month`, filter `dimension_type = beneficiary_country`, and rank `total_cost_usd` descending |
| 2 | Which sectors receive the largest reported aid allocations? | Total reported aid value by sector | `snapshot_month`, `dimension_type`, `dimension_value`, `total_cost_usd` | `project_sector`, `total_cost_usd` | Filter to one `snapshot_month`, filter `dimension_type = project_sector`, and rank `total_cost_usd` descending |
| 3 | Which donor entities contribute the most reported aid? | Total reported aid value by donor entity | `snapshot_month`, `dimension_type`, `dimension_value`, `total_cost_usd` | `project_donor`, `total_cost_usd` | Filter to one `snapshot_month`, filter `dimension_type = project_donor`, and rank `total_cost_usd` descending |
| Supporting | How are project records distributed by status? | Project record count by status | `snapshot_month`, `dimension_type`, `dimension_value`, `record_count` | `project_status` | Filter to one `snapshot_month`, filter `dimension_type = project_status`, and rank or compare `record_count` |

---

## Source Field Mapping

The logical source fields are consistent across releases, although the original Arabic column names differ slightly.

| Analytical Field | 25M10 | 25M12 | 26M03 |
|---|---|---|---|
| Beneficiary Country | `الدولة_المستفيدة` | `الدولة المستفيدة` | `الدولة المستفيدة` |
| Project Sector | `قطاع_المشروع` | `قطاع المشروع` | `قطاع المشروع` |
| Donor Entity | `الجهة_المانحة_للمشروع` | `الجهة المانحة للمشروع` | `الجهة المانحة للمشروع` |
| Project Status | `حالة_المشروع` | `حالة المشروع` | `حالة المشروع` |
| Total Project Cost | `مجموع_التكاليف_بالدولار` | `مجموع التكاليف` | `مجموع التكاليف $` |

These source fields are normalized during ingestion before being exposed to downstream analytical models.

---

## Data Engineering Flow

The platform currently uses two complementary execution paths.

### Local Development Workflow

Apache Airflow orchestrates the local development workflow:

```text
Saudi Open Data CSV Snapshots
              ↓
        Source Validation
              ↓
     Schema Standardization
              ↓
 Assign record + snapshot_month
              ↓
        Raw Preservation
              ↓
        Record Validation
          ↙          ↘
       Valid        Invalid
         ↓             ↓
      Cleaning      Quarantine
         ↓
Snapshot-scoped Deduplication
         ↓
       DuckDB
         ↓
     dbt (dev)
```

Airflow coordinates the local workflow through:

```text
prepare_run
    ↓
ingest_snapshot
    ↓
dbt_incremental
```

### Cloud Analytical Path

The implemented cloud analytical path is separate from the local Airflow workflow:

```text
Python --cloud
      ↓
Google Cloud Storage
      ↓
BigQuery Raw
      ↓
dbt (BigQuery)
      ↓
BigQuery Analytical Mart
      ↓
Streamlit Dashboard
```

The current Airflow DAG does not yet orchestrate this complete cloud path end-to-end.

---

## Trace Validation

All ranked stakeholder questions can be answered using the available source fields.

No additional external source is required for the current core analytical questions.

The main data-engineering requirements are therefore:

- standardize schema differences between releases,
- preserve raw records for traceability,
- validate record quality,
- quarantine invalid records,
- convert reported project cost to a numeric value,
- remove standardized exact duplicates within each snapshot,
- preserve `snapshot_month`,
- prevent aggregation across overlapping snapshots,
- build reusable analytical models,
- expose reliable metrics through BigQuery and Streamlit.

---

## Analytical Output

The final platform provides snapshot-aware analysis for:

- Beneficiary countries
- Project sectors
- Donor entities
- Project statuses

The dashboard uses the BigQuery analytical mart as its serving layer.

Reported project costs represent values published in the source data and should not be interpreted as confirmed disbursements.