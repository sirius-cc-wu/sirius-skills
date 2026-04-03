# Slice Planning

Use this file to decompose repo stories into execution-ready slices before bootstrapping execution slices.

## 1. Planning Scope

- Feature: Hierarchical scope support
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `user-stories.md`
  - adjacent precedent from `planning-workflow`, `proposal-workflow`, and `execution-workflow`
- Execution system: repository-managed slices
- Execution mode: `single-agent`
- Notes:
  - This feature changes shared path-resolution behavior used by planning, proposal, and execution helpers, so the first pass should preserve one serial critical path.
  - The MVP keeps repository-root fallback behavior, but nested scopes become explicit local workspaces via `.skills/`.
  - Scoped slices are part of the intended outcome: execution should follow the resolved scope rather than stay in one global repo-root slice pool.

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| HSS-01 | M | medium | keep | Repository-root fallback is one cohesive foundation slice with one primary compatibility validation path. | 1 |
| HSS-02 | M | medium | keep | Local planning and proposal registries should land as one bounded nested-scope capability. | 1 |
| HSS-03 | M | medium | keep | Nearest-scope CLI resolution is one focused runtime integration once scope roots exist. | 1 |
| HSS-04 | M | high | split | Generic ambiguity handling and promotion-specific cross-scope targeting have different failure modes and should validate separately. | 2 |
| HSS-05 | L | medium | keep | One scope-entry skill plus routing docs is a coherent user-facing packet after the runtime contract stabilizes. | 1 |
| HSS-06 | L | high | split | Config inheritance and scope-local execution touch different helper stacks and validation paths, so combining them would be brittle. | 2 |

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
| I1 | Scope-aware planning works from root and nested directories | HSS-01, HSS-02, HSS-03 | HSS-01-root-fallback, HSS-02-local-registries, HSS-03-nearest-scope | A maintainer can run planning/proposal commands from a nested scope and get local registries while repo-root behavior still works unchanged. | Simplest end-to-end usable path |
| I2 | Multi-scope targeting is safe and configurable | HSS-04, HSS-06 | HSS-04-scope-selection, HSS-04-promotion-targeting, HSS-06-config-inheritance | Ambiguous slug lookups stop for explicit scope choice, cross-scope promotion requires explicit targeting, and child scopes override parent config deterministically. | Depends on I1 |
| I3 | Execution follows the resolved scope | HSS-06 | HSS-06-scoped-execution | A nested scope can bootstrap and manage slices using its resolved `execution.json`, `conventions.json`, and `slice_dir`. | Depends on I2 |
| I4 | Users get one scope-aware workflow entrypoint | HSS-05 | HSS-05-guide-scope | `guide-scope` can resolve the active scope and hand off cleanly to planning, execution, or bootstrap flows. | Depends on I3 |

Rules:

