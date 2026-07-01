# User Stories: Treehouse Durable Leasing

- **TDL-01 (L)**: As a script author, I want `treehouse get --lease` to return
  only a path so I can capture the worktree in command substitution.

- **TDL-02 (M)**: As an agent runner, I want a lease to survive with no live
  process inside the worktree so the workspace remains mine until I return it.

- **TDL-03 (M)**: As a maintainer, I want leased worktrees to stay out of
  default acquisition and pruning so they cannot be handed out accidentally.

- **TDL-04 (S)**: As a reviewer, I want the lease holder to be visible in
  status output so ownership is easy to diagnose.
