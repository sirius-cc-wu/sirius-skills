# Slice Specification: Track owned changes and formatter scope

**Slice ID**: `scc-owned-change-set`  
**Story**: `TAW-02`  
**Increment**: `I1`  
**Feature**: `ship-slice-close-commit-controls`

## Objective

Teach `ship-slice` to distinguish the delegated run's owned file changes from
pre-existing unrelated worktree dirtiness, scope formatting to the owned file
set, and stop safely when a formatter spills beyond that boundary or encounters
same-file ownership conflicts.

## Functional Requirements

- **FR-001** `ship-slice` snapshots pre-run worktree state so it can derive the
  delegated run's owned file set deterministically.
- **FR-002** When formatting is enabled, `ship-slice` runs formatting only
  against the owned file set.
- **FR-003** `ship-slice` reports unrelated dirty files outside the owned file
  set without blocking delegated progress.
- **FR-004** `ship-slice` stops with explicit readiness context when formatter
  spillover touches files outside the owned file set.
- **FR-005** `ship-slice` stops when the delegated run would modify a file that
  already had unrelated user changes before the run started.

## Assumptions

- The first rollout only needs ownership tracking and formatter-safety logic;
  closure and commit automation will land in the following slice.
- Existing readiness output remains the public surface for stop reasons.
- Formatter invocation can be scoped by explicit file paths in the targeted
  workflows used by this repository.

## Validation

- `pytest -q skills/ship-slice/tests/test_ship_slice.py`

