# Slice Specification: Integrate backlog delegation from ship to ship-slice

**Slice ID**: `taw-ship-backlog-integration`  
**Story**: `TAW-02`  
**Increment**: `I3`  
**Feature**: `throughput-acceleration-workflow`

## Objective

Add the optional backlog-mode integration where `ship` can delegate one active
slice to `ship-slice` when execution config enables that behavior. The
delegation must remain additive and preserve `ship` as the backlog resolver.

## Functional Requirements

- **FR-001** `ship` reads `accelerators.ship.delegate_to_ship_slice` from
  `.skills/execution.json`.
- **FR-002** When delegation is enabled and one active slice exists, `ship`
  invokes `ship-slice` with the current handoff payload and returns the
  delegated result in JSON output.
- **FR-003** When delegation is disabled, `ship` keeps its current standalone
  behavior.
- **FR-004** The repo execution config documents the accelerator defaults used
  by the throughput layer.
- **FR-005** Delegation is covered by focused regression tests.

## Validation

- `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py -k delegation`
