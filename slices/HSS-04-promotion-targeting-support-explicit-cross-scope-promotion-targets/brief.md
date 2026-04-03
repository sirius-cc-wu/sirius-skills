# Slice Specification: Support explicit cross-scope promotion targets

**Slice**: `HSS-04-promotion-targeting-support-explicit-cross-scope-promotion-targets`
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: "HSS-04-promotion-targeting Support explicit cross-scope promotion targets"

## 1. Work Item Summary

- **Work Item**: Allow proposal promotion to target a different canonical planning scope only when the user explicitly provides a target scope.
- **Source Story / Increment / Slice**: HSS-04 / I2 / HSS-04-promotion-targeting
- **Requested Outcome**: As a planner promoting a proposal from one scope into canonical planning elsewhere, I can supply `--target-scope` for the feature destination, while same-scope promotion stays the default when no target scope is provided.
- **Why this matters**: Cross-scope promotion is powerful but unsafe if it can happen implicitly; the destination scope must be an explicit user choice.
- **Independent Test**: Proposal promotion creates canonical planning in the proposal scope by default, and only creates canonical planning in another scope when `--target-scope` is provided.

## 2. Acceptance Scenarios

1. **Given** an accepted proposal in a child scope, **When** a maintainer promotes it without `--target-scope`, **Then** the canonical feature is created in that same child scope.
2. **Given** the same accepted proposal, **When** a maintainer promotes it with `--target-scope` pointing at the repository root or another valid scope, **Then** the canonical feature is created in the selected target scope.
3. **Given** a `--target-scope` outside the repository or otherwise invalid, **When** the maintainer attempts promotion, **Then** the command fails clearly without creating canonical planning in the wrong place.

## 3. Functional Requirements

- **FR-001**: The system MUST keep same-scope proposal promotion as the default when `--target-scope` is omitted.
- **FR-002**: The system MUST accept an additive `--target-scope` for cross-scope proposal promotion.
- **FR-003**: The system MUST create canonical feature planning in the explicitly selected target scope when `--target-scope` is provided.
- **FR-004**: The system MUST fail clearly when `--target-scope` points outside the repository or cannot resolve to a valid scope target.
- **FR-005**: The slice MUST not change the generic ambiguity-handling contract already established by HSS-04-scope-selection.

## 4. Key Entities

- **Proposal Scope**: The scope that owns the accepted proposal being promoted.
- **Target Scope**: The explicitly selected scope where canonical feature planning should be created.
- **Same-Scope Promotion**: The default promotion path where the target scope is the proposal scope itself.

## 5. Edge Cases

- A promotion is launched from a working directory that is not the proposal’s own scope.
- A valid target scope exists but already has canonical planning for the same feature slug.
- A provided `--target-scope` path points outside the repository root.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: HSS-04-scope-selection already provides explicit `--scope` for resolving the proposal’s source scope safely.
- **A2**: The target scope path may be the repository root or a nested child scope, but it must remain inside the same repository.

### Dependencies

- **D1**: HSS-04-scope-selection is already in place.
- **D2**: Proposal promotion logic in `skills/guide-planning/scripts/manage_planning.py`.

## 7. Success Criteria

- **SC-001**: Same-scope promotion remains the default and still works without `--target-scope`.
- **SC-002**: Cross-scope promotion succeeds only when `--target-scope` is explicitly provided.
- **SC-003**: Invalid target scope paths fail clearly without creating canonical planning in the wrong location.

## 8. Open Clarifications

- None.
