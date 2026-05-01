# Slice Specification: Add high-autonomy planning orchestration

**Slice ID**: `taw-autoplan`  
**Story**: `TAW-01`  
**Increment**: `I3`  
**Feature**: `throughput-acceleration-workflow`

## Objective

Implement `autoplan` as the planning-side accelerator above `guide-planning`.
The first version should resolve one planning target, read durable learnings,
write checkpoint and runtime events, surface the next planning owner, and stop
explicitly at the approval boundary.

## Functional Requirements

- **FR-001** `autoplan` resolves one feature target and reports the next
  planning owner from its current planning status.
- **FR-002** The skill reads active and candidate learnings for the target
  scope.
- **FR-003** The skill writes resumable checkpoint and event-log records.
- **FR-004** The skill reads `accelerators.autoplan.auto_decision_policy` from
  planning config and reports it in output.
- **FR-005** The skill stops at `planning_reviewed` with an explicit approval
  action instead of continuing into execution bootstrap.

## Validation

- `pytest -q skills/autoplan/tests/test_autoplan.py`
