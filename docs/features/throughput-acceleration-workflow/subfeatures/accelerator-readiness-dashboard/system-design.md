# System Design: Accelerator Readiness Dashboard

## Goal

Expose one normalized readiness payload for accelerator entrypoints so operators
and downstream tooling can reason about the next valid action consistently.

## Design Summary

- Add a shared readiness shape to `autoplan`, `ship`, and `ship-slice`.
- Keep the payload focused on decision support:
  `can_proceed`, `next_owner`, `blocked_by`, `stop_reason`,
  `approval_gate`, and `commit_checkpoint`.
- Build readiness from existing planning/execution truth plus explicit runtime
  checkpoint context.

## Validation

- Focused accelerator tests assert readiness behavior at approval boundaries,
  review boundaries, commit checkpoints, and happy-path advancement.
- Wiki guidance now uses the readiness shape as part of the two-step operator
  flow.
