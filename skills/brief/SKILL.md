---
name: brief
description: Creates optional slice-scoped clarification briefs for legacy or ambiguous execution slices.
---

# Brief

Use this skill only when a slice needs a standalone clarification artifact before
technical planning, or when maintaining legacy slices that already use
`brief.md` and `brief_ready`.

For new normal slices, put the slice contract directly in `blueprint.md` and
route draft slices to `blueprint` instead of requiring `brief.md` first.

## Responsibilities

1. Create or update `<slice_path>/brief.md`.
2. Clarify only what is necessary.
3. Validate the brief before handoff.

## Required Outputs

- `<slice_path>/brief.md`
- legacy only: `<slice_path>/checklists/requirements.md`

Resolve `<slice_path>` through `guide-execution`.

## Artifact Ownership

`brief` owns the content of:

- `<slice_path>/brief.md`

`checklists/requirements.md` is legacy-only. Do not create it for new slices;
required checks belong in `blueprint.md`.

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
2. Fill `brief-template.md` with only the clarification needed before planning.
3. For legacy slices only, update the requirements checklist if it already exists.
4. Run validation and revise if needed.
5. Stop when the clarification is ready for `blueprint`.
