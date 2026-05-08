---
name: design
description: Produces feature-level system-design.md artifacts before breakdown when a feature needs architecture, interface, constraint, failure-handling, or validation decisions captured durably.
---

# Design

Use this skill when a feature needs architecture, integration, interface, operational, or validation decisions captured durably before `breakdown`, whether the input comes from `discover.md`, direct prompting, or current implementation review.

Read these references when relevant:

- `references/system-design-template.md` for the required `system-design.md` structure and quality bar
- `references/behavioral-systems.md` when the feature includes shared state, routing, connection/session reuse, concurrency, retries, recovery, or protocol error mapping
- `references/config-surface-governance.md` when the feature touches configuration, startup, compatibility boundaries, environment injection, or test harness inputs

## Responsibilities

1. Translate project framing into a concrete technical approach.
2. Capture architecture, interfaces, data flow, and constraints.
3. Make major tradeoffs, risks, and assumptions explicit.
4. Define the validation strategy needed before implementation starts.
5. Produce feature-scoped PlantUML diagrams that clarify the system design.
6. Make failure handling, recovery behavior, and concurrency invariants explicit when they materially affect correctness.
7. Reuse existing typed configuration and state carriers before introducing new control surfaces.

## Required Output

- `<feature_path>/system-design.md`

Optional companion output:

- updates to `<feature_path>/discover.md`
- updates to `<feature_path>/user-stories.md`
- `<feature_path>/figures/*.puml` and `<feature_path>/figures/*.svg` when configured for linked SVG output

## Preferred Inputs

- `<feature_path>/discover.md` when present
- optional `<feature_path>/reference-research.md` when present
- `impact-analysis.md` when present
- direct user prompt or backlog context when `discover.md` does not exist
- relevant existing docs, ADRs, or feature notes
- relevant code paths when documenting current implemented behavior

## Feature Path Resolution

Resolve `<feature_path>` as either:

- `<planning_dir>/<feature-slug>/` for canonical feature planning
- `<planning_dir>/<feature-slug>/subfeatures/<subfeature-id>/` for a selected durable subfeature

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.
- If `.skills/planning.json` defines `design_diagram_mode`, honor it. Otherwise default to `embedded`.

## Tooling

```bash
# Scaffold a starter system-design.md for a feature or subfeature
python3 skills/design/scripts/scaffold_design.py "<feature-selector-or-path>"

# Overwrite an existing scaffold deliberately
python3 skills/design/scripts/scaffold_design.py "<feature-selector-or-path>" --force
```

## Design Rules

- Keep this skill feature-scoped, not slice-scoped.
- Focus on decisions that unblock later decomposition and execution.
- Document interfaces, dependencies, and operational constraints clearly.
- Call out risks that should affect slice ordering or stop-and-ask gates.
- Minimize control surfaces: prefer typed structs, parameters, and owned configuration objects over new environment variables, CLI flags, globals, or duplicate compatibility shims.
- Support these entry modes explicitly:
  - discover-led design from existing planning docs
  - prompt-led design when engineers want to start from requirements or chat context
  - current-state design when engineers want to reverse engineer implementation into a reviewable design document
- Prefer explicit section headings over loosely structured prose so reviewers can scan decisions quickly.
- Default to forward-looking design. If the feature is already implemented and the task is to capture current behavior, label it clearly as current-state or implemented design instead of presenting it as pre-implementation intent.
- When implementation and intended design differ, record the delta explicitly so later planning and review do not treat drift as intent.
- When `reference-research.md` exists and affects the chosen approach, preserve
  its borrowing-path decision and tradeoffs in `system-design.md` instead of
  silently re-deriving or replacing them.
- Use PlantUML as the UML language whenever you include diagrams.
- If `design_diagram_mode` is `embedded`, include system-design diagrams directly in `system-design.md` with fenced `plantuml` blocks.
- If `design_diagram_mode` is `linked_svg`, write the PlantUML source files under `<feature_path>/figures/`, generate matching SVGs into the same directory, and link those SVGs from `system-design.md` with relative Markdown image links such as `![Component diagram](figures/component-diagram.svg)`.
- In `linked_svg` mode, keep figure backgrounds explicitly white: set `skinparam backgroundColor white` in PlantUML, and ensure each emitted SVG includes an explicit white canvas rect such as `<rect fill="#FFFFFF" height="100%" width="100%" x="0" y="0"/>` so rendered diagrams do not inherit transparent or dark backgrounds.
- In `linked_svg` mode, do not also embed the same diagram as a fenced `plantuml` block in `system-design.md`.
- Use stable, descriptive figure names such as `component-diagram.puml`, `component-diagram.svg`, `sequence-diagram.puml`, and `sequence-diagram.svg`.
- Prefer feature-level diagrams such as component, package, sequence, state, or deployment diagrams over low-level implementation detail.
- When the feature contains shared mutable state, cache entries, connection/session lifecycles, or cross-boundary protocol translation, include the relevant invariants, state transitions, and error-mapping policy instead of leaving them implicit.
- Before adding a new configuration surface, inspect the parent feature constraints and any existing typed carriers so the design inherits existing ownership unless it records a deliberate delta.
- Process-global inputs such as environment variables or CLI flags belong only at the outermost compatibility boundary and should be converted immediately into typed state.
- Do not introduce multiple control planes for the same value without documenting why the extra surface is required and who owns it.

## Workflow

1. Gather the best available inputs:
   - read `discover.md`, optional `reference-research.md`, `impact-analysis.md`, and existing feature planning docs when present
   - otherwise derive the design from the user prompt, backlog context, and repository context
2. Inspect the relevant codebase or adjacent systems as needed, especially existing interfaces, ownership boundaries, operational constraints, and already-owned configuration/state surfaces.
3. Read `.skills/planning.json` when present to determine whether diagrams stay embedded or are emitted under `<feature_path>/figures/`.
4. Choose the framing mode:
   - planned design for work that is not yet implemented
   - current-state design for documenting existing implemented behavior
5. Write `system-design.md` using the structure in `references/system-design-template.md`, adding the behavioral guidance from `references/behavioral-systems.md` and `references/config-surface-governance.md` when applicable.
   When the packet has no `system-design.md` yet, you may scaffold the file first with `python3 skills/design/scripts/scaffold_design.py <feature-selector-or-path>` and then replace the placeholders with the real design.
6. Add PlantUML system-design diagrams or linked SVG figures, depending on configuration.
7. Refine story boundaries when the design changes implementation shape.
8. Run `python3 skills/guide-planning/scripts/manage_planning.py sync-status <feature-selector> --through design_ready`. If UI flow is required and `ui-design.md` is still missing, treat the blocked transition as a signal to hand off to `ui-flow` before claiming design readiness.
9. Stop when the work is concrete enough for `breakdown`.

## Guardrails

- Do not generate slice-scoped `blueprint.md` or other execution-slice artifacts.
- Do not create execution-ready slices for vague or unresolved designs.
- If the work is purely UX-focused, use `ui-flow` instead or alongside this skill.
- Do not let feature-level UML drift into slice-scoped class-by-class implementation design; that belongs in `plan`.
- Do not treat missing research as a design failure when the feature never
  needed upstream comparison in the first place.
- Do not leave critical behavior such as retry semantics, cache invalidation, ownership scope, or protocol error mapping as undocumented "implementation details" when they shape correctness or operator expectations.
- Do not fail just because `discover.md` is absent; use the best available prompt, backlog, documentation, and code context instead.
