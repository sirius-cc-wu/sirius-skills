# Slice Planning

## 1. Planning Scope

- Feature: Planning workflow
- Planning sources:
  - `README.md`
  - `SKILLS_METHODOLOGY.md`
  - `skills/guide-planning/SKILL.md`
  - `skills/discover/SKILL.md`
  - `skills/design/SKILL.md`
  - `skills/breakdown/SKILL.md`
  - `skills/review-planning/SKILL.md`
  - `skills/slice/SKILL.md`
- Execution system: repository-managed slices (reverse-engineered repo planning only)
- Execution mode: `single-agent`
- Notes: This breakdown models the planning-layer capability already present in the repo.

## 2. Story Decisions

| Story ID | Story Size | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- |
| PW-01 | M | keep | Planning registry bootstrap is a coherent slice with clear validation. | 1 |
| PW-02 | L | split | Readiness transitions and artifact validation form two related but distinct packets. | 2 |
| PW-03 | L | split | Breakdown template generation and slice quality guidance should be separated. | 2 |
| PW-04 | M | split | Review readiness and execution handoff are adjacent but different concerns. | 2 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Durable feature planning bootstrap | PW-01, PW-02 | pw-registry, pw-gates | A maintainer can initialize a feature and advance to `discovery_ready` / `design_ready` with valid artifacts. | Simplest end-to-end planning flow |
| I2 | Execution-ready decomposition | PW-03 | pw-templates, pw-breakdown-guidance | A feature can produce increments and slices in `slice-planning.md` and `slice-traceability.md`. | Depends on I1 |
| I3 | Reviewed handoff to execution | PW-04 | pw-review-readiness, pw-slice-handoff | Planning review notes and ready slice IDs can be recorded before execution bootstrap. | Depends on I2 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pw-registry | PW-01 | Initialize planning registry and metadata | Manage planning config, registry, and `.planning-meta.json` lifecycle. | `skills/guide-planning/scripts/manage_planning.py` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py` | create slice |  | yes |
| pw-gates | PW-02 | Enforce planning readiness gates | Validate required artifacts across discovery and design transitions. | `skills/guide-planning/scripts/manage_planning.py` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py` | create slice | pw-registry | yes |
| pw-routing | PW-02 | Document routing across planning skills | Keep guide-planning routing and lifecycle guidance aligned with docs. | `README.md`, `SKILLS_METHODOLOGY.md`, `skills/guide-planning/SKILL.md` | primary | Review docs for consistent routing and states | create slice | pw-gates | yes |
| pw-templates | PW-03 | Maintain breakdown scaffolding | Keep breakdown templates and scaffold behavior aligned with planning needs. | `skills/breakdown/assets`, `skills/breakdown/scripts` | primary | `pytest -q skills/breakdown/tests/test_scaffold_breakdown.py` | create slice | pw-routing | yes |
| pw-breakdown-guidance | PW-03 | Produce execution-ready slice guidance | Ensure decomposition guidance yields traceable, demonstrable increments. | `skills/breakdown/SKILL.md`, templates | primary | Review generated artifacts for coherent increments and slice IDs | create slice | pw-templates | yes |
| pw-review-readiness | PW-04 | Record planning review readiness | Require review notes and validate reviewed state before handoff. | `skills/review-planning/`, `manage_planning.py` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py` | create slice | pw-breakdown-guidance | yes |
| pw-slice-handoff | PW-04 | Bootstrap execution from reviewed planning output | Pass ready slice IDs to `slice` without moving execution logic into planning, then allow canonical features to advance to `implemented` after execution-backed completion. | `skills/slice/SKILL.md`, planning docs | primary | Validate `slice_ready` with `--slice-id` using `manage_planning.py` | create slice | pw-review-readiness | yes |

## 5. Dependency Notes

- Critical path: registry bootstrap -> readiness gates -> breakdown templates -> review/handoff.
- Explicit blockers: planning review depends on breakdown artifacts being concrete.
- Parallel-safe slices: none recommended; the planning workflow is tightly coupled.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: guide-planning to discover/design/breakdown, then review-planning, then slice.
- Integration checkpoints: validate-feature after each readiness milestone.

## 6. Bootstrap Order

1. pw-registry
2. pw-gates, pw-routing
3. pw-templates, pw-breakdown-guidance
4. pw-review-readiness, pw-slice-handoff

## 7. Open Questions / Stop-and-Ask Items

- Should planning review ever become a tooling-enforced gate before slice bootstrap?
- How much semantic validation should the repo enforce beyond non-empty planning artifacts?
## 8. Review Notes

- Review outcome: Ready for `slice` after selecting concrete slices from this backlog.
- Blocking findings: none. Discovery intent, design boundaries, and breakdown sequencing are consistent.
- Handoff note: start with `pw-registry`, then preserve the documented dependency chain through `pw-slice-handoff`.
- Follow-up improvements: if the repo later wants stronger review enforcement, consider structured evidence for artifact-quality checks in addition to file-presence validation.
