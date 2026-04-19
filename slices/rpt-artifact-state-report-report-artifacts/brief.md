# Slice Specification: Build the cross-artifact report command

**Slice**: `rpt-artifact-state-report`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: "rpt-artifact-state-report report-artifacts"

## 1. Work Item Summary

- **Work Item**: Add a read-only reporting capability for proposals, features,
  subfeatures, and slices.
- **Source Story / Increment / Slice**: CAM-03 / I1 /
  rpt-artifact-state-report
- **Requested Outcome**: A maintainer can generate concise operational summaries
  for workflow state, grouped by artifact type, status, or parent feature.
- **Why this matters**: Maintainers still have to inspect several folders and
  registries to answer simple operational questions about active, reviewed,
  stale, or closed workflow packets.
- **Independent Test**: A fixture repo with proposals, features, subfeatures,
  and slices in different statuses produces grouped report output and stale
  classifications from one shared result shape.

## 2. Acceptance Scenarios

1. **Given** a repo with multiple artifact types, **When** a maintainer runs the
   report command with no grouping override, **Then** the output summarizes
   artifact totals and stale counts by type.
2. **Given** artifacts in different lifecycle states, **When** a maintainer runs
   the report command grouped by status, **Then** the output shows coherent
   status buckets without inventing a new lifecycle model.
3. **Given** subfeatures and slices tied to parent features, **When** a
   maintainer groups by parent, **Then** the output shows operational load by
   feature ownership.

## 3. Functional Requirements

- **FR-001**: The repository MUST include a `report-artifacts` capability for
  read-only operational reporting.
- **FR-002**: The report MUST summarize proposals, features, subfeatures, and
  slices from durable repo metadata and registries.
- **FR-003**: The report MUST support grouping by artifact type, lifecycle
  status, and parent feature.
- **FR-004**: The report MUST support explicit stale classification through a
  configurable threshold.
- **FR-005**: The report MUST provide both human-readable and JSON output from
  the same report result.
- **FR-006**: The report MUST remain read-only and MUST NOT rewrite repo
  artifacts.

## 4. Key Entities

- **Report Record**: A normalized row describing one proposal, feature,
  subfeature, or slice.
- **Report Group**: A grouped aggregate keyed by artifact type, status, or
  parent feature.
- **Stale Classification**: A derived flag based on `updated_at` and the chosen
  stale-day threshold.

## 5. Edge Cases

- Some artifact types may have no parent feature context.
- Different owner scripts expose different status vocabularies.
- Repos may contain valid artifacts with no updated timestamp recent enough to
  avoid staleness under the selected threshold.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The shared inventory helper remains the source of artifact discovery.
- **A2**: The first version can expose grouped summaries without writing
  persistent report files.

### Dependencies

- **D1**: `skills/audit-artifacts/scripts/artifact_inventory.py`
- **D2**: metadata readers owned by proposal, planning, subfeature, and
  execution scripts

## 7. Success Criteria

- **SC-001**: One command can summarize workflow state across the supported
  artifact types.
- **SC-002**: Text and JSON output are derived from the same underlying report
  result.
- **SC-003**: Stale classification stays explicit and configurable.

## 8. Open Clarifications

- None.
