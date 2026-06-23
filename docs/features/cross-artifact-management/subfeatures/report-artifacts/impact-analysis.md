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
- A later retention-aware revision can stop reporting pruned archived slices as
  ordinary closed execution packets once their history has been retained in
  planning docs.

## Affected existing artifacts

- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/user-stories.md`
- `sirius_skills.commands.artifact_inventory`
- `sirius_skills.commands.trace_data`
- `sirius manage-proposals`
- `sirius manage-planning`
- `sirius manage-subfeatures`
- `sirius manage-execution`

## New artifacts likely required

- `skills/report-artifacts/SKILL.md`
- `sirius_skills.commands.report_data`
- `sirius report-artifacts`
- `skills/report-artifacts/tests/test_report_artifacts.py`

## Risks and constraints

- Reporting must stay read-only and must not become a parallel source of truth.
- Staleness should remain explicit and configurable because repositories differ
  in expected planning and execution cadence.
- The first version should prefer reusable aggregates over one-off dashboards so
  later automation can consume the same output structure.
- Historical slice retention and active operational reporting should stay
  intentionally separate so cleanup does not look like workflow breakage.

## Story and slice framing

- Parent story: `CAM-03` — report artifact state
- Planned slice: `rpt-artifact-state-report`
