# Impact Analysis: Two Step Approval Gate

## Scope

This subfeature reconciles the explicit approval gate that now separates
planning acceleration from execution acceleration.

## Affected Areas

- `sirius ship`
- `skills/ship/tests/test_ship.py`
- `docs/wiki/concepts/two-step-autonomy-roadmap.md`
- `README.md`

## Impact

- Execution autopilot now requires an explicit durable approval record after
  planning review.
- Approval evidence can be invalidated automatically when planning artifacts
  change.
- The change hardens the two-step operating model without creating a parallel
  lifecycle registry.
