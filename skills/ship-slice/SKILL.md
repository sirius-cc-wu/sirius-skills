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
5. Optionally continue through owned-file formatting, delegated closure, and
   owned-file commit when execution config enables the terminal automation tail.
6. Report the next owner for the slice and write a resumable checkpoint plus
   execution event.
7. Stop at review, close, commit, or verification boundaries unless the
   configured continuation policy and terminal automation tail both allow safe
   continuation.
8. Emit a `readiness` summary in JSON output (`can_proceed`, `blocked_by`,
   `stop_reason`, approval/commit gate state) so `ship` and dashboards can
   read one-slice acceleration status without parsing owner-chain internals.

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
      "stop_on_owner": ["review-execution"],
      "continuation_policy": {
        "review_boundary": "stop",
        "commit_checkpoint": "stop"
      },
      "auto_format": false,
      "format_command": ["./scripts/format-owned.sh"],
      "auto_close": false,
      "auto_commit": false
    }
  }
}
```

Optional CLI overrides:

- `--execute-owner-chain` / `--no-execute-owner-chain`
- `--stop-on-owner <owner>` (repeatable)

Terminal automation notes:

- `auto_commit` requires `auto_close`
- `auto_format` requires `format_command`
- formatting and staging stay scoped to the delegated run's owned file set
- `continuation_policy.review_boundary` and
  `continuation_policy.commit_checkpoint` accept `stop` or `continue`
- defaults are `stop`; policy remains config-only in the first rollout

## Guardrails

- Do not replace `ship` backlog resolution.
- Prefer current execution artifacts over stale checkpoint context.
- Keep execution status transitions owned by `guide-execution` tooling and
  validation.
- Emit structured stop context for review boundaries, verification/missing-input
  failures, explicit owner stops, formatter spillover, owned-file conflicts,
  partial-success commit failures, and commit checkpoints, plus policy action
  metadata in readiness output.
- Keep approval, owned-file conflicts, formatter spillover, and verification
  failures as hard stops regardless of continuation policy.
- Do not format or stage unrelated dirty files outside the owned file set.
- Keep stop-reason classification and readiness invariants aligned with shared
  accelerator guardrail helpers in `workflow_runtime`.
- Keep runtime files supplemental; do not rewrite planning or execution truth
  from checkpoint state.
