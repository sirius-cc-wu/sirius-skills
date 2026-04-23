# System Design: Two Step Approval Gate

## Goal

Preserve an explicit human approval boundary between planning completion and
delegated execution acceleration.

## Design Summary

- Store approval as a durable marker owned by the execution accelerator layer.
- Require approval before `ship` can resume delegated execution autopilot.
- Invalidate stale approvals when the reviewed planning packet changes.
- Surface approval state through the same readiness payload used by the
  accelerator entrypoints.

## Validation

- `ship` tests cover approval-required delegation and invalidation after
  planning changes.
- Wiki guidance now documents the operator flow:
  `autoplan --execute-owner-chain` -> review -> `ship --approve` ->
  `ship --resume`.
