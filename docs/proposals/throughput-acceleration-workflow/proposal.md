# Proposal: Throughput Acceleration Workflow

## Problem

`sirius-skills` is optimized for durable, reviewable, repo-native workflow
artifacts. That is a strength, but it also creates repeated handoff cost for a
solo maintainer or a small team trying to move through many slices quickly.

The current workflow asks the user or agent to cross many explicit boundaries:

- plan with multiple distinct skills
- stop at human approval
- bootstrap a slice
- route through `brief`
- route through `blueprint`
- implement
- review execution
- close the slice
- commit and open a PR through separate steps

The local `ship` change moves in the right direction by reporting
the next owner, but it does not fundamentally solve throughput on its own.
Compared with `gstack`, the bigger gap is not one routing function. It is the
absence of an optional accelerator layer that compresses low-risk handoffs,
preserves resumable context, and finishes the last mile of review, commit, and
PR creation.

The opportunity is to add that accelerator layer without replacing the current
planning and execution ownership model.

## Goals

- Increase end-to-end feature throughput for maintainers who want a more
  autonomous workflow.
- Preserve the current repo-native planning and execution artifacts as the
  durable source of truth.
- Add optional accelerator skills above the existing workflow rather than
  collapsing current skill boundaries into one opaque tool.
- Reduce restart cost through resumable checkpoints and persistent learnings.
- Keep the core system generic-first, agent-neutral, and compatible with the
  current manual workflow.

## Non-Goals

- Turn `sirius-skills` into a broad product like `gstack`, with browser
  automation, deployment orchestration, or host-specific onboarding flows.
- Replace `guide-planning`, `guide-execution`, or `ship` as the
  canonical owners of their current workflow state.
- Remove explicit approval boundaries where the repository intentionally wants
  human confirmation.
- Optimize for raw LOC counts as the primary success metric.
- Introduce hidden runtime state that supersedes repo artifacts.

## Proposed Direction

Add a small optional accelerator layer on top of the current two-layer workflow.

### Minimum New Skills

- `autoplan`
  - Purpose: compress the planning phase into one reviewed planning pass.
  - Scope: orchestrate `guide-planning`, `discover`, `design`, optional
    `ui-flow`, `breakdown`, and `review-planning`.
  - Behavior: auto-decide low-risk planning questions, write the normal planning
    artifacts, and stop at the existing approval boundary.
  - Reason to exist: remove repeated planning handoff latency without replacing
    durable planning artifacts.

- `ship-slice`
  - Purpose: finish execution work from active slice or reviewed backlog to a
    clean commit and PR checkpoint.
  - Scope: drive the active execution path through verification, review,
    closure, commit, and PR preparation.
  - Behavior: use the existing execution owners where possible, call
    `ship` for backlog resolution when relevant, and stop only for
    real blockers or explicit approval gates.
  - Reason to exist: `sirius-skills` currently lacks a single finish-line skill
    comparable to the role `ship` plays in `gstack`.

- `learn`
  - Purpose: surface, search, prune, and export durable workflow learnings.
  - Scope: manage project-scoped operational patterns, pitfalls, and
    preferences gathered from planning, execution, review, and closure.
  - Behavior: keep learnings append-only by default, with explicit pruning and
    staleness checks.
  - Reason to exist: throughput gains compound when repeated mistakes and
    routing hints survive across sessions.

### Supporting Capabilities Without New Workflow Ownership

- **Checkpoint and resume runtime**
  - Add optional continuous checkpoints and explicit resume support.
  - Keep this as support infrastructure, not a new source of truth.
  - Store decisions, remaining work, and failed approaches in a durable,
    inspectable format.

- **Review and execution event logs**
  - Record enough structured history that `ship-slice`, `learn`, and later reporting
    tooling can reason about past runs.
  - Keep logs supplemental; registry and artifact state remain primary.

## Proposed Ownership Boundaries

### Boundaries To Keep

- `guide-planning` remains the owner of planning readiness and planning-layer
  routing.
- `guide-execution` remains the owner of slice readiness and execution-layer
  routing.
- `ship` remains the owner of backlog resolution, increment order,
  and deciding which planned slice should move next.
- `brief`, `blueprint`, `review-execution`, `close-slice`, and `commit` remain
  the owners of their current artifacts or transitions.
- Proposal promotion and canonical planning entry remain owned by the planning
  layer, not by accelerator skills.

### Boundaries To Add

- `autoplan` owns orchestration across existing planning skills, but not
  planning registry semantics.
