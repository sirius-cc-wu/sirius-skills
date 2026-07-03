# User Stories: Treehouse Pool Lifecycle

- **TPL-01 (M)**: As a user, I want `treehouse get` to place me in a clean
  reusable worktree so I can work in isolation without cloning each time.

- **TPL-02 (M)**: As a maintainer, I want pool entries to be reused and reset
  instead of recreated so the repo keeps warm dependencies and build caches.

- **TPL-03 (M)**: As a user, I want `treehouse status` to show which worktrees
  are available, in use, dirty, leased, or "you're here" so I can understand
  pool health quickly.

- **TPL-04 (S)**: As a maintainer, I want stale state to self-heal so deleted
  worktrees and dead owner reservations do not linger forever.
