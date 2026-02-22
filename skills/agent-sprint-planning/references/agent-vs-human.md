# Agent vs Human Sprint Planning

## Core difference

Human sprint planning is communication-first.
Agent sprint planning is execution-first.

## Planning unit

- Human: user stories and team tasks, often open to interpretation.
- Agent: execution packets with strict scope and explicit commands.

## Definition of Done

- Human: often includes qualitative language and review judgment.
- Agent: must be machine-checkable with concrete pass/fail commands.

## Dependencies

- Human: managed through meetings and social coordination.
- Agent: encoded directly as graph edges and blocker fields.

## Risk handling

- Human: tacitly handled by senior engineers during implementation.
- Agent: pre-declared stop gates and escalation triggers in plan artifacts.

## Throughput model

- Human: bounded by calendar and meeting overhead.
- Agent: bounded by context window, tool latency, and verification cycles.

## Re-planning cadence

- Human: sprint ceremonies (daily standup, mid-sprint adjustments).
- Agent: continuous micro-loop after each verification checkpoint.

## Recommended rule

If a task cannot be verified by a command or concrete artifact check, it is not agent-ready.
