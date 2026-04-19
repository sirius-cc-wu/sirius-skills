# Implementation Plan: Add one scope-aware entry skill

**Slice**: `hss-guide-scope-add-one-scope-aware-entry-skill`  
**Date**: 2026-04-04  
**Status**: Reviewed
**Spec**: `brief.md`

## 1. Summary

HSS-05 adds `guide-scope` as an optional scope-aware entry skill for multi-scope
repositories. The implementation should stay thin: document how to resolve the
active scope, stop on ambiguity, and hand off to `guide-planning`,
`guide-execution`, or `bootstrap`, then align the top-level repo docs and managed
skill installation list with that new entrypoint.

## 2. Technical Context

- Current system context:
  - planning and execution helpers already resolve scope correctly
  - bootstrap can target selected scopes
  - no user-facing scope-entry skill exists yet
- Target modules / files:
  - `skills/guide-scope/SKILL.md`
  - `README.md`
  - `SKILLS_METHODOLOGY.md`
  - `Makefile`
- Constraints:
  - keep `guide-scope` routing-only
  - do not duplicate lifecycle ownership already documented in `guide-planning`
    or `guide-execution`
  - keep single-scope repos backward compatible by describing `guide-scope` as
    optional unless scope selection matters
- Assumptions:
  - existing scope runtime and scoped execution behavior are already stable
  - a skill-only implementation is sufficient for this slice
- Out of scope:
  - new runtime helpers
  - feature-level reconcile
  - extra planning or execution CLI flags beyond what already exists

## 3. Planning Gates

### Architecture / Constraints

- Decision: implement `guide-scope` as a documentation-and-routing skill, then
  align install/docs surfaces around it.
- Result: PASS
- Notes: the scope runtime is already established in repo tooling, so this slice
  should not add a parallel routing subsystem.

### Risk / Compliance

- Decision: keep downstream ownership boundaries explicit and describe
  `guide-scope` as optional in single-scope repos.
- Result: PASS
- Notes: the main risk is claiming behavior the repo does not actually implement,
  so the skill must stick to existing scope-selection and handoff contracts.

### Testability

- Decision: review the new skill examples and run planning/execution regressions
  plus the repo suite.
- Result: PASS
- Notes: this slice is complete when the docs are aligned and existing runtime
  behavior remains green.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S001, S002 | V001 |
| FR-003 | S002 | V001 |
| FR-004 | S003 | V001 |
| FR-005 | S001, S002, S003 | V001, V002 |

## 5. Execution Plan

### Packet P01: Add the guide-scope skill

- Scope: create the new routing skill and document its handoff contract.
- Target files:
  - `skills/guide-scope/SKILL.md`
- Dependencies: hss-promotion-targeting, hss-scoped-execution
- Steps:
  - [x] S001 Author `guide-scope/SKILL.md` with scope discovery, ambiguity
        handling, and routing guidance to planning, execution, and bootstrap.
- Validation:
  - [x] V001 Review `skills/guide-scope/SKILL.md` handoff examples.
- Definition of Done: the repo has one clear scope-entry skill that documents the
  existing scope contract without duplicating downstream ownership.
- Rollback / Mitigation: keep the skill thin and route-only so it can be removed
  without affecting runtime behavior.

### Packet P02: Align repo guidance and installation

- Scope: add `guide-scope` to top-level workflow docs and managed skill install.
- Target files:
  - `README.md`
  - `SKILLS_METHODOLOGY.md`
  - `Makefile`
- Dependencies: P01
- Steps:
  - [x] S002 Update repo docs to present `guide-scope` as the optional
        multi-scope entrypoint before planning, execution, or bootstrap.
  - [x] S003 Add `guide-scope` to the managed skill set in `Makefile`.
- Validation:
  - [x] V002 `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/guide-execution/tests/test_manage_execution.py`
  - [x] V003 `pytest -q`
- Definition of Done: installation and repo guidance mention `guide-scope`
  consistently and do not contradict existing planning/execution contracts.
- Rollback / Mitigation: keep doc edits localized to scope-entry guidance so
  reverting them does not disturb the underlying workflow docs.

## 6. Supporting Notes

### Research Decisions

- Decision: do not add a new helper script in this slice.
- Rationale: the repository already has the shared scope runtime and route owners;
  the missing piece is the user-facing skill and aligned repo guidance.
- Alternative considered: add a standalone `manage_scope.py`; rejected because the
  planned validation and target files do not require new runtime tooling.

### Interface Notes

- Interface: `guide-scope` routes users to one of:
  - `guide-planning`
  - `guide-execution`
  - `bootstrap`
- Error states / compatibility notes:
  - stop for explicit scope choice when multiple scopes are plausible
  - keep `guide-scope` optional when the repository effectively has one scope
  - do not claim lifecycle ownership already documented in downstream skills

### Verification Scenarios

- Happy path:
  - multi-scope users can start from `guide-scope` and understand the next routed
    skill immediately
- Edge case:
  - single-scope repos are told that direct `guide-planning` or
    `guide-execution` entry remains valid
- Regression checks:
  - planning and execution tests remain green
  - full `pytest -q` remains green

## 7. Delivery Notes

- Sequencing rationale: add the skill first, then align repo docs and install so
  the new entrypoint is not discoverable in one place but missing elsewhere.
- Risks to monitor: accidental overstatement of implemented scope behavior, or
  doc changes that imply `guide-scope` is mandatory in repos where it is not.
- Handoff notes for implementation: keep examples concrete and route-oriented so
  future runtime changes can evolve underneath the skill without rewriting its
  core purpose.

## 8. Execution Review Outcome

- Outcome: ready for `close-slice`
- Review classification:
  - brief-to-implementation gap: none
  - intent-to-brief gap: none
  - follow-up outside the active slice: none
- Durable artifact note:
  - HSS-05 adds `skills/guide-scope/SKILL.md` as the optional scope-aware entry
    skill, updates repo guidance to explain when to route through it, and adds
    the new skill to the managed install set without changing the underlying
    planning or execution ownership model.
- Validation evidence:
  - `pytest -q skills/guide-planning/tests/test_manage_planning.py skills/guide-execution/tests/test_manage_execution.py`
  - `pytest -q`
