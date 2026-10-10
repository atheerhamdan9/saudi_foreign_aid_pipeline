# ADR 0001: Batch Processing or Streaming

- Status: Proposed — pending team review
- Date: 2026-10-10

## Context

The Saudi Foreign Aid Projects dataset is provided as separate CSV
snapshots. The available snapshots are October 2025, December 2025,
and March 2026.

The project aims to make the published data easier to access, explore,
and analyze. The current scope does not require real-time processing.

## Proposed Decision

Use batch processing for the initial pipeline.

Each available CSV snapshot will be processed as a separate input.
The pipeline will preserve the original source files and produce
standardized, validated analytical outputs.

## Rationale

- The source data is delivered as periodic snapshots.
- Batch processing fits file-based ingestion and repeatable transformations.
- Processing snapshots separately helps avoid combining repeated records
  across different versions of the source.
- A streaming architecture would add complexity without a current
  real-time requirement.

## Consequences

- The pipeline will run when a snapshot is available or when the team
  chooses to process it.
- Each snapshot will be tracked and analyzed separately.
- The team must agree on duplicate handling and cost-conversion rules
  before the transformation logic is finalized.
- This proposal can be revised if the source or project requirements change.

## Open Questions

- How should exact duplicate records be handled in analytical outputs?
- How should variations in the total-cost column and its values be handled?
- What output format and analytical grain should the team adopt?
