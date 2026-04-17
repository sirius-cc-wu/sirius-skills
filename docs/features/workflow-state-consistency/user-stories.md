# User Stories: Workflow State Consistency

- **WSC-01 (M)**: As a maintainer, I want state-changing skills to run narrow
  consistency checks after important transitions so stale subfeature or planning
  metadata is caught immediately.

- **WSC-02 (M)**: As an artifact-maintenance skill author, I want audit, trace,
  and repair workflows to share one reconciliation model so they do not drift in
  how they interpret traceability and slice linkage.

- **WSC-03 (M)**: As a maintainer, I want a safe preview path for semantic
  workflow drift so I can distinguish derived registry repair from metadata
  reconciliation work.

- **WSC-04 (S)**: As a repo owner, I want the active installed skills checked
  against the checked-in repo source so stale packaged behavior is visible before
  I trust a repair or audit result.

- **WSC-05 (M)**: As a reviewer, I want CI or repeatable validation hooks to
  fail when durable workflow artifacts disagree about execution completion or
  planning status.
