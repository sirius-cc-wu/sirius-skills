# Slice Specification: Build the cross-artifact trace command

**Slice**: `tat-trace-artifact-lineage`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: "tat-trace-artifact-lineage trace-artifacts"

## 1. Work Item Summary

- **Work Item**: Add a read-only lineage capability for proposals, features,
  subfeatures, planned slices, and execution slices.
- **Source Story / Increment / Slice**: CAM-02 / I1 /
  tat-trace-artifact-lineage
- **Requested Outcome**: A maintainer can request the lineage of one artifact or
  a broader lineage summary and get a coherent result built only from durable
  repo signals.
- **Why this matters**: Cross-artifact relationships already exist in metadata
  and planning docs, but maintainers still have to assemble them manually across
  multiple folders and formats.
- **Independent Test**: A fixture repo with linked proposals, features,
  subfeatures, planned slices, and execution slices produces targeted lineage
  output and summary lineage output from the same underlying graph.

## 2. Acceptance Scenarios

1. **Given** a proposal that targets or promotes a canonical feature, **When** a
   maintainer traces that proposal, **Then** the output shows the linked feature
   lineage without guessing unrelated nodes.
2. **Given** a subfeature with planned and execution slice mappings,
   **When** a maintainer traces that subfeature or planned slice, **Then** the
   output includes the parent feature plus planned/execution slice lineage where
   the traceability docs record it.
3. **Given** no specific target artifact, **When** a maintainer runs the trace
   capability, **Then** the output summarizes the discovered lineage graph in a
   reusable form.

## 3. Functional Requirements

- **FR-001**: The repository MUST include a `trace-artifacts` user-facing
  capability for targeted lineage queries and broader lineage summaries.
- **FR-002**: The trace MUST reuse durable repo signals from metadata,
  traceability docs, and slice relations instead of inferring unsupported links.
- **FR-003**: The trace MUST model proposal, feature, subfeature, planned-slice,
  and execution-slice lineage where those links are present.
- **FR-004**: The trace MUST provide both human-readable and JSON output from
  the same lineage graph.
- **FR-005**: The trace MUST fail clearly when a requested target artifact does
  not exist.
- **FR-006**: The trace MUST remain read-only and MUST NOT rewrite repo
  artifacts.

## 4. Key Entities

- **Lineage Graph**: The in-memory typed graph built from metadata,
  traceability docs, and slice relations.
- **Traceability Record**: A parsed row from `slice-traceability.md` that links
  planned slice IDs to execution slice IDs and story context.
- **Target Artifact**: The specific artifact type and ID requested for a
  targeted trace.
- **Lineage Edge**: A durable relation such as proposal-to-feature,
  subfeature-to-parent, planned-slice-to-execution-slice, or slice-to-slice.

## 5. Edge Cases

- Traceability tables may vary in shape as long as the required lineage columns
  are present.
- A requested artifact may exist but have no downstream or upstream lineage
  links.
- Some repositories may record planned slice lineage without execution slice IDs
  yet.
- Slice relation metadata may connect execution slices even when planning docs do
  not.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The shared audit inventory helper remains the source of artifact
  discovery for this slice.
- **A2**: The first version can treat stories as row context instead of
  first-class graph nodes.

### Dependencies

- **D1**: `skills/audit-artifacts/scripts/artifact_inventory.py`
- **D2**: proposal metadata owned by `skills/propose/scripts/manage_proposals.py`
- **D3**: planning metadata and traceability docs under `docs/features/`
- **D4**: slice metadata owned by `skills/guide-execution/scripts/manage_execution.py`

## 7. Success Criteria

- **SC-001**: A targeted trace query returns the connected durable lineage for a
  supported artifact type.
- **SC-002**: Summary output and targeted output come from the same lineage
  graph.
- **SC-003**: Missing or absent lineage signals do not cause the trace command
  to invent unsupported links.

## 8. Open Clarifications

- None.
