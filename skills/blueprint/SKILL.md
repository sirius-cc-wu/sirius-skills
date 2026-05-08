---
name: blueprint
description: Produces an actionable implementation plan from a completed brief, including required PlantUML detailed design diagrams.
---

# Blueprint

Use this skill to convert `brief.md` into a concrete `blueprint.md`.
For new slices, `blueprint.md` is the final execution artifact before implementation begins.
When `.skills/execution.json` sets `auto_start_implementation` to `true`, the blueprint handoff should continue directly into implementation after the slice is marked `blueprint_ready`.

## Responsibilities

1. Read the active slice's `brief.md` as the slice contract.
2. Produce `<slice_path>/blueprint.md`.
3. Make implementation decisions explicit.
4. Map each brief requirement to execution and validation.
5. Capture at least one slice-scoped detailed design diagram in PlantUML so reviewers can understand the implementation quickly.

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

- Treat `brief.md` as the source of truth for slice intent, expected behavior, and acceptance.
- Do not duplicate large narrative sections from `brief.md`; reference and translate them into implementation detail.
- Use the existing codebase and target module as context.
- Keep file paths concrete where possible.
- Every requirement must map to implementation work.
- Every requirement must map to validation.
- Avoid leaving major design decisions unresolved.
- Use PlantUML as the UML language for the required detailed design diagrams.
- Include at least one slice-scoped detailed design diagram in every blueprint. Choose the simplest class, sequence, state, activity, or component-style view that lets a reviewer understand the slice quickly.
- Keep execution-layer diagrams focused on the active work item rather than the whole feature.
- When the detailed design depends mainly on sequence/activity/state behavior
  across multiple objects or services, include at least one structural
  class/component-style diagram that anchors those interactions.
- Keep depth proportional to implementation risk and complexity, but do not omit diagrams entirely; even simple slices should include the lightest useful diagram that explains the work.

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
7. At least one PlantUML detailed design diagram

## Workflow

1. Resolve the active slice with `guide-execution`.
2. Read `brief.md` and scan the target codebase.
3. Fill `plan-template.md` without recreating the brief narrative.
4. Add at least one PlantUML detailed design diagram, choosing the lightest view that makes the slice understandable quickly; when structure, behavior, or state transitions need extra precision, expand the diagram set and pair sequence-heavy designs with at least one structural class/component-style view.
5. Validate traceability and gates.
6. Update the slice through `guide-execution` when the blueprint is ready.
7. If `auto_start_implementation` is enabled, continue directly into repository implementation work after the handoff; otherwise stop when the plan is actionable and ready for execution.
