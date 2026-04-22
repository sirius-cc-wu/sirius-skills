# Addy Agent-Skills Reference

## Scope

Comparison between:

- Addy Osmani `agent-skills` (`https://github.com/addyosmani/agent-skills`)
- `sirius-skills`

Reference baseline used here:

- local clone: `andyosmali-agent-skills/`
- local commit: `1f66d57`
- upstream `HEAD` verified at same commit

## Architecture Comparison

| Dimension | `agent-skills` | `sirius-skills` |
|---|---|---|
| Core model | General engineering workflow skills + slash-command orchestration. | Repo-native planning/execution artifact workflow with explicit state owners. |
| Primary state | Conversation + command workflow state. | Durable repository artifacts (`docs/features`, `docs/proposals`, `slices`, registries, metadata). |
| Skill granularity | 20 broad engineering skills across define/plan/build/verify/review/ship. | Many workflow-owner and artifact-management skills with planning/execution boundary enforcement. |
| Entrypoints | 7 lifecycle commands (`/spec`, `/plan`, `/build`, `/test`, `/review`, `/code-simplify`, `/ship`). | Guide + accelerator entrypoints (`guide-*`, `autoplan`, `ship`, `ship-slice`) plus durable planning docs. |
| `/ship` shape | Parallel fan-out orchestrator (code reviewer + security auditor + test engineer) with merged go/no-go. | Backlog resolver and one-slice routing/checkpoint flow; PR/deploy ownership intentionally external. |
| Reusability target | Cross-project coding discipline pack. | Repo-governed planning/execution system with strong traceability. |

## What Transfers Well To Sirius

1. **Clear command contract**
   Keep user-facing steps simple (for example, two primary commands) while
   preserving internal ownership boundaries.
2. **Orchestration-first docs**
   Explicitly document "what this command runs automatically" versus "where it
   stops and asks".
3. **Parallel specialist reviews**
   Consider optional parallel review fan-out as an enhancement around
   `review-execution` or pre-commit checkpoints, without replacing execution
   owners.

## What Should Not Be Copied Directly

1. Replacing durable artifact truth with chat/session-only workflow state
2. Removing planning/execution owner boundaries (`guide-planning`,
   `guide-execution`, lifecycle metadata writers)
3. Turning `ship` into a deployment/PR command that bypasses current repo-native
   planning traceability model

## Two-Step UX Implication

`agent-skills` validates that users prefer a small set of lifecycle commands.
For `sirius-skills`, this supports making:

1. `autoplan` the primary planning command
2. post-approval `ship` the primary execution command

while still keeping internal owner skills and artifact invariants intact.

## Main Sources

- `andyosmali-agent-skills/README.md`
- `andyosmali-agent-skills/AGENTS.md`
- `andyosmali-agent-skills/.claude/commands/plan.md`
- `andyosmali-agent-skills/.claude/commands/build.md`
- `andyosmali-agent-skills/.claude/commands/ship.md`
- `skills/autoplan/SKILL.md`
- `skills/autoplan/scripts/autoplan.py`
- `skills/ship/SKILL.md`
- `skills/ship/scripts/ship.py`
- `skills/ship-slice/SKILL.md`
- `skills/ship-slice/scripts/ship_slice.py`
