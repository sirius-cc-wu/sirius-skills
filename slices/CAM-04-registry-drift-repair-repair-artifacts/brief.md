# Slice Specification: Build the cross-artifact repair command

**Slice**: `CAM-04-registry-drift-repair`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: "CAM-04-registry-drift-repair repair-artifacts"

## 1. Work Item Summary

- **Work Item**: Add a conservative repair capability for proposal, feature,
  subfeature, and slice registries.
- **Source Story / Increment / Slice**: CAM-04 / I1 /
  CAM-04-registry-drift-repair
- **Requested Outcome**: A maintainer can preview and optionally rebuild active
  registry/readme files from durable directories plus valid metadata.
- **Why this matters**: Audit can identify drift, but maintainers still need a
  supported remediation path after merges, manual edits, or interrupted runs.
- **Independent Test**: A fixture repo with broken active registries produces a
  dry-run repair plan and can apply rebuilt proposal, feature, subfeature, and
  slice registries from the same repair model.

## 2. Acceptance Scenarios

1. **Given** broken active registries, **When** a maintainer runs repair in
   dry-run mode, **Then** the output shows the planned registry rebuilds without
   writing files.
2. **Given** the maintainer approves the repairs, **When** they rerun with
   `--apply`, **Then** the active registry/readme files are regenerated through
   the existing owner-script writers.
3. **Given** malformed metadata, **When** repair runs, **Then** that artifact is
   left out of rebuilt rows and surfaced as manual follow-up instead of being
   guessed.

## 3. Functional Requirements

- **FR-001**: The repository MUST include a `repair-artifacts` capability for
  conservative registry/readme repair.
- **FR-002**: Repair MUST support dry-run planning before apply mode.
- **FR-003**: Repair MUST rebuild proposal, feature, subfeature, and slice
  active registries/readmes from durable directories plus valid metadata.
- **FR-004**: Repair MUST reuse owner-script normalizers and registry writers.
- **FR-005**: Repair MUST surface skipped malformed metadata as manual follow-up.
- **FR-006**: Apply mode MUST stay limited to derived registry/readme artifacts.

## 4. Key Entities

- **Repair Plan**: The in-memory set of rebuilt rows, skipped artifacts, and
  pending writes for one or more artifact layers.
- **Repair Action**: A planned or applied registry/readme regeneration for one
  artifact layer.
- **Skipped Artifact**: A directory with unreadable metadata that requires
  manual attention.

## 5. Edge Cases

- A selected artifact layer may have no valid rows to rebuild.
- Current registry files may be missing, malformed, or stale.
- One broken metadata file should not block repair of other artifact layers.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The shared inventory helper remains the source of artifact discovery.
- **A2**: Registry/readme files are derived views and safe to regenerate when the
  maintainer explicitly confirms apply mode.

### Dependencies

- **D1**: `skills/audit-artifacts/scripts/artifact_inventory.py`
- **D2**: owner registry writers in proposal, planning, subfeature, and
  execution scripts

## 7. Success Criteria

- **SC-001**: Dry-run output clearly explains intended repair actions.
- **SC-002**: Apply mode rebuilds the selected active registries through owner
  helpers.
- **SC-003**: Repair leaves malformed metadata for manual follow-up instead of
  guessing corrections.

## 8. Open Clarifications

- None.
