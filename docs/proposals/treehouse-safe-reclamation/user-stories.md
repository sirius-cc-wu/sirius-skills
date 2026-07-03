# User Stories: Treehouse Safe Reclamation

- **TSR-01 (M)**: As a maintainer, I want prune to delete only idle, clean,
  merged worktrees so I can reclaim space without risking unfinished work.

- **TSR-02 (L)**: As an operator, I want dry-run previews with clear categories
  so I can see what would be removed before confirming deletion.

- **TSR-03 (L)**: As a maintainer, I want destroy to require explicit opt-in
  flags for unlanded, in-use, or leased worktrees so risky removals are never
  accidental.

- **TSR-04 (M)**: As a repo owner, I want orphaned worktrees to be treated as
  special cases so missing backing repositories do not get deleted casually.
