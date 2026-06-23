---
name: learn
description: Query, promote, prune, and export durable repo-scoped workflow learnings from the shared accelerator runtime.
---

# Learn

Use this skill when a maintainer wants to inspect or curate repo-scoped
workflow learnings stored in the shared accelerator runtime.

## Responsibilities

1. Read durable learnings from the configured repo-scoped learnings store.
2. Query learnings by scope, skill, and state without rewriting records.
3. Promote a learning to `active` or prune it to `pruned`.
4. Keep lifecycle changes explicit and non-destructive.

## Tooling

```bash
sirius learn query throughput-acceleration-workflow
sirius learn query throughput-acceleration-workflow --state active --skill ship --json
sirius learn promote L001
sirius learn prune L001
sirius learn export throughput-acceleration-workflow --state active
```

## Guardrails

- Keep learnings supplemental to repo planning and execution artifacts.
- Do not hard-delete learnings during normal lifecycle changes.
- Default to the configured repo-scoped learnings file instead of ad hoc
  scratch files.
- Stop with a clear error when the requested learning ID does not exist.
