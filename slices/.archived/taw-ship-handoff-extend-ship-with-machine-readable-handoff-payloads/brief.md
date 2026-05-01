# Slice Specification: Extend ship with machine-readable handoff payloads

**Slice ID**: `taw-ship-handoff`  
**Story**: `TAW-02`  
**Increment**: `I2`  
**Feature**: `throughput-acceleration-workflow`

## Objective

Keep `ship` as the backlog resolver while extending its JSON output with a
stable machine-readable handoff payload for the active slice. The payload must
be derived from existing planning and execution artifacts so later accelerators
such as `ship-slice` can reuse it without creating a second source of truth.

## Functional Requirements

- **FR-001** `ship --json` must include a stable handoff payload for one active
  slice whenever a mapped active slice exists.
- **FR-002** The handoff payload must include target identity, planned slice
  identity, execution slice identity/path, current slice status, next owner,
  and handoff action.
- **FR-003** The payload must be validated through the shared
  `workflow_runtime.handoff` contract rather than ad hoc dict shape.
- **FR-004** Existing human-readable `ship` behavior must remain intact.
- **FR-005** The skill docs and regression tests must describe the new machine
  handoff surface.

## Constraints

- Keep backlog resolution and next-owner semantics owned by `ship`.
- Do not write handoff state back into planning or execution registries.
- Keep the payload backward-compatible by adding new JSON fields rather than
  replacing existing ones.

## Validation

- `pytest -q skills/ship/tests/test_ship.py -k handoff`