- `ship-slice` owns end-to-end execution finishing, but not the internal semantic
  rules of `brief`, `blueprint`, `close-slice`, or `commit`.
- `learn` owns learnings curation and retrieval, but not workflow state.
- Checkpoint support owns resumable context capture, but not artifact truth.

### Boundaries To Avoid Crossing

- Do not teach `ship` to become the default implementation,
  review, closure, commit, and PR tool all by itself.
- Do not let `ship-slice` bypass execution state mutations by editing registries
  directly when existing owners already encapsulate those rules.
- Do not let learnings or checkpoints become hidden replacements for repo
  planning artifacts.

## Interaction With Existing Skills

### `ship`

This proposal keeps `ship` as an orchestrator, but tightens its
role:

- keep backlog resolution and ready-slice selection in `ship`
- correct its contract so it reports only owners it can actually derive today,
  or extend the execution state model until those owners are real
- add an optional machine-readable handoff payload that `ship-slice` can consume
- add an optional drive mode later only if it still routes through the existing
  execution owners

This means the recent local change is useful, but it should be treated as one
building block for `ship-slice`, not as the complete throughput answer.

### `guide-planning` and `guide-execution`

Accelerator skills should call into the same durable planning and execution
logic that manual users rely on. The fast path and the manual path should share
artifacts, validations, and state transitions.

## Suggested Artifact and Config Surface

- `.skills/execution.json`
  - add optional checkpoint and accelerator-related settings such as:
    - `checkpoint_mode`
    - `checkpoint_push`
    - `ship_slice_pr_mode`
    - `autoplan_auto_decision_policy`

- project-scoped learnings file
  - candidate location: `.skills/learnings.jsonl` or
    `.skills/runtime/learnings.jsonl`
  - keep repo-local and inspectable

- project-scoped checkpoint directory
  - candidate location: `.skills/checkpoints/`
  - store human-readable summaries and optional git-linked recovery metadata

- execution event log
  - candidate location: `.skills/runtime/execution-log.jsonl`
  - record enough structured lifecycle events for later reporting

## Phased Rollout

### Phase 1: Support Runtime

- Add checkpoint and learnings data models.
- Add helper utilities for append, search, prune, and resume.
- Teach selected skills to write lightweight learnings and progress context.

### Phase 2: `autoplan`

- Compose existing planning skills into one optional high-autonomy entrypoint.
- Preserve the existing human approval boundary before slice bootstrap.
- Validate that the generated artifacts match the current manual planning
  output shape.

### Phase 3: `ship-slice` For One Slice

- Drive one active slice through verification, review, closure, commit, and PR
  preparation.
- Reuse existing execution owners instead of replacing their semantics.

### Phase 4: `ship` + `ship-slice` Integration

- Integrate `ship-slice` with `ship` for reviewed backlogs.
- Allow a maintainer to continue slice-by-slice until the next real blocker or
  commit checkpoint.

## Success Criteria

- A reviewed feature can move from planning request to approval-ready planning
  artifacts with one optional accelerator skill and one explicit approval gate.
- An active slice can move from current execution state to reviewed, closed, and
  committed with one optional finishing skill.
- Interrupted work can be resumed from durable checkpoint context without
  guessing what happened last.
- Repeated repo-specific issues become easier to avoid because learnings are
  durable and searchable.
- The manual path and accelerated path share the same artifact truth and do not
  drift semantically.

## Key Risks

- Accelerator skills could become opaque wrappers that hide too much state or
  silently bypass ownership boundaries.
- Checkpointing could create noisy git history or confusing local state if the
  cleanup path is weak.
- Learnings can become stale or misleading if they are not pruned and tied back
  to files or workflow areas.
- `ship-slice` could become too broad if it tries to absorb browser QA, deploy, and
  product-specific release logic from `gstack`.

## Why This Direction Instead Of Copying `gstack`

`gstack` is a software-factory product with many specialist roles, proactive
behavior, and a strong single-sprint posture. `sirius-skills` has a different
center of gravity: durable repo-native planning and execution artifacts with
generic-first workflow ownership.

The right borrowing strategy is:

- copy the throughput accelerants
- keep the durable artifact model
- preserve explicit ownership boundaries
- avoid importing product-specific or host-specific surface area that does not
  fit the repository's current purpose

## Why This Is Still A Proposal

- The work is not yet accepted as a canonical feature.
- The proposal intentionally spans new skills, shared runtime support, config
  surface, and workflow semantics.
- The team may decide to adopt only part of the accelerator layer, such as
  `autoplan` first and `ship-slice` later.
- Keep speculative notes here until the team decides to promote or reject it.
