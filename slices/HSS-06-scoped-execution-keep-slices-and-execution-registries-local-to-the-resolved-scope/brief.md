# Slice Specification: Keep slices and execution registries local to the resolved scope

**Slice**: `HSS-06-scoped-execution-keep-slices-and-execution-registries-local-to-the-resolved-scope`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: "HSS-06-scoped-execution Keep slices and execution registries local to the resolved scope"

## 1. Work Item Summary

- **Work Item**: Apply the resolved execution scope to guide-execution and slice bootstrap so nested scopes manage their own slice registries and slice folders.
- **Source Story / Increment / Slice**: HSS-06 / I3 / HSS-06-scoped-execution
- **Requested Outcome**: As a maintainer working inside a nested scope, execution commands and slice bootstrap use that scope's effective `execution.json`, `conventions.json`, and `slice_dir` instead of falling back to one repository-root execution area.
- **Why this matters**: Config inheritance alone is not enough if execution helpers still write slices and registry state into the repository-root `slices/` tree.
- **Independent Test**: Running guide-execution or bootstrap-slice from a child scope creates and updates slices in that child scope's resolved slice directory while root-scope behavior remains unchanged.

## 2. Acceptance Scenarios

1. **Given** a nested scope with its own `planning.json` and an inherited or local `execution.json`, **When** `manage_execution.py add` runs from inside that scope, **Then** the slice folder and registry entry are created under that scope's resolved `slice_dir`.
2. **Given** a nested scope without its own `execution.json` but with a parent `slice_dir`, **When** execution commands run in the child scope, **Then** the inherited `slice_dir` is resolved relative to the child scope root.
3. **Given** a nested scope and `bootstrap_slice.py`, **When** bootstrap runs from that scope, **Then** it reuses the resolved execution and conventions config for that scope instead of initializing or reading only the repository-root execution area.

## 3. Functional Requirements

- **FR-001**: Guide-execution MUST resolve execution config, conventions config, and registry paths from the active execution scope instead of assuming one repository-root `.skills/execution.json`.
- **FR-002**: Guide-execution MUST keep slice registries and slice folders local to the resolved scope's `slice_dir`.
- **FR-003**: Inherited `slice_dir` values MUST resolve relative to the active scope root.
- **FR-004**: `bootstrap_slice.py` MUST bootstrap slices against the resolved execution scope and MUST reuse inherited execution config when available.
- **FR-005**: Repository-root execution behavior MUST remain unchanged when no nested scope applies.

## 4. Key Entities

- **Execution Scope Context**: The nearest active scope used by execution helpers.
- **Scoped Slice Registry**: The `README.md` and `registry.json` pair under the resolved scope's `slice_dir`.
- **Scoped Slice Folder**: The slice directory created under the resolved scope's effective `slice_dir`.

## 5. Edge Cases

- A child scope inherits `slice_dir` from a parent and must still create the registry locally under the child scope root.
- A child scope with no local `execution.json` should not be forced to initialize one just to reuse inherited defaults.
- Root-scope execution commands must keep their current behavior when no child scope exists.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: HSS-06-config-inheritance already provides merged execution and conventions config views for a resolved scope.
- **A2**: Execution scope discovery continues to use the shared scope runtime and the nearest explicit planning scope.

### Dependencies

- **D1**: `skills/guide-execution/scripts/manage_execution.py`
- **D2**: `skills/slice/scripts/bootstrap_slice.py`
- **D3**: Execution and slice bootstrap regression suites

## 7. Success Criteria

- **SC-001**: Nested-scope execution commands create and update slices in that scope's local registry tree.
- **SC-002**: `bootstrap_slice.py` reuses inherited scoped execution config instead of requiring a repository-root execution config.
- **SC-003**: Repository-root execution tests remain green after scoped execution is added.

## 8. Open Clarifications

- None.
