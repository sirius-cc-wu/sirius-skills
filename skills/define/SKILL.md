---
name: define
description: Creates and validates task-scoped specifications.
---

# Define

Use this skill to turn one execution-ready work item into a complete `spec.md`.

## Responsibilities

1. Create or update `<track_path>/spec.md`.
2. Create or update `<track_path>/checklists/requirements.md`.
3. Clarify only what is necessary.
4. Validate the spec before handoff.

## Required Outputs

- `<track_path>/spec.md`
- `<track_path>/checklists/requirements.md`

Resolve `<track_path>` through `spec-driver`.

## Artifact Ownership

`define` owns the content of:

- `<track_path>/spec.md`
- `<track_path>/checklists/requirements.md`

`spec-driver` should resolve the active track and enforce readiness gates, but it should not take over specification authoring that belongs to `define`.

## Authoring Rules

- Focus on user value, expected behavior, and outcomes.
- Avoid implementation details.
- Use reasonable defaults when details are missing.
- Capture traceability back to the originating story, slice, or tracker task when available.
- Record assumptions explicitly.
- Keep unresolved clarifications to a maximum of 3, and only for critical decisions.

## Clarification Protocol

1. Identify missing or ambiguous information.
2. Prioritize by impact.
3. Ask one clarification group at a time.
4. Integrate the answer before moving on.

## Validation Gates

Before handoff, confirm:

1. No implementation leakage
2. Requirements are testable and unambiguous
3. Success criteria are measurable and technology-agnostic
4. The spec describes one independently valuable work item that fits the active track
5. Checklist is updated to reflect current status

## Workflow
1. Resolve the active track with `spec-driver`.
2. Fill `spec-template.md`.
3. Create or update the requirements checklist.
4. Run validation and revise if needed.
5. Stop when the spec is ready for planning.
