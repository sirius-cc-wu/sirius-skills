# User Stories: Treehouse-Inspired Sirius Worktree Config And Hooks

- **TCH-01 (M)**: As a project maintainer, I want any `sirius worktree` config
  file to have safe defaults so I can adopt treehouse-like pool behavior without
  manual bootstrapping.

- **TCH-02 (M)**: As a team lead, I want user-level hooks for create and destroy
  lifecycles so setup and teardown actions can be automated.

- **TCH-03 (S)**: As a repository user, I want the shared worktree root to
  resolve predictably from config or derived defaults so layouts stay portable.

- **TCH-04 (S)**: As a maintainer, I want `sirius worktree` to keep `.gitignore`
  synchronized with its managed root if the root is repo-local so generated
  worktree paths stay out of the repo.
