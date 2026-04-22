---
name: ship-slice
description: Reconcile one active execution slice, surface the next owner, and persist checkpointed resume context for one-slice acceleration.
---

# Ship Slice

Use this skill when one active execution slice should be resumed from its
current state with checkpointed runtime context.

## Responsibilities

1. Resolve one active slice from an explicit slice selector, a `ship`
   `handoff_payload`, or a previously written checkpoint.
2. Read active and candidate learnings for the target scope.
3. Reconcile the current slice status against execution artifacts.
4. Report the next owner for the slice and write a resumable checkpoint plus
   execution event.
5. Stop at review, close, commit, or verification boundaries rather than
   replacing existing owner skills.

## Tooling

```bash
python3 skills/ship-slice/scripts/ship_slice.py taw-ship-slice-loop --json
python3 skills/ship-slice/scripts/ship_slice.py --handoff /tmp/handoff.json --json
python3 skills/ship-slice/scripts/ship_slice.py --resume --json
```

## Guardrails

- Do not replace `ship` backlog resolution.
- Prefer current execution artifacts over stale checkpoint context.
- Stop at commit checkpoints instead of silently batching more work.
- Keep runtime files supplemental; do not rewrite planning or execution truth
  from checkpoint state.
