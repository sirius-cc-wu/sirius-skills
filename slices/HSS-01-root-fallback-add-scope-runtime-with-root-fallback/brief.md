# Slice Specification: Add scope runtime with root fallback

**Slice**: `HSS-01-root-fallback-add-scope-runtime-with-root-fallback`
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: "HSS-01-root-fallback Add scope runtime with root fallback"

## 1. Work Item Summary

- **Work Item**: Introduce a scope-resolution baseline that preserves current repository-root planning behavior.
- **Source Story / Increment / Slice**: HSS-01 / I1 / HSS-01-root-fallback
- **Requested Outcome**: As a repository maintainer, when a repository uses the current single-scope layout, planning and proposal helpers continue to operate against the repository root while a reusable scope runtime is introduced.
- **Why this matters**: The hierarchy-aware workflow needs a compatibility-safe foundation before nested scopes, ambiguity checks, and scoped execution can be layered on top.
- **Independent Test**: Root-scoped planning and proposal commands behave the same as today in a repository without nested local scopes, and the expected planning/proposal tests pass.

## 2. Acceptance Scenarios

1. **Given** a repository that uses the current root `.skills/`, `docs/features/`, and `docs/proposals/` layout, **When** a planning or proposal helper resolves its active scope, **Then** it treats the repository root as the active scope and continues using the root planning and proposal registries.
2. **Given** a repository with no nested explicit scope selected, **When** a maintainer runs the existing planning or proposal commands from the repository root, **Then** the commands keep their current behavior and do not require new input just to preserve the single-scope flow.
3. **Given** the new scope runtime exists, **When** downstream planning or proposal helpers consume it, **Then** they receive a stable scope context that later slices can extend for nested-scope behavior without changing the root fallback contract.

## 3. Functional Requirements

- **FR-001**: The system MUST resolve the repository root as the active scope when no nearer explicit nested scope is in play.
- **FR-002**: The system MUST preserve current root-scoped planning and proposal paths for single-scope repositories.
- **FR-003**: Planning and proposal helpers MUST be able to consume a shared resolved scope context instead of each command inferring root behavior independently.
- **FR-004**: The root fallback behavior MUST remain backward compatible with existing planning and proposal command usage.
- **FR-005**: The slice MUST establish the baseline contract that later nested-scope slices can extend without redefining root fallback semantics.

## 4. Key Entities

- **Scope Root**: The directory selected as the active planning workspace for the current command; in this slice it falls back to the repository root when no nearer explicit scope applies.
- **Scope Context**: The normalized runtime view of the active scope that downstream planning and proposal helpers consume.
- **Root Planning Workspace**: The existing repository-root `.skills/`, `docs/features/`, and `docs/proposals/` layout that must continue to work unchanged for single-scope repositories.

## 5. Edge Cases

- A repository uses only the current root layout and should not need any new scope-specific input.
- A helper begins using the shared scope runtime but must not silently shift planning/proposal writes away from the current root paths.
- Later nested-scope work should be able to extend the runtime without breaking repositories that never add nested scopes.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: This slice focuses on repository-root fallback only; nested local registries, ambiguity handling, and scoped execution belong to later slices.
- **A2**: Existing planning and proposal tests represent the current single-scope behavior that must remain intact.

### Dependencies

- **D1**: Current planning and proposal helpers under `skills/guide-planning/` and `skills/propose/`.
- **D2**: The reviewed planning packet in `docs/features/hierarchical-scope-support/`, especially the HSS-01 backlog entry and validation notes.

## 7. Success Criteria

- **SC-001**: A maintainer can continue using the repository-root planning and proposal workflow without changing command inputs for the single-scope case.
- **SC-002**: The slice establishes one reusable root-fallback scope contract that downstream slices can consume.
- **SC-003**: Validation for root-scoped planning and proposal behavior succeeds after the shared fallback runtime is introduced.

## 8. Open Clarifications

- None.
