---
name: autoplan
description: Reconcile one planning target, surface the next planning owner, and persist checkpointed resume context until the approval boundary.
---

# Autoplan

Use this skill when one feature or proposal should be driven through the normal
planning stack with checkpointed resume support.

## Responsibilities

1. Resolve one planning target through the existing planning registry.
2. Read active and candidate learnings for the target scope.
3. Surface the next planning owner based on the current planning status.
4. Write runtime checkpoint and event-log context for resume.
5. Stop explicitly at the `planning_reviewed` approval boundary.

## Tooling

```bash
python3 skills/autoplan/scripts/autoplan.py throughput-acceleration-workflow --json
python3 skills/autoplan/scripts/autoplan.py --resume --json
```

## Guardrails

- Do not replace `guide-planning` as the source of planning truth.
- Keep approval as an explicit stop boundary.
- Prefer current planning artifacts over stale checkpoint context.
