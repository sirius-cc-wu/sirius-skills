---
name: blueprint
description: Produces an actionable implementation plan from a completed brief, including PlantUML detailed design when needed.
---

# Blueprint

Use this skill to convert `brief.md` into a concrete `blueprint.md`.
For new slices, `blueprint.md` is the final execution artifact before implementation begins.

## Responsibilities

1. Read the active slice's `brief.md`.
2. Produce `<slice_path>/blueprint.md`.
3. Make implementation decisions explicit.
4. Map requirements to execution and validation.
5. Capture slice-scoped detailed design diagrams in PlantUML when they clarify implementation.

## Required Output

- `<slice_path>/blueprint.md`

Optional sections may cover:
- research notes
- data model notes
- interface notes
- detailed design diagrams
- verification scenarios

Resolve `<slice_path>` through `guide-execution`.

## Artifact Ownership

`blueprint` owns the content of `<slice_path>/blueprint.md`.

`guide-execution` should route into planning and validate readiness, but it should not take over implementation-plan authoring that belongs to `blueprint`.

## Planning Rules

- Use the existing codebase and target module as context.
- Keep file paths concrete where possible.
- Every requirement must map to implementation work.
- Every requirement must map to validation.
- Avoid leaving major design decisions unresolved.
- Use PlantUML as the UML language whenever you include detailed design diagrams.
- Prefer slice-scoped detailed design diagrams such as class, sequence, state, or activity diagrams when they help explain non-trivial implementation work.
- Keep execution-layer diagrams focused on the active work item rather than the whole feature.

## Planning Gates

1. **Architecture / Constraints**
   - stack and structural constraints are explicit

2. **Risk / Compliance**
   - security, retention, and compliance risks are identified

3. **Testability**
   - every requirement has a clear validation path

Failed gates must be fixed or explicitly waived with rationale.

## `blueprint.md` Requirements

`<slice_path>/blueprint.md` must include:

1. Technical context and assumptions
2. Gate outcomes
3. Requirement traceability
4. Ordered execution packets or steps
5. Validation steps
6. Delivery notes for sequencing and risk

## Workflow

1. Resolve the active slice with `guide-execution`.
2. Read `brief.md` and scan the target codebase.
3. Fill `plan-template.md`.
4. Add PlantUML detailed design where structure, behavior, or state transitions need extra precision.
5. Validate traceability and gates.
6. Stop when the plan is actionable and ready for execution.
