# User Stories: Throughput Acceleration Workflow

- **TAW-01 (L, medium)**: As a maintainer, I want one planning entrypoint that
  can run the normal planning stack end to end so that I only stop for
  high-value planning decisions and final approval.
  Acceptance signals:
  - The workflow writes the same canonical planning artifacts the manual path
    would have produced.
  - The workflow does not bypass `review-planning` or the explicit approval
    boundary before execution.

- **TAW-02 (XL, high)**: As an implementer, I want one finishing workflow for
  an active slice so that review, closure, commit, and PR preparation do not
  require manual re-routing through multiple terminal steps.
  Acceptance signals:
  - The workflow respects the existing execution-state model.
  - The workflow stops only for real blockers, failing verification, or
    explicit approval gates.

- **TAW-03 (L, high)**: As a maintainer working across long sessions, I want
  resumable checkpoint context so that I can recover decisions made, remaining
  work, and failed approaches without reconstructing the whole session from
  memory.
  Acceptance signals:
  - Checkpoints are inspectable and durable.
  - Resume support does not replace repo artifacts as the source of truth.

- **TAW-04 (M, medium)**: As a repeat user of `sirius-skills`, I want workflow
  learnings to persist across sessions so that the system can avoid recurring
  mistakes and route me more efficiently through familiar repo patterns.
  Acceptance signals:
  - Learnings can be searched, reviewed, and pruned.
  - Learnings stay project-scoped by default and remain explicit rather than
    hidden in chat history.
