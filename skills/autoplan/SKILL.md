---
name: autoplan
description: Reconcile one planning target, optionally execute planning owners in sequence, and persist checkpointed resume context through approval and planning-commit handoff.
---

# Autoplan

Use this skill when one feature or proposal should be driven through the planning
stack with checkpointed resume support.

## Responsibilities

1. Resolve one planning target through the existing planning registry.
2. Read active and candidate learnings for the target scope.
3. Surface the next planning owner based on the current planning status.
4. Optionally execute the planning owner chain (`discover`, `design`,
   `breakdown`, `review-planning`) in sequence until a hard boundary is hit.
5. Evaluate the durable human-approval gate for `planning_reviewed` targets.
6. After approval is recorded, hand approved-but-uncommitted planning back to the
   `commit` owner before execution begins.
7. Write runtime checkpoint and event-log context for resume, including owner-chain
   stop context when owner-chain mode is enabled.
8. Emit a `readiness` summary in JSON output (`can_proceed`, `blocked_by`,
   `stop_reason`, approval/commit gate state) so upstream orchestrators can
   detect whether autoplan can continue automatically.
9. Log failure events in the runtime log with recovery and improvement
   suggestions when `autoplan` exits non-zero or stops on a failure boundary.
10. Refuse to treat already-implemented planning as the active owner chain when
    the real request is follow-on delta work for that feature; send that case
    back through `guide-planning` to open or continue a subfeature.
11. Write a shared `.skills/runtime/request-handoff.json` summary so another
    agent can resume from the latest planning route without relying on
    agent-local scratch plans.

## Tooling

```bash
python3 skills/autoplan/scripts/autoplan.py throughput-acceleration-workflow --json
python3 skills/autoplan/scripts/autoplan.py --resume --json
python3 skills/autoplan/scripts/autoplan.py throughput-acceleration-workflow --execute-owner-chain --review-note "Planning reviewed" --json
python3 skills/autoplan/scripts/autoplan.py throughput-acceleration-workflow --approve --approval-note "approved for execution" --json
```

## Configuration

Configure owner-chain behavior in `.skills/planning.json` under
`accelerators.autoplan`.

```json
{
  "planning_dir": "docs/features",
  "proposal_dir": "docs/proposals",
  "design_diagram_mode": "embedded",
  "accelerators": {
    "autoplan": {
      "auto_decision_policy": "conservative",
      "execute_owner_chain": false,
      "stop_on_owner": ["review-planning"]
    }
  }
}
```

Optional CLI overrides:

- `--execute-owner-chain` / `--no-execute-owner-chain`
- `--stop-on-owner <owner>` (repeatable)
- `--review-note <text>` (used when advancing to `planning_reviewed`)
- `--approve`
- `--approval-note <text>`

## Workflow

1. Run `autoplan.py <target> --json` (or `--resume --json` when resuming) and
   inspect the JSON output instead of treating the script as the whole owner
   chain.
2. If `execute_owner_chain` is disabled, report the routed `next_owner` and
   stop.
3. If `owner_handoff.should_invoke_skill` is true, treat that as an instruction
   to continue the owner chain by invoking the returned planning skill instead
   of stopping at the first `missing_required_input` boundary.
4. Before invoking `breakdown`, run any `owner_handoff.bootstrap_commands`
   first. This is especially important when the only blocker is the missing
   scaffold pair:
   - `slice-planning.md`
   - `slice-traceability.md`
5. Invoke the returned owner skill (`discover`, `design`, `breakdown`, or
   `review-planning`) and let that skill author or repair the planning
   artifacts it owns.
6. After the owner skill completes, rerun `autoplan.py <target> --json` and
   continue looping until one of these explicit stop boundaries is reached:
   - `approval_required`
   - `commit_checkpoint`
   - `owner_stop`
   - a non-automatable owner
   - an unresolved ambiguity or validation failure that the owner skill could
     not repair
7. When `next_owner=approval`, stop for explicit human approval. Record that
   approval with `autoplan.py <target> --approve [--approval-note "..."] --json`.
8. When `next_owner=commit`, invoke the existing `commit` skill so the approved
   planning artifacts and durable approval record are committed before execution.
9. Once approval is valid and the planning commit checkpoint is clear, hand off
   to `slice` or `ship` for execution bootstrap.
10. If the target is already `implemented` and the user is actually reporting a
    new fix, regression, or missing behavior on that feature, stop and route
    back to `guide-planning`/`add-subfeature` instead of resuming the old
    feature packet or suggesting archive/ship.

## Runtime outputs

`autoplan` writes shared runtime state under `.skills/runtime/`, including:

- `checkpoints/autoplan-active.json`
- `execution-log.jsonl`
- `request-handoff.json`

Use `request-handoff.json` for the latest request-level route decision when a
later agent needs to continue the same planning request without depending on a
private plan-mode scratch file.

`autoplan.py` remains the checkpointing and readiness source of truth, but the
skill is responsible for actually chaining into downstream planning-owner
skills.

## Guardrails

- Do not replace `guide-planning` as the source of planning truth.
- Keep approval as an explicit human gate and planning commit as the durable
  checkpoint before execution.
- Keep planning transitions owned by planning-layer validation and metadata.
- Stop with structured context when owner-chain boundaries are hit (explicit
   stop owner, missing required input, validation failure, or approval).
- Keep raw failure incidents in runtime logs; use durable learnings only for
  curated patterns worth keeping.
- Do not stop just because `autoplan.py` reported `missing_required_input` for
  the next automatable owner; if `owner_handoff.should_invoke_skill` is true,
  that owner is expected to create or repair the missing artifacts.
- Keep stop-reason classification and readiness invariants aligned with shared
  accelerator guardrail helpers in `workflow_runtime`.
- Prefer current planning artifacts over stale checkpoint context.
- Do not use an `implemented` target as proof that nothing remains to do when
  the user is describing new delta work; implemented status on the parent
  feature is a signal to open a follow-on subfeature, not to archive first.
