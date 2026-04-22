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
python3 skills/learn/scripts/learn.py query throughput-acceleration-workflow
python3 skills/learn/scripts/learn.py query throughput-acceleration-workflow --state active --skill ship --json
python3 skills/learn/scripts/learn.py promote L001
python3 skills/learn/scripts/learn.py prune L001
python3 skills/learn/scripts/learn.py export throughput-acceleration-workflow --state active
```

## Guardrails

- Keep learnings supplemental to repo planning and execution artifacts.
- Do not hard-delete learnings during normal lifecycle changes.
- Default to the configured repo-scoped learnings file instead of ad hoc
  scratch files.
- Stop with a clear error when the requested learning ID does not exist.
