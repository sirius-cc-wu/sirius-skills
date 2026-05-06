---
name: brief
description: Creates and validates lean slice-scoped briefs.
---

# Brief

Use this skill to turn one execution-ready work item into a concise `brief.md`.
`brief` defines the slice contract: what outcome the slice must deliver, how success will be recognized, and what assumptions or dependencies shape the work.
It should stay intentionally lighter than `blueprint`.

## Responsibilities

1. Create or update `<slice_path>/brief.md`.
2. Create or update `<slice_path>/checklists/requirements.md`.
3. Clarify only what is necessary.
4. Validate the brief before handoff.

## Required Outputs

- `<slice_path>/brief.md`
- `<slice_path>/checklists/requirements.md`

Resolve `<slice_path>` through `guide-execution`.

## Artifact Ownership

`brief` owns the content of:

- `<slice_path>/brief.md`
- `<slice_path>/checklists/requirements.md`

`guide-execution` should resolve the active slice and enforce readiness gates, but it should not take over brief authoring that belongs to `brief`.

## What `brief` should capture

Keep `brief.md` focused on the minimum contract needed to guide implementation and later review:

- slice summary and requested outcome
- user value or operational value
- acceptance scenarios
- testable functional requirements
- key assumptions and dependencies
- edge cases that materially affect expected behavior
- traceability back to the originating story, increment, or planned slice

For simple slices, prefer a compact brief that still satisfies the validation gates rather than expanding every section to full detail.

## What `brief` must avoid

Do not turn `brief.md` into a technical plan. Keep these concerns in `blueprint.md` instead:

- architecture decisions
- file or module change plans
- implementation options or tradeoff analysis
- ordered coding steps or execution packets
- low-level technical validation strategy beyond the independent test and acceptance contract

## Authoring Rules

- Focus on user value, expected behavior, and outcomes.
- Avoid implementation details.
- Use reasonable defaults when details are missing.
- Capture traceability back to the originating story, increment, or slice when available.
- Record assumptions explicitly.
- Keep unresolved clarifications to a maximum of 3, and only for critical decisions.
- Prefer concise wording over exhaustive prose.

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

1. Resolve the active slice with `guide-execution`.
2. Fill `brief-template.md` with a lean slice contract.
3. Create or update the requirements checklist.
4. Run validation and revise if needed.
5. Stop when the brief is ready for `blueprint`.
