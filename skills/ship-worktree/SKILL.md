---
name: ship-worktree
description: Create or resume a dedicated git worktree for one feature or subfeature, drive `ship` inside that worktree, and hand the finished branch back as a pull request to the original branch.
---

# Ship Worktree

Use this skill when a feature or subfeature should be implemented in its own git
worktree instead of on the current branch.

## Responsibilities

1. Resolve exactly one feature or subfeature target through the existing `ship`
   backlog surface.
2. Record durable worktree-session metadata under the git common directory so
   the same target can be resumed from any linked worktree.
3. Create or reuse a dedicated worktree branch and path derived from the target
   slug.
4. Run `ship --resume` or `ship --finalize` inside that worktree without moving
   backlog ownership out of `ship` and `ship-slice`.
5. Reuse or create a pull request back to the original base branch when the
   target has been implemented and the worktree is ready to open review.

## Tooling

```bash
sirius ship-worktree <target> --json
sirius ship-worktree <target> --resume --json
sirius ship-worktree <target> --finalize --json
sirius ship-worktree <target> --create-pr --json
sirius ship-worktree <target> --resume --create-pr --json
```

## Configuration

Optional execution config lives under `.skills/execution.json` in
`accelerators.ship_worktree`.

```json
{
  "accelerators": {
    "ship_worktree": {
      "worktree_root": "../.repo-worktrees",
      "branch_prefix": "wt",
      "draft_pr": true
    }
  }
}
```

Defaults:

- `worktree_root`: sibling directory `.<repo-name>-worktrees` next to the repo
- `branch_prefix`: `wt`
- `draft_pr`: `true`

## Workflow

1. Run `ship_worktree.py <target> --json` to resolve the target and ensure the
   dedicated worktree exists.
2. Use `--resume` to continue the feature or subfeature backlog from inside that
   worktree through the existing `ship` orchestration.
3. Use `--finalize` when all slices are completed and the target is ready for
   final archive/reconciliation handling.
4. Use `--create-pr` when the worktree branch is ready to open review back to
   the original base branch.

## Guardrails

- Keep feature and subfeature execution ownership in `ship`, `ship-slice`,
  `review-execution`, `close-slice`, `reconcile-execution`, and `commit`.
- Do not create a pull request from a dirty worktree.
- Reuse an existing target-specific worktree when it already exists instead of
  creating a duplicate checkout.
- Store worktree-session state under the git common directory so linked
  worktrees share the same durable record.
- Keep PR creation pointed at the original base branch captured when the
  worktree session started.
