---
name: ship-worktree
description: Create or resume a treehouse-managed leased worktree for one feature or subfeature, drive `ship` inside that worktree, and hand the finished branch back as a pull request to the original branch.
---

# Ship Worktree

Use this skill when a feature or subfeature should be implemented in its own
treehouse-managed worktree instead of on the current branch.

## Responsibilities

1. Resolve exactly one feature or subfeature target through the existing `ship`
   backlog surface.
2. Use treehouse to lease a reusable worktree and keep that lease available for
   later resume or finalization calls.
3. Derive the PR branch from the target slug, but let treehouse own the checkout
   path and lifecycle.
4. Run `ship --resume` or `ship --finalize` inside the leased worktree without
   moving backlog ownership out of `ship` and `ship-slice`.
5. Reuse or create a pull request back to the original base branch when the
   target has been implemented and the worktree is ready to open review.

## Tooling

```bash
sirius ship-worktree <target> --json
sirius ship-worktree <target> --resume --json
sirius ship-worktree <target> --finalize --json
sirius ship-worktree <target> --create-pr --json
sirius ship-worktree <target> --resume --create-pr --json
treehouse get --lease --lease-holder <target>
treehouse return <worktree-path> --force
```

## Configuration

Treehouse owns the worktree pool configuration.

```toml
# Repo-level treehouse config
max_trees = 16
root = "$HOME/.treehouse"

[hooks]
post_create = ["./scripts/setup-venv.sh"]
pre_destroy = ["./scripts/teardown.sh"]
```

Use `treehouse init` to write the repo config, and use
`~/.config/treehouse/config.toml` for user-level settings.

## Workflow

1. Run `ship_worktree.py <target> --json` to resolve the target and ensure the
   leased worktree exists.
2. Use `--resume` to continue the feature or subfeature backlog from inside that
   leased worktree through the existing `ship` orchestration.
3. Use `--finalize` when all slices are completed and the target is ready for
   final archive/reconciliation handling.
4. Use `--create-pr` when the worktree branch is ready to open review back to
   the original base branch.

## Guardrails

- Keep feature and subfeature execution ownership in `ship`, `ship-slice`,
  `review-execution`, `close-slice`, `reconcile-execution`, and `commit`.
- Do not create a pull request from a dirty worktree.
- Reuse an existing leased worktree when it already exists instead of creating
  a duplicate checkout.
- Keep PR creation pointed at the original base branch captured when the lease
  started.
- Return the leased worktree through treehouse once the PR handoff is complete.
