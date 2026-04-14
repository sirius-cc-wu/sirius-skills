---
name: execute-all-slices
description: Resolves one reviewed feature or subfeature backlog into remaining planned slices and, in later slices, will execute them sequentially with one commit per completed slice.
---

# Execute All Slices

Use this skill when a maintainer wants to work through all planned slices for
one reviewed and committed feature or subfeature.

## Responsibilities

The first slice of this capability establishes durable scope and backlog
resolution:

1. Resolve exactly one feature or subfeature planning packet.
2. Read its planned slices and dependency order from planning artifacts.
3. Compare planned slices with execution-slice lineage and closure state.
4. Report which planned slices are completed, active, ready next, or blocked.

Later slices will extend this skill into sequential execution, stop/resume
semantics, and per-slice commit checkpoints.

## Preferred Input

- a feature slug, subfeature slug, or planning packet path
- optional `--scope <path>` when nested planning scopes are ambiguous

## Tooling

```bash
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target>
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target> --json
python3 skills/execute-all-slices/scripts/execute_all_slices.py <target> --scope apps/payments
```

## Guardrails

- Resolve exactly one planning scope; do not guess across ambiguous scopes.
- Do not create or mutate execution slices during the first slice of this
  capability.
- Treat planning and execution registries as the source of truth for backlog and
  completion state.
- Keep one-slice execution ownership in the existing `slice`,
  `guide-execution`, `review-execution`, `close-slice`, and `commit` skills.
