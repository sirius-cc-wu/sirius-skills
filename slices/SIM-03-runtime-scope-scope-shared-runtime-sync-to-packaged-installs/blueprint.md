# Implementation Plan: Scope shared-runtime sync to packaged installs

**Slice**: `SIM-03-runtime-scope`  
**Date**: 2026-04-19  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice adds regression coverage for the install-path boundary that now
exists in the `Makefile`: local source-linked install must not run shared
runtime sync, while packaged install and its compatibility alias must continue
to do so.

## 2. Technical Context

- Current system context:
  - `install-local` already runs only `scripts/install_local_skills.py`.
  - `install-packaged` still depends on `sync-shared-runtime` and
    `sync-shared-references`, and `install` is an alias to that path.
  - No existing tests currently protect that boundary.
- Target modules / files:
  - new `tests/test_install_target_modes.py`
  - slice artifacts under
    `slices/SIM-03-runtime-scope-scope-shared-runtime-sync-to-packaged-installs/`
- Constraints:
  - keep behavior unchanged unless the tests reveal a mismatch
  - avoid coupling the tests too tightly to every individual `npx skills add`
    line
  - validate by inspecting `make -n` output rather than running the real
    packaged install flow
- Assumptions:
  - `make` is available in the test environment
  - `python3 -m pytest` remains the reliable test invocation in this repo
- Out of scope:
  - parity behavior
  - migration-guidance docs
  - local helper logic

## 3. Planning Gates

### Architecture / Constraints

- Decision: codify the install-path boundary with target-surface tests instead
  of changing behavior that already appears correct.
- Result: PASS
- Notes: This is the lowest-risk way to keep the boundary durable.

### Risk / Compliance

- Decision: keep tests focused on sync-boundary markers and representative
  packaged behavior rather than every generated command line.
- Result: PASS
- Notes: Overly brittle `Makefile` tests would create noisy maintenance work.

### Testability

- Decision: use `subprocess.run(["make", "-n", target])` in pytest to capture
  rendered commands for each relevant target.
- Result: PASS
- Notes: This directly validates the user-facing command surface this slice
  owns.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S001 | V001 |
| FR-003 | S001 | V001 |
| FR-004 | S001, S002 | V001 |
| FR-005 | S002 | V001 |

## 5. Execution Plan

### Packet P01: Add install-path boundary regression coverage

- Scope: Add one focused pytest module for local-versus-packaged target output.
- Target files:
  - `tests/test_install_target_modes.py`
- Dependencies: none
- Steps:
  - [ ] S001 Add tests that capture `make -n install-local`,
        `make -n install-packaged`, and `make -n install`, then assert the
        presence or absence of sync commands as appropriate.
  - [ ] S002 Keep the assertions focused on the shared-runtime boundary and one
        representative packaged registration command.
- Validation:
  - [ ] V001 Run `python3 -m pytest -q tests/test_install_target_modes.py`
- Definition of Done: The test suite protects the intended local-versus-packaged
  sync boundary without changing runtime behavior.
- Rollback / Mitigation: If target rendering proves too environment-sensitive,
  narrow assertions to the minimal command markers needed for boundary coverage.

## 6. Supporting Notes

### Verification Scenarios

- Happy path: `install-local` output excludes both sync scripts.
- Edge case: `install` alias still includes the packaged sync steps.
- Regression checks: `install-packaged` continues to show one representative
  `npx skills add` command after the sync steps.

## 7. Delivery Notes

- Sequencing rationale: protect the packaged boundary before the next slice
  narrows parity semantics against that same boundary.
- Risks to monitor: brittle assertions tied to command ordering beyond the
  install-path boundary this slice owns.
- Handoff notes for implementation: prefer small helper functions in the test
  file over introducing new repo production code.
