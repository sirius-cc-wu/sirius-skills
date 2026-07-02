# Proposal: Treehouse Pool Lifecycle

## Problem

Treehouse needs a core pool model that can hand out reusable per-repository
worktrees, reset them to a clean detached HEAD, and give them back safely when
the caller exits. That core loop also needs to keep local state in sync so the
same pool can be reused by later sessions without cloning a new repository each
time.

## Goals

- Manage one pool per repository under a configurable treehouse root.
- Resolve the pool root from repo-level or user-level configuration.
- Acquire a clean worktree from the pool or create a new one when capacity
  allows.
- Reset reused worktrees to the current default branch before handing them out.
- Record short-lived owner reservations while a session holds a worktree.
- Report pool status with available, in-use, dirty, leased, and current-worktree
  states.
- Auto-heal stale state entries when managed worktrees disappear or reservations
  expire.
- Keep repo-local housekeeping in place, including the generated `.gitignore`
  entry for the treehouse root.

## Non-Goals

- Durable leases.
- Pruning or destruction workflows.
- Self-update or release management.
- Any daemon or background service.

## Desired Outcome

`treehouse` can act as a reusable worktree switchboard: enter a clean isolated
worktree, do work, return it to the pool, and have the pool still be usable for
the next session.

## Success Criteria

- `treehouse get` opens a subshell in a managed worktree.
- `treehouse status` shows the worktree pool with process-aware status labels.
- Returning a worktree clears the short-lived reservation and resets the tree.
- Stale or vanished managed entries do not accumulate indefinitely in state.
- The same repo can be reused across multiple sessions without repeated cloning.

## Why This Is Still A Proposal

- The pool lifecycle is a capability candidate, not yet canonical planning.
- The exact feature boundary still needs to stay separate from leasing and
  reclamation.
