---
name: execute-all-slices
description: Resolves one reviewed feature or subfeature backlog into remaining planned slices and routes each active slice to the next owning execution step with one commit per completed slice.
---

# Execute All Slices

Use this skill when a maintainer wants to work through all planned slices for
one reviewed and committed feature or subfeature.

## Responsibilities

The first slice of this capability establishes durable scope and backlog
resolution:

1. Resolve exactly one feature or subfeature planning packet.
2. Read its planned slices, increment order, and dependency order from planning artifacts.
3. Compare planned slices with execution-slice lineage and closure state.
4. Report which planned slices are completed, active, ready next, blocked, or deferred by an earlier unfinished increment.

The second slice adds conservative sequential orchestration:

5. Bootstrap exactly one next-ready execution slice from the current unfinished
   increment when no mapped slice is already active.
6. Record the bootstrapped execution slice ID back into `slice-traceability.md`.
7. Hand the active slice to the concrete next owner inside the execution layer.

The third slice adds stop/resume semantics:

8. Resume an already-active mapped slice instead of creating a second one.
9. Recompute progress from closed slices, active slices, increments, and
   dependencies without a batch-only progress file.
10. Report whether the active slice next belongs to `brief`, `blueprint`,
    repository implementation, `guide-execution`, `review-execution`,
    `close-slice`, or `commit`.
11. Stop explicitly when unfinished planned slices remain but none are ready.

The fourth slice adds per-slice commit checkpoints:

12. Refuse to bootstrap the next slice while the repository still has uncommitted
    changes after a completed mapped slice.
13. Hand that checkpoint back to the existing `commit` owner instead of silently
    absorbing more work into the next slice.
14. Report when an increment is complete and execution is moving on to the next
    increment.

## Preferred Input

- a feature slug, subfeature slug, or planning packet path
- optional `--scope <path>` when nested planning scopes are ambiguous

## Tooling

```bash
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target>
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target> --json
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target> --bootstrap-next
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target> --resume
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target> --scope apps/payments
```

## Guardrails

- Resolve exactly one planning scope; do not guess across ambiguous scopes.
- Do not create or mutate execution slices during the first slice of this
  capability beyond explicit `--bootstrap-next` orchestration.
- Treat planning and execution registries as the source of truth for backlog and
  completion state.
- Respect increment ordering first and slice dependency order second; do not
  bootstrap a later-increment slice while an earlier increment still has
  unfinished planned slices.
- Refuse batch bootstrap when `slice-traceability.md` groups multiple planned
  slices into one row; the mapping is ambiguous and should be split first.
- Stop when unfinished planned slices remain but no mapped slice is active and no
  dependency-ready slice exists.
- Require a clean worktree before continuing past a completed mapped slice so one
  commit still represents one completed execution slice.
- Keep one-slice execution ownership in the existing `slice`, `brief`,
  `blueprint`, `guide-execution`, `review-execution`, `close-slice`, and
  `commit` skills.
- Route to the next concrete owner, but do not absorb artifact authoring or
  closure logic that belongs to those owner skills.
