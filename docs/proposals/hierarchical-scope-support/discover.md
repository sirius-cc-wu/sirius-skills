# Discover: Hierarchical Scope Support

## Problem

`sirius-skills` currently assumes one planning workspace per repository. The
shared planning and proposal helpers read one repository-root `.skills/`
configuration and default to one `docs/features/` and `docs/proposals/` tree.

That model breaks down in repositories that are organized as a large umbrella
project with several nested subprojects. In those repos, the repository root is
often a valid planning scope, but subprojects also need their own local
planning, proposals, conventions, and execution settings. Without an explicit
hierarchy-aware model, users have to choose between:

- collapsing everything into one shared planning space, which blurs ownership
  boundaries
- forking workflow skills for each project shape
- or relying on manual path conventions that the skills do not understand

The missing capability is not a new planning stage. The missing capability is a
first-class way to resolve and operate within the right planning scope.

## Goals

- Support a repository root as a valid planning scope.
- Support nested subproject scopes with their own `.skills/`, `docs/features/`,
  and `docs/proposals/`.
- Make scope resolution explicit and predictable for both humans and agents.
- Preserve the existing planning and execution workflow once a scope is chosen.
- Keep the current single-project behavior working as the backward-compatible
  fallback.
- Keep core skills generic rather than creating project-specific copies of the
  workflow.

## Non-Goals

- Replace the existing planning or execution lifecycle with a different model.
- Introduce a shared global registry that merges features or proposals across
  unrelated scopes.
- Require every repository to define nested scopes.
- Add automatic plugin loading from arbitrary project-local directories.
- Solve implementation-routing or build-tool orchestration outside the planning
  scope problem.

## Proposed Concept: Hierarchical Scopes

Use **scope** as the durable term instead of **project**.

A scope is any directory that owns a local planning workspace. The repository
root may be a scope, and nested directories may also be scopes.

Examples:

- repository scope:
  - `.skills/`
  - `docs/features/`
  - `docs/proposals/`
- nested scope:
  - `apps/payments/.skills/`
  - `apps/payments/docs/features/`
  - `apps/payments/docs/proposals/`

This lets the whole repository act as a large project while also allowing
subprojects to plan independently.

## Resolution Model

Default rule:

- resolve the **nearest enclosing scope** for the current working directory or
  the user-provided path

Override rule:

- allow the user to target a different scope explicitly when needed

Inheritance rule:

- a child scope may inherit parent defaults when it does not define local
  overrides
- a child scope may override parent planning, execution, or conventions config
  by defining its own `.skills/*.json`

Ambiguity rule:

- do not silently search the entire repository for a bare feature slug when
  multiple scopes are possible
- if the active scope is unclear, require a scope selection step before
  planning/proposal work continues

## Expected Capability Changes

- Path resolution helpers should become **scope-relative** instead of assuming
  one repository-root configuration.
- Registry files should remain **local to each scope** rather than being merged
  across the repository.
- Existing planning skills should continue to operate the same way after scope
  resolution.
- `bootstrap` should be able to initialize config inside a selected scope, not
  only at repository root.
- Proposal and planning promotion flows should stay inside the selected scope.

## Candidate Skill Changes

- **New entry skill: `guide-scope`**
  - discover available scopes
  - resolve the active scope
  - disambiguate when multiple scopes match
  - hand off to `guide-planning`, `guide-execution`, or `bootstrap`

- **Extend existing skills instead of cloning them**
  - `bootstrap` should support writing `.skills/` inside a chosen scope
  - `guide-planning`, `propose`, `discover`, `design`, `breakdown`,
    `review-planning`, `slice`, and `guide-execution` should use resolved scope
    paths

- **Do not add duplicate per-project workflow skills**
  - the workflow itself is still the same
  - only the workspace-resolution layer changes

## Primary Actors

- Repository maintainer managing a monorepo or multi-area repository.
- Team lead owning one nested subproject with local planning artifacts.
- Planner working from inside a subdirectory and expecting local docs to be
  used automatically.
- Agent or reviewer that needs deterministic path resolution before touching
  planning state.

## Constraints

- The generic single-project layout must remain valid.
- Core workflow skills should stay reusable across repositories.
- Scope IDs and paths should be treated as durable repository objects, not
  hidden chat state.
- The system should avoid accidental cross-scope writes.
- Backward compatibility matters for repositories that only use root-level
  `.skills/`.

## Desired Outcomes

- A repository can have one root scope plus zero or more nested subproject
  scopes.
- Teams can keep features, proposals, and execution settings local to the scope
  that owns them.
- Agents can resolve the right scope before writing planning artifacts.
- Maintainers do not need to fork the workflow just to support monorepo-style
  structure.

## Success Criteria

- The repository root and nested subprojects can each maintain independent
  `docs/features/` and `docs/proposals/` registries.
- Existing workflow skills work unchanged from the user's perspective once the
  active scope is resolved.
- Single-project repositories continue to work without adding any scope
  metadata.
- The design is explicit enough to support canonical planning later without
  introducing cross-scope ambiguity.

## Risks and Open Questions

- How should scopes be discovered: explicit markers only, or implicit detection
  from `.skills/` plus docs layout?
- Should child scopes inherit missing config values from parents automatically,
  or should each scope be fully explicit?
- Should `guide-scope` be mandatory in multi-scope repos, or only used when the
  current directory is ambiguous?
- How should accepted proposal promotion behave when the target feature should
  live in a parent scope rather than the current child scope?

## Why This Is Still A Proposal

- The repository needs an explicit decision on the scope model before changing
  shared path-resolution helpers.
- The right inheritance and discovery semantics are still open design
  questions.
- The workflow impact spans multiple existing skills, so the boundary decisions
  should be accepted before canonical feature planning begins.
