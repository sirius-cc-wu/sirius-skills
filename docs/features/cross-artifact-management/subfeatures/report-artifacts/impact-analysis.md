# Impact Analysis: Report Artifacts

## Why this subfeature exists

`cross-artifact-management` now has shared artifact inventory and lineage
helpers, but maintainers still lack a concise operational summary for active,
reviewed, stale, and closed workflow packets. `report-artifacts` turns those
durable repo signals into a read-only reporting surface.

## Expected user-visible outcome

- Maintainers can generate concise summaries for proposals, features,
  subfeatures, and slices without manually opening multiple registries.
- Reporting can group by artifact type, lifecycle status, or parent feature.
- The first version can highlight stale artifacts through an explicit threshold
  instead of burying that logic in ad hoc scripts.

## Affected existing artifacts

- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/user-stories.md`
- `skills/audit-artifacts/scripts/artifact_inventory.py`
- `skills/trace-artifacts/scripts/trace_data.py`
- `skills/propose/scripts/manage_proposals.py`
- `skills/guide-planning/scripts/manage_planning.py`
- `skills/add-subfeature/scripts/manage_subfeatures.py`
- `skills/guide-execution/scripts/manage_execution.py`

## New artifacts likely required

- `skills/report-artifacts/SKILL.md`
- `skills/report-artifacts/scripts/report_data.py`
- `skills/report-artifacts/scripts/report_artifacts.py`
- `skills/report-artifacts/tests/test_report_artifacts.py`

## Risks and constraints

- Reporting must stay read-only and must not become a parallel source of truth.
- Staleness should remain explicit and configurable because repositories differ
  in expected planning and execution cadence.
- The first version should prefer reusable aggregates over one-off dashboards so
  later automation can consume the same output structure.

## Story and slice framing

- Parent story: `CAM-03` — report artifact state
- Planned slice: `CAM-03-artifact-state-report`
