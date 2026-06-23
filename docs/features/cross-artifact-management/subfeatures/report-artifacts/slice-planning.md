# Slice Planning: Report Artifacts

## Slice Summary

- Story: `CAM-03` — report artifact state
- Increment: `I1`
- Planned slice: `rpt-artifact-state-report`
- Value: one read-only reporting command that summarizes operational workflow
  state across proposals, features, subfeatures, and slices.

## Slice Boundaries

### In scope

- a normalized reporting-record layer built from shared inventory plus owner
  metadata
- grouped summary output by artifact type, lifecycle status, and parent feature
- explicit stale detection with a configurable threshold
- text and JSON output from one in-memory report result
- repo wiring, docs, and tests

### Out of scope

- repair actions
- archival actions
- persistent dashboard files

## Execution notes

- Reuse `sirius_skills.commands.artifact_inventory`.
- Keep grouping logic in a dedicated reporting helper so later archive and
  repair views can reuse the same normalized records when useful.
- Default the stale threshold conservatively and make it explicit in the CLI.

## Validation

- `pytest -q skills/report-artifacts/tests/test_report_artifacts.py`
- `pytest -q`

## Review Notes

- Planning reviewed: one slice is sufficient because the reporting layer is
  read-only, composes existing inventory/metadata sources, and produces grouped
  summaries without altering workflow ownership boundaries.
