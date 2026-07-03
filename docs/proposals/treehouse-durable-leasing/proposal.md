# Proposal: Treehouse-Inspired Sirius Worktree Durable Leasing

## Problem

Some callers need a worktree to persist as a long-lived home without keeping a
shell session or foreground process attached to it. `sirius worktree` needs a
treehouse-like durable reservation model that is independent of live process
detection and survives until it is explicitly released.

## Goals

- Support a non-interactive acquire path that prints only the worktree path.
- Persist leases in `sirius worktree` pool state instead of deriving them from
  processes.
- Allow an optional human-readable lease holder label for diagnostics.
- Keep leased worktrees out of later `get` allocations and default prune runs.
- Preserve leased worktrees until `sirius worktree return <path>` clears the
  lease.
- Surface lease state clearly in `sirius worktree status`.

## Non-Goals

- Replacing the normal `get` subshell workflow.
- Inferring leases from running processes.
- Bulk deletion of leased worktrees.
- Turning a lease into a hidden background daemon.
- Implementing treehouse as a separate runtime dependency.

## Desired Outcome

Scripts and agents can reserve a reusable worktree as a stable home, capture its
path once, and rely on that lease until they intentionally release it.

## Success Criteria

- `sirius worktree get` emits only the absolute worktree path on stdout by
  default, with machine-readable output available through `--json`.
- A leased worktree is never handed out by a later `get`.
- A leased worktree is skipped by default prune behavior.
- `sirius worktree return <path>` clears the lease and returns the worktree to
  the pool.
- `sirius worktree status` shows the recorded lease holder when one exists.

## Why This Is Still A Proposal

- Leases change the reservation model and need to stay isolated from the core
  pool lifecycle proposal.
- The bulk-destroy and prune rules around leased homes are part of a larger
  safety story.
