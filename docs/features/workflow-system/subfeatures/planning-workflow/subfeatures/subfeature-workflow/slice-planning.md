# Slice Planning

## 1. Planning Scope

- Feature: Subfeature workflow
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
  - adjacent precedent from `planning-workflow` and `execution-workflow`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes: The first iteration focuses on one parent feature and one durable
  child subfeature at a time. Execution remains slice-scoped.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| FEW-01 | M | medium | split | Registry initialization and child-folder bootstrap touch different failure modes. | 2 |
| FEW-02 | M | medium | keep | Impact analysis has one coherent output and one primary validation path. | 1 |
| FEW-03 | L | high | split | Metadata/state enforcement and subfeature-local artifact support touch different planning surfaces. | 2 |
| FEW-04 | L | medium | split | Breakdown generation and feature-level finalization should be validated independently. | 2 |
| FEW-05 | L | medium | split | Cleanup semantics and routing/docs updates affect different audiences. | 2 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Start a durable subfeature under an existing feature | FEW-01, FEW-03 | FEW-01-registry, FEW-01-initiate-change, FEW-03-change-metadata | A maintainer can create `docs/features/<feature>/subfeatures/<subfeature-id>/` with registry and metadata tracked durably. | Simplest usable path |
| I2 | Assess and design the subfeature cleanly | FEW-02, FEW-03 | FEW-02-impact-analysis, FEW-03-change-artifacts | A reviewer can inspect changed intent, affected artifacts, and subfeature-local planning docs before breakdown. | Depends on I1 |
| I3 | Prepare reviewed subfeatures for execution | FEW-04 | FEW-04-change-breakdown, FEW-04-finalization-workflow | A reviewed subfeature can produce execution-ready slice-planning output plus explicit finalization behavior. | Depends on I2 |
| I4 | Close and finalize implemented subfeatures | FEW-05 | FEW-05-history-closure, FEW-05-routing-docs | Completed slices can be cleaned up and the durable subfeature can be marked implemented without deleting it. | Depends on I3 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FEW-01-registry | FEW-01 | Initialize subfeature registry | Add per-feature `subfeatures/README.md`, `registry.json`, and registry lifecycle management for subfeatures. | `skills/add-subfeature/scripts/manage_subfeatures.py` | primary | `pytest -q skills/add-subfeature/tests/test_manage_subfeatures.py` | create slice |  | yes |
| FEW-01-initiate-change | FEW-01 | Bootstrap one durable subfeature | Resolve the parent feature, create `subfeatures/<subfeature-id>/`, and seed child planning artifacts. | `skills/add-subfeature/SKILL.md`, `skills/add-subfeature/scripts/manage_subfeatures.py` | primary | `pytest -q skills/add-subfeature/tests/test_manage_subfeatures.py` | create slice | FEW-01-registry | yes |
| FEW-02-impact-analysis | FEW-02 | Produce impact analysis for a subfeature | Inspect parent planning docs and write `impact-analysis.md` with affected stories, artifacts, and slice implications. | `skills/assess/SKILL.md`, `skills/assess/`, subfeature docs | primary | Review generated `impact-analysis.md` plus `pytest -q skills/assess/tests/test_analyze_impact.py` | create slice | FEW-01-initiate-change | yes |
| FEW-03-change-metadata | FEW-03 | Enforce subfeature state model | Add `.subfeature-meta.json` shape, state transitions, and artifact-gated validation for durable subfeatures. | `skills/add-subfeature/scripts/manage_subfeatures.py` | primary | `pytest -q skills/add-subfeature/tests/test_manage_subfeatures.py` | create slice | FEW-01-initiate-change | yes |
| FEW-03-change-artifacts | FEW-03 | Support subfeature-local planning artifacts | Extend path resolution so `design` and `breakdown` can operate on a selected subfeature cleanly. | `skills/design/`, `skills/breakdown/`, path-resolution helpers | primary | Validate one subfeature reaches `design_ready` / `breakdown_ready` using tooling or fixture tests | create slice | FEW-02-impact-analysis, FEW-03-change-metadata | yes |
| FEW-04-change-breakdown | FEW-04 | Break subfeatures into execution-ready slices | Generate subfeature-local `slice-planning.md` and `slice-traceability.md` that produce execution-ready slices from reviewed child planning. | `skills/breakdown/SKILL.md`, templates, subfeature examples | primary | Review generated planning docs and add fixture coverage for subfeature-local breakdown | create slice | FEW-03-change-artifacts | yes |
| FEW-04-finalization-workflow | FEW-04 | Finalize reviewed subfeatures explicitly | Add a `finalize-subfeature` workflow that verifies slice closure, removes completed execution slices, and advances the durable child planning folder to implemented. | `skills/finalize-subfeature/SKILL.md`, `skills/finalize-subfeature/scripts/finalize_subfeature.py` | primary | `pytest -q skills/finalize-subfeature/tests/test_finalize_subfeature.py` | create slice | FEW-04-change-breakdown | yes |
| FEW-05-history-closure | FEW-05 | Keep implemented subfeatures as durable history | Preserve the subfeature folder after finalization while cleaning up completed execution slices. | `skills/finalize-subfeature/`, subfeature metadata, execution registry cleanup | primary | Validate cleanup behavior in fixture tests | create slice | FEW-04-finalization-workflow | yes |
| FEW-05-routing-docs | FEW-05 | Document routing for evolving features | Update methodology and skill docs so users know when to start a subfeature versus a net-new feature. | `README.md`, `SKILLS_METHODOLOGY.md`, `skills/guide-planning/SKILL.md` | primary | Review docs for route consistency and examples | create slice | FEW-05-history-closure | yes |

## 5. Dependency Notes

- Critical path: subfeature registry -> subfeature bootstrap -> impact analysis
  -> artifact support -> breakdown -> finalization -> routing/docs.
- Explicit blockers: finalization depends on reviewed subfeature-local planning
  outputs and closed execution slices.
- Parallel-safe slices: none recommended in the first iteration because nested
  path resolution, state transitions, and cleanup semantics are tightly coupled.
- Increment ordering: I1 -> I2 -> I3 -> I4.
- Lane owners and handoffs: `guide-planning` routes into `add-subfeature`;
  `assess`, `design`, and `breakdown` operate on the selected subfeature;
  `review-planning` confirms readiness before slice bootstrap;
  `finalize-subfeature` closes the feature-level cleanup loop.

## 6. Bootstrap Order

1. FEW-01-registry
2. FEW-01-initiate-change
3. FEW-02-impact-analysis
4. FEW-03-change-metadata
5. FEW-03-change-artifacts
6. FEW-04-change-breakdown
7. FEW-04-finalization-workflow
8. FEW-05-history-closure
9. FEW-05-routing-docs

## 7. Review Notes

- Review outcome: Ready for `slice` after selecting concrete slices from the
  reviewed backlog.
- Blocking findings: none. Discovery intent, design boundaries, and breakdown
  sequencing are consistent with durable subfeature planning.
- Handoff note: start with `FEW-01-registry`, then `FEW-01-initiate-change`,
  and keep feature-level finalization explicit and non-destructive.
