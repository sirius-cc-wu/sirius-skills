# User Stories: Treehouse Distribution Lessons For Sirius Worktree

- **TDU-01 (M)**: As a user, I want `sirius worktree` to arrive through the
  normal packaged `sirius` install path so worktree management does not add a
  second CLI distribution channel.

- **TDU-02 (M)**: As a user, I want `sirius worktree` to avoid release checks
  during routine worktree operations so the command stays fast and offline-safe.

- **TDU-03 (M)**: As a maintainer, I want any future packaged `sirius` updater
  to verify release artifacts before replacement so update safety stays outside
  the worktree command itself.

- **TDU-04 (S)**: As a cross-platform user, I want `sirius worktree` behavior to
  stay portable without embedding platform-specific binary replacement logic.
