# Slice Specification: Create shared workflow-state library

**Slice**: `WSC-02-shared-library`  
**Created**: 2026-04-17  
**Status**: Draft  
**Input**: `workflow-state-consistency / WSC-02-shared-library`

## 1. Work Item Summary

- **Work Item**: Establish the canonical repo-local workflow-state library that normalizes artifact loading, traceability parsing, and reconciliation inputs for workflow maintenance.
- **Source Story / Increment / Slice**: `WSC-02` / `I1` / `WSC-02-shared-library`
- **Requested Outcome**: As an artifact-maintenance skill author, we want one shared workflow-state library so maintenance workflows can interpret artifact identity and slice linkage consistently.
- **Why this matters**: This removes the duplicated semantic logic that let maintenance skills drift apart and miss or disagree on the same workflow-state problems.
- **Independent Test**: Targeted audit and trace regression tests confirm that one canonical workflow-state interpretation still resolves feature and subfeature traceability correctly after the shared library is introduced.

## 2. Acceptance Scenarios

1. **Given** a repository with feature and subfeature planning artifacts, **When** a maintenance workflow loads workflow state, **Then** it can obtain normalized artifact and traceability records from one canonical repo-local library.
2. **Given** the concrete stale-state case that motivated this feature, **When** shared workflow-state helpers are used to interpret slice linkage, **Then** audit and trace validation continue to agree on the affected feature, subfeature, and slice relationships.
3. **Given** existing lifecycle owners and registry writers, **When** the shared workflow-state library is introduced, **Then** it interprets workflow state without taking over direct mutation of planning or execution metadata.

## 3. Functional Requirements

- **FR-001**: The system MUST provide one repo-local workflow-state library that exposes canonical artifact inventory and traceability-loading behavior for workflow maintenance flows.
- **FR-002**: The shared library MUST normalize feature-level and subfeature-level traceability into one consistent interpretation of planned-slice and execution-slice linkage.
- **FR-003**: The shared library MUST provide reusable reconciliation inputs that preserve the existing concrete stale-state coverage already proven by current audit and trace regression cases.
- **FR-004**: The shared library MUST remain read-only with respect to planning and execution metadata unless a separate owner command explicitly chooses to write state.
- **FR-005**: The slice MUST preserve a deterministic validation path for the shared semantics using existing repository tests for the affected maintenance workflows.

## 4. Key Entities

- **Workflow-state library**: The canonical repo-local shared package that owns normalized artifact loading and traceability interpretation for maintenance workflows.
- **Artifact inventory record**: A normalized view of proposals, features, subfeatures, planned slices, and execution slices loaded from durable repo artifacts.
- **Traceability record**: The normalized mapping between story IDs, planned slices, and execution slices used to reason about linkage and completion state.
- **Reconciliation input**: Shared semantic data passed to maintenance workflows so they can derive findings without each skill re-implementing linkage rules.

## 5. Edge Cases

- A target feature or subfeature omits `slice-traceability.md`; the shared library should still return a safe empty linkage result instead of inventing records.
- Traceability rows contain multiple planned slices or execution slices; the shared library must preserve the recorded relationships without silently collapsing them.
- Metadata files are malformed or incomplete; the shared library should surface explicit failures rather than guessing repairs.
- Feature-level and subfeature-level traceability coexist in one repository; the shared library must keep ownership boundaries explicit so callers can distinguish them.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: This slice establishes the shared semantic foundation only; broader maintenance-skill adoption and install/package sync are handled by later planned slices.
- **A2**: Existing regression fixtures around audit and trace artifact interpretation are sufficient to prove that the shared semantics preserve the motivating stale-state behavior.

### Dependencies

- **D1**: The reviewed `workflow-state-consistency` planning packet remains the source of truth for scope, especially the owner-boundary rule that the shared library stays read-only.
- **D2**: Existing maintenance workflow tests for audit and trace behavior remain available as the primary independent validation path for this slice.

## 7. Success Criteria

- **SC-001**: Repository maintainers can point maintenance workflows at one canonical workflow-state library instead of duplicating artifact-loading and traceability semantics inside each skill.
- **SC-002**: The shared library preserves the known stale-state interpretation needed by current audit and trace regression coverage.
- **SC-003**: The slice completes without expanding direct write ownership beyond the existing lifecycle and registry-owner commands.

## 8. Open Clarifications

- None.
