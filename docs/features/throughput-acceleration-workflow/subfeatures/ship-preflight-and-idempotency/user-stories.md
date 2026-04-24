# User Stories: Ship Preflight And Idempotency

- **SPI-01 (M, medium)**: As an operator, I want `ship` rerun behavior
  documented as an explicit idempotency contract so I know what can be safely
  retried after an interruption.
  Acceptance signals:
  - The contract distinguishes read-only recomputation from mutation-only
    actions such as bootstrap, approval writes, and delegated execution.
  - Rerun guidance states which boundaries still intentionally stop progress.

- **SPI-02 (M, high)**: As a maintainer, I want an optional preflight check
  before `ship --bootstrap-next` or `ship --resume` so I can stop before
  execution state changes when the run is not safe.
  Acceptance signals:
  - The first rollout evaluates local repo evidence before mutation on both
    command paths.
  - When preflight blocks, the result uses the existing readiness and
    stop-reason model instead of inventing a second status plane.

- **SPI-03 (S, medium)**: As a repository author, I want any preflight
  behavior to be enabled through typed config so stricter safety policy stays
  opt-in and repo-specific.
  Acceptance signals:
  - Preflight configuration lives under the existing `accelerators.ship`
    execution-config owner.
  - The first rollout adds no new CLI flags or environment variables.

- **SPI-04 (S, low)**: As a reviewer, I want preflight and rerun behavior
  reflected in `ship` docs and roadmap guidance so the two-step autonomy path
  stays understandable without reading code.
  Acceptance signals:
  - `skills/ship/SKILL.md` describes the rerun contract in the same terms the
    implementation uses.
  - Wiki guidance explains when preflight runs, what it checks, and why it can
    stop before mutation.
