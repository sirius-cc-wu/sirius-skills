# Slice Specification: Build the cross-artifact archive command

**Slice**: `arc-safe-slice-archival`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: "arc-safe-slice-archival archive-artifacts"

## 1. Work Item Summary

- **Work Item**: Add a conservative archive capability that reports archive
  candidates across proposals, finalized subfeatures, and slices, and safely
  archives one closed execution slice at a time.
- **Source Story / Increment / Slice**: CAM-05 / I1 /
  arc-safe-slice-archival
- **Requested Outcome**: A maintainer can inspect archive candidates and perform
  explicit closed-slice archival through the execution owner helper.
- **Why this matters**: The repo prefers durable history, but active workflow
  surfaces can become noisy without an explicit archival step.
- **Independent Test**: A fixture repo with archived-state candidates and one
  closed slice produces candidate output and can archive that slice safely from
  the same command surface.

## 2. Acceptance Scenarios

1. **Given** proposals, finalized subfeatures, or closed slices that qualify as
   archive candidates, **When** a maintainer runs the archive command in read-only
   mode, **Then** the output lists those candidates clearly.
2. **Given** one closed execution slice, **When** a maintainer targets it with
   `--artifact-type slice --artifact-id ... --apply`, **Then** the slice is
   archived through the execution owner helper.
3. **Given** an unsupported non-slice apply request, **When** the maintainer
   asks archive to apply it, **Then** the command fails clearly instead of
   inventing a broad cross-artifact archive flow.

## 3. Functional Requirements

- **FR-001**: The repository MUST include an `archive-artifacts` capability for
  archive candidate discovery.
- **FR-002**: The archive command MUST surface candidates for proposals,
  finalized subfeatures, and closed slices.
- **FR-003**: The first version MUST support apply mode only for one closed
  execution slice at a time.
- **FR-004**: Slice archival MUST delegate to the execution owner helper.
- **FR-005**: Text and JSON output MUST be derived from the same archive result.
- **FR-006**: Unsupported apply requests MUST fail clearly.

## 4. Key Entities

- **Archive Candidate**: An artifact that matches the current archive policy in
  read-only mode.
- **Archive Target**: The specific artifact requested for apply mode.
- **Archive Outcome**: The in-memory result describing candidates and any apply
  action performed.

## 5. Edge Cases

- Some repositories may have no current archive candidates.
- Candidate reporting may include artifact layers that do not yet support apply
  mode.
- A targeted slice may exist but not be closed and therefore not be archivable.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: Shared inventory remains the source of candidate discovery.
- **A2**: The execution owner helper remains the only supported slice archive
  writer in v1.

### Dependencies

- **D1**: `skills/audit-artifacts/scripts/artifact_inventory.py`
- **D2**: `skills/guide-execution/scripts/manage_execution.py`
- **D3**: proposal and subfeature metadata readers for candidate discovery

## 7. Success Criteria

- **SC-001**: Candidate discovery is clear and read-only.
- **SC-002**: One closed slice can be archived explicitly through the archive
  command.
- **SC-003**: Unsupported apply targets are rejected clearly.

## 8. Open Clarifications

- None.
