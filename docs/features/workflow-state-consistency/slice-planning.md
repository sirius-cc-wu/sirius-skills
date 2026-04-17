# Slice Planning

Use this file to decompose repo stories into execution-ready slices before bootstrapping execution slices.

## 1. Planning Scope

- Feature: Workflow state consistency
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
  - current maintenance and lifecycle owners under `skills/audit-artifacts/`, `skills/trace-artifacts/`, `skills/repair-artifacts/`, `skills/report-artifacts/`, `skills/guide-planning/`, `skills/add-subfeature/`, `skills/guide-execution/`, and `skills/close-slice/`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes:
  - The first pass should keep one serial critical path because the shared workflow-state library defines semantics reused by every downstream slice.
  - Planned slices intentionally separate read-only preview/reporting work from owner-mediated transition checks so validation stays deterministic.
  - No slice introduces new user-facing config by default; any invariant escape hatch stays a later review decision.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| WSC-01 | M | high | keep | Transition guardrails touch several lifecycle owners, but the work is still one cohesive packet once shared findings and blocking rules are defined. | 1 |
| WSC-02 | M | high | split | Shared-library extraction and multi-skill adoption have different validation paths and should not be coupled into one brittle packet. | 2 |
| WSC-03 | M | medium | keep | Preview-only semantic drift reporting is one bounded maintenance behavior once shared reconciliation exists. | 1 |
| WSC-04 | S | low | keep | Installed-vs-repo parity inspection is isolated and independently verifiable. | 1 |
| WSC-05 | M | medium | keep | Read-only consistency hooks and automation wiring can land as one focused validation packet after the invariants stabilize. | 1 |

Decision rules:

- `keep` means the story is already small enough to map to one executable slice.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not be executed yet.
- split any `XL` story before slice bootstrap
- `S`/`M`/`L` stories may also split when risk, validation shape, coupling, or handoff complexity would make one packet brittle
- record the main reason for the decision, not just the size label

Risk rubric:

- `low`: one cohesive packet with one clear validation path
- `medium`: some coupling, multiple touchpoints, or moderate sequencing/handoff risk
- `high`: cross-subsystem impact, migration/reconciliation, compatibility risk, or materially different validation paths

## 3. Increment Plan

Use increments to group related slices into small, demonstrable outcomes. Increment 1 should usually be the simplest end-to-end usable path.

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Maintenance skills share one canonical workflow-state interpretation | WSC-02 | WSC-02-shared-library, WSC-02-maintenance-adoption | Audit, trace, repair, and report agree on the same fixture-repo linkage findings in targeted tests. | Simplest end-to-end usable path and foundation for all later guardrails |
| I2 | Maintainers can preview semantic drift and lifecycle owners surface it during transitions | WSC-01, WSC-03 | WSC-03-semantic-preview, WSC-01-transition-guardrails | Repair/report preview separates semantic drift from derived drift, and close/finalize flows warn or block on the same high-confidence findings. | Depends on I1 |
| I3 | Repo owners can detect stale installed behavior and enforce consistency in automation | WSC-04, WSC-05 | WSC-04-installed-parity, WSC-05-validation-hooks | Installed-vs-repo mismatches become visible, and repeatable validation fails on fixture-backed workflow drift. | Depends on I2 |

Rules:

