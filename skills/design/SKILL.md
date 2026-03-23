---
name: design
description: Produces feature-level system design artifacts covering architecture, interfaces, constraints, validation strategy, and PlantUML diagrams.
---

# Design

Use this skill after `discover` when the work needs architecture, integration, or validation decisions before task breakdown.

## Responsibilities

1. Translate project framing into a concrete technical approach.
2. Capture architecture, interfaces, data flow, and constraints.
3. Make major tradeoffs, risks, and assumptions explicit.
4. Define the validation strategy needed before implementation starts.
5. Produce feature-scoped PlantUML diagrams that clarify the system design.

## Required Output

- `<feature_path>/system-design.md`

Optional companion output:

- updates to `<feature_path>/discover.md`
- updates to `<feature_path>/user-stories.md`

## Feature Path Resolution

Resolve `<feature_path>` as `<planning_dir>/<feature-slug>/`.

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.

## Design Rules

- Keep this skill feature-scoped, not task-scoped.
- Focus on decisions that unblock later decomposition and execution.
- Document interfaces, dependencies, and operational constraints clearly.
- Call out risks that should affect task ordering or stop-and-ask gates.
- Use PlantUML as the UML language whenever you include diagrams.
- Include system-design diagrams directly in `system-design.md` with fenced `plantuml` blocks unless a separate adjacent `.puml` file is clearly better.
- Prefer feature-level diagrams such as component, package, sequence, state, or deployment diagrams over low-level implementation detail.

## Workflow

1. Read `discover.md` and any existing feature planning docs.
2. Inspect the relevant codebase or adjacent systems as needed.
3. Write `system-design.md` with architecture, interfaces, constraints, validation notes, and PlantUML system-design diagrams.
4. Refine story boundaries when the design changes implementation shape.
5. Stop when the work is concrete enough for `breakdown`.

## Guardrails

- Do not generate task-scoped `plan.md` or other execution-track artifacts.
- Do not create tracker tasks for vague or unresolved designs.
- If the work is purely UX-focused, use `ui-flow` instead or alongside this skill.
- Do not let feature-level UML drift into task-scoped class-by-class implementation design; that belongs in `plan`.
