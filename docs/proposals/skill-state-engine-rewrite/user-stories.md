# User Stories: Skill State Engine Rewrite

- **SER-01 (L)**: As a skill maintainer, I want one canonical workflow artifact
  model so status semantics and cross-artifact relationships are not duplicated
  across maintenance skills.

- **SER-02 (L)**: As a maintainer, I want transactional state-change operations
  so updating subfeature or execution state does not leave partially synchronized
  metadata behind.

- **SER-03 (M)**: As a skill author, I want audit, trace, repair, and report
  skills to call one shared engine so semantic fixes land once instead of being
  copied into each script.

- **SER-04 (M)**: As a repo owner, I want the migration to happen incrementally
  so the existing skill surface remains usable while the internal model is
  consolidated.

- **SER-05 (M)**: As a reviewer, I want regression tests for known drift cases
  to anchor the rewrite so the new engine proves it fixes real workflow failures.
