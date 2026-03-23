# Task Planning

## 1. Planning Scope

- Feature: Execution workflow
- Planning sources:
  - `README.md`
  - `SKILLS_METHODOLOGY.md`
  - `skills/execution-driver/SKILL.md`
  - `skills/define/SKILL.md`
  - `skills/plan/SKILL.md`
  - `skills/review-execution/SKILL.md`
  - `skills/close-track/SKILL.md`
  - `skills/commit/SKILL.md`
  - `skills/create-pr/SKILL.md`
- Execution tracker: none (reverse-engineered repo planning only)
- Execution mode: `single-agent`
- Notes: This breakdown models the existing task-scoped execution system in the repo.

## 2. Story Decisions

| Story ID | Story Size | Decision | Reason | Output Task Count |
| --- | --- | --- | --- | --- |
| EW-01 | M | keep | Track bootstrap and registry initialization are tightly related. | 1 |
| EW-02 | L | split | Brief authoring and checklist enforcement are adjacent but separable. | 2 |
| EW-03 | L | split | Plan generation and readiness gating should be isolated for validation. | 2 |
| EW-04 | L | split | Review, relation handling, and closure publication create multiple execution slices. | 3 |

## 3. Increment Plan

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Task-scoped track bootstrap | EW-01, EW-02 | EW-01-bootstrap, EW-02-brief, EW-02-checklist | A new work item can produce a valid track, `brief.md`, and requirements checklist. | Simplest executable path |
| I2 | Ready-to-code execution plan | EW-03 | EW-03-plan, EW-03-gates | A track can advance to `execution_ready` with traceable packets and validation steps. | Depends on I1 |
| I3 | Durable review and closure | EW-04 | EW-04-review, EW-04-relations, EW-04-close | A completed track can be reviewed, related to older tracks, and published non-destructively. | Depends on I2 |

## 4. Execution Task Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Tracker Action | Depends On | Track Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EW-01-bootstrap | EW-01 | Bootstrap execution registry and tracks | Manage config, track registry, metadata, and track creation. | `skills/execution-driver/scripts/manage_execution.py` | primary | `pytest -q skills/execution-driver/tests/test_manage_execution.py` | create task |  | yes |
| EW-02-brief | EW-02 | Author task brief structure | Maintain `brief.md` structure, acceptance framing, and requirement sections. | `skills/define/SKILL.md`, `skills/define/templates/brief-template.md` | primary | Review generated brief against skill rules | create task | EW-01-bootstrap | yes |
| EW-02-checklist | EW-02 | Enforce requirement checklist readiness | Keep requirements checklist aligned with brief readiness gates. | `skills/define/SKILL.md`, `manage_execution.py` | primary | `pytest -q skills/execution-driver/tests/test_manage_execution.py` | create task | EW-02-brief | yes |
| EW-03-plan | EW-03 | Generate execution plan packets | Maintain `plan.md` structure with gates, packets, and traceability. | `skills/plan/SKILL.md`, `skills/plan/templates/plan-template.md` | primary | Review plan completeness and traceability | create task | EW-02-checklist | yes |
| EW-03-gates | EW-03 | Enforce plan readiness transitions | Validate plan presence and readiness state progression. | `skills/execution-driver/scripts/manage_execution.py` | primary | `pytest -q skills/execution-driver/tests/test_manage_execution.py` | create task | EW-03-plan | yes |
| EW-04-review | EW-04 | Review implementation against execution artifacts | Keep review guidance aligned with brief-to-implementation comparisons. | `skills/review-execution/SKILL.md` | primary | Review workflow docs for consistent review boundary | create task | EW-03-gates | yes |
| EW-04-relations | EW-04 | Record durable track relations | Maintain relation types, scoping, and reciprocal integrity. | `skills/execution-driver/scripts/manage_execution.py` | primary | `pytest -q skills/execution-driver/tests/test_manage_execution.py` | create task | EW-04-review | yes |
| EW-04-close | EW-04 | Close and publish tracks non-destructively | Record closure metadata and optional publication output. | `skills/close-track/scripts/close_track.py` | primary | `pytest -q skills/close-track/tests/test_close_track.py` | create task | EW-04-relations | yes |

## 5. Dependency Notes

- Critical path: bootstrap -> brief/checklist -> plan/gates -> review -> relations -> close.
- Explicit blockers: closure requires a fully ready execution artifact chain.
- Parallel-safe slices: none recommended; the artifacts and state transitions are tightly coupled.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: track -> execution-driver -> define/plan -> review-execution -> close-track.
- Integration checkpoints: validate-track before review and before closure publication.

## 6. Bootstrap Order

1. EW-01-bootstrap
2. EW-02-brief, EW-02-checklist
3. EW-03-plan, EW-03-gates
4. EW-04-review, EW-04-relations, EW-04-close

## 7. Open Questions / Stop-and-Ask Items

- Should the repo eventually enforce structured evidence that validation steps in `plan.md` were run?
- Should relation auditing become part of the default close-track path instead of an explicit extra command?
## 8. Review Notes

- Review outcome: Ready for `track` after choosing the first execution slice to bootstrap.
- Blocking findings: none. The brief, plan, review, relation, and closure responsibilities are aligned across discovery, design, and breakdown.
- Handoff note: bootstrap from `EW-01-bootstrap` or `EW-02-brief`; keep the later review and closure slices behind the documented readiness gates.
- Follow-up improvements: future planning could define how validation evidence from `plan.md` should be surfaced during execution review.
