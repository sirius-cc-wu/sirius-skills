---
name: plan
description: Produces an actionable implementation plan from a completed spec.
---

# Plan

Use this skill to convert `spec.md` into a concrete `plan.md`.
For new tracks, `plan.md` is the final execution artifact before implementation begins.

## Responsibilities

1. Read the active track's `spec.md`.
2. Produce `<track_path>/plan.md`.
3. Make implementation decisions explicit.
4. Map requirements to execution and validation.

## Required Output

- `<track_path>/plan.md`

Optional sections may cover:
- research notes
- data model notes
- interface notes
- verification scenarios

Resolve `<track_path>` through `spec-driver`.

## Planning Rules

- Use the existing codebase and target module as context.
- Keep file paths concrete where possible.
- Every requirement must map to implementation work.
- Every requirement must map to validation.
- Avoid leaving major design decisions unresolved.

## Planning Gates

1. **Architecture / Constraints**
   - stack and structural constraints are explicit

2. **Risk / Compliance**
   - security, retention, and compliance risks are identified

3. **Testability**
   - every requirement has a clear validation path

Failed gates must be fixed or explicitly waived with rationale.

## `plan.md` Requirements

`<track_path>/plan.md` must include:

1. Technical context and assumptions
2. Gate outcomes
3. Requirement traceability
4. Ordered execution packets or steps
5. Validation steps
6. Delivery notes for sequencing and risk

## Workflow

1. Resolve the active track with `spec-driver`.
2. Read `spec.md` and scan the target codebase.
3. Fill `plan-template.md`.
4. Validate traceability and gates.
5. Stop when the plan is actionable and ready for execution.
