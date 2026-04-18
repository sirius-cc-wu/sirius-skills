# Slice Specification: Adopt shared reconciliation across maintenance skills

**Slice**: `WSC-02-maintenance-adoption`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `workflow-state-consistency / WSC-02-maintenance-adoption`

## 1. Work Item Summary

- **Work Item**: Move audit, trace, repair, and report maintenance flows onto the canonical shared workflow-state interpretation and keep managed installed skill copies aligned with that shared behavior.
- **Source Story / Increment / Slice**: `WSC-02` / `I1` / `WSC-02-maintenance-adoption`
- **Requested Outcome**: As an artifact-maintenance skill author, we want maintenance workflows and managed installed skill copies to consume the same shared workflow-state interpretation so they report and act on the same workflow-state findings.
- **Why this matters**: This removes the remaining semantic split between the new shared library and the maintenance skills that still interpret workflow state independently, which is required before later slices can add preview, guardrail, and validation behavior on top of one stable contract.
- **Independent Test**: Targeted audit, trace, repair, and report regression coverage plus a managed install/package check confirm that repo-local maintenance workflows and self-contained installed skill copies use the same shared workflow-state behavior.

## 2. Acceptance Scenarios

1. **Given** a repository with feature and subfeature planning artifacts, **When** audit, trace, repair, and report maintenance flows interpret workflow state, **Then** they all derive their linkage and inventory inputs from the same canonical shared workflow-state behavior.
2. **Given** the known stale-state and traceability cases already covered by maintenance tests, **When** the affected maintenance skills run after this slice, **Then** they continue to agree on the same findings rather than drifting by skill.
3. **Given** a maintainer refreshes the managed installed skill set, **When** the installed copies are produced from the repo, **Then** the self-contained installed maintenance skills include the shared workflow-state support needed to preserve the same behavior outside the repo working tree.

## 3. Functional Requirements

- **FR-001**: The system MUST route audit, trace, repair, and report maintenance workflows through one shared workflow-state interpretation for artifact inventory and slice traceability.
- **FR-002**: The system MUST preserve the existing maintenance-skill behavior for the known workflow-state cases already covered by repository regression tests.
- **FR-003**: The system MUST keep maintenance outputs behaviorally consistent across repo-local execution paths so maintainers do not receive conflicting findings from different maintenance skills for the same repository state.
- **FR-004**: The system MUST ensure the managed installed maintenance-skill set carries the shared workflow-state support required for those skills to run with the same interpretation outside the repo source tree.
- **FR-005**: The slice MUST preserve the existing ownership boundaries in which maintenance skills consume shared workflow-state data without taking over direct mutation rights that belong to other workflow owners.

## 4. Key Entities

- **Maintenance workflow**: One of the audit, trace, repair, or report skill flows that reads repository workflow artifacts and surfaces findings to maintainers.
- **Shared workflow-state interpretation**: The canonical repo-local behavior that normalizes artifact inventory and traceability linkage for maintenance consumers.
- **Managed installed skill set**: The packaged, self-contained copy of repository skills installed for runtime use outside the repo source tree.
- **Workflow-state finding**: A maintenance result derived from artifact inventory and traceability interpretation, such as stale linkage, drift, or missing durable references.

## 5. Edge Cases

- A maintenance skill still depends on a legacy interpretation path after this slice; the resulting behavior would diverge from the other maintenance skills and must be prevented.
- Managed installed skill copies omit the shared workflow-state support; installed maintenance commands would then disagree with repo-local behavior.
- Repositories contain both feature-level and subfeature-level traceability; maintenance skills must stay aligned on both without one flow silently dropping relationships the others preserve.
- Repository artifacts are malformed; maintenance flows should continue surfacing explicit failures instead of masking them with inconsistent fallback behavior.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `WSC-02-shared-library` remains the canonical source of shared workflow-state behavior, and this slice focuses on consumer adoption rather than redefining that contract.
- **A2**: Existing maintenance regression coverage plus one managed install/package check are sufficient to prove that repo-local and installed maintenance behavior stay aligned in this slice.

### Dependencies

- **D1**: `WSC-02-shared-library` is complete and remains the prerequisite shared semantic foundation for all affected maintenance workflows.
- **D2**: The reviewed `workflow-state-consistency` planning packet remains the source of truth for the maintenance-skill adoption scope and the requirement to sync self-contained installed skill copies.

## 7. Success Criteria

- **SC-001**: Audit, trace, repair, and report consume one shared workflow-state interpretation instead of maintaining separate workflow-state logic.
- **SC-002**: Existing maintenance regression coverage continues to pass for the targeted audit, trace, repair, and report workflows after adoption.
- **SC-003**: A managed install/package verification confirms that installed maintenance-skill copies retain the shared workflow-state support needed to match repo-local behavior.

## 8. Open Clarifications

- None.
