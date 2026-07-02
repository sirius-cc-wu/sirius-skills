# Proposal: Treehouse Safe Reclamation

## Problem

Treehouse needs a way to reclaim disk space without making destructive behavior
the default. That means stale worktrees should be pruned only when they are
clean, idle, and already merged, while more dangerous removals require explicit
opt-in flags and clear previews.

## Goals

- Prune only managed worktrees that are idle, clean, and merged into the
  default branch.
- Support dry-run previews as the default behavior for reclamation.
- Sweep all managed pools when requested, not just the current repository.
- Recognize true orphans where the backing repository is missing.
- Classify dirty, unmerged, in-use, leased, and unverified worktrees
  independently so the caller can opt into the exact risk it wants.
- Destroy worktrees only when explicitly named or when a pool-wide clear is
  requested with the correct flags.
- Terminate lingering worktree processes cleanly before removing in-use trees.
- Run pre-destroy hooks before removal.

## Non-Goals

- Global destructive deletion without an explicit pool target.
- A single `--force` flag that overrides every protection at once.
- Removing leased worktrees in bulk.
- Silent removal of unverified or unmerged worktrees.

## Desired Outcome

Maintenance commands can reclaim disk space and clean up abandoned worktrees
while still making every risky override obvious to the operator.

## Success Criteria

- `treehouse prune` is a dry run unless `--yes` is passed.
- `treehouse prune --all` can sweep every managed pool from the user-level root.
- `treehouse destroy` previews risk, labels what is being removed, and requires
  explicit opt-in for dangerous classes.
- Orphaned or unverified worktrees are never removed accidentally.
- Bulk skips are non-fatal, while a single-target skip is surfaced loudly.

## Why This Is Still A Proposal

- Reclamation is safety-sensitive and deserves its own capability boundary.
- The exact destroy/prune safety model is broader than the pool lifecycle or
  leasing stories.
