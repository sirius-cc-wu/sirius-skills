# Impact Analysis: Accelerator Transition Guardrails

## Scope

This subfeature reconciles the shared accelerator guardrail runtime into a
durable subfeature packet.

## Affected Areas

- `lib/workflow_runtime/accelerator_guardrails.py`
- `skills/autoplan/scripts/autoplan.py`
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/scripts/ship_slice.py`

## Impact

- Accelerator entrypoints now share transition classification and stop-reason
  normalization logic.
- High-confidence readiness invariants are built in one place instead of being
  duplicated in each accelerator.
- Packaged runtime sync now carries the shared guardrail helper into installed
  skill copies.
