---
name: agent-sprint-planning
description: Plan coding sprints for AI agents using execution packets, machine-checkable Definition of Done, dependency gating, and re-planning loops.
---

# Agent Sprint Planning Skill

Use this skill when the user asks to create or improve sprint planning for coding agents.

## Why this skill exists

Human sprint planning optimizes for team communication and coordination.

Agent sprint planning optimizes for deterministic execution:
- Explicit constraints and scope boundaries
- Small, context-local tasks
- Machine-checkable acceptance and verification commands
- Dependency-aware ordering and parallel work lanes
- Continuous re-planning after each verification cycle

For a concise comparison, see `references/agent-vs-human.md`.
For mode choice and readiness checks, use `assets/mode-comparison-checklist.md`.

## Inputs

Collect or infer the following before drafting the sprint:
1. Sprint objective and hard constraints
2. Codebase boundaries (modules, repos, services)
3. Quality gates (tests, lint, security, performance)
4. Risk class (low/medium/high impact)
5. Execution mode and throughput assumptions (`single-agent` or `multi-agent`)

## Mode selection

Use `single-agent` when:
- Work has a tight critical path.
- Task coupling is high and handoff risk is non-trivial.
- Codebase context is concentrated in one subsystem.

Use `multi-agent` when:
- There are clear parallel lanes with minimal overlap.
- Integration points can be validated with deterministic checks.
- Ownership and handoff boundaries can be explicitly documented.

## Workflow

1. Define sprint objective
- Convert business goals into repository outcomes.
- Name target artifacts (code paths, migrations, docs, PRs).

2. Build execution packets
- Split work into atomic packets using `assets/task-card-template.md`.
- Keep each packet scoped to a small set of files or one subsystem.
- Add exact verification commands per packet.

3. Build dependency graph
- Mark blockers and sequencing constraints.
- Mark safe parallel packets explicitly.
- In `multi-agent` mode, assign each packet an owner and handoff target.

4. Add risk and stop gates
- Add stop-and-ask gates for destructive or high-risk actions:
  - schema/data migrations
  - auth/permission logic
  - public API/contract breaks
  - production config and infrastructure changes

5. Draft sprint board
- Create a sprint plan from `assets/sprint-plan-template.md`.
- Fill all required sections; avoid placeholders in final output.

6. Define re-planning loop
- After each packet: execute, verify, record outcome, and re-plan if needed.
- Split packets that fail repeatedly or exceed context budget.
- In `multi-agent` mode, include an integration checkpoint after each lane completes.

## Definition of Done standard

A packet is complete only if all are true:
1. Required code changes are present.
2. Verification commands pass exactly as specified.
3. Non-functional checks pass (lint/type/security/perf as applicable).
4. Required artifacts are updated (docs, changelog, migration notes).
5. Rollback or mitigation note exists for medium/high risk packets.
6. In `multi-agent` mode, handoff notes are attached for downstream packets.

## Output format

Default output should be a filled sprint board plus packet cards:
1. One sprint board document
2. One task card per packet
3. Explicit dependency and parallelization labels
4. A short "First execution order" list
5. In `multi-agent` mode, lane owners and integration checkpoints

## Guardrails

- Prefer many small packets over a few large stories.
- Never leave acceptance criteria untestable.
- Never use vague DoD language like "looks good".
- Avoid plans that require broad codebase context in a single packet.
- If essential inputs are missing, state assumptions clearly.
