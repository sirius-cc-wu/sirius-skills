---
name: design
description: Produces feature-level system design artifacts covering architecture, interfaces, constraints, validation strategy, and PlantUML diagrams.
---

# Design

Use this skill after `discover` when the work needs architecture, integration, or validation decisions before slice breakdown.

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
- `<feature_path>/figures/*.puml` and `<feature_path>/figures/*.svg` when configured for linked SVG output

## Feature Path Resolution

Resolve `<feature_path>` as either:

- `<planning_dir>/<feature-slug>/` for canonical feature planning
- `<planning_dir>/<feature-slug>/subfeatures/<subfeature-id>/` for a selected durable subfeature

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.
- If `.skills/planning.json` defines `design_diagram_mode`, honor it. Otherwise default to `embedded`.

## Design Rules

- Keep this skill feature-scoped, not slice-scoped.
- Focus on decisions that unblock later decomposition and execution.
- Document interfaces, dependencies, and operational constraints clearly.
- Call out risks that should affect slice ordering or stop-and-ask gates.
- Use PlantUML as the UML language whenever you include diagrams.
- If `design_diagram_mode` is `embedded`, include system-design diagrams directly in `system-design.md` with fenced `plantuml` blocks.
- If `design_diagram_mode` is `linked_svg`, write the PlantUML source files under `<feature_path>/figures/`, generate matching SVGs into the same directory, and link those SVGs from `system-design.md` with relative Markdown image links such as `![Component diagram](figures/component-diagram.svg)`.
- In `linked_svg` mode, do not also embed the same diagram as a fenced `plantuml` block in `system-design.md`.
- Use stable, descriptive figure names such as `component-diagram.puml`, `component-diagram.svg`, `sequence-diagram.puml`, and `sequence-diagram.svg`.
- Prefer feature-level diagrams such as component, package, sequence, state, or deployment diagrams over low-level implementation detail.

## Workflow

1. Read `discover.md`, `impact-analysis.md` when present, and any existing feature planning docs.
2. Inspect the relevant codebase or adjacent systems as needed.
3. Read `.skills/planning.json` when present to determine whether diagrams stay embedded or are emitted under `<feature_path>/figures/`.
4. Write `system-design.md` with architecture, interfaces, constraints, validation notes, and PlantUML system-design diagrams or linked SVG figures, depending on configuration.
5. Refine story boundaries when the design changes implementation shape.
6. Stop when the work is concrete enough for `breakdown`.

## Guardrails

- Do not generate slice-scoped `blueprint.md` or other execution-slice artifacts.
- Do not create execution-ready slices for vague or unresolved designs.
- If the work is purely UX-focused, use `ui-flow` instead or alongside this skill.
- Do not let feature-level UML drift into slice-scoped class-by-class implementation design; that belongs in `plan`.
