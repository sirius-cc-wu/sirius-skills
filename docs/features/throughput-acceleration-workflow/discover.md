# Discover: Throughput Acceleration Workflow

## Problem

`sirius-skills` already provides a strong repo-native planning and execution
model, but the current workflow optimizes more for durable ownership boundaries
than for sprint throughput. For a maintainer working alone or coordinating a
small number of agents, repeated workflow handoffs create visible drag:

- planning is split across multiple explicit skills
- reviewed planning still requires manual movement into execution bootstrap
- active slice work still crosses multiple end-of-slice owners before commit
  and PR creation
- interrupted work has limited durable recovery context beyond the repo
  artifacts themselves
- repeated repo-specific workflow lessons are not yet captured as reusable
  project memory

The recent `ship` work improves backlog resolution and owner
reporting, but it does not by itself create a high-throughput path comparable to
the acceleration patterns seen in systems such as `gstack`.

The feature needs to define an optional accelerator layer that improves planning
and execution throughput while preserving the existing durable artifact model
and skill ownership boundaries.

## Goals

- Add an optional fast path that reduces planning and execution handoff latency.
- Preserve `docs/features/`, slice artifacts, registries, and metadata as the
  durable source of truth.
- Keep the current planning and execution owners intact while adding higher-level
  orchestration skills above them.
- Improve recoverability of interrupted work with resumable checkpoint context.
- Make repeated repo-specific workflow patterns reusable through durable
  learnings.

## Non-Goals

- Turn `sirius-skills` into a broad product surface matching `gstack`.
- Add browser QA, deployment automation, or host-specific onboarding as part of
  this feature.
- Replace `guide-planning`, `guide-execution`, `ship`, `brief`,
  `blueprint`, `review-execution`, `close-slice`, or `commit` as the canonical
  owners of their semantics.
- Collapse explicit human approval boundaries that the current workflow
  intentionally preserves.
- Optimize around raw LOC output instead of shipped work and durable artifacts.

## Primary Actors

- Maintainer who wants a faster end-to-end planning and shipping loop while
  keeping repo-native workflow artifacts.
- Planner who wants a single high-autonomy entrypoint for early planning work.
- Implementer who wants a single finishing workflow from active slice to commit
  and PR checkpoint.
- Reviewer who needs accelerated execution to still preserve clear ownership and
  verification boundaries.
- Repository author extending `sirius-skills` without turning it into a
  product-specific automation stack.

## Constraints

- The solution must remain generic-first and reusable across repositories.
- Repo-native planning and execution artifacts must remain the durable source of
  truth.
- `guide-planning` must continue owning planning readiness and proposal
  promotion semantics.
- `guide-execution` must continue owning slice readiness and execution-layer
  routing semantics.
- `ship` must remain an orchestrator for backlog resolution rather
  than absorbing implementation, review, and closure ownership by default.
- New accelerator behavior should be optional and configuration-driven rather
  than mandatory for all repositories.

## Confirmed Signals In Repo

- `guide-planning` already owns planning readiness, proposal promotion, and
  routing into `discover`, `design`, `breakdown`, and `review-planning`.
- `guide-execution` already owns slice readiness and transitions between
  `draft`, `brief_ready`, `blueprint_ready`, `execution_ready`, and `closed`.
- `ship` already resolves reviewed backlog state, increment order,
  ready slices, and commit checkpoints.
- The current execution flow still requires explicit progression through
  `brief`, `blueprint`, implementation, review, closure, and later commit/PR
  work.
- The repository already uses durable metadata and registries extensively, so
  any accelerator path has to share those artifacts instead of introducing a
  parallel hidden workflow.

## Assumptions

- The highest-value throughput gains come from compressing low-risk workflow
  handoffs, not from weakening artifact quality or approval boundaries.
- A small accelerator layer can deliver most of the benefit without copying the
  much broader product surface of `gstack`.
- Repo-specific learnings and resumable context will improve repeated execution
  more than further owner-label refinement inside `ship` alone.
- The feature should treat the recent `ship` work as a building
  block for a future finishing workflow, not as the final throughput solution.

## Candidate Capability Areas

- **Autoplan**
  - Add one optional planning entrypoint that composes the existing planning
    stack into one reviewed planning pass.
  - Preserve the explicit human approval boundary before execution bootstrap.

- **Ship Slice**
  - Add one optional finishing workflow that drives active slice work through
    verification, review, closure, commit, and PR preparation.
  - Reuse existing execution owners instead of replacing their semantics.

- **Learn**
  - Add durable project-scoped workflow learnings for recurring pitfalls,
    preferences, and routing hints.
  - Keep learnings inspectable, searchable, and prunable.

- **Checkpoint and resume support**
  - Add resumable context capture for long-running or interrupted planning and
    execution work.
  - Keep checkpoints supplemental rather than replacing planning or slice
    artifacts.

- **Execution event logging**
  - Add lightweight structured history that later reporting or throughput
    tooling can consume.
  - Keep logs derived and append-only rather than authoritative.

## Desired Outcomes

- A maintainer can choose a faster planning path without losing the current
  planning artifacts or approval semantics.
- A maintainer can choose a faster slice-finishing path without bypassing
  existing execution-state owners.
- Interrupted work can be resumed from durable context instead of reconstructing
  the prior session from memory.
- Repeated repo-specific workflow lessons become durable and reusable across
  sessions.

## Success Criteria

- The repository has a coherent design target for optional `autoplan`, `ship-slice`,
  `learn`, and checkpoint/runtime support.
- The accelerator layer preserves current ownership boundaries instead of
  centralizing all workflow semantics into one opaque skill.
- The resulting capability set is concrete enough for `design` to define
  artifact locations, config surfaces, and interaction boundaries.

## Risks And Open Questions

- `ship-slice` can become too broad if it tries to absorb unrelated product-automation
  behavior instead of focusing on repo-native execution finishing.
- Checkpoint support can create noisy or confusing state if its cleanup and
  recovery rules are not explicit.
- Learnings can become stale or misleading if they are not tied to workflow
  scope and pruning rules.
- The boundary between a stronger `ship` and a separate `ship-slice`
  skill needs to remain clear so execution ownership does not blur.
