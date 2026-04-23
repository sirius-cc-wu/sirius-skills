# Slice Specification: Auto-format, close, and commit owned changes

**Slice ID**: `scc-terminal-automation`  
**Story**: `TAW-02`  
**Increment**: `I2`  
**Feature**: `ship-slice-close-commit-controls`

## Objective

Extend `ship-slice` so delegated runs can optionally format owned files, close
the active slice, and create an owned-file-only commit while preserving
deterministic stop behavior and partial-success reporting.

## Functional Requirements

- **FR-001** `ship-slice` reads `auto_format`, `auto_close`, and `auto_commit`
  from `accelerators.ship_slice`, with `auto_commit` requiring `auto_close`.
- **FR-002** When `auto_format` is enabled, `ship-slice` runs a path-scoped
  formatter against owned files only and stops on formatter spillover.
- **FR-003** When `auto_close` is enabled, `ship-slice` closes the active slice
  through the existing `close-slice` owner instead of mutating closure state
  directly.
- **FR-004** When `auto_commit` is enabled, `ship-slice` stages and commits
  only owned changed files, leaving unrelated dirty files untouched.
- **FR-005** If close succeeds but commit fails, `ship-slice` reports explicit
  partial success with the slice left closed and `next_owner=commit`.

## Assumptions

- Formatter execution can be supplied as a path-scoped command in execution
  config for repositories that opt into `auto_format`.
- A deterministic default commit message may be synthesized from slice context
  when repo conventions do not define a custom format.
- Unrelated dirty files outside the owned file set remain visible in readiness
  output but must not block owned-file commit automation.

## Validation

- `pytest -q skills/ship-slice/tests/test_ship_slice.py skills/close-slice/tests/test_close_slice.py`
