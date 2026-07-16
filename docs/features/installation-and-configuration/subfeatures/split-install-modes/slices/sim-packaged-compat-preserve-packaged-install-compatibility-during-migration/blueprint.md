# Implementation Plan: Preserve packaged install compatibility during migration

**Slice**: `sim-packaged-compat`  
**Date**: 2026-04-19  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice aligns the repo’s guidance with the new explicit packaged target
names. After `sim-packaged-targets`, the code surface now has
`install-packaged` and `uninstall-packaged`; this slice makes the docs and
source comments reflect that `install` / `uninstall` are compatibility aliases
preserved during the migration.

## 2. Technical Context

- Current system context:
  - `Makefile` exposes local and packaged target names plus compatibility
    aliases.
  - README and AGENTS still describe `install` / `uninstall` as if they were
    the packaged target names rather than aliases.
  - The parent installation docs still reflect the pre-rename wording.
- Target modules / files:
  - `README.md`
  - `AGENTS.md`
  - `docs/features/installation-and-configuration/discover.md`
  - `docs/features/installation-and-configuration/system-design.md`
  - `Makefile`
- Constraints:
  - keep the compatibility aliases in place
  - do not decide the later default flip in this slice
  - keep all wording grounded in current implemented commands
- Assumptions:
  - the explicit packaged names should now be the documented primary packaged
    path
  - a small `Makefile` comment is enough to expose alias intent in source
- Out of scope:
  - changing runtime-sync scope
  - parity/reporting changes
  - flipping `install` to point at local mode

## 3. Planning Gates

### Architecture / Constraints

- Decision: keep the current aliasing behavior, but update docs and `Makefile`
  comments so `install-packaged` is treated as the real packaged interface.
- Result: PASS
- Notes: This keeps behavior stable while making migration intent explicit.

### Risk / Compliance

- Decision: avoid any command-surface behavior change beyond comments and docs.
- Result: PASS
- Notes: The main risk is confusing maintainers by documenting a future state
  instead of the current alias state.

### Testability

- Decision: validate the target surface with `make -n` and review the updated
  docs against the actual `Makefile`.
- Result: PASS
- Notes: This slice is mostly documentation plus comments, so doc-to-command
  consistency is the right verification mode.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S003 | V001 |
| FR-002 | S001, S002, S003 | V001 |
| FR-003 | S002, S003 | V001 |
| FR-004 | S004 | V001 |
| FR-005 | S004 | V001 |

## 5. Execution Plan

### Packet P01: Align packaged-path documentation

- Scope: Update README, AGENTS, and installation feature docs to describe the
  explicit packaged path and the compatibility aliases.
- Target files:
  - `README.md`
  - `AGENTS.md`
  - `docs/features/installation-and-configuration/discover.md`
  - `docs/features/installation-and-configuration/system-design.md`
- Dependencies: none
- Steps:
  - [ ] S001 Present `install-packaged` / `uninstall-packaged` as the explicit
        packaged path in the README.
  - [ ] S002 Align AGENTS and the parent installation docs with the same
        compatibility wording.
  - [ ] S003 Remove pre-rename wording that still treats `install` /
        `uninstall` as the only packaged names.
- Validation:
  - [ ] V001 Cross-check the updated docs against the `Makefile` command
        surface and run `make -n`.
- Definition of Done: The repo docs consistently describe the explicit packaged
  path and the remaining aliases.
- Rollback / Mitigation: If the docs become too verbose, reduce them to
  current-state facts and move longer migration language to the later guidance
  slice.

### Packet P02: Mark compatibility aliases in source

- Scope: Make the alias intent visible in `Makefile`.
- Target files:
  - `Makefile`
- Dependencies: none
- Steps:
  - [ ] S004 Add a small comment or structure cue showing that `install` and
        `uninstall` are preserved as compatibility aliases for now.
- Validation:
  - [ ] V001 Run `make -n install-packaged uninstall-packaged install uninstall`
        and confirm behavior is unchanged.
- Definition of Done: Maintainers can see both the alias intent and unchanged
  packaged behavior directly in source.
- Rollback / Mitigation: If comments add noise, keep the alias structure clear
  without extra prose.

## 6. Supporting Notes

### Verification Scenarios

- Happy path: README clearly points packaged users to `install-packaged`.
- Edge case: `install` and `uninstall` remain documented as aliases rather than
  disappearing from the migration story.
- Regression checks: `make -n` still renders the packaged flow for both the
  explicit targets and the compatibility aliases.

## 7. Delivery Notes

- Sequencing rationale: make the explicit packaged names visible before the
  later runtime-scope and parity changes rely on that boundary.
- Risks to monitor: documentation drifting again if later slices change alias
  semantics without updating the same files.
- Handoff notes for implementation: keep the behavioral surface unchanged in
  this slice.
