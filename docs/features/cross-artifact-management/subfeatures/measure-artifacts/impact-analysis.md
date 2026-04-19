# Impact Analysis: Measure Artifacts

## Why this subfeature exists

`cross-artifact-management` can already tell a maintainer what workflow
artifacts exist and what state they are in, but it cannot yet explain how much
implementation effort a completed feature or subfeature required or whether the
chosen workflow was proportionate to the work.

`measure-artifacts` adds that missing evidence layer. Its purpose is not to
replace planning or execution ownership. Its purpose is to compute durable,
reusable metrics that can later support:

- operational reporting
- archive summaries
- workflow calibration
- future agent-level improvement of `guide-scope`, `guide-planning`, and
  `guide-execution`

## Expected user-visible outcome

- Maintainers can inspect completed features and subfeatures with durable
  metrics instead of relying on anecdote.
- Repositories can compare direct implementation with `guide-execution` using
  real project history.
- Future workflow evaluation can reuse the same metrics instead of inventing a
  second evidence store.

## Affected existing artifacts

- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/user-stories.md`
- `docs/features/cross-artifact-management/subfeatures/README.md`
- `docs/features/cross-artifact-management/subfeatures/registry.json`
- `skills/report-artifacts/SKILL.md`
- `skills/archive-artifacts/SKILL.md`
- `skills/close-slice/SKILL.md`
- `skills/guide-planning/scripts/manage_planning.py`
- `skills/add-subfeature/scripts/manage_subfeatures.py`
- `skills/guide-execution/scripts/manage_execution.py`

## New artifacts likely required

- `skills/measure-artifacts/SKILL.md`
- `skills/measure-artifacts/scripts/measure_artifacts.py`
- shared metric-reading helpers that can consume feature, subfeature, and slice
  metadata consistently
- tests covering metric derivation and cross-artifact integration

## Risks and constraints

- The first version must stay generic-first and avoid hardcoded thresholds for
  when repositories should skip `guide-execution`.
- Metrics should not silently redefine owner metadata semantics in planning or
  execution tooling.
- "Implementation line count" must be defined clearly enough to be reproducible.
- Outcome interpretation should remain conservative; metrics inform workflow
  decisions but should not fully automate them alone.

## Story and slice framing

- Parent story: `CAM-06` — measure workflow evidence
- Planned slices:
  - `mea-metrics-foundation`
  - `mea-metrics-consumers`
