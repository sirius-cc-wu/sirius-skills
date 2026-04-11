# Slice Planning: Archive Artifacts

## Slice Summary

- Story: `CAM-05` — archive durable history safely
- Increment: `I1`
- Planned slice: `CAM-05-safe-slice-archival`
- Value: one explicit archive command that reports archive candidates across
  relevant artifact layers and safely archives one closed execution slice at a
  time through the execution owner helper.

## Slice Boundaries

### In scope

- archive candidate discovery for proposals, finalized subfeatures, and closed
  slices
- targeted apply mode for one closed execution slice
- human-readable and JSON output
- repo wiring, docs, and tests

### Out of scope

- bulk archival by default
- proposal or subfeature move logic in v1
- implicit cleanup during normal closure

## Execution notes

- Reuse the shared inventory helper for candidate discovery.
- Reuse `manage_execution.archive_slice(...)` for actual slice archival.
- Keep apply mode explicit and reject unsupported non-slice archive requests.

## Validation

- `pytest -q skills/archive-artifacts/tests/test_archive_artifacts.py`
- `pytest -q`

## Review Notes

- Planning reviewed: one slice is sufficient because v1 keeps apply mode narrow,
  candidate reporting read-only, and actual archive writes delegated to the
  execution owner helper.