- keep increments feature-scoped planning artifacts, not execution slices
- each increment should be demonstrable without requiring the full project to be complete
- an increment can include one or many execution-ready slices
- planned slices and execution slices remain slice-scoped even when they belong to the same increment

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HSS-01-root-fallback | HSS-01 | Add scope runtime with root fallback | Introduce shared scope resolution and preserve current repository-root behavior when no explicit nested scope exists. | shared scope helper, `skills/guide-planning/scripts/manage_planning.py`, `skills/propose/scripts/manage_proposals.py` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/propose/tests/test_manage_proposals.py` | create slice |  | yes |
| HSS-02-local-registries | HSS-02 | Keep planning and proposal registries local to each scope | Resolve feature and proposal roots inside the selected scope instead of assuming one repository-root planning area. | `skills/guide-planning/scripts/manage_planning.py`, `skills/propose/scripts/manage_proposals.py` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/propose/tests/test_manage_proposals.py` | create slice | HSS-01-root-fallback | yes |
| HSS-03-nearest-scope | HSS-03 | Default CLI operations to the nearest enclosing scope | Add nearest-scope resolution for planning and proposal commands when `--scope` is not provided. | shared scope helper, planning/proposal CLI entrypoints | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/propose/tests/test_manage_proposals.py` | create slice | HSS-01-root-fallback, HSS-02-local-registries | yes |
| HSS-04-scope-selection | HSS-04 | Require explicit scope selection for ambiguous lookups | Detect multi-scope ambiguity, surface candidate scopes, and fail safely for slug-only lookups. | shared scope helper, planning/proposal lookup helpers | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/propose/tests/test_manage_proposals.py` | create slice | HSS-03-nearest-scope | yes |
| HSS-04-promotion-targeting | HSS-04 | Support explicit cross-scope promotion targets | Keep same-scope promotion as default while requiring `--target-scope` when canonical planning should be created elsewhere. | `skills/guide-planning/scripts/manage_planning.py`, `skills/propose/scripts/manage_proposals.py` | primary | `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/propose/tests/test_manage_proposals.py` | create slice | HSS-04-scope-selection | yes |
| HSS-06-config-inheritance | HSS-06 | Merge parent and child `.skills` config by scope | Load planning, execution, and conventions config from the scope chain with child overrides and preserved unknown keys. | shared scope helper, `skills/bootstrap/`, `skills/guide-planning/`, `skills/propose/`, `skills/guide-execution/` | primary | `pytest -q skills/bootstrap/tests/test_bootstrap.py skills/guide-planning/tests/test_manage_planning.py skills/propose/tests/test_manage_proposals.py skills/guide-execution/tests/test_manage_execution.py` | create slice | HSS-03-nearest-scope | yes |
| HSS-06-scoped-execution | HSS-06 | Keep slices and execution registries local to the resolved scope | Apply the resolved scope's `execution.json`, `conventions.json`, and `slice_dir` to execution helpers and slice bootstrap. | `skills/guide-execution/scripts/manage_execution.py`, `skills/slice/scripts/bootstrap_slice.py` | primary | `pytest -q skills/guide-execution/tests/test_manage_execution.py skills/slice/tests/test_bootstrap_slice.py` | create slice | HSS-06-config-inheritance | yes |
| HSS-05-guide-scope | HSS-05 | Add one scope-aware entry skill | Create `guide-scope` and align repo docs and examples around scope discovery, explicit targeting, and workflow handoff. | `skills/guide-scope/`, `README.md`, `SKILLS_METHODOLOGY.md` | primary | review `skills/guide-scope/SKILL.md` handoff examples + `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/guide-execution/tests/test_manage_execution.py` | create slice | HSS-04-promotion-targeting, HSS-06-scoped-execution | yes |

## 5. Dependency Notes

- Critical path: root fallback -> local registries -> nearest-scope routing -> ambiguity guards -> promotion targeting/config inheritance -> scoped execution -> guide-scope routing.
- Explicit blockers: scope-local execution must wait for config inheritance, and `guide-scope` should not hand off until planning and execution contracts share the same scope model.
- Parallel-safe slices: none recommended in the first iteration because the shared scope runtime and config semantics are foundational across all downstream slices.
- Increment ordering: I1 -> I2 -> I3 -> I4.
- Lane owners and handoffs: establish the shared scope runtime first, integrate planning and proposal flows next, then execution/slice bootstrap, and finally add the user-facing `guide-scope` routing layer.
- Integration checkpoints:
  - validate repository-root fallback and nested planning/proposal behavior after I1
  - validate ambiguity errors, explicit targeting, and inherited config after I2
  - validate nested-scope execution and slice bootstrap after I3
  - validate `guide-scope` handoff examples and top-level workflow docs after I4

## 6. Bootstrap Order

1. HSS-01-root-fallback
2. HSS-02-local-registries
3. HSS-03-nearest-scope
4. HSS-04-scope-selection
5. HSS-04-promotion-targeting
6. HSS-06-config-inheritance
7. HSS-06-scoped-execution
8. HSS-05-guide-scope

## 7. Open Questions / Stop-and-Ask Items

- Resolved for MVP: nested scopes are explicit via local `.skills/`, while the repository root remains the compatibility fallback scope.
- Resolved for MVP: slices are scope-local through the resolved `slice_dir`, not pooled globally under one repository-root execution backlog.
- Resolved for MVP: cross-scope promotion requires explicit `--target-scope`; it must not happen implicitly from slug-only lookups.

## 8. Review Notes

- Review outcome: Ready for `slice` after bootstrapping the first reviewed backlog item from the documented dependency chain.
- Blocking findings: none. Discovery goals, scope decisions, design contracts, and backlog sequencing are aligned, and the serial-first execution strategy is appropriate for the shared scope runtime.
- Handoff note: start with `HSS-01-root-fallback`, then preserve the dependency chain through `HSS-06-scoped-execution` before adding `HSS-05-guide-scope`.
- Follow-up improvements: if later iterations need broader observability, add a follow-on slice for repository-wide scope discovery/reporting without changing the local-registry ownership model.

## Notes

- This file is feature-scoped planning, not slice-scoped execution.
- Keep increment definitions here, not in execution-slice artifacts.
- Once planned slices are created, record the actual slice IDs in `slice-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from traceability notes and planning discussion.
