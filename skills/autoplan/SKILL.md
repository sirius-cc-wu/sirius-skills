---
name: autoplan
description: Reconcile one planning target, optionally execute planning owners in sequence, and persist checkpointed resume context until the approval boundary.
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
5. Stop explicitly at the `planning_reviewed` approval boundary.
6. Write runtime checkpoint and event-log context for resume, including owner-chain
   stop context when owner-chain mode is enabled.

## Tooling

```bash
python3 skills/autoplan/scripts/autoplan.py throughput-acceleration-workflow --json
python3 skills/autoplan/scripts/autoplan.py --resume --json
python3 skills/autoplan/scripts/autoplan.py throughput-acceleration-workflow --execute-owner-chain --review-note "Planning reviewed" --json
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

## Guardrails

- Do not replace `guide-planning` as the source of planning truth.
- Keep approval as an explicit stop boundary.
- Keep planning transitions owned by planning-layer validation and metadata.
- Stop with structured context when owner-chain boundaries are hit (explicit
  stop owner, missing required input, validation failure, or approval).
- Prefer current planning artifacts over stale checkpoint context.
