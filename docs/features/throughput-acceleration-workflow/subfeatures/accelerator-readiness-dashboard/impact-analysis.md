# Impact Analysis: Accelerator Readiness Dashboard

## Scope

This subfeature reconciles the normalized readiness payload now shared across
the accelerator entrypoints.

## Affected Areas

- `skills/autoplan/scripts/autoplan.py`
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/scripts/ship_slice.py`
- accelerator test suites and wiki guidance

## Impact

- Operators now get one machine-readable readiness contract across planning and
  execution accelerators.
- Approval requirements, commit checkpoints, blockers, and next-owner routing
  are exposed consistently.
- The payload stays derived from durable artifacts and runtime context instead
  of creating a new source-of-truth registry.
