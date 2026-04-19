# Implementation Plan: Document the source-linked local install path

**Slice**: `sim-local-docs`  
**Date**: 2026-04-19  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice updates the repo’s install guidance to reflect the state after
`sim-local-helper`: a new `install-local` / `uninstall-local` source-linked
workflow now exists, while `make install` / `make uninstall` still remain the
current packaged compatibility path.

## 2. Technical Context

- Current system context:
  - `Makefile` now exposes `install-local` and `uninstall-local`, backed by the
    new `scripts/install_local_skills.py` helper.
  - `install` and `uninstall` still run the original packaged `npx skills`
    registration flow.
  - README, AGENTS, and installation planning docs still describe only the old
    packaged install path.
- Target modules / files:
  - `README.md`
  - `AGENTS.md`
  - `docs/features/installation-and-configuration/discover.md`
  - `docs/features/installation-and-configuration/system-design.md`
- Constraints:
  - document only the behavior that exists after `sim-local-helper`
  - do not refer to `install-packaged` / `uninstall-packaged` as current
    commands yet
  - keep the local workflow generic for multiple CLIs
- Assumptions:
  - the local workflow should be presented as the preferred contributor path
  - the packaged path should remain documented as the current compatibility path
    until the later rename slice lands
- Out of scope:
  - command-surface renames to `install-packaged`
  - parity/reporting behavior changes
  - shared-runtime sync changes

## 3. Planning Gates

### Architecture / Constraints

- Decision: update only the operator-facing install docs that currently describe
  the old one-mode workflow, and describe the current state as two explicit
  modes without pre-documenting future target names.
- Result: PASS
- Notes: This keeps the docs truthful to current behavior while still guiding
  contributors toward the new local workflow.

### Risk / Compliance

- Decision: describe the packaged path as a compatibility path rather than
  deprecating it early in README or AGENTS.
- Result: PASS
- Notes: The main risk is promising a future target rename or removal too early.

### Testability

- Decision: validate by cross-checking the updated docs against the current
  helper behavior and `Makefile` surface already implemented in `sim-local-helper`.
- Result: PASS
- Notes: No code-path tests are needed in this slice; the validation is doc-to-
  implementation consistency.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001 | V001 |
| FR-002 | S001 | V001 |
| FR-003 | S002 | V001 |
| FR-004 | S003 | V001 |
| FR-005 | S001, S002, S003 | V001 |

## 5. Execution Plan

### Packet P01: Update top-level install guidance

- Scope: Refresh README install instructions to show both current install modes.
- Target files:
  - `README.md`
- Dependencies: none
- Steps:
  - [ ] S001 Add a source-linked local install section that documents
        `install-local`, `uninstall-local`, `SKILLS_HOME`, and the current
        packaged compatibility path.
- Validation:
  - [ ] V001 Review the README text against the actual `Makefile` commands.
- Definition of Done: README accurately explains how to choose between current
  local and packaged install paths.
- Rollback / Mitigation: If wording becomes too transitional, simplify it to
  current-state facts only.

### Packet P02: Align agent-facing guidance

- Scope: Update AGENTS install guidance to match the repo README.
- Target files:
  - `AGENTS.md`
- Dependencies: P01
- Steps:
  - [ ] S002 Describe the same local-versus-packaged distinction in the
        installation guidance for agents.
- Validation:
  - [ ] V001 Review AGENTS wording against the README and current `Makefile`.
- Definition of Done: Agent guidance no longer assumes the packaged path is the
  only install mode.
- Rollback / Mitigation: If too much detail is distracting in AGENTS, keep the
  rule short and point back to README.

### Packet P03: Update durable installation feature docs

- Scope: Bring the parent installation feature docs up to date with the current
  interim install split.
- Target files:
  - `docs/features/installation-and-configuration/discover.md`
  - `docs/features/installation-and-configuration/system-design.md`
- Dependencies: P01
- Steps:
  - [ ] S003 Reflect the current two-mode install surface in the feature’s
        durable discovery and design docs without pre-claiming later packaged
        target renames.
- Validation:
  - [ ] V001 Cross-check the feature docs against the current README and
        `Makefile`.
- Definition of Done: Durable install docs reflect the same interim state as
  the operator-facing docs.
- Rollback / Mitigation: If the parent feature docs get too noisy, keep the
  details brief and point to the subfeature packet for rollout specifics.

## 6. Supporting Notes

### Verification Scenarios

- Happy path: a contributor reads README and can identify `make install-local`
  as the preferred local workflow.
- Edge case: a maintainer still needs the packaged flow and can see that
  `make install` / `make uninstall` remain available today.
- Regression checks: AGENTS and installation feature docs do not mention
  `install-packaged` before that target exists.

## 7. Delivery Notes

- Sequencing rationale: publish the docs immediately after the local helper so
  contributors see the new path before later target renames begin.
- Risks to monitor: docs drifting ahead of actual target names in the next slice.
- Handoff notes for implementation: keep all wording grounded in currently
  shipped commands and avoid speculative migration instructions in this slice.
