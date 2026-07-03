# Proposal: Treehouse Durable Leasing

## Problem

Some callers need a worktree to persist as a long-lived home without keeping a
shell session or foreground process attached to it. Treehouse needs a durable
reservation model that is independent of live process detection and survives
until it is explicitly released.

## Goals

- Support a non-interactive acquire path that prints only the worktree path.
- Persist leases in treehouse state instead of deriving them from processes.
- Allow an optional human-readable lease holder label for diagnostics.
- Keep leased worktrees out of later `get` allocations and default prune runs.
- Preserve leased worktrees until `treehouse return <path>` clears the lease.
- Surface lease state clearly in `treehouse status`.

## Non-Goals

- Replacing the normal `get` subshell workflow.
- Inferring leases from running processes.
- Bulk deletion of leased worktrees.
- Turning a lease into a hidden background daemon.

## Desired Outcome

Scripts and agents can reserve a reusable worktree as a stable home, capture its
path once, and rely on that lease until they intentionally release it.

## Success Criteria

- `treehouse get --lease` emits only the absolute worktree path on stdout.
- A leased worktree is never handed out by a later `get`.
- A leased worktree is skipped by default prune behavior.
- `treehouse return <path>` clears the lease and returns the worktree to the
  pool.
- `treehouse status` shows the recorded lease holder when one exists.

## Why This Is Still A Proposal

- Leases change the reservation model and need to stay isolated from the core
  pool lifecycle proposal.
- The bulk-destroy and prune rules around leased homes are part of a larger
  safety story.
