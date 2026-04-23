# System Design: Autoplan Owner Chain

## Goal

Allow `autoplan` to orchestrate the planning owner chain without replacing the
underlying planning skills as the source of workflow truth.

## Design Summary

- Gate the behavior behind explicit config and CLI controls.
- Execute the existing planning owners in order:
  `discover` -> `design` -> optional `ui-flow` -> `breakdown` ->
  `review-planning`.
- Persist structured stop context when the chain reaches approval, missing
  input, validation failure, or an explicit owner stop.
- Keep planning artifacts in the existing feature packet and runtime context in
  the existing accelerator runtime.

## Validation

- Focused `autoplan` tests cover the owner-chain happy path and stop-boundary
  behavior.
- Wiki and skill docs describe the two-step operator flow that now depends on
  this capability.
