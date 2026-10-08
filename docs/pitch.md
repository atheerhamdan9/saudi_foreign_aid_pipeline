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
