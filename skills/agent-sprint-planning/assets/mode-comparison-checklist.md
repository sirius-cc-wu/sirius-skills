# Single-Agent vs Multi-Agent Checklist

Use this checklist before creating packet backlog.

## 1. Mode Selection Quick Test

Choose `single-agent` if 2 or more are true:
- Critical path is mostly sequential.
- Same files/modules will be touched across most packets.
- Contract details are still evolving.
- Handoff overhead is likely higher than parallelization gain.

Choose `multi-agent` if 2 or more are true:
- At least 2 independent lanes can run after an early contract freeze.
- Lane boundaries can be expressed by files/modules and interfaces.
- Integration points have deterministic verification commands.
- Owners and handoff contracts can be written unambiguously.

## 2. Planning Differences

| Area | Single-Agent | Multi-Agent |
|---|---|---|
| Branch strategy | One branch/worktree | One integration branch + lane worktrees |
| Packet design | Sequential packets | Lane-scoped packets with owners |
| Dependencies | Linear critical path | DAG with explicit cross-lane edges |
| Handoffs | Usually none | Required and documented |
| Re-planning trigger | Packet-level failures | Lane blocking and integration failures |
| Integration | End-of-sprint verification | Repeated checkpoints + final integration lane |

## 3. Required Fields by Mode

Single-agent required:
- Packet objective, scope, acceptance, verification commands
- Dependencies and stop-and-ask triggers

Multi-agent required:
- All single-agent fields
- Owner, handoff target, handoff contract
- Integration checkpoint definition
- Shared-file conflict rule

## 4. Risk Controls by Mode

Single-agent:
- Stop gates on destructive changes
- Retry limit per packet
- Rollback note for medium/high risk

Multi-agent:
- Same controls as single-agent
- Contract freeze checkpoints
- Merge/integration owner for conflict arbitration
- Lane timeout threshold for forced re-plan

## 5. Exit Criteria

Single-agent ready when:
- Ordered packet list has no unresolved blockers
- Every packet has executable verification commands

Multi-agent ready when:
- Every lane has owner and handoff contract
- Integration checkpoints and final gate are scheduled
- Conflict resolution rule is explicit
