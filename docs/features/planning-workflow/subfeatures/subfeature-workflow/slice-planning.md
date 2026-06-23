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
| I1 | Start a durable subfeature under an existing feature | FEW-01, FEW-03 | sfw-registry, sfw-initiate-change, sfw-change-metadata | A maintainer can create `docs/features/<feature>/subfeatures/<subfeature-id>/` with registry and metadata tracked durably. | Simplest usable path |
| I2 | Assess and design the subfeature cleanly | FEW-02, FEW-03 | sfw-impact-analysis, sfw-change-artifacts | A reviewer can inspect changed intent, affected artifacts, and subfeature-local planning docs before breakdown. | Depends on I1 |
| I3 | Prepare reviewed subfeatures for execution | FEW-04 | sfw-change-breakdown, sfw-finalization-workflow | A reviewed subfeature can produce execution-ready slice-planning output plus explicit finalization behavior. | Depends on I2 |
| I4 | Close and finalize implemented subfeatures | FEW-05 | sfw-history-closure, sfw-routing-docs | Completed slices can be cleaned up and the durable subfeature can be marked implemented without deleting it. | Depends on I3 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sfw-registry | FEW-01 | Initialize subfeature registry | Add per-feature `subfeatures/README.md`, `registry.json`, and registry lifecycle management for subfeatures. | `sirius manage-subfeatures` | primary | `pytest -q skills/add-subfeature/tests/test_manage_subfeatures.py` | create slice |  | yes |
| sfw-initiate-change | FEW-01 | Bootstrap one durable subfeature | Resolve the parent feature, create `subfeatures/<subfeature-id>/`, and seed child planning artifacts. | `skills/add-subfeature/SKILL.md`, `sirius manage-subfeatures` | primary | `pytest -q skills/add-subfeature/tests/test_manage_subfeatures.py` | create slice | sfw-registry | yes |
| sfw-impact-analysis | FEW-02 | Produce impact analysis for a subfeature | Inspect parent planning docs and write `impact-analysis.md` with affected stories, artifacts, and slice implications. | `skills/assess/SKILL.md`, `skills/assess/`, subfeature docs | primary | Review generated `impact-analysis.md` plus `pytest -q skills/assess/tests/test_analyze_impact.py` | create slice | sfw-initiate-change | yes |
| sfw-change-metadata | FEW-03 | Enforce subfeature state model | Add `.subfeature-meta.json` shape, state transitions, and artifact-gated validation for durable subfeatures. | `sirius manage-subfeatures` | primary | `pytest -q skills/add-subfeature/tests/test_manage_subfeatures.py` | create slice | sfw-initiate-change | yes |
| sfw-change-artifacts | FEW-03 | Support subfeature-local planning artifacts | Extend path resolution so `design` and `breakdown` can operate on a selected subfeature cleanly. | `skills/design/`, `skills/breakdown/`, path-resolution helpers | primary | Validate one subfeature reaches `design_ready` / `breakdown_ready` using tooling or fixture tests | create slice | sfw-impact-analysis, sfw-change-metadata | yes |
| sfw-change-breakdown | FEW-04 | Break subfeatures into execution-ready slices | Generate subfeature-local `slice-planning.md` and `slice-traceability.md` that produce execution-ready slices from reviewed child planning. | `skills/breakdown/SKILL.md`, templates, subfeature examples | primary | Review generated planning docs and add fixture coverage for subfeature-local breakdown | create slice | sfw-change-artifacts | yes |
| sfw-finalization-workflow | FEW-04 | Represent implemented subfeatures without a dedicated finalization skill | Keep reviewed subfeatures non-destructive after execution by relying on closed slice state plus planning metadata instead of a separate cleanup skill. | `sirius manage-subfeatures`, `skills/close-slice/`, methodology docs | primary | Validate subfeature metadata and closure behavior in fixture tests | create slice | sfw-change-breakdown | yes |
| sfw-history-closure | FEW-05 | Keep implemented subfeatures as durable history | Preserve the subfeature folder and closed execution slices as durable history unless explicit archive maintenance is requested later. | `skills/add-subfeature/`, `skills/close-slice/`, archive docs | primary | Review docs and fixture behavior for retained history | create slice | sfw-finalization-workflow | yes |
| sfw-routing-docs | FEW-05 | Document routing for evolving features | Update methodology and skill docs so users know when to start a subfeature versus a net-new feature. | `README.md`, `SKILLS_METHODOLOGY.md`, `skills/guide-planning/SKILL.md` | primary | Review docs for route consistency and examples | create slice | sfw-history-closure | yes |

## 5. Dependency Notes

- Critical path: subfeature registry -> subfeature bootstrap -> impact analysis
  -> artifact support -> breakdown -> retained-history semantics -> routing/docs.
- Explicit blockers: retained-history semantics depend on reviewed
  subfeature-local planning outputs and closed execution slices.
- Parallel-safe slices: none recommended in the first iteration because nested
  path resolution, state transitions, and cleanup semantics are tightly coupled.
- Increment ordering: I1 -> I2 -> I3 -> I4.
- Lane owners and handoffs: `guide-planning` routes into `add-subfeature`;
  `assess`, `design`, and `breakdown` operate on the selected subfeature;
  `review-planning` confirms readiness before slice bootstrap;
  retained-history semantics close the feature-level execution loop without a
  dedicated finalization skill.

## 6. Bootstrap Order

1. sfw-registry
2. sfw-initiate-change
3. sfw-impact-analysis
4. sfw-change-metadata
5. sfw-change-artifacts
6. sfw-change-breakdown
7. sfw-finalization-workflow
8. sfw-history-closure
9. sfw-routing-docs

## 7. Review Notes

- Review outcome: Ready for `slice` after selecting concrete slices from the
  reviewed backlog.
- Blocking findings: none. Discovery intent, design boundaries, and breakdown
  sequencing are consistent with durable subfeature planning.
- Handoff note: start with `sfw-registry`, then `sfw-initiate-change`,
  and keep feature-level finalization explicit and non-destructive.
