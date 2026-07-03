# Proposal: Treehouse Distribution Lessons For Sirius Worktree

## Problem

The restored treehouse notes include distribution and self-update concerns for
a standalone cross-platform CLI. Those concerns do not directly fit
`sirius worktree`, which is packaged under the existing `sirius` command, but
they still document useful boundaries for what should not be pulled into the
worktree command.

## Goals

- Record that standalone treehouse installation and self-update behavior is
  reference material, not a required `sirius worktree` capability.
- Keep `sirius worktree` distribution tied to the existing packaged `sirius`
  install/update path.
- Avoid adding network update checks to routine worktree commands.
- Preserve any relevant release safety lessons, such as explicit user action and
  checksum verification, for the broader packaged CLI if needed later.

## Non-Goals

- Adding `sirius worktree update`.
- Downloading or replacing binaries from `sirius worktree`.
- Background auto-update or release checks during worktree operations.
- Replacing the repository's existing packaged install workflow.

## Desired Outcome

The `sirius worktree` proposal set stays focused on worktree pool behavior, and
standalone treehouse distribution concerns remain explicitly out of scope.

## Success Criteria

- No `sirius worktree` command performs release discovery or binary updates.
- Documentation points users to the existing `sirius` packaged install/update
  path.
- Any future packaged CLI update mechanism remains explicit and opt-in.
- Treehouse distribution details are treated as reference input only.

## Why This Is Still A Proposal

- Distribution and updating are a separate capability from worktree management
  and may not belong in this proposal family at all.
- Keeping this packet as a boundary note avoids accidentally importing
  standalone CLI concerns into `sirius worktree`.
