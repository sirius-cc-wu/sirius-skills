# Slice Specification: Default CLI operations to the nearest enclosing scope

**Slice**: `hss-nearest-scope-default-cli-operations-to-the-nearest-enclosing-scope`
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: "hss-nearest-scope Default CLI operations to the nearest enclosing scope"

## 1. Work Item Summary

- **Work Item**: Make planning and proposal helpers default to the nearest enclosing explicit scope from the current working directory.
- **Source Story / Increment / Slice**: HSS-03 / I1 / hss-nearest-scope
- **Requested Outcome**: As an agent operating from inside a subdirectory of a child scope, planning and proposal commands land in that child scope's local artifacts without requiring the user to run from the scope root.
- **Why this matters**: Local registries are only practical when commands keep working from ordinary nested working directories inside the selected scope.
- **Independent Test**: Running planning and proposal commands from a directory nested beneath a child scope writes to the nearest enclosing child scope registries while preserving root fallback outside that child scope.

## 2. Acceptance Scenarios

1. **Given** a child scope with its own `.skills/planning.json` and a deeper working directory inside that scope, **When** a maintainer runs planning commands from the deeper working directory, **Then** the child scope's planning registry and metadata are used.
2. **Given** the same child scope and deeper working directory, **When** a maintainer runs proposal commands from that deeper working directory, **Then** the child scope's proposal registry and metadata are used.
3. **Given** a repository path that is outside any child scope but still inside the repository, **When** a maintainer runs the same commands, **Then** repository-root fallback behavior continues to work.

## 3. Functional Requirements

- **FR-001**: The system MUST resolve the nearest enclosing explicit planning scope from the current working directory.
- **FR-002**: Planning commands run below a child scope root MUST use that child scope's planning registry and feature metadata.
- **FR-003**: Proposal commands run below a child scope root MUST use that child scope's proposal registry and proposal metadata.
- **FR-004**: Repository-root fallback MUST remain the default when no nearer explicit scope exists.
- **FR-005**: The slice MUST define nearest-scope default behavior without adding ambiguity selection or cross-scope targeting.

## 4. Key Entities

- **Nearest Enclosing Scope**: The closest ancestor directory that declares an explicit planning scope for the current command.
- **Nested Working Directory**: A path below the scope root where users may run planning or proposal commands during normal work.
- **Scope Fallback Path**: The repository-root planning area used only when no nearer explicit scope exists.

## 5. Edge Cases

- Commands run from a directory several levels below the child scope root must still resolve the child scope rather than the repository root.
- A repository path outside the child scope but still inside the repository must keep repository-root fallback behavior.
- This slice must not change ambiguity handling when multiple separate child scopes exist elsewhere in the repository.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: An explicit child scope is represented by its own `.skills/planning.json`.
- **A2**: HSS-02 already established local registry ownership once a child scope is selected; this slice extends that behavior to deeper working directories beneath that scope root.

### Dependencies

- **D1**: HSS-01 root fallback and HSS-02 local registry ownership are already in place.
- **D2**: Planning and proposal helpers under `skills/guide-planning/` and `skills/propose/`.

## 7. Success Criteria

- **SC-001**: Planning commands run from a nested child-scope directory use the child scope registry without manual path changes.
- **SC-002**: Proposal commands run from a nested child-scope directory use the child scope registry without manual path changes.
- **SC-003**: Validation confirms repository-root fallback still works when no nearer child scope exists.

## 8. Open Clarifications

- None.
