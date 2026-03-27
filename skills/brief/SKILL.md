---
name: brief
description: Creates and validates slice-scoped briefs.
---

# Brief

Use this skill to turn one execution-ready work item into a complete `brief.md`.

## Responsibilities

1. Create or update `<slice_path>/brief.md`.
2. Create or update `<slice_path>/checklists/requirements.md`.
3. Clarify only what is necessary.
4. Validate the brief before handoff.

## Required Outputs

- `<slice_path>/brief.md`
- `<slice_path>/checklists/requirements.md`

Resolve `<slice_path>` through `execution-driver`.

## Artifact Ownership

`brief` owns the content of:

- `<slice_path>/brief.md`
- `<slice_path>/checklists/requirements.md`

`execution-driver` should resolve the active slice and enforce readiness gates, but it should not take over brief authoring that belongs to `brief`.

## Authoring Rules

- Focus on user value, expected behavior, and outcomes.
- Avoid implementation details.
- Use reasonable defaults when details are missing.
- Capture traceability back to the originating story, slice, or tracker slice when available.
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
4. The brief describes one independently valuable work item that fits the active slice
5. Checklist is updated to reflect current status

## Workflow
1. Resolve the active slice with `execution-driver`.
2. Fill `brief-template.md`.
3. Create or update the requirements checklist.
4. Run validation and revise if needed.
5. Stop when the brief is ready for planning.
