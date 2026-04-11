# Slice Planning: Repair Artifacts

## Slice Summary

- Story: `CAM-04` — repair artifact drift
- Increment: `I1`
- Planned slice: `CAM-04-registry-drift-repair`
- Value: one conservative repair command that previews and optionally rebuilds
  active registry/readme artifacts from durable directories plus valid metadata.

## Slice Boundaries

### In scope

- shared repair planning from inventory plus valid metadata
- dry-run repair plans
- apply mode for proposal, feature, subfeature, and slice registry/readme
  regeneration
- human-readable and JSON output
- repo wiring, docs, and tests

### Out of scope

- semantic metadata correction
- archive flows
- silent force-sync behavior

## Execution notes

- Reuse the shared inventory helper to discover candidate directories.
- Reuse owner-script registry writers to preserve README/JSON formatting.
- Treat unreadable metadata as manual follow-up and exclude it from rebuilt rows.

## Validation

- `pytest -q skills/repair-artifacts/tests/test_repair_artifacts.py`
- `pytest -q`

## Review Notes

- Planning reviewed: one slice is sufficient because the repair surface is
  limited to derived registry/readme regeneration and preserves explicit dry-run
  review before apply mode.
