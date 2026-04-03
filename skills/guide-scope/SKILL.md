---
name: guide-scope
description: Resolves the active repository scope and routes to planning, execution, or bootstrap without duplicating downstream ownership.
---

# Guide Scope

Use this skill as the optional multi-scope entrypoint when the repository may
contain nested scopes and the user should not have to remember whether the next
handoff belongs to planning, execution, or bootstrap.

## Responsibilities

1. Resolve the active scope from the current working directory.
2. Discover candidate scopes when the repository contains nested `.skills/`
   workspaces.
3. Stop for explicit scope choice when the target scope is ambiguous.
4. Route the request to `guide-planning`, `guide-execution`, or `bootstrap`.
5. Keep scope resolution durable in repository tooling instead of inventing a
   second scope model in chat.

## Entry Decision Guide

Use `guide-scope` when:

- the repository may have multiple explicit scopes
- the user is working from a nested directory and the target scope is not
  obvious
- the user wants to configure a nested scope with `bootstrap`
- the user wants a single entry skill that decides whether the next step is
  planning-layer or execution-layer work

Route from `guide-scope` using these rules:

- If the next work is feature planning, proposal management, promotion,
  discovery, design, breakdown, or slice bootstrap, route to `guide-planning`.
- If an execution slice already exists or execution-layer readiness is the next
  question, route to `guide-execution`.
- If the request is to initialize or update `.skills/` configuration for the
  selected scope, route to `bootstrap`.

If the repository effectively has one scope and the user already knows they want
planning or execution, `guide-scope` is optional and direct entry through
`guide-planning` or `guide-execution` remains valid.

## Workflow Boundary

`guide-scope` owns scope discovery and handoff only.

- Resolve the active scope using the same nearest-scope and repository-root
  fallback rules already implemented by repository tooling.
- Surface candidate scopes or ask for an explicit scope path when ambiguity
  matters.
- Do not mutate planning metadata, slice metadata, or config files directly
  unless the downstream routed skill owns that work.
- Do not replace `guide-planning`, `guide-execution`, or `bootstrap`; route into
  them after scope selection is settled.

Typical handoff:

```text
guide-scope -> guide-planning
guide-scope -> guide-execution
guide-scope -> bootstrap
```

## Preflight

1. Resolve the active scope from the nearest `.skills/planning.json`; if none
   exists in ancestor directories, fall back to the repository root when inside
   a Git worktree.
2. If the user already supplied an explicit scope path, validate that it is
   inside the repository.
3. When slug-only lookups or nested-scope context make the target ambiguous,
   stop and ask the user to choose the scope explicitly.
4. Keep scope labels relative to the repository root so downstream handoffs stay
   readable.
5. Route into the downstream skill without changing its lifecycle ownership.

## Tooling

Use the existing repository helpers rather than inventing a new scope runtime:

- planning and proposal routing: `skills/guide-planning/scripts/manage_planning.py`
  and `skills/propose/scripts/manage_proposals.py`
  - use `--scope <path>` when an explicit planning or proposal scope is needed
  - use `--target-scope <path>` for explicit cross-scope promotion targets
- execution routing: `skills/guide-execution/scripts/manage_execution.py`
  - execution commands already follow the nearest execution scope and keep slice
    registries local to that scope
- slice bootstrap: `skills/slice/scripts/bootstrap_slice.py`
  - bootstrap reuses scoped execution config and inherited defaults from the
    active scope chain
- scope configuration: `skills/bootstrap/scripts/bootstrap.py`
  - use `--repo-root <scope-root>` to initialize or update the selected scope's
    `.skills/` files

## Examples

### Example 1: Multi-scope planning handoff

Request: "Start planning from inside `apps/payments`."

Action:

1. Resolve the active scope for `apps/payments`.
2. If the target scope is unambiguous, route to `guide-planning`.
3. If the user needs a different planning scope, ask for an explicit scope path
   and then route with that scope.

### Example 2: Scoped execution handoff

Request: "Continue the active slice from this nested service directory."

Action:

1. Resolve the nearest execution scope from the current path.
2. Confirm the handoff belongs in execution rather than planning.
3. Route to `guide-execution`, letting execution helpers use the resolved local
   slice registry automatically.

### Example 3: Configure a nested scope

Request: "Set up `.skills` for the `apps/payments` scope."

Action:

1. Resolve or confirm the target scope path.
2. Route to `bootstrap`.
3. Use `bootstrap.py --repo-root <scope-root>` so config is written inside the
   selected scope rather than assuming the repository root.
