# Slice Planning

## 1. Planning Scope

- Feature: Execution workflow
- Planning sources:
  - `README.md`
  - `SKILLS_METHODOLOGY.md`
  - `skills/guide-execution/SKILL.md`
  - `skills/brief/SKILL.md`
  - `skills/blueprint/SKILL.md`
  - `skills/review-execution/SKILL.md`
  - `skills/close-slice/SKILL.md`
  - `skills/commit/SKILL.md`
  - `skills/create-pr/SKILL.md`
- Execution system: repository-managed slices (reverse-engineered repo planning only)
- Execution mode: `single-agent`
- Notes: This breakdown models the existing slice-scoped execution system in the repo.

## 2. Story Decisions

| Story ID | Story Size | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- |
| EW-01 | M | keep | Slice bootstrap and registry initialization are tightly related. | 1 |
| EW-02 | L | split | Brief authoring and checklist enforcement are adjacent but separable. | 2 |
| EW-03 | L | split | Plan generation and readiness gating should be isolated for validation. | 2 |
| EW-04 | L | split | Review, relation handling, and closure publication create multiple execution slices. | 3 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Execution slice bootstrap | EW-01, EW-02 | EW-01-bootstrap, EW-02-brief, EW-02-checklist | A new work item can produce a valid slice, `brief.md`, and requirements checklist. | Simplest executable path |
| I2 | Ready-to-code execution plan | EW-03 | EW-03-plan, EW-03-gates | A slice can advance to `execution_ready` with traceable packets and validation steps. | Depends on I1 |
| I3 | Durable review and closure | EW-04 | EW-04-review, EW-04-relations, EW-04-close | A completed slice can be reviewed, related to older slices, and published non-destructively. | Depends on I2 |

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01-bootstrap | EW-01 | Bootstrap execution registry and slices | Manage config, slice registry, metadata, and slice creation. | `skills/guide-execution/scripts/manage_execution.py` | primary | `pytest -q skills/guide-execution/tests/test_manage_execution.py` | create slice |  | yes |
| EW-02-brief | EW-02 | Author slice brief structure | Maintain `brief.md` structure, acceptance framing, and requirement sections. | `skills/brief/SKILL.md`, `skills/brief/templates/brief-template.md` | primary | Review generated brief against skill rules | create slice | EW-01-bootstrap | yes |
| EW-02-checklist | EW-02 | Enforce requirement checklist readiness | Keep requirements checklist aligned with brief readiness gates. | `skills/brief/SKILL.md`, `manage_execution.py` | primary | `pytest -q skills/guide-execution/tests/test_manage_execution.py` | create slice | EW-02-brief | yes |
| EW-03-plan | EW-03 | Generate execution plan packets | Maintain `blueprint.md` structure with gates, packets, and traceability. | `skills/blueprint/SKILL.md`, `skills/blueprint/templates/plan-template.md` | primary | Review plan completeness and traceability | create slice | EW-02-checklist | yes |
| EW-03-gates | EW-03 | Enforce plan readiness transitions | Validate plan presence and readiness state progression. | `skills/guide-execution/scripts/manage_execution.py` | primary | `pytest -q skills/guide-execution/tests/test_manage_execution.py` | create slice | EW-03-plan | yes |
| EW-04-review | EW-04 | Review implementation against execution artifacts | Keep review guidance aligned with brief-to-implementation comparisons. | `skills/review-execution/SKILL.md` | primary | Review workflow docs for consistent review boundary | create slice | EW-03-gates | yes |
| EW-04-relations | EW-04 | Record durable slice relations | Maintain relation types, scoping, and reciprocal integrity. | `skills/guide-execution/scripts/manage_execution.py` | primary | `pytest -q skills/guide-execution/tests/test_manage_execution.py` | create slice | EW-04-review | yes |
| EW-04-close | EW-04 | Close and publish slices non-destructively | Record closure metadata and optional publication output. | `skills/close-slice/scripts/close_slice.py` | primary | `pytest -q skills/close-slice/tests/test_close_slice.py` | create slice | EW-04-relations | yes |

## 5. Dependency Notes

- Critical path: bootstrap -> brief/checklist -> plan/gates -> review -> relations -> close.
- Explicit blockers: closure requires a fully ready execution artifact chain.
- Parallel-safe slices: none recommended; the artifacts and state transitions are tightly coupled.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: slice -> guide-execution -> brief/plan -> review-execution -> close-slice.
- Integration checkpoints: validate-slice before review and before closure publication.

## 6. Bootstrap Order

1. EW-01-bootstrap
2. EW-02-brief, EW-02-checklist
3. EW-03-plan, EW-03-gates
4. EW-04-review, EW-04-relations, EW-04-close

## 7. Open Questions / Stop-and-Ask Items

- Should the repo eventually enforce structured evidence that validation steps in `blueprint.md` were run?
- Should relation auditing become part of the default close-slice path instead of an explicit extra command?
## 8. Review Notes

- Review outcome: Ready for `slice` after choosing the first execution slice to bootstrap.
- Blocking findings: none. The brief, plan, review, relation, and closure responsibilities are aligned across discovery, design, and breakdown.
- Handoff note: bootstrap from `EW-01-bootstrap` or `EW-02-brief`; keep the later review and closure slices behind the documented readiness gates.
- Follow-up improvements: future planning could define how validation evidence from `blueprint.md` should be surfaced during execution review.
