# System Design: Ship Slice Owner Chain

## Goal

Allow `ship-slice` to drive one active slice through the execution owner chain
without taking ownership away from the underlying execution skills.

## Design Summary

- Gate chained execution behind explicit config and CLI controls.
- Reuse the normalized handoff payload from `ship`.
- Advance through the existing execution owners only while the durable slice and
  planning artifacts stay consistent.
- Emit structured stop context for review boundaries, verification failures,
  explicit owner stops, and commit checkpoints.

## Validation

- Focused `ship-slice` tests cover owner advancement, stop boundaries, and
  deterministic checkpoint behavior.
- The design keeps `ship` as backlog resolver and limits `ship-slice` to
  one-slice finishing.
