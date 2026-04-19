# Implementation Plan: Add source-linked local install helper

**Slice**: `SIM-01-local-helper`  
**Date**: 2026-04-19  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice adds a generic local-install helper that links each managed
`sirius-skills` skill from the repo into a selected skill home and exposes that
helper through new `install-local` and `uninstall-local` `Makefile` targets.
The existing packaged `install` and `uninstall` flow stays unchanged in this
slice.

## 2. Technical Context

- Current system context:
  - `Makefile` currently owns the managed skill list and only supports packaged
    install and uninstall through `npx skills add/remove`.
  - The repo already uses Python helper scripts for install-related sync work
    such as `scripts/sync_shared_skill_runtime.py`.
  - Local source-linked install needs deterministic filesystem behavior that is
    testable against a temporary directory rather than a real global skill home.
- Target modules / files:
  - new `scripts/install_local_skills.py`
  - `Makefile`
  - new targeted tests under `tests/test_install_local_skills.py`
  - slice artifacts under `slices/SIM-01-local-helper-add-source-linked-local-install-helper/`
- Constraints:
  - keep `make install` and `make uninstall` behavior unchanged in this slice
  - do not delete unrelated entries from the skill home
  - fail clearly on ambiguous managed targets instead of overwriting real
    directories silently
  - keep skill-home selection as a helper or `Makefile` override, not a new
    durable repo config file
- Assumptions:
  - `SKILLS_HOME` is a sufficient neutral override for multi-CLI local usage and
    tests
  - the managed skill list can stay defined in `Makefile`, with the helper
    receiving that list explicitly rather than re-parsing `Makefile`
- Out of scope:
  - renaming `install` / `uninstall` into packaged aliases
  - changing shared-runtime sync behavior
  - narrowing parity or maintenance-reporting defaults

## 3. Planning Gates

### Architecture / Constraints

- Decision: add one Python helper with `install` and `uninstall` modes that
  receives the managed skill names, repo root, and skill home, then wire new
  local `Makefile` targets to that helper while leaving the existing packaged
  targets untouched.
- Result: PASS
- Notes: This keeps filesystem behavior centralized and testable without mixing
  local-install logic into shell-heavy `Makefile` recipes.

### Risk / Compliance

- Decision: restrict uninstall to managed symlinks that point back into the repo
  and fail on ambiguous non-symlink collisions for managed names.
- Result: PASS
- Notes: The main operational risk is deleting or overwriting a user-managed
  skill entry; the helper should bias toward explicit failure over destructive
  cleanup.

### Testability

- Decision: cover helper behavior with temporary-directory tests for create,
  refresh, and managed-only cleanup, plus a light `Makefile`-surface assertion
  through the helper invocation contract.
- Result: PASS
- Notes: The helper should expose importable functions so tests can validate
  filesystem behavior directly without invoking a real global install.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S002 | V001, V002 |
| FR-002 | S001, S003 | V001 |
| FR-003 | S001, S004 | V001 |
| FR-004 | S002 | V002 |
| FR-005 | S003, S004 | V001 |

## 5. Execution Plan

### Packet P01: Build the local install helper

- Scope: Implement the helper logic for managed symlink creation and cleanup.
- Target files:
  - `scripts/install_local_skills.py`
- Dependencies: none
- Steps:
  - [ ] S001 Implement deterministic install and uninstall functions that manage
        per-skill symlinks under a selected skill home, create the skill home
        when needed, and refuse ambiguous non-symlink collisions.
- Validation:
  - [ ] V001 Run targeted helper tests against temporary directories.
- Definition of Done: The helper can create, refresh, and clean up managed
  symlinks safely without touching unrelated entries.
- Rollback / Mitigation: If collision handling is too strict for one edge case,
  keep the failure explicit and document the operator action needed rather than
  broadening deletion behavior.

### Packet P02: Expose the helper through local Make targets

- Scope: Add neutral local install entrypoints without changing packaged
  defaults.
- Target files:
  - `Makefile`
- Dependencies: P01
- Steps:
  - [ ] S002 Add `install-local` and `uninstall-local` targets that call the
        helper with `REPO_ROOT`, `MANAGED_SKILLS`, and an overridable
        `SKILLS_HOME`, while leaving `install` and `uninstall` unchanged.
- Validation:
  - [ ] V002 Inspect the `Makefile` contract and run the helper through one
        temporary `SKILLS_HOME` invocation.
- Definition of Done: Maintainers have a repo-supported local install path
  without any change to the packaged compatibility path.
- Rollback / Mitigation: If target naming needs adjustment later, keep the
  helper stable and confine any rename to the `Makefile` surface in `SIM-02`.

### Packet P03: Lock helper behavior with deterministic tests

- Scope: Add focused regression coverage for managed symlink lifecycle behavior.
- Target files:
  - `tests/test_install_local_skills.py`
- Dependencies: P01
- Steps:
  - [ ] S003 Add temporary-directory tests for fresh install and idempotent
        reruns.
  - [ ] S004 Add cleanup and collision tests that prove unrelated entries remain
        untouched and ambiguous managed-name collisions fail clearly.
- Validation:
  - [ ] V003 Run `pytest -q tests/test_install_local_skills.py`
- Definition of Done: The helper behavior is validated without depending on a
  real global skills home.
- Rollback / Mitigation: If a `Makefile`-level test is too brittle, keep the
  filesystem behavior asserted at the helper-function layer and cover only the
  explicit target names manually.

## 6. Supporting Notes

### Detailed Design Diagrams (PlantUML)

- Diagram purpose: show how the new local helper owns symlink lifecycle while
  `Makefile` remains the user-facing entrypoint.
- Diagram type: sequence

```plantuml
@startuml
skinparam backgroundColor white

actor Maintainer
participant Makefile
participant "install_local_skills.py" as Helper
folder "repo skills/" as Repo
folder "skill home" as SkillHome

Maintainer -> Makefile : make install-local
Makefile -> Helper : install(managed skills, repo root, SKILLS_HOME)
Helper -> Repo : verify managed skill paths
Helper -> SkillHome : create/refresh managed symlinks
Helper --> Makefile : success / explicit collision error
Makefile --> Maintainer : local install result
@enduml
```

### Interface Notes

- Interface: `scripts/install_local_skills.py`
- Inputs / outputs:
  - inputs: mode, repo root, skill home, managed skill names
  - outputs: zero exit on success, non-zero with explicit error on collision or
    missing managed skill path
- Error states / compatibility notes:
  - do not remove non-symlink collisions automatically
  - do not remove unrelated skill-home entries during uninstall

### Verification Scenarios

- Happy path: install into an empty temporary skill home and verify per-skill
  symlinks point into the repo.
- Edge case: rerun install with an already-correct managed symlink and verify no
  failure or destructive rewrite occurs.
- Regression checks: uninstall removes only managed symlinks and preserves an
  unrelated entry in the same skill home.

## 7. Delivery Notes

- Sequencing rationale: land helper behavior before command-surface renames so
  later slices can reuse a stable local install implementation.
- Risks to monitor: accidental deletion of user-managed skill-home entries and
  ambiguous behavior when a managed name already exists as a real directory.
- Handoff notes for implementation: keep the helper importable for tests and
  avoid coupling it to `npx skills` or packaged-install behavior.
