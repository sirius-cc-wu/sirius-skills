# Slice Planning

## 1. Planning Scope

- Feature: Feature evolution workflow
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
  - adjacent precedent from `planning-workflow` and `execution-workflow`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes: The first iteration focuses on one canonical feature and one feature
  change at a time. Execution remains slice-scoped; change packets stay
  planning-scoped.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| FEW-01 | M | medium | split | Registry lifecycle and per-change bootstrap touch different failure modes, and splitting lowers setup/debug risk. | 2 |
| FEW-02 | M | medium | keep | Impact analysis has one coherent output and one primary validation path. | 1 |
| FEW-03 | L | high | split | Change-state enforcement and change-local artifact reuse affect different subsystems and would be brittle as one packet. | 2 |
| FEW-04 | L | high | split | Change-local breakdown and canonical reconciliation have different validation paths and higher auditability risk if combined. | 2 |
| FEW-05 | L | medium | split | Closure/history behavior and guide-planning routing docs can be validated separately and have different change surfaces. | 2 |

Decision rules:

- `keep` means the story is already small enough to map to one executable slice.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not be executed yet.

## 3. Increment Plan

Use increments to group related slices into small, demonstrable outcomes. Increment 1 should usually be the simplest end-to-end usable path.

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Start a change against an existing feature | FEW-01, FEW-03 | FEW-01-registry, FEW-01-initiate-change, FEW-03-change-metadata | A maintainer can create `docs/features/<feature>/changes/<change-id>/` with registry and metadata tracked durably. | Simplest end-to-end usable path |
| I2 | Assess and design the change cleanly | FEW-02, FEW-03 | FEW-02-impact-analysis, FEW-03-change-artifacts | A reviewer can inspect changed intent, affected stories/slices, and change-local design artifacts before breakdown. | Depends on I1 |
| I3 | Prepare execution-ready work from an approved change | FEW-04 | FEW-04-change-breakdown, FEW-04-reconciliation-workflow | A change packet can produce reviewed slice-planning output plus an explicit reconciliation plan for canonical docs. | Depends on I2 |
| I4 | Close and retain change history without archiving canonical features | FEW-05 | FEW-05-history-closure, FEW-05-routing-docs | A reconciled change can be closed with durable backlinks, retained history, and documented handoff behavior. | Depends on I3 |

Rules:

