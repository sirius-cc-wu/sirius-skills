# User Stories: Hierarchical Scope Support

- **HSS-01 (M)**: As a repository maintainer, I want the repository root to act
  as one planning scope so that umbrella-level work can keep its own features
  and proposals.

- **HSS-02 (M)**: As a subproject owner, I want a nested directory to have its
  own `.skills/`, `docs/features/`, and `docs/proposals/` so that local planning
  stays independent from the rest of the repository.

- **HSS-03 (M)**: As an agent operating from inside a subdirectory, I want the
  nearest enclosing scope to resolve by default so that planning work lands in
  the correct local artifacts without manual path juggling.

- **HSS-04 (M)**: As a planner, I want ambiguous multi-scope situations to stop
  for explicit scope selection so that a bare feature slug cannot accidentally
  update the wrong project area.

- **HSS-05 (L)**: As a maintainer, I want one scope-entry skill such as
  `guide-scope` instead of duplicate per-project workflow skills so that the
  current planning and execution lifecycle remains reusable.

- **HSS-06 (L)**: As a project adopter, I want child scopes to override parent
  `.skills` configuration when needed so that local conventions can differ
  without breaking generic defaults.