- keep increments feature-scoped planning artifacts, not execution slices
- each increment should be demonstrable without requiring the full project to be complete
- an increment can include one or many execution-ready slices
- planned slices and execution slices remain slice-scoped even when they belong to the same increment

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WSC-02-shared-library | WSC-02 | Create shared workflow-state library | Introduce the canonical repo-local workflow-state package for normalized models, artifact inventory, traceability parsing, reconciliation, transition helpers, and parity primitives without changing writer ownership. | `lib/workflow_state/`, `skills/audit-artifacts/`, `skills/trace-artifacts/` | primary | `pytest -q skills/audit-artifacts/tests/test_audit_artifacts.py skills/trace-artifacts/tests/test_trace_artifacts.py` | create slice |  | yes |
| WSC-02-maintenance-adoption | WSC-02 | Adopt shared reconciliation across maintenance skills | Move audit, trace, repair, and report wrappers onto the shared workflow-state interfaces, and wire managed install/package sync so self-contained installed skills receive the shared library deterministically. | `skills/audit-artifacts/`, `skills/trace-artifacts/`, `skills/repair-artifacts/`, `skills/report-artifacts/`, `Makefile` | primary | `pytest -q skills/audit-artifacts/tests/test_audit_artifacts.py skills/trace-artifacts/tests/test_trace_artifacts.py skills/repair-artifacts/tests/test_repair_artifacts.py skills/report-artifacts/tests/test_report_artifacts.py` plus a managed install/package artifact check for the synced shared library | create slice | WSC-02-shared-library | yes |
| WSC-03-semantic-preview | WSC-03 | Add preview-only semantic drift reporting | Extend maintenance output so semantic metadata drift is previewed separately from derived registry/readme rebuild work and can be reviewed safely before any owner-mediated write path. | `skills/repair-artifacts/`, `skills/report-artifacts/` | primary | `pytest -q skills/repair-artifacts/tests/test_repair_artifacts.py skills/report-artifacts/tests/test_report_artifacts.py` | create slice | WSC-02-maintenance-adoption | yes |
| WSC-01-transition-guardrails | WSC-01 | Add high-confidence transition consistency checks | Wire shared transition checks into planning, subfeature, execution, and close/finalize owners so obvious stale-state mutations surface immediately and deterministically. | `skills/guide-planning/`, `skills/add-subfeature/`, `skills/guide-execution/`, `skills/close-slice/` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/add-subfeature/tests/test_manage_subfeatures.py skills/guide-execution/tests/test_manage_execution.py skills/close-slice/tests/test_close_slice.py` | create slice | WSC-03-semantic-preview | yes |
| WSC-04-installed-parity | WSC-04 | Surface installed-vs-repo skill parity drift | Add one shared parity inspection path surfaced through existing maintenance commands and shared output fields so maintainers can tell when active installed maintenance-skill behavior no longer matches the checked-in repo source. | `lib/workflow_state/parity.py`, maintenance skill entrypoints, `Makefile` | primary | `pytest -q skills/audit-artifacts/tests/test_audit_artifacts.py skills/report-artifacts/tests/test_report_artifacts.py` and a parity output check against a stale-install fixture or staged package copy | create slice | WSC-02-shared-library | yes |
| WSC-05-validation-hooks | WSC-05 | Add repeatable workflow consistency validation hooks | Turn the stabilized read-only reconciliation checks into a repeatable validation entrypoint suitable for CI and maintainer reruns against fixture-backed drift cases. | `Makefile`, `skills/audit-artifacts/`, `skills/report-artifacts/` | primary | `pytest -q skills/audit-artifacts/tests/test_audit_artifacts.py skills/report-artifacts/tests/test_report_artifacts.py skills/guide-planning/tests/test_manage_planning.py skills/close-slice/tests/test_close_slice.py` | create slice | WSC-01-transition-guardrails, WSC-04-installed-parity | yes |

## 5. Dependency Notes

- Critical path: shared library -> maintenance adoption -> semantic preview -> transition guardrails -> installed parity -> validation hooks.
- Explicit blockers: transition owners should not enforce guardrails until the preview path stabilizes the shared finding shapes, and repeatable validation should wait until both transition checks and parity inspection exist.
- Parallel-safe slices: none recommended in the first iteration because the shared workflow-state library and invariant set are foundational across all downstream slices.
- Increment ordering: I1 -> I2 -> I3.
- Lane owners and handoffs: establish canonical shared semantics first, then add read-only preview/reporting, then wire owner-script enforcement, and finally expose parity plus repeatable automation hooks.
- Integration checkpoints:
  - validate shared maintenance-skill semantics and install/package sync after I1
  - validate preview output and transition-owner enforcement after I2
  - validate parity reporting and repeatable automation entrypoints after I3

## 6. Bootstrap Order

1. WSC-02-shared-library
2. WSC-02-maintenance-adoption
3. WSC-03-semantic-preview
4. WSC-01-transition-guardrails
5. WSC-04-installed-parity
6. WSC-05-validation-hooks

## 7. Open Questions / Stop-and-Ask Items

- Resolved for the first rollout: block only on the highest-confidence subfeature/slice invariants and keep broader heuristics as warnings or follow-on work until more fixture coverage exists.
- Resolved for the first rollout: surface installed-vs-repo parity through existing maintenance commands and shared output fields rather than a dedicated command.

## 8. Review Notes

- Review outcome: Ready for `slice` after selecting the first reviewed backlog item from the documented dependency chain.
- Blocking findings: none. Discovery goals, design boundaries, install-time packaging expectations, configuration ownership, and slice sequencing are aligned.
- Handoff note: start with `WSC-02-shared-library`, then preserve the documented dependency chain through `WSC-05-validation-hooks`; `WSC-02-maintenance-adoption` must include managed install/package sync for self-contained skills.
- Follow-up improvements: if parity or CI wiring grows beyond this scope, promote it into a follow-on subfeature instead of widening the first increment.

## Notes

- This file is feature-scoped planning, not slice-scoped execution.
- Keep increment definitions here, not in execution-slice artifacts.
- Once planned slices are created, record the actual slice IDs in `slice-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from traceability notes and planning discussion.
