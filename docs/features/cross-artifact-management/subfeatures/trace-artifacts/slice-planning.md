# Slice Planning

## 1. Planning Scope

- Feature: Trace artifacts
- Planning sources:
  - `discover.md`
  - `impact-analysis.md`
  - `system-design.md`
  - parent `docs/features/cross-artifact-management/user-stories.md`
- Execution system: repository-managed code changes and tests
- Execution mode: `single-agent`
- Notes: The first slice should reuse the shared audit inventory and add a
  durable lineage graph plus traceability parsing, rather than building a second
  discovery stack.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| CAM-02 | L | medium | keep | Shared inventory reuse, traceability parsing, and targeted query output form one coherent read-only lineage capability. | 1 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Trace one artifact's lineage or summarize the repo's lineage graph | CAM-02 | tat-trace-artifact-lineage | A maintainer can trace proposal, feature, subfeature, planned-slice, or execution-slice lineage from one command. | Simplest usable path |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tat-trace-artifact-lineage | CAM-02 | Build the cross-artifact trace command | Add a lineage graph helper, parse planning traceability docs, expose targeted and summary trace output, and ship the `trace-artifacts` skill with tests and docs. | `skills/trace-artifacts/`, `sirius_skills.commands.artifact_inventory`, planning traceability parsing | primary | `pytest -q skills/trace-artifacts/tests/test_trace_artifacts.py` and `pytest -q` | create slice |  | yes |

## 5. Dependency Notes

- Critical path: shared inventory reuse -> traceability parsing -> lineage graph
  queries -> skill/docs/tests.
- Explicit blockers: none.
- Parallel-safe slices: none recommended; the query surface depends on one
  consistent graph model.
- Increment ordering: I1 only.
- Lane owners and handoffs: `trace-artifacts` owns read-only lineage queries;
  planning and execution continue to own their source metadata.
- Integration checkpoints: verify targeted and summary output from the same
  graph model.

## 6. Bootstrap Order

1. tat-trace-artifact-lineage

## 7. Review Notes

- Review outcome: Ready for `slice` with `tat-trace-artifact-lineage`.
- Blocking findings: none. The design stays read-only, reuses the shared
  inventory helper, and limits lineage edges to durable repo signals.
- Handoff note: keep planned slices as typed graph nodes and parse
  `slice-traceability.md` by column names so the first version tolerates the
  repo's current table variants.

## 8. Notes

- This subfeature should expose lineage, not repair or reclassify it.
- The lineage graph created here should stay reusable for later
  `report-artifacts` work.
