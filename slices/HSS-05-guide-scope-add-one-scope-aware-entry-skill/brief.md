# Slice Specification: Add one scope-aware entry skill

**Slice**: `HSS-05-guide-scope-add-one-scope-aware-entry-skill`  
**Created**: 2026-04-04  
**Status**: Draft  
**Input**: "HSS-05-guide-scope Add one scope-aware entry skill"

## 1. Work Item Summary

- **Work Item**: Add a `guide-scope` skill that resolves the active scope and routes work into planning, execution, or bootstrap without duplicating their ownership rules.
- **Source Story / Increment / Slice**: HSS-05 / I4 / HSS-05-guide-scope
- **Requested Outcome**: As a maintainer working in a multi-scope repository, I can enter through one scope-aware skill that discovers the current scope, handles ambiguity, and then hands off cleanly to the correct downstream workflow skill.
- **Why this matters**: The scope runtime is now stable for planning and execution, so users need one documented entrypoint instead of remembering where scope matters across multiple workflows.
- **Independent Test**: The new `skills/guide-scope/SKILL.md` plus top-level docs explain when to use `guide-scope`, how it resolves scope, and how it hands off to `guide-planning`, `guide-execution`, or `bootstrap` without changing existing planning/execution behavior.

## 2. Acceptance Scenarios

1. **Given** a multi-scope repository, **When** a user starts from `guide-scope`, **Then** the skill explains how to resolve the active scope, stop on ambiguity, and route to the right downstream workflow skill.
2. **Given** a request to configure a nested scope, **When** `guide-scope` routes to bootstrap, **Then** the handoff describes how to target the selected scope without implying that the repository root is the only valid config location.
3. **Given** a single-scope repository, **When** a user reads the docs, **Then** it is clear that `guide-scope` is optional and existing planning/execution entrypoints remain valid.

## 3. Functional Requirements

- **FR-001**: The repository MUST include a `guide-scope` skill with explicit scope-resolution and handoff instructions.
- **FR-002**: `guide-scope` MUST describe routing to `guide-planning`, `guide-execution`, or `bootstrap` without duplicating downstream lifecycle ownership.
- **FR-003**: Repository docs MUST mention `guide-scope` as the optional scope-aware entrypoint for multi-scope repositories.
- **FR-004**: Installation helpers MUST include `guide-scope` in the managed skill set.
- **FR-005**: Existing planning and execution behavior MUST remain unchanged.

## 4. Key Entities

- **Guide Scope Skill**: The thin scope-aware entry skill.
- **Active Scope**: The nearest explicit scope or repository-root fallback resolved from the working directory.
- **Scope Handoff**: The downstream routing decision into planning, execution, or bootstrap.

## 5. Edge Cases

- A repository may have only one effective scope, so `guide-scope` must stay optional rather than mandatory ceremony.
- Scope ambiguity should stop for explicit user choice instead of pretending one nested scope is the default target.
- The skill must not claim to own planning or execution state transitions that belong to downstream skills.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: HSS-04 and HSS-06 already stabilized scope selection, config inheritance, and scoped execution behavior.
- **A2**: `guide-scope` can remain a thin routing/documentation skill because the shared scope runtime already exists in repository tooling.

### Dependencies

- **D1**: `skills/guide-planning/`
- **D2**: `skills/guide-execution/`
- **D3**: `skills/bootstrap/`
- **D4**: top-level workflow docs and installation helpers

## 7. Success Criteria

- **SC-001**: `guide-scope` clearly documents scope discovery, ambiguity handling, and downstream routing.
- **SC-002**: `README.md`, `SKILLS_METHODOLOGY.md`, and `Makefile` include `guide-scope` consistently.
- **SC-003**: Planning and execution regression tests remain green after the new skill/docs land.

## 8. Open Clarifications

- None.
