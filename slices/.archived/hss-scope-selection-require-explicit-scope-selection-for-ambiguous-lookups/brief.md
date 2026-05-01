# Slice Specification: Require explicit scope selection for ambiguous lookups

**Slice**: `hss-scope-selection-require-explicit-scope-selection-for-ambiguous-lookups`
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: "hss-scope-selection Require explicit scope selection for ambiguous lookups"

## 1. Work Item Summary

- **Work Item**: Detect ambiguous multi-scope feature and proposal lookups and require explicit scope selection.
- **Source Story / Increment / Slice**: HSS-04 / I2 / hss-scope-selection
- **Requested Outcome**: As a planner working in a repository with nested scopes, slug-only lookups stop with candidate scope information when more than one scope could match, and commands allow an explicit `--scope` to resolve the correct scope.
- **Why this matters**: Once multiple scopes can own local planning state, slug-only updates must fail safely instead of relying on an implicit or accidental scope choice.
- **Independent Test**: Ambiguous feature and proposal lookups fail with candidate scope paths, while `--scope` allows the same operations to complete against the intended scope.

## 2. Acceptance Scenarios

1. **Given** the same feature or proposal slug exists in more than one plausible scope, **When** a maintainer runs a slug-only status or validation command without `--scope`, **Then** the command fails with an ambiguity error and candidate scope paths.
2. **Given** the same ambiguous slug and an explicit `--scope`, **When** the maintainer reruns the command, **Then** the command operates only on the selected scope.
3. **Given** a single-scope repository or an unambiguous lookup inside the active scope, **When** the maintainer omits `--scope`, **Then** the command keeps the current behavior.

## 3. Functional Requirements

- **FR-001**: The system MUST detect when a slug-only feature or proposal selector matches more than one plausible scope.
- **FR-002**: The system MUST fail ambiguous lookups safely and surface candidate scope paths.
- **FR-003**: The system MUST accept an additive `--scope` selector for ambiguous planning and proposal lookup commands.
- **FR-004**: The system MUST keep single-scope and unambiguous lookups backward compatible when `--scope` is omitted.
- **FR-005**: The slice MUST not introduce cross-scope promotion targeting or config inheritance behavior.

## 4. Key Entities

- **Plausible Scope**: The active scope and any nested explicit scopes beneath it that could legitimately own the selector being looked up.
- **Ambiguous Lookup**: A slug-only selector that matches more than one plausible scope.
- **Explicit Scope Selector**: A user-provided `--scope` path that resolves one intended scope for the command.

## 5. Edge Cases

- A slug exists in both the active scope and a nested child scope.
- A slug does not exist in the active scope but does exist in one or more nested child scopes.
- A provided `--scope` path points outside the repository or does not resolve to the intended scope.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: Nearest-enclosing default behavior from the working directory is already in place from HSS-03.
- **A2**: Explicit scope selection in this slice covers generic lookup commands; explicit cross-scope promotion targets belong to hss-promotion-targeting.

### Dependencies

- **D1**: HSS-01 through HSS-03 already established root fallback, local registries, and nearest-scope defaulting.
- **D2**: Planning and proposal helper CLIs under `skills/guide-planning/` and `skills/propose/`.

## 7. Success Criteria

- **SC-001**: Ambiguous planning lookups fail with candidate scope information instead of updating the wrong scope.
- **SC-002**: Ambiguous proposal lookups fail with candidate scope information instead of updating the wrong scope.
- **SC-003**: Explicit `--scope` selection allows the same commands to succeed against the intended scope while existing single-scope flows still work.

## 8. Open Clarifications

- None.
