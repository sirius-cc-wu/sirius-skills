# Slice Planning

## 1. Planning Scope

- Feature: Throughput Acceleration Workflow
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
- Execution system: repository-managed skills, shared runtime, and tests
- Execution mode: `single-agent`
- Notes:
  - This feature adds accelerators above the existing planning and execution
    owners instead of replacing them.
  - The first increment establishes supplemental runtime support and durable
    learnings before introducing new orchestration behavior.
  - `ship` remains a standalone backlog resolver; any later `ship-slice`
    delegation must remain optional.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| TAW-01 | L | medium | keep | `autoplan` is one cohesive planning-layer orchestration feature once the shared runtime and learnings readers exist. | 1 |
| TAW-02 | XL | high | split | One-slice finishing spans handoff contracts, slice finishing semantics, and backlog delegation, which should land as separate packets to keep review and regression scope manageable. | 3 |
| TAW-03 | L | high | split | Shared runtime support and owner-level resume behavior are tightly related but should not land in one packet because they change different boundaries and validation paths. | 2 |
| TAW-04 | M | medium | keep | One learnings skill can remain cohesive once the shared runtime store exists. | 1 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Supplemental runtime state and durable learnings are available for later accelerators | TAW-03, TAW-04 | taw-runtime-foundation, taw-learn-skill | Shared runtime helpers package cleanly, and maintainers can query or promote repo-scoped learnings without relying on chat memory. | Establish runtime and memory primitives before automation layers depend on them |
| I2 | One active slice can finish end to end with durable handoff and resume support | TAW-02, TAW-03 | taw-ship-handoff, taw-ship-slice-loop | `ship` emits a stable handoff payload, and `ship-slice` can reconcile one active slice through owner-driven finishing with checkpointed resume support. | Keep `ship` standalone while adding optional one-slice acceleration |
| I3 | The accelerated backlog path and accelerated planning path both work above the current owners | TAW-01, TAW-02 | taw-ship-backlog-integration, taw-autoplan | Reviewed backlogs can optionally delegate one slice at a time to `ship-slice`, and planning can run through `review-planning` in one `autoplan` invocation. | Complete both execution and planning accelerators after their shared foundations exist |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| taw-runtime-foundation | TAW-03 | Add shared accelerator runtime support | Introduce `lib/workflow_runtime`, runtime file-locking helpers, checkpoint/event-log/learnings stores, and centralized packaged runtime for consuming skills. | new `lib/workflow_runtime/`, the centralized packaged runtime, packaging tests | primary | `pytest -q tests/test_install_target_modes.py skills/ship/tests/test_ship.py -k runtime` | create slice |  | yes |
| taw-learn-skill | TAW-04 | Add durable learnings skill | Implement `learn` query/promote/prune flows on top of the new runtime learnings store and wire repo-scoped learnings ownership into docs and tests. | new `skills/learn/`, `lib/workflow_runtime/learnings.py`, docs | primary | `pytest -q skills/learn/tests/test_learn.py` | create slice | taw-runtime-foundation | yes |
| taw-ship-handoff | TAW-02 | Extend ship with machine-readable handoff payloads | Keep `ship` standalone while adding validated handoff payload output that `ship-slice` can consume without changing backlog ownership semantics. | `skills/ship/`, `lib/workflow_runtime/handoff.py`, ship tests | primary | `pytest -q skills/ship/tests/test_ship.py -k handoff` | create slice | taw-runtime-foundation | yes |
| taw-ship-slice-loop | TAW-02 | Add one-slice finishing and resume orchestration | Implement `ship-slice` so one active slice can reconcile state, progress through remaining owners, checkpoint stop boundaries, and resume safely. | new `skills/ship-slice/`, `skills/guide-execution/` integration points, runtime checkpoints | primary | `pytest -q skills/ship-slice/tests/test_ship_slice.py -k finish_or_resume` | create slice | taw-ship-handoff | yes |
| taw-ship-backlog-integration | TAW-02 | Integrate backlog delegation from ship to ship-slice | Add optional `ship` delegation to `ship-slice` for one active slice at a time while preserving one-active-slice semantics and repo-artifact truth. | `skills/ship/`, `skills/ship-slice/`, execution config handling | primary | `pytest -q skills/ship/tests/test_ship.py skills/ship-slice/tests/test_ship_slice.py -k delegation` | create slice | taw-ship-slice-loop | yes |
| taw-autoplan | TAW-01 | Add high-autonomy planning orchestration | Implement `autoplan` as a planning-layer accelerator that composes `guide-planning`, `discover`, `design`, optional `ui-flow`, `breakdown`, and `review-planning` while stopping at approval boundaries. | new `skills/autoplan/`, `skills/guide-planning/`, planning tests | primary | `pytest -q skills/autoplan/tests/test_autoplan.py` | create slice | taw-runtime-foundation | yes |

## 5. Dependency Notes

- Critical path: taw-runtime-foundation -> taw-ship-handoff -> taw-ship-slice-loop -> taw-ship-backlog-integration.
- Explicit blockers:
  - `taw-learn-skill` depends on the runtime learnings store and locking helpers from `taw-runtime-foundation`.
  - `taw-ship-handoff` depends on the new handoff serialization support and packaged runtime sync.
  - `taw-ship-slice-loop` depends on `taw-ship-handoff` so the one-slice finisher can consume the same normalized contract that backlog mode will later use.
  - `taw-ship-backlog-integration` depends on `taw-ship-slice-loop` so backlog delegation reuses an already-tested one-slice finisher.
  - `taw-autoplan` depends only on `taw-runtime-foundation`; it should not wait for `ship-slice` work.
- Parallel-safe slices: none recommended in the first pass because runtime packaging, shared config, and learnings storage touch the same new control surfaces.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs:
  - the feature remains `single-agent`
  - `ship` keeps backlog traversal ownership
  - `ship-slice` owns optional one-slice finishing only
  - `autoplan` owns planning-layer orchestration only
- Integration checkpoints:
  - verify packaged installs still include any new shared runtime used by accelerator skills
  - verify `ship` still works without `ship-slice` enabled
  - verify checkpoint reconciliation prefers planning and execution artifacts when runtime state drifts
  - verify `autoplan` stops at the explicit approval boundary rather than bootstrapping execution

## 6. Bootstrap Order

1. taw-runtime-foundation
2. taw-learn-skill
3. taw-ship-handoff
4. taw-ship-slice-loop
5. taw-ship-backlog-integration
6. taw-autoplan

## 7. Open Questions / Stop-and-Ask Items

- Should the first `ship-slice` implementation prepare PR metadata only, or invoke `create-pr` directly when repository configuration allows it?
- Should `autoplan` persist checkpoints only at stop boundaries in the first version, or after every planning-phase completion?

## 8. Review Notes

- Review outcome: ready for human approval and planning commit.
- Blocking findings: none.
- Readiness note: the packet preserves the intended ownership boundary where
  `ship` remains a standalone backlog resolver, `ship-slice` is optional, and
  supplemental runtime state never replaces planning or execution artifacts as
  workflow truth.
- Follow-up considerations:
  - decide whether the first `ship-slice` slice stops at PR preparation or also
    invokes `create-pr`
  - decide whether `autoplan` checkpoints should be stop-boundary only in the
    first implementation

## 9. Notes

- This breakdown stays feature-scoped and keeps accelerators above the current planning and execution owners.
- `ship` remains valid as a standalone backlog resolver even if later slices for `ship-slice`, `autoplan`, or `learn` are not yet implemented.
- The first implementation should prefer explicit typed runtime helpers over ad hoc JSON handling inside each skill.
