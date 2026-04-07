# Discover: Hierarchical Scope Support

## Problem

`sirius-skills` currently assumes one planning workspace per repository. The
shared planning and proposal helpers read one repository-root `.skills/`
configuration and default to one `docs/features/` and `docs/proposals/` tree.

That model breaks down in repositories organized as umbrella projects with
several nested subprojects. In those repos, the repository root may be a valid
planning scope, but subprojects also need local planning, proposals,
conventions, and execution settings. Without an explicit hierarchy-aware model,
users must choose between:

- collapsing planning into one shared space that blurs ownership boundaries
- forking workflow skills for each project shape
- relying on manual path conventions that the skills do not understand

The missing capability is not a new planning stage. The missing capability is a
first-class way to resolve and operate within the correct planning scope.

## Goals

- Support a repository root as a valid planning scope.
- Support nested subproject scopes with local `.skills/`, `docs/features/`, and
  `docs/proposals/`.
- Make scope resolution explicit and predictable for both humans and agents.
- Preserve the existing planning and execution workflow once a scope is chosen.
- Keep current single-project behavior as the backward-compatible default.
- Keep core skills generic rather than creating project-specific copies.

## Non-Goals

- Replace the existing planning or execution lifecycle.
- Introduce a global registry that merges features or proposals across
  unrelated scopes.
- Require every repository to define nested scopes.
- Add arbitrary plugin loading from project-local directories.
- Solve implementation routing or build-tool orchestration beyond planning
  scope resolution.

## Primary Actors

- Repository maintainer managing a monorepo or multi-area repository.
- Team lead owning a nested subproject with local planning artifacts.
- Planner working from inside a subdirectory and expecting local docs to be
  selected automatically.
- Agent or reviewer that needs deterministic path resolution before touching
  planning state.

## Constraints

- The generic single-project layout must remain valid.
- Core workflow skills should stay reusable across repositories.
- Scope identifiers and paths should be treated as durable repository objects,
  not hidden chat state.
- The system should avoid accidental cross-scope writes.
- Backward compatibility matters for repositories that only use root-level
  `.skills/`.

## Desired Outcomes

- A repository can have one root scope plus zero or more nested subproject
  scopes.
- Teams can keep features, proposals, and execution settings local to the scope
  that owns them.
- Agents can resolve the correct scope before writing planning artifacts.
- Maintainers do not need to fork the workflow just to support monorepo-style
  structure.

## Candidate Capability Areas

- **Scope model**
  - Use **scope** as the durable term instead of **project**.
  - Treat any directory that owns a local planning workspace as a scope.
  - Allow both repository-root and nested scopes.

- **Scope resolution**
  - Resolve the nearest enclosing scope for the current working directory or a
    user-provided path by default.
  - Allow explicit scope targeting when the user needs to work outside the
    nearest scope.
  - Stop for explicit scope selection when a bare feature or proposal reference
    is ambiguous across scopes.

- **Configuration behavior**
  - Let child scopes inherit parent defaults when local overrides are absent.
  - Let child scopes override planning, execution, or conventions config with
    local `.skills/*.json` files.
  - Keep registry files local to each scope rather than merged globally.

- **Workflow integration**
  - Make planning and proposal promotion flows stay inside the selected scope.
  - Extend existing workflow skills to use scope-relative path resolution.
  - Support initializing workflow config inside a selected scope, not only at
    repository root.

- **Entry routing**
  - Add one scope-aware entrypoint such as `guide-scope` to discover available
    scopes, resolve the active scope, handle ambiguity, and route into
    `guide-planning`, `guide-execution`, or `bootstrap`.

## Confirmed Signals in Repo

- `.skills/planning.json` currently defines one repo-root `planning_dir` and
  `proposal_dir`.
- `skills/guide-planning/scripts/manage_planning.py` assumes one resolved
  planning area and promotes proposals into canonical feature folders within
  that area.
- `skills/propose/scripts/manage_proposals.py` keeps proposal registries local
  to the configured `proposal_dir`.
- Repository guidance in `AGENTS.md` and top-level docs emphasizes
  configuration-first behavior, durable repository artifacts, and clear
  ownership boundaries between planning and execution.

## Assumptions

- Existing workflow stages remain valid once scope resolution happens before
  each planning or execution action.
- The first version can focus on deterministic path resolution and local config
  ownership before deeper tooling integration.
- Scope discovery and inheritance semantics may need explicit metadata or helper
  utilities during design.

## Success Criteria

- The repository root and nested subprojects can each maintain independent
  `docs/features/` and `docs/proposals/` registries.
- Existing workflow skills behave the same from the user's perspective once the
  active scope is resolved.
- Single-project repositories continue to work without adding scope metadata.
- The feature definition is concrete enough for `design` to specify resolution
  rules, configuration precedence, and artifact ownership.

## Risks and Open Questions

- Should scopes be discovered from explicit markers only, or also inferred from
  `.skills/` plus docs layout?
- Should child scopes inherit missing config values automatically, or should
  each scope be fully explicit?
- Should `guide-scope` be mandatory in multi-scope repos, or only used when the
  current directory is ambiguous?
- How should accepted proposal promotion behave when the target feature belongs
  in a parent scope rather than the current child scope?
