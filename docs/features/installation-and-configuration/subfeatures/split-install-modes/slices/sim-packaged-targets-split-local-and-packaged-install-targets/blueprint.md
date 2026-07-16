# Implementation Plan: Split local and packaged install targets

**Slice**: `sim-packaged-targets`  
**Date**: 2026-04-19  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice adds explicit packaged target names to the `Makefile` while keeping
the current compatibility behavior intact. The goal is to make the command
surface clearly show two install modes: `install-local` for source-linked local
use and `install-packaged` for the packaged flow.

## 2. Technical Context

- Current system context:
  - `Makefile` already exposes `install-local` and `uninstall-local`.
  - `install` and `uninstall` still contain the full packaged workflow.
  - The local docs slice already tells users that explicit packaged naming is
    a later step, so this slice can now make that true.
- Target modules / files:
  - `Makefile`
  - slice artifacts under
    `slices/sim-packaged-targets-split-local-and-packaged-install-targets/`
- Constraints:
  - preserve the current packaged commands
  - keep `install` and `uninstall` available in this slice
  - avoid widening scope into runtime-sync or parity behavior changes
- Assumptions:
  - target aliases are sufficient for this slice; no doc updates are required
    until the later compatibility slice decides how `install` should be framed
  - `make -n` is an acceptable target-selection verification path here
- Out of scope:
  - changing what `install` points to
  - removing compatibility aliases
  - changing shared-runtime sync scope

## 3. Planning Gates

### Architecture / Constraints

- Decision: factor the existing packaged flow behind explicit
  `install-packaged` / `uninstall-packaged` targets, then keep `install` /
  `uninstall` as aliases to those packaged targets in this slice.
- Result: PASS
- Notes: This makes the mode boundary explicit without yet changing operator
  defaults.

### Risk / Compliance

- Decision: preserve the existing packaged command body exactly and minimize the
  change to target naming and aliasing.
- Result: PASS
- Notes: The main risk is accidentally changing packaged behavior while trying
  to split naming.

### Testability

- Decision: validate the target surface with `make -n install-packaged`,
  `make -n uninstall-packaged`, and one check that the compatibility aliases
  still render successfully.
- Result: PASS
- Notes: Since the slice is `Makefile`-only, target rendering is the most
  stable verification path.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S001 | V001 |
| FR-003 | S001 | V001 |
| FR-004 | S002 | V001 |
| FR-005 | S003 | V001 |

## 5. Execution Plan

### Packet P01: Add explicit packaged target names

- Scope: Extract the existing packaged flow behind explicit target names.
- Target files:
  - `Makefile`
- Dependencies: none
- Steps:
  - [ ] S001 Add `install-packaged` and `uninstall-packaged` targets that own
        the current packaged sync and `npx skills` commands.
  - [ ] S002 Keep `install` and `uninstall` available as compatibility aliases
        to the packaged targets.
  - [ ] S003 Verify the resulting target surface with `make -n`.
- Validation:
  - [ ] V001 Run `make -n install-packaged uninstall-packaged install uninstall`
        and confirm the rendered packaged commands are still present.
- Definition of Done: The `Makefile` clearly shows both local and packaged
  install modes while preserving current compatibility aliases.
- Rollback / Mitigation: If aliasing causes confusing duplication, keep the
  explicit packaged targets and revert only the alias form, not the target names.

## 6. Supporting Notes

### Verification Scenarios

- Happy path: `make -n install-packaged` renders the packaged sync plus
  `npx skills add` commands.
- Edge case: `make -n uninstall-packaged` still renders the managed packaged
  removal path.
- Regression checks: `make -n install uninstall` still render successfully as
  compatibility aliases.

## 7. Delivery Notes

- Sequencing rationale: make packaged target names explicit before tackling the
  more opinionated compatibility and default-path decisions in the next slice.
- Risks to monitor: accidental behavior change in the packaged flow while
  refactoring target names.
- Handoff notes for implementation: keep the packaged command body identical and
  limit the change to target structure.
