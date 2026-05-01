# Slice Specification: Add one-slice finishing and resume orchestration

**Slice ID**: `taw-ship-slice-loop`  
**Story**: `TAW-02`  
**Increment**: `I2`  
**Feature**: `throughput-acceleration-workflow`

## Objective

Implement `ship-slice` as the optional one-slice accelerator above the existing
execution owners. The first version should resolve one active slice, read
durable learnings, persist checkpoint and event-log context, and report the
next owner or commit checkpoint without taking over backlog traversal.

## Functional Requirements

- **FR-001** `ship-slice` resolves one active slice from an explicit selector,
  a `ship` handoff payload, or a prior checkpoint.
- **FR-002** The skill reads active and candidate learnings for the target
  scope before reporting the next owner.
- **FR-003** The skill writes a resumable checkpoint and execution event after
  each stop boundary.
- **FR-004** The skill routes the active slice to `brief`, `blueprint`,
  implementation, or `commit` based on the reconciled slice state.
- **FR-005** The first version remains additive and does not replace `ship`
  backlog selection or existing owner skills.

## Validation

- `pytest -q skills/ship-slice/tests/test_ship_slice.py -k finish_or_resume`
