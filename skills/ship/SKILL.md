---
name: ship
description: Resolves one reviewed feature or subfeature backlog into remaining planned slices and routes each active slice to the next owning execution step with one commit per completed slice.
---

# Ship

Use this skill when a maintainer wants to work through all planned slices for
one reviewed and committed subfeature. Direct feature targets remain supported
for existing planning packets, but new delivery work should normally ship from a
subfeature.

## Responsibilities

The first slice of this capability establishes durable scope and backlog
resolution:

1. Resolve exactly one feature or subfeature planning packet.
2. Read its planned slices, increment order, and dependency order from planning artifacts.
3. Compare planned slices with execution-slice lineage and closure state.
4. Report which planned slices are completed, active, ready next, blocked, or deferred by an earlier unfinished increment.

The second slice adds conservative sequential orchestration:

5. Bootstrap exactly one next-ready execution slice from the current unfinished
   increment when no mapped slice is already active; for subfeatures, the slice
   is created under the owning subfeature's local `slices/` root.
6. Record the bootstrapped execution slice ID back into `slice-traceability.md`.
7. Hand the active slice to the concrete next owner inside the execution layer.

The third slice adds stop/resume semantics:

8. Resume an already-active mapped slice instead of creating a second one.
9. Recompute progress from closed slices, active slices, increments, and
   dependencies without a batch-only progress file.
10. Report whether the active slice next belongs to `blueprint`, legacy `brief`,
     repository implementation, `guide-execution`, `review-execution`,
    `close-slice`, or `commit`.
11. Expose a stable machine-readable handoff payload for the active slice in
    JSON output without changing backlog ownership semantics.
12. Stop explicitly when unfinished planned slices remain but none are ready.

The fourth slice adds per-slice commit checkpoints:

12. Refuse to bootstrap the next slice while the repository still has uncommitted
    changes after a completed mapped slice.
13. Hand that checkpoint back to the existing `commit` owner instead of silently
    absorbing more work into the next slice.
14. Report when an increment is complete and execution is moving on to the next
    increment.

The fifth slice adds explicit two-step approval gating for delegated autopilot:

15. Record durable approval decisions for `planning_reviewed` targets.
16. Require a valid approval record before delegating into `ship-slice` autopilot.
17. Invalidate approval automatically when planning artifacts change after approval.

The sixth slice adds a machine-readable readiness dashboard:

18. Emit a consistent `readiness` object in JSON output for backlog, resume, and
    delegated flows.
19. Summarize blocked reasons (`approval_required`, `commit_checkpoint`,
    `review_boundary`, etc.) without replacing planning/execution source-of-truth
    artifacts.

The seventh slice adds explicit terminal finalization:

20. Finalize one completed `implemented` feature or subfeature explicitly through
    `--finalize`.
21. Before requiring terminal planning status, run shared owner-completion
    reconciliation so a target with all traced execution slices closed can be
    promoted through the same shared completion hook used by `close-slice`.
22. Require a durable execution reconciliation record in `system-design.md`
    before archive.
23. Stop on `reconcile-execution` when the canonical design has not yet been
    reconciled with completed slice execution.
24. Invoke `archive-artifacts` only after reconciliation passes.

## Preferred Input

- a feature slug, subfeature slug, or planning packet path
- optional `--scope <path>` when nested planning scopes are ambiguous

## Tooling

```bash
sirius ship <target>
sirius ship <target> --json
sirius ship <target> --bootstrap-next
sirius ship <target> --resume
sirius ship <target> --finalize
sirius ship <target> --approve --approval-note "approved for execution"
sirius ship <target> --scope apps/payments
```

## Rerun Contract

Treat `ship` as deterministic with respect to current repository artifacts, but
not as universally side-effect free.

- **Read-only recomputation**
  - `sirius ship <target>`
  - `sirius ship <target> --json`
  - route-only `--resume` when an active slice already exists and `ship` is only
    handing that slice to the next owner without bootstrapping or delegating
- **Guarded mutation**
  - `--approve` records or refreshes the durable approval record for a
    `planning_reviewed` target
  - `--bootstrap-next` may create one next-ready execution slice and write the
    mapped execution slice ID back into `slice-traceability.md`
  - `--resume` may bootstrap the next slice when no active mapped slice exists
  - `--finalize` may first reconcile completed owner status from closed traced
    execution slices, then archive a completed `implemented` target after the
    durable reconciliation gate passes
- **Delegated side effects**
  - when `accelerators.ship.delegate_to_ship_slice` is enabled, `--resume` may
    hand execution to `ship-slice`, which then owns downstream execution
    boundaries

## Preflight Contract

`ship` now exposes one repo-owned preflight surface under
`accelerators.ship.preflight.mode`.

Supported values:

- `off` (default)
- `local_only`

Behavior:

- `ship <target>` / `ship --json` remain backlog-resolution only and report
  `readiness.preflight.status=disabled` or `skipped`
- local-only preflight applies only to mutation-capable paths:
  `--bootstrap-next`, mutation-capable `--resume`, and `--finalize`
- when local-only preflight blocks on ship-local guardrails, `ship` keeps the
  canonical blocker codes (`approval_required`, `commit_checkpoint`) and marks
  `readiness.stop_reason.phase=preflight`
- route-only resume remains non-blocking and reports preflight as `skipped`
- once `ship` delegates into `ship-slice`, downstream stop-policy behavior such
  as `review_boundary` remains owned by `ship-slice`, not by ship preflight

## Guardrails

- Resolve exactly one planning scope; do not guess across ambiguous scopes.
- Do not create or mutate execution slices during the first slice of this
  capability beyond explicit `--bootstrap-next` orchestration.
- Treat planning and execution registries as the source of truth for backlog and
  completion state.
- Use shared owner-completion reconciliation for terminal planning status; do
  not duplicate feature/subfeature completion promotion logic inside `ship`.
- Respect increment ordering first and slice dependency order second; do not
  bootstrap a later-increment slice while an earlier increment still has
  unfinished planned slices.
- Refuse batch bootstrap when `slice-traceability.md` groups multiple planned
  slices into one row; the mapping is ambiguous and should be split first.
- Stop when unfinished planned slices remain but no mapped slice is active and no
  dependency-ready slice exists.
- Require a clean worktree before continuing past a completed mapped slice so one
  commit still represents one completed execution slice.
- Require a durable `execution-reconciliation` block in `system-design.md`
  before terminal archive mutation.
- Keep one-slice execution ownership in the existing `slice`, `blueprint`,
  optional legacy `brief`, `guide-execution`, `review-execution`,
  `close-slice`, and `commit` skills.
- Keep terminal reconciliation owned by `reconcile-execution` and archive
  mutation owned by `archive-artifacts`, even when `ship` orchestrates both.
- Keep explicit human approval as a durable gate before delegated execution
  autopilot starts from `planning_reviewed`.
- Keep readiness and stop-reason guardrails aligned with the shared
  `workflow_runtime` accelerator guardrail helper used by `autoplan` and
  `ship-slice`.
- Keep `accelerators.ship.preflight.mode` repo-owned; do not add CLI flags or
  environment-variable overrides for the same policy.
- Route to the next concrete owner, but do not absorb artifact authoring or
  closure logic that belongs to those owner skills.
- Keep any machine-readable handoff payload derived from existing planning and
  execution artifacts instead of introducing a second source of truth.
