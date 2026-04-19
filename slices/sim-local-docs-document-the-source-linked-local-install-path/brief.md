# Slice Specification: Document the source-linked local install path

**Slice**: `sim-local-docs`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `split-install-modes / sim-local-docs`

## 1. Work Item Summary

- **Work Item**: Document the new local source-linked install path and clarify that the existing `make install` / `make uninstall` path remains the packaged compatibility path for now.
- **Source Story / Increment / Slice**: `SIM-01` / `I1` / `sim-local-docs`
- **Requested Outcome**: As a contributor, I want the repo docs to tell me when to use `install-local` versus `install` so I do not accidentally pick the wrong workflow.
- **Why this matters**: The first helper slice introduced a second install mode. Without aligned docs, contributors will still assume the packaged path is the only or preferred local workflow.
- **Independent Test**: README, AGENTS, and installation feature docs all describe the same two-mode state: `install-local` for source-linked local use and `install` / `uninstall` as the current packaged compatibility path.

## 2. Acceptance Scenarios

1. **Given** a contributor reading the repo README, **When** they look for install instructions, **Then** they can see the new local source-linked path and the current packaged compatibility path clearly separated.
2. **Given** an agent reading repo guidance in `AGENTS.md`, **When** it plans install-related work, **Then** it sees that local source-linked install exists and that packaged install remains available.
3. **Given** a planner reading the installation feature docs, **When** they compare current behavior with the new subfeature direction, **Then** the docs reflect the interim state introduced by `sim-local-helper`.

## 3. Functional Requirements

- **FR-001**: The README MUST document `make install-local` and `make uninstall-local` as the preferred local source-linked workflow.
- **FR-002**: The README MUST state that `make install` and `make uninstall` still represent the packaged compatibility path in the current rollout.
- **FR-003**: `AGENTS.md` MUST reflect the same local-versus-packaged distinction so agent guidance matches user-facing docs.
- **FR-004**: The installation planning docs MUST acknowledge the interim two-mode state introduced by this slice.
- **FR-005**: The slice MUST keep documentation aligned with the current implementation only and avoid promising later `install-packaged` naming before that slice lands.

## 4. Key Entities

- **Local source-linked install**: The new `install-local` / `uninstall-local` path that symlinks repo skills into a selected skill home.
- **Packaged compatibility install**: The existing `install` / `uninstall` path that still runs the packaged `npx skills add/remove` flow.
- **Skill home override**: The `SKILLS_HOME` override used for local multi-CLI installs and tests.

## 5. Edge Cases

- A reader only sees one doc page; that page should still explain the current install split correctly.
- Contributors may assume `install-packaged` already exists; docs must not promise it before the Makefile actually exposes it.
- The local skill home is not the default `~/.agents/skills/`; docs should mention the `SKILLS_HOME` override without turning it into a new durable config surface.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `sim-local-helper` has already landed and introduced working `install-local` / `uninstall-local` targets.
- **A2**: The later command-surface rename to `install-packaged` is still future work and should be described as such, not as current behavior.

### Dependencies

- **D1**: README and AGENTS remain the primary operator-facing install documentation.
- **D2**: The parent `installation-and-configuration` feature docs remain the canonical durable design context for current repo install behavior.

## 7. Success Criteria

- **SC-001**: Contributors can find and use the local source-linked install path from README alone.
- **SC-002**: Agents and maintainers see the same install split in `AGENTS.md` and the installation feature docs.
- **SC-003**: No documentation claims `install-packaged` exists before the later implementation slice adds it.

## 8. Open Clarifications

- None.
