# Slice Specification: Build the cross-artifact audit command

**Slice**: `CAM-01-cross-artifact-audit`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: "CAM-01-cross-artifact-audit audit-artifacts"

## 1. Work Item Summary

- **Work Item**: Add a read-only audit capability for proposals, features,
  subfeatures, and slices.
- **Source Story / Increment / Slice**: CAM-01 / I1 /
  CAM-01-cross-artifact-audit
- **Requested Outcome**: A maintainer can run one audit-oriented capability and
  get a coherent report of missing required files, registry drift, broken
  cross-artifact links, and slice relation issues.
- **Why this matters**: Durable workflow artifacts are now spread across
  multiple layers, and maintainers need one supported inspection path instead of
  manual directory-by-directory checks.
- **Independent Test**: A fixture repo with missing files, registry drift, and
  broken links produces grouped audit findings in both human-readable and JSON
  forms.

## 2. Acceptance Scenarios

1. **Given** a repository with valid proposals, features, subfeatures, and
   slices, **When** a maintainer runs the audit capability, **Then** the output
   reports a clean result without mutating any artifacts.
2. **Given** a repository with missing required files or invalid metadata,
   **When** a maintainer runs the audit capability, **Then** the output records
   those findings per artifact instead of failing on the first broken packet.
3. **Given** a repository with registry drift or broken cross-artifact links,
   **When** a maintainer runs the audit capability, **Then** the output makes
   those inconsistencies explicit enough for later repair or reporting work.

## 3. Functional Requirements

- **FR-001**: The repository MUST include an `audit-artifacts` user-facing
  capability for proposals, features, subfeatures, and slices.
- **FR-002**: The audit MUST surface artifact-local validation failures such as
  missing required files or invalid metadata without stopping the rest of the
  audit.
- **FR-003**: The audit MUST surface registry drift between registry rows and
  on-disk artifact folders.
- **FR-004**: The audit MUST surface broken cross-artifact links, including
  proposal-to-feature, subfeature-to-parent, and slice-relation problems.
- **FR-005**: The audit MUST provide both human-readable and JSON output from
  the same findings set.
- **FR-006**: The audit MUST remain read-only and MUST NOT repair or rewrite
  artifacts.

## 4. Key Entities

- **Artifact Inventory**: The in-memory catalog of proposals, features,
  subfeatures, and slices assembled from registries and on-disk folders.
- **Finding**: A structured audit result with artifact context, category,
  severity, and message.
- **Registry Reference**: A machine-readable registry row that should align with
  an artifact directory on disk.
- **Cross-Artifact Link**: A durable reference such as proposal target feature,
  subfeature parent feature, or slice relation.

## 5. Edge Cases

- Registry files may exist while specific artifact directories are missing.
- Artifact metadata may be invalid JSON or structurally incomplete.
- Some artifact directories may exist on disk but be absent from their registry.
- Slice relations may point at missing targets or miss reciprocal entries.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: Existing owner scripts remain the source of truth for artifact-local
  validation rules.
- **A2**: The first version does not need configurable time-based stale
  thresholds to be useful.

### Dependencies

- **D1**: `skills/propose/scripts/manage_proposals.py`
- **D2**: `skills/guide-planning/scripts/manage_planning.py`
- **D3**: `skills/add-subfeature/scripts/manage_subfeatures.py`
- **D4**: `skills/guide-execution/scripts/manage_execution.py`

## 7. Success Criteria

- **SC-001**: One audit run reports findings across proposal, planning,
  subfeature, and slice artifacts from one command.
- **SC-002**: Invalid or missing metadata in one artifact does not prevent the
  audit from reporting other findings.
- **SC-003**: Human-readable output and JSON output describe the same finding
  set.

## 8. Open Clarifications

- None.
