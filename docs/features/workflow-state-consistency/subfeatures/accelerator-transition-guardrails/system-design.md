# System Design: Accelerator Transition Guardrails

## Goal

Centralize accelerator transition checks so planning and execution accelerators
report consistent stop reasons and readiness invariants.

## Design Summary

- Add shared accelerator guardrail helpers under `lib/workflow_runtime`.
- Consume those helpers from `autoplan`, `ship`, and `ship-slice` instead of
  keeping local classification logic.
- Normalize stop reasons, approval-gate reporting, and readiness construction in
  one runtime path.
- Sync the shared runtime into packaged skill copies so repo and installed
  behavior stay aligned.

## Validation

- Shared guardrail tests cover normalization behavior.
- Accelerator suites revalidate planning and execution stop-boundary behavior
  through the shared runtime.
