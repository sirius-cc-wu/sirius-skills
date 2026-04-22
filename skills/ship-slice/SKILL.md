---
name: ship-slice
description: Reconcile one active execution slice, optionally execute owner-chain routing, and persist checkpointed resume context for one-slice acceleration.
---

# Ship Slice

Use this skill when one active execution slice should be resumed from its
current state with checkpointed runtime context.

## Responsibilities

1. Resolve one active slice from an explicit slice selector, a `ship`
   `handoff_payload`, or a previously written checkpoint.
2. Read active and candidate learnings for the target scope.
3. Reconcile the current slice status against execution artifacts.
4. Optionally run owner-chain orchestration for one slice (`brief`, `blueprint`,
   implementation routing) until review/checkpoint boundaries.
5. Report the next owner for the slice and write a resumable checkpoint plus
   execution event.
6. Stop at review, close, commit, or verification boundaries rather than
   replacing existing owner skills.

## Tooling

```bash
python3 skills/ship-slice/scripts/ship_slice.py taw-ship-slice-loop --json
python3 skills/ship-slice/scripts/ship_slice.py --handoff /tmp/handoff.json --json
python3 skills/ship-slice/scripts/ship_slice.py --resume --json
python3 skills/ship-slice/scripts/ship_slice.py taw-ship-slice-loop --execute-owner-chain --json
```

## Configuration

Configure owner-chain behavior in `.skills/execution.json` under
`accelerators.ship_slice`.

```json
{
  "slice_dir": "slices",
  "preferred_workflow": "TDD",
  "auto_start_implementation": true,
  "accelerators": {
    "ship_slice": {
      "execute_owner_chain": false,
      "stop_on_owner": ["review-execution"]
    }
  }
}
```

Optional CLI overrides:

- `--execute-owner-chain` / `--no-execute-owner-chain`
- `--stop-on-owner <owner>` (repeatable)

## Guardrails

- Do not replace `ship` backlog resolution.
- Prefer current execution artifacts over stale checkpoint context.
- Keep execution status transitions owned by `guide-execution` tooling and
  validation.
- Emit structured stop context for review boundaries, verification/missing-input
  failures, explicit owner stops, and commit checkpoints.
- Stop at commit checkpoints instead of silently batching more work.
- Keep runtime files supplemental; do not rewrite planning or execution truth
  from checkpoint state.
