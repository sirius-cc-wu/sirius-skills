# Slice Specification: Keep planning and proposal registries local to each scope

**Slice**: `HSS-02-local-registries-keep-planning-and-proposal-registries-local-to-each-scope`
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: "HSS-02-local-registries Keep planning and proposal registries local to each scope"

## 1. Work Item Summary

- **Work Item**: Make each explicit scope own its own planning and proposal registries and metadata.
- **Source Story / Increment / Slice**: HSS-02 / I1 / HSS-02-local-registries
- **Requested Outcome**: As a subproject owner, when a nested directory defines its own `.skills/`, planning and proposal helpers write features, proposals, and registry updates inside that scope instead of reusing the repository-root planning area.
- **Why this matters**: Hierarchical scope support only becomes useful once nested scopes can keep their own planning state independent from the repository root.
- **Independent Test**: Planning and proposal commands run against a nested explicit scope create and read local `docs/features/` and `docs/proposals/` registries without mutating the root scope registries.

## 2. Acceptance Scenarios

1. **Given** a repository root scope and a nested child scope that both define `.skills/planning.json`, **When** a maintainer creates or updates a feature from the child scope, **Then** the child scope's `docs/features/` registry and metadata are used.
2. **Given** the same repository and child scope, **When** a maintainer creates or updates a proposal in the child scope, **Then** the child scope's `docs/proposals/` registry and metadata are used.
3. **Given** a repository with both root and child scopes, **When** work is created in the child scope, **Then** the root scope registries remain unchanged unless the root scope itself is the active scope.

## 3. Functional Requirements

- **FR-001**: The system MUST keep feature registries and feature metadata local to the resolved scope.
- **FR-002**: The system MUST keep proposal registries and proposal metadata local to the resolved scope.
- **FR-003**: The system MUST initialize missing planning and proposal registries inside the active scope without redirecting writes to the repository root.
- **FR-004**: The system MUST preserve repository-root ownership for root-scope work while allowing child scopes to own separate local planning state.
- **FR-005**: The slice MUST establish local registry ownership semantics without introducing cross-scope merged registries or cross-scope writes.

## 4. Key Entities

- **Explicit Scope**: A directory that declares its own planning workspace through local `.skills/` configuration.
- **Scope-Local Planning Registry**: The `docs/features/README.md` and `docs/features/registry.json` pair owned by one resolved scope.
- **Scope-Local Proposal Registry**: The `docs/proposals/README.md` and `docs/proposals/registry.json` pair owned by one resolved scope.

## 5. Edge Cases

- A child scope creates its first feature or proposal and must initialize local registries in that child scope.
- The same slug may exist in both the root scope and a child scope, but child-scope work must not silently rewrite the root scope entry.
- Repositories that never add child scopes must continue using the root registries without behavior changes.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: Explicit child scopes are represented by local `.skills/planning.json` files.
- **A2**: Defaulting to the nearest enclosing scope from an arbitrary nested working directory is handled by HSS-03; this slice only establishes correct local ownership once a child scope is selected.

### Dependencies

- **D1**: HSS-01 root fallback is already in place to provide the shared scope runtime and compatibility baseline.
- **D2**: Current planning and proposal helpers under `skills/guide-planning/` and `skills/propose/`.

## 7. Success Criteria

- **SC-001**: A child scope can create and track its own features without updating the root feature registry.
- **SC-002**: A child scope can create and track its own proposals without updating the root proposal registry.
- **SC-003**: Validation confirms that root and child scopes keep independent planning and proposal registries.

## 8. Open Clarifications

- None.
