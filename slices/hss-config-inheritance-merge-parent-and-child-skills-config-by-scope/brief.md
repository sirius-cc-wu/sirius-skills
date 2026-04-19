# Slice Specification: Merge parent and child .skills config by scope

**Slice**: `hss-config-inheritance-merge-parent-and-child-skills-config-by-scope`
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: "hss-config-inheritance Merge parent and child .skills config by scope"

## 1. Work Item Summary

- **Work Item**: Merge parent and child `.skills` config values through the scope chain with child override precedence.
- **Source Story / Increment / Slice**: HSS-06 / I2 / hss-config-inheritance
- **Requested Outcome**: As a project adopter working with nested scopes, child scopes inherit parent planning, execution, and conventions config by default while still being able to override specific keys locally.
- **Why this matters**: Nested scopes are not practical if every child scope must repeat the full `.skills` configuration instead of inheriting generic defaults.
- **Independent Test**: Planning, proposal, bootstrap, and execution helpers read merged config from the scope chain, preserve unknown keys, and resolve inherited relative paths against the active scope root.

## 2. Acceptance Scenarios

1. **Given** a root scope with planning, execution, or conventions config and a child scope that overrides only one key, **When** a command runs in the child scope, **Then** the effective config contains both inherited parent keys and child overrides.
2. **Given** a child scope that omits a config file or omits some keys, **When** a command runs in that child scope, **Then** the missing values are inherited from parent scopes.
3. **Given** an inherited relative directory value such as `planning_dir` or `slice_dir`, **When** a child scope consumes that value, **Then** the path resolves relative to the child scope root rather than the parent scope where it was defined.

## 3. Functional Requirements

- **FR-001**: The system MUST merge `.skills/planning.json`, `.skills/execution.json`, and `.skills/conventions.json` from outer scope to inner scope with child override precedence.
- **FR-002**: The system MUST preserve unknown config keys during merged reads.
- **FR-003**: Relative directory values inherited from parent scopes MUST resolve against the active scope root.
- **FR-004**: Planning, proposal, bootstrap, and execution config consumers MUST use the merged config view where relevant to this slice.
- **FR-005**: The slice MUST not yet relocate execution registries or slices; that behavior belongs to hss-scoped-execution.

## 4. Key Entities

- **Scope Chain**: The ordered parent-to-child list of scopes from repository root to the active scope.
- **Merged Config View**: The effective config object produced by overlaying child keys onto parent keys.
- **Inherited Relative Path**: A directory-like config value defined in a parent scope but interpreted relative to the active child scope.

## 5. Edge Cases

- A child scope overrides one config key while inheriting other keys from multiple ancestor scopes.
- Unknown config keys must survive the merge instead of being dropped.
- An active child scope inherits `planning_dir`, `proposal_dir`, or `slice_dir` from a parent and must resolve the path locally.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: HSS-01 through HSS-04 already established scope resolution, local registries, ambiguity handling, and explicit promotion targeting.
- **A2**: Scope-local execution registry placement itself is deferred to hss-scoped-execution even though execution config merging starts here.

### Dependencies

- **D1**: Shared scope runtime in `skills/guide-planning/scripts/scope_runtime.py`.
- **D2**: Config consumers in `skills/guide-planning/`, `skills/propose/`, `skills/bootstrap/`, and `skills/guide-execution/`.

## 7. Success Criteria

- **SC-001**: Child scopes inherit parent planning, execution, and conventions defaults unless they explicitly override them.
- **SC-002**: Unknown config keys remain visible in merged config reads.
- **SC-003**: Validation confirms inherited relative paths resolve against the active child scope root rather than the parent definition scope.

## 8. Open Clarifications

- None.
