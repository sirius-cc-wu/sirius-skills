---
name: discover
description: Frames a project or feature before implementation by capturing goals, constraints, stakeholders, and initial story candidates.
---

# Discover

Use this skill at the start of a project, capability, or larger feature before system design or task breakdown begins.

## Responsibilities

1. Clarify the problem, desired outcomes, and non-goals.
2. Capture stakeholders, users, constraints, and assumptions.
3. Identify initial capabilities or story candidates.
4. Produce repository-first planning artifacts without creating execution tracks.

## Required Output

- `<project_path>/discover.md`

Optional companion output:

- `<project_path>/user-stories.md`

If the repository uses the standard planning layout, prefer:

```text
doc/specs/projects/<project-slug>/
```

## Discovery Rules

- Keep product thinking in the repository, not in the execution tracker.
- Record success criteria and constraints explicitly.
- Separate confirmed facts from assumptions and open questions.
- Name candidate stories in a way that later decomposition can preserve traceability.

## Workflow

1. Identify or create the project planning folder.
2. Inspect the repository, existing docs, and relevant context.
3. Write `discover.md` with problem framing, actors, goals, constraints, and risks.
4. If helpful, draft an initial `user-stories.md` with stable story identifiers.
5. Stop when the work is concrete enough for `design`.

## Guardrails

- Do not create task-scoped execution tracks.
- Do not move directly into implementation planning.
- If the request is already architecture-focused, hand off to `design`.
