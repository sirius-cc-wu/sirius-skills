# Implementation Plan: Publish the migration path and operator guidance

**Slice**: `SIM-04-migration-guidance`  
**Date**: 2026-04-19  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This final slice turns the now-implemented split-install behavior into a
coherent migration guide. It documents which commands contributors should use
today, which old commands still work as aliases, and how packaged parity has
moved behind an explicit flag.

## 2. Technical Context

- Current system context:
  - `install-local` / `uninstall-local` are the source-linked local workflow.
  - `install-packaged` / `uninstall-packaged` are the explicit packaged
    workflow.
  - `install` / `uninstall` still alias the packaged path.
  - packaged parity checks in audit/report are now opt-in through
    `--check-packaged-parity`.
- Target modules / files:
  - `README.md`
  - `docs/features/installation-and-configuration/subfeatures/split-install-modes/discover.md`
  - `docs/features/installation-and-configuration/subfeatures/split-install-modes/system-design.md`
- Constraints:
  - keep this slice guidance-only
  - do not commit to a future default flip that has not been implemented
  - keep the guidance concise and current-state oriented
- Assumptions:
  - the README is the best place for the operator-facing command map
  - the subfeature docs should retain the durable migration rationale and
    packaged-parity guidance
- Out of scope:
  - any further `Makefile` changes
  - new CLI flags beyond the already-implemented parity flag

## 3. Planning Gates

### Architecture / Constraints

- Decision: add one concise migration section to the README and align the
  subfeature docs with the implemented command/flag surface.
- Result: PASS
- Notes: This gives operators one practical guide while keeping durable context
  in planning.

### Risk / Compliance

- Decision: describe only the current alias state and parity flag behavior.
- Result: PASS
- Notes: The main risk is implying the future default flip is already decided.

### Testability

- Decision: validate by cross-checking the new guidance against the current
  `Makefile` targets and the report/audit parity flags.
- Result: PASS
- Notes: This is documentation-only work.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S001, S002 | V001 |
| FR-003 | S001, S002 | V001 |
| FR-004 | S002 | V001 |
| FR-005 | S001, S002 | V001 |

## 5. Execution Plan

### Packet P01: Publish the operator migration map

- Scope: Add one concise migration section to the README.
- Target files:
  - `README.md`
- Dependencies: none
- Steps:
  - [ ] S001 Add a command map that explains local install, explicit packaged
        install, compatibility aliases, and packaged parity flags.
- Validation:
  - [ ] V001 Cross-check the README commands and flags against the implemented
        behavior.
- Definition of Done: A contributor can read the README and choose the right
  current command path without guessing.
- Rollback / Mitigation: If the guidance becomes too long, keep the command map
  and trim the surrounding explanation.

### Packet P02: Align durable migration docs

- Scope: Reflect the implemented migration state in the subfeature docs.
- Target files:
  - `docs/features/installation-and-configuration/subfeatures/split-install-modes/discover.md`
  - `docs/features/installation-and-configuration/subfeatures/split-install-modes/system-design.md`
- Dependencies: none
- Steps:
  - [ ] S002 Add or update migration guidance that reflects the current alias
        policy and opt-in packaged-parity behavior.
- Validation:
  - [ ] V001 Cross-check the durable docs against the README and current
        command/flag surface.
- Definition of Done: Durable planning docs match the implemented migration
  state instead of the pre-implementation rollout assumptions.
- Rollback / Mitigation: If the planning docs become repetitive, keep the README
  command map primary and reduce the durable notes to a short current-state
  summary.

## 6. Supporting Notes

### Verification Scenarios

- Happy path: README tells a former `make install` user which command to use for
  local work and which for packaged work.
- Edge case: packaged parity guidance points to `--check-packaged-parity`
  instead of implying default parity output.
- Regression checks: durable subfeature docs no longer lag behind the
  implemented command and flag surface.

## 7. Delivery Notes

- Sequencing rationale: this closes the subfeature by summarizing the migration
  only after all command-surface and parity changes are already in place.
- Risks to monitor: guidance drifting again if a future default flip lands
  without updating the same files.
- Handoff notes for implementation: keep the migration notes concrete and
  operational.
