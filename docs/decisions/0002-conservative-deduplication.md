# ADR 0002: Conservative Deduplication Strategy

**Date:** 2026-10-12  
**Status:** Accepted

## 1. Context

Our Saudi Foreign Aid dataset contains three CSV snapshots:

- October 2025 (25M10)
- December 2025 (25M12)
- March 2026 (26M03)

The source files do not contain a unique project ID, and approximately 8–9% of rows within each snapshot are exact duplicates.

Some duplicates may represent legitimate repeated activities, but the available data does not provide enough information to confirm this.

This creates a data engineering challenge when calculating total aid amounts and comparing records across snapshots.

## 2. Decision

We decided to adopt a conservative deduplication strategy:

1. Preserve the original CSV files in the raw data layer.
2. Assign a `snapshot_id` to identify the source file of each record.
3. Remove exact duplicate rows within each individual snapshot during data processing.
4. Keep records from different snapshots separate for historical comparison.
5. Use the latest snapshot for current analytical totals to avoid counting the same projects multiple times across snapshots.

## 3. Rationale

Our main goal is to build a reliable and accessible data analytics pipeline for Saudi Foreign Aid data.

Since we cannot confidently distinguish repeated activities from accidental duplicates, counting all identical rows could overestimate total aid amounts.

We chose conservative accounting to reduce this risk while keeping the pipeline manageable within the capstone timeline.

## 4. Trade-offs and Limitations

- Some identical rows may represent legitimate separate activities.
- Removing these rows may underestimate actual aid amounts.
- The dataset does not provide a stable project identifier.
- `snapshot_id` identifies the source snapshot, not an individual project.
- We cannot reliably identify all new projects and updates between snapshots.

## 5. Consequences

- Original data remains available for future reprocessing.
- Processed datasets contain unique rows within each snapshot.
- Snapshot-level comparisons remain possible.
- Analytical totals must not be calculated by simply combining all snapshots.
- The strategy can be revisited if additional project identifiers or activity dates become available.

## 6. Alternatives Considered

**Keep all duplicates:** Preserves potentially legitimate activities but risks overestimating total aid amounts.

**Generate surrogate project keys:** Could support more detailed tracking but requires additional implementation and still cannot guarantee accurate identification without a source project ID.

We selected conservative deduplication as a practical balance between data quality, project scope, and implementation time.