# Slice Planning

Use this file to decompose repo stories into execution-ready slices before
bootstrapping execution slices.

## 0. Subfeature Context

- Parent feature: `cross-artifact-management`
- Parent feature path: `docs/features/cross-artifact-management`
- Subfeature ID: `measure-artifacts`
- Subfeature type: `additive`
- Current subfeature status: `reviewed`
- Impact input: `impact-analysis.md` is present and should drive the
  subfeature-local slice plan.

### Affected Story IDs

- `CAM-06`

### Affected Canonical Slice IDs

- No affected canonical slice IDs were recorded yet.

### Affected Baseline Artifacts

- `docs/features/cross-artifact-management/discover.md`
- `docs/features/cross-artifact-management/user-stories.md`
- `skills/report-artifacts/SKILL.md`
- `skills/archive-artifacts/SKILL.md`
- `skills/close-slice/SKILL.md`
- `sirius manage-planning`
- `sirius manage-subfeatures`
- `sirius manage-execution`

## 1. Planning Scope

- Feature: measure-artifacts
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - parent `docs/features/cross-artifact-management/user-stories.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes:
  - This is subfeature-local breakdown for `measure-artifacts` under parent
    feature `cross-artifact-management`.
  - Plan only the new or amended slices required by this subfeature.
  - Keep this subfeature's `slice-planning.md` and `slice-traceability.md` as
    the execution-planning source of truth for the child capability.
  - The parent feature does not currently carry top-level breakdown artifacts,
    so this subfeature packet is the canonical execution backlog for `CAM-06`.
  - Subfeature-local planning assigns an explicit size and risk to `CAM-06`
    because the parent story table records the story but not sizing fields.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| CAM-06 | L | high | split | The work spans metric derivation/storage plus consumer integration, and the validation paths differ enough that one packet would be brittle. | 2 |

Decision rules:

- `keep` means the story is already small enough to map to one executable slice.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not be executed yet.
- split any `XL` story before slice bootstrap
- `S`/`M`/`L` stories may also split when risk, validation shape, coupling, or
  handoff complexity would make one packet brittle
- record the main reason for the decision, not just the size label

Risk rubric:

- `low`: one cohesive packet with one clear validation path
- `medium`: some coupling, multiple touchpoints, or moderate
  sequencing/handoff risk
- `high`: cross-subsystem impact, migration/reconciliation, compatibility risk,
  or materially different validation paths

## 3. Increment Plan

Use increments to group related slices into small, demonstrable outcomes.
Increment 1 should usually be the simplest end-to-end usable path.

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | First durable implementation-evidence packet | CAM-06 | mea-metrics-foundation | A maintainer can compute and persist story-size, slice-count, execution-mode, and explicit churn availability in `implementation-metrics.json`. | Establishes the sidecar model and reusable measurement engine without changing other skills yet. |
| I2 | Metrics become reusable workflow signals | CAM-06 | mea-metrics-consumers | A maintainer can run `measure-artifacts` directly and see persisted metrics reused by reporting output when present. | Finishes the user-facing skill wiring and consumer integration. |

Rules:

- keep increments feature-scoped planning artifacts, not execution slices
- each increment should be demonstrable without requiring the full project to be
  complete
- an increment can include one or many execution-ready slices
- planned slices and execution slices remain slice-scoped even when they belong
  to the same increment

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mea-metrics-foundation | CAM-06 | Build metrics record and sidecar engine | Add the reusable metrics schema, story-size and slice-count derivation, execution-mode classification, and deterministic `implementation-metrics.json` read/write behavior with explicit unavailable churn handling. | `skills/measure-artifacts`, shared metric helpers, planning/execution artifact readers | primary | `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py` | create slice |  | yes |
| mea-metrics-consumers | CAM-06 | Wire measure-artifacts skill and reporting consumers | Add the `measure-artifacts` skill wrapper/CLI, JSON/text output, persistence mode, and read-only consumption hooks for `report-artifacts` without changing lifecycle ownership; leave archive-facing display as a later follow-up once persisted metrics prove stable. | `skills/measure-artifacts`, `skills/report-artifacts`, docs/tests | primary | `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py && pytest -q skills/report-artifacts/tests/test_report_artifacts.py` | create slice | mea-metrics-foundation | yes |

## 5. Dependency Notes

- Critical path: `mea-metrics-foundation -> mea-metrics-consumers`
- Explicit blockers: consumer integration depends on the sidecar schema and
  derivation engine being stable first
- Parallel-safe slices: none; the second slice consumes the interfaces created by
  the first
- Increment ordering: `I1 -> I2`
- Lane owners and handoffs: single-agent flow; no multi-lane handoff is planned
- Integration checkpoints:
  - after `I1`, verify that a completed feature or subfeature can produce a
    stable metrics sidecar with explicit null/unavailable fields where evidence
    is missing
  - after `I2`, verify that the new skill renders those metrics and that
    read-only reporting tolerates absent or present sidecars consistently

## 6. Bootstrap Order

1. `mea-metrics-foundation`
2. `mea-metrics-consumers`

## 7. Review Notes

- Review outcome: Ready for human approval, planning commit, and later `slice`
  bootstrap beginning with `mea-metrics-foundation`.
- Blocking findings: none. Discovery intent, impact scope, sidecar ownership,
  evidence-source rules, and the two-slice breakdown are now aligned.
- Review resolution: `I2` should integrate persisted metrics into
  `measure-artifacts` and `report-artifacts` only; archive-facing consumers stay
  out of the initial execution packet.
- Non-blocking follow-up: commit-provenance capture remains a later workflow
  enhancement, so `I1` should keep churn fields explicitly unavailable when
  durable provenance is absent.

## 8. Notes

- This file is feature-scoped planning, not slice-scoped execution.
- Keep increment definitions here, not in execution-slice artifacts.
- Once planned slices are created, record the actual slice IDs in
  `slice-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from
  traceability notes and planning discussion.
