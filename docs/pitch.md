# Saudi Foreign Aid Data Analytics Platform

## Decision

Saudi foreign aid analysts and decision makers need a reliable way to understand where reported Saudi foreign aid is allocated across beneficiary countries, sectors, donor entities, and project statuses using consistent data across published releases.

## Ranked Key Questions

1. Which beneficiary countries receive the highest reported aid value?
2. Which sectors receive the largest reported aid allocations?
3. Which donor entities contribute the most reported aid?

Project status will be used as a supporting analytical dimension and filter.

## Problem

Saudi foreign aid data is publicly available, but it is not fully analysis-ready.

The published data spans multiple releases and contains differences in column naming and formatting. Important categorical values are recorded in Arabic, duplicate-looking records exist, and the source does not provide a reliable unique project identifier.

These issues make consistent analysis across releases more difficult.

## Problem Statement

Transform raw Saudi foreign aid open data into clean, standardized, validated, reusable, and analysis-ready datasets.

## Stakeholders

- Aid policy analysts
- Decision makers
- Data analysts
- Researchers

## Solution

Build a data platform that:

1. Ingests Saudi foreign aid source data.
2. Preserves the original raw records.
3. Standardizes schemas across releases.
4. Cleans and validates the data.
5. Converts reported project costs into numeric values.
6. Standardizes and translates relevant categorical fields.
7. Detects and flags duplicate-looking records.
8. Produces structured analytical datasets.
9. Provides reliable metrics for downstream analysis and visualization.

## Rabbit Holes

The following areas could increase project complexity and will therefore be limited or avoided:

- Attempting to identify the same project across releases without a reliable project ID.
- Translating thousands of individual project titles.
- Attempting to measure the economic or social impact of aid.
- Adding large external datasets that are not required for the core questions.
- Automatically deleting duplicate-looking records when their true identity is uncertain.

## No-Gos

The project will not include:

- Real-time streaming.
- Machine-learning prediction.
- Economic or social impact measurement.
- Political analysis.
- Comparison of Saudi aid with other donor countries.
- Mobile application development.


## Backwards Trace

The analytical questions were traced backwards from the stakeholder question to the metric, analytical model columns, and original source fields.

All metrics are calculated within a single dataset release because the published releases are overlapping snapshots and must not be summed together.

Exact duplicate rows are removed in the cleaned analytical layer before calculating the metrics, while the original raw files remain unchanged.

| Priority | Stakeholder Question | Metric | Mart Columns | Source Fields | Calculation |
|---|---|---|---|---|---|
| 1 | Which beneficiary countries receive the highest reported aid value? | Total reported aid value by beneficiary country | `beneficiary_country`, `total_cost_usd`, `release_code` | Beneficiary Country + Total Project Cost | Filter to one release, remove exact duplicates, group by beneficiary country, sum `total_cost_usd`, and rank descending |
| 2 | Which sectors receive the largest reported aid allocations? | Total reported aid value by sector | `project_sector`, `total_cost_usd`, `release_code` | Project Sector + Total Project Cost | Filter to one release, remove exact duplicates, group by sector, sum `total_cost_usd`, and rank descending |
| 3 | Which donor entities contribute the most reported aid? | Total reported aid value by donor entity | `donor_entity`, `total_cost_usd`, `release_code` | Donor Entity + Total Project Cost | Filter to one release, remove exact duplicates, group by donor entity, sum `total_cost_usd`, and rank descending |
| Supporting | How are project records distributed by status? | Project record count by status | `project_status`, `release_code` | Project Status | Filter to one release, remove exact duplicates, group by project status, and count records |

### Source Field Mapping

The logical source fields are consistent across releases, although the original Arabic column names differ slightly.

| Analytical Field | 25M10 | 25M12 | 26M03 |
|---|---|---|---|
| Beneficiary Country | `الدولة_المستفيدة` | `الدولة المستفيدة` | `الدولة المستفيدة` |
| Project Sector | `قطاع_المشروع` | `قطاع المشروع` | `قطاع المشروع` |
| Donor Entity | `الجهة_المانحة_للمشروع` | `الجهة المانحة للمشروع` | `الجهة المانحة للمشروع` |
| Project Status | `حالة_المشروع` | `حالة المشروع` | `حالة المشروع` |
| Total Project Cost | `مجموع_التكاليف_بالدولار` | `مجموع التكاليف` | `مجموع التكاليف $` |

These fields will be standardized during ingestion and transformation before being exposed to the analytical models.

### Trace Validation

All ranked stakeholder questions can be answered using the available source fields.

No additional external source is required for the current core analytical questions.

The main data-engineering requirements are therefore:

- standardize schema differences between releases,
- convert project cost to a numeric value,
- standardize categorical values,
- remove only exact duplicate rows in the cleaned analytical layer,
- preserve the release identifier so metrics are calculated within the correct snapshot.