- keep increments feature-scoped planning artifacts, not execution slices
- each increment should be demonstrable without requiring the full project to be complete
- an increment can include one or many execution-ready slices
- planned slices and execution slices remain slice-scoped even when they belong to the same increment

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FEW-01-registry | FEW-01 | Initialize feature change registry | Add per-feature `changes/README.md`, `registry.json`, and registry lifecycle management for change packets. | `skills/evolve-feature/scripts/manage_feature_changes.py` | primary | `pytest -q skills/evolve-feature/tests/test_manage_feature_changes.py` | create slice |  | yes |
| FEW-01-initiate-change | FEW-01 | Bootstrap one feature change packet | Resolve canonical feature, create `changes/<change-id>/`, and seed change-local discovery artifacts. | `skills/evolve-feature/SKILL.md`, `skills/evolve-feature/scripts/manage_feature_changes.py` | primary | `pytest -q skills/evolve-feature/tests/test_manage_feature_changes.py` | create slice | FEW-01-registry | yes |
| FEW-02-impact-analysis | FEW-02 | Produce impact analysis for changed features | Inspect canonical planning docs and write `impact-analysis.md` with affected stories, artifacts, and slice implications. | `skills/assess/SKILL.md`, `skills/assess/`, change packet docs | primary | Review generated `impact-analysis.md` plus `pytest -q skills/assess/tests/test_analyze_impact.py` | create slice | FEW-01-initiate-change | yes |
| FEW-03-change-metadata | FEW-03 | Enforce feature-change state model | Add `.feature-change-meta.json` shape, state transitions, and artifact-gated validation for change packets. | `skills/evolve-feature/scripts/manage_feature_changes.py` | primary | `pytest -q skills/evolve-feature/tests/test_manage_feature_changes.py` | create slice | FEW-01-initiate-change | yes |
| FEW-03-change-artifacts | FEW-03 | Support change-local design and breakdown artifacts | Extend planning path resolution so `design` and `breakdown` can operate on a selected change packet cleanly. | `skills/design/`, `skills/breakdown/`, path-resolution helpers | primary | Validate one change packet reaches `design_ready` / `breakdown_ready` using tooling or fixture tests | create slice | FEW-02-impact-analysis, FEW-03-change-metadata | yes |
| FEW-04-change-breakdown | FEW-04 | Break change packets into execution-ready slices | Generate change-local `slice-planning.md` and `slice-traceability.md` that produce execution-ready slices from approved deltas. | `skills/breakdown/SKILL.md`, templates, change packet examples | primary | Review generated planning docs and add fixture coverage for change-local breakdown | create slice | FEW-03-change-artifacts | yes |
| FEW-04-reconciliation-workflow | FEW-04 | Reconcile approved changes into canonical feature docs | Add a `reconcile-feature` workflow that updates canonical docs explicitly and records durable backlinks. | `skills/reconcile-feature/SKILL.md`, `skills/reconcile-feature/scripts/reconcile_feature_change.py` | primary | `pytest -q skills/reconcile-feature/tests/test_reconcile_feature_change.py` | create slice | FEW-04-change-breakdown | yes |
| FEW-05-history-closure | FEW-05 | Record feature change closure and retained history | Add change closure metadata and optional feature-local history publishing without deleting change packets or canonical docs. | `skills/reconcile-feature/`, feature change metadata, optional history doc | primary | Validate closure metadata and history output in fixture tests | create slice | FEW-04-reconciliation-workflow | yes |
| FEW-05-routing-docs | FEW-05 | Document guide-planning routing for evolving features | Update methodology and skill docs so users know when to start a feature change versus a net-new feature. | `README.md`, `SKILLS_METHODOLOGY.md`, `skills/guide-planning/SKILL.md` | primary | Review docs for route consistency and examples | create slice | FEW-05-history-closure | yes |

## 5. Dependency Notes

- Critical path: change registry -> initiate change -> impact analysis/state model -> change-local artifact support -> change breakdown -> reconciliation -> closure/docs.
- Explicit blockers: reconciliation depends on reviewed change-local planning outputs and stable canonical update semantics.
- Parallel-safe slices: none recommended in the first iteration because path resolution, state transitions, and reconciliation semantics are tightly coupled.
- Increment ordering: I1 -> I2 -> I3 -> I4.
- Lane owners and handoffs: `guide-planning` routes into `evolve-feature`; `assess`, `design`, and `breakdown` operate on the selected change packet; `review-planning` confirms readiness before slice bootstrap; `reconcile-feature` closes the planning delta loop.
- Integration checkpoints:
  - validate feature change creation and registry state after I1
  - validate one change packet reaches impact/design/breakdown readiness after I2
  - validate canonical reconciliation and backlink creation after I3
  - validate closure/history behavior and guide-planning docs after I4

## 6. Bootstrap Order

1. FEW-01-registry
2. FEW-01-initiate-change
3. FEW-02-impact-analysis
4. FEW-03-change-metadata
5. FEW-03-change-artifacts
6. FEW-04-change-breakdown
7. FEW-04-reconciliation-workflow
8. FEW-05-history-closure
9. FEW-05-routing-docs

## 7. Open Questions / Stop-and-Ask Items

- Resolved for MVP: keep `assess` as a separate skill so the artifact has a distinct owner and review surface.
- Resolved for MVP: keep change closure inside `reconcile-feature` instead of adding a separate `close-feature-change` skill yet.
- Resolved for MVP: allow one active open change per canonical feature; if a second change is requested, stop and ask whether to continue the active change or defer the new one.

## 8. Review Notes

- Review outcome: Ready for `slice` after selecting concrete slices from the reviewed backlog.
- Blocking findings: none. Discovery intent, design boundaries, and breakdown sequencing are consistent, and the MVP decisions for closure and active-change handling are now explicit.
- Handoff note: start with `FEW-01-registry`, then `FEW-01-initiate-change`, and preserve the explicit non-destructive reconciliation model described in `system-design.md`.
- Follow-up improvements: if multiple simultaneous open changes become important, add a later slice for active-change resolution policy and conflict handling.
