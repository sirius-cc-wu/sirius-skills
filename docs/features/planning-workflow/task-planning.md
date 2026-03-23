# Task Planning

## 1. Planning Scope

- Feature: Planning workflow
- Planning sources:
  - `README.md`
  - `SKILLS_METHODOLOGY.md`
  - `skills/planning-driver/SKILL.md`
  - `skills/discover/SKILL.md`
  - `skills/design/SKILL.md`
  - `skills/breakdown/SKILL.md`
  - `skills/review-planning/SKILL.md`
  - `skills/track/SKILL.md`
- Execution tracker: none (reverse-engineered repo planning only)
- Execution mode: `single-agent`
- Notes: This breakdown models the planning-layer capability already present in the repo.

## 2. Story Decisions

| Story ID | Story Size | Decision | Reason | Output Task Count |
| --- | --- | --- | --- | --- |
| PW-01 | M | keep | Planning registry bootstrap is a coherent slice with clear validation. | 1 |
| PW-02 | L | split | Readiness transitions and artifact validation form two related but distinct packets. | 2 |
| PW-03 | L | split | Breakdown template generation and slice quality guidance should be separated. | 2 |
| PW-04 | M | split | Review readiness and execution handoff are adjacent but different concerns. | 2 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Durable feature planning bootstrap | PW-01, PW-02 | PW-01-registry, PW-02-gates | A maintainer can initialize a feature and advance to `discovery_ready` / `design_ready` with valid artifacts. | Simplest end-to-end planning flow |
| I2 | Execution-ready decomposition | PW-03 | PW-03-templates, PW-03-breakdown-guidance | A feature can produce increments and slices in `task-planning.md` and `task-traceability.md`. | Depends on I1 |
| I3 | Reviewed handoff to execution | PW-04 | PW-04-review-readiness, PW-04-track-handoff | Planning review notes and ready task IDs can be recorded before execution bootstrap. | Depends on I2 |

## 4. Execution Task Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Tracker Action | Depends On | Track Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PW-01-registry | PW-01 | Initialize planning registry and metadata | Manage planning config, registry, and `.planning-meta.json` lifecycle. | `skills/planning-driver/scripts/manage_planning.py` | primary | `pytest -q skills/planning-driver/tests/test_manage_planning.py` | create task |  | yes |
| PW-02-gates | PW-02 | Enforce planning readiness gates | Validate required artifacts across discovery and design transitions. | `skills/planning-driver/scripts/manage_planning.py` | primary | `pytest -q skills/planning-driver/tests/test_manage_planning.py` | create task | PW-01-registry | yes |
| PW-02-routing | PW-02 | Document routing across planning skills | Keep planning-driver routing and lifecycle guidance aligned with docs. | `README.md`, `SKILLS_METHODOLOGY.md`, `skills/planning-driver/SKILL.md` | primary | Review docs for consistent routing and states | create task | PW-02-gates | yes |
| PW-03-templates | PW-03 | Maintain breakdown scaffolding | Keep breakdown templates and scaffold behavior aligned with planning needs. | `skills/breakdown/assets`, `skills/breakdown/scripts` | primary | `pytest -q skills/breakdown/tests/test_scaffold_breakdown.py` | create task | PW-02-routing | yes |
| PW-03-breakdown-guidance | PW-03 | Produce execution-ready slice guidance | Ensure decomposition guidance yields traceable, demonstrable increments. | `skills/breakdown/SKILL.md`, templates | primary | Review generated artifacts for coherent increments and slice IDs | create task | PW-03-templates | yes |
| PW-04-review-readiness | PW-04 | Record planning review readiness | Require review notes and validate reviewed state before handoff. | `skills/review-planning/`, `manage_planning.py` | primary | `pytest -q skills/planning-driver/tests/test_manage_planning.py` | create task | PW-03-breakdown-guidance | yes |
| PW-04-track-handoff | PW-04 | Bootstrap execution from reviewed planning output | Pass ready task IDs to `track` without moving execution logic into planning. | `skills/track/SKILL.md`, planning docs | primary | Validate `track_ready` with `--task-id` using `manage_planning.py` | create task | PW-04-review-readiness | yes |

## 5. Dependency Notes

- Critical path: registry bootstrap -> readiness gates -> breakdown templates -> review/handoff.
- Explicit blockers: planning review depends on breakdown artifacts being concrete.
- Parallel-safe slices: none recommended; the planning workflow is tightly coupled.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: planning-driver to discover/design/breakdown, then review-planning, then track.
- Integration checkpoints: validate-feature after each readiness milestone.

## 6. Bootstrap Order

1. PW-01-registry
2. PW-02-gates, PW-02-routing
3. PW-03-templates, PW-03-breakdown-guidance
4. PW-04-review-readiness, PW-04-track-handoff

## 7. Open Questions / Stop-and-Ask Items

- Should planning review ever become a tooling-enforced gate before tracker task creation?
- How much semantic validation should the repo enforce beyond non-empty planning artifacts?
## 8. Review Notes

- Review outcome: Ready for `track` after selecting concrete slices from this backlog.
- Blocking findings: none. Discovery intent, design boundaries, and breakdown sequencing are consistent.
- Handoff note: start with `PW-01-registry`, then preserve the documented dependency chain through `PW-04-track-handoff`.
- Follow-up improvements: if the repo later wants stronger review enforcement, consider structured evidence for artifact-quality checks in addition to file-presence validation.
