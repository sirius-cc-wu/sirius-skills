# Proposal: Treehouse-Inspired Sirius Worktree Pool Lifecycle

## Problem

`sirius worktree` needs a treehouse-like core pool model that can hand out
reusable per-repository worktrees, reset them to a clean baseline, and return
them safely when the caller is done. The command should borrow treehouse's
operational shape while staying inside the packaged `sirius` CLI and this
repo's workflow ownership boundaries.

## Goals

- Manage one reusable worktree pool per owning repository for `sirius
  worktree`.
- Resolve the default pool root from the owning repo's sibling
  `<repo>.worktrees` directory, with future room for configuration if needed.
- Acquire a clean worktree from the pool or create a new one when capacity
  allows.
- Reset reused worktrees to the selected baseline branch before handing them
  out.
- Record short-lived owner reservations while a session holds a worktree.
- Report pool status with available, in-use, dirty, leased, and current-worktree
  states.
- Auto-heal stale state entries when managed worktrees disappear or reservations
  expire.

## Non-Goals

- Building or depending on a standalone `treehouse` binary.
- Replacing `sirius ship-worktree` or changing its treehouse-managed behavior.
- Durable leases.
- Pruning or destruction workflows.
- Self-update or release management.
- Any daemon or background service.

## Desired Outcome

`sirius worktree` can act as a reusable worktree switchboard: acquire a clean
isolated worktree, do work, return it to the pool, and have the pool still be
usable for the next session.

## Success Criteria

- `sirius worktree get` prints or reports a managed worktree path.
- `sirius worktree status` shows the worktree pool with process-aware status
  labels.
- `sirius worktree return <path>` clears the reservation and resets the tree.
- Stale or vanished managed entries do not accumulate indefinitely in state.
- The same repo can be reused across multiple sessions without repeated cloning.

## Why This Is Still A Proposal

- The pool lifecycle remains a capability candidate, not yet canonical planning.
- The exact feature boundary still needs to stay separate from leasing and
  reclamation.
