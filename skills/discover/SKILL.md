---
name: discover
description: Frames a project or feature before implementation by capturing goals, constraints, stakeholders, and initial story candidates.
---

# Discover

Use this skill at the start of a project, capability, or larger feature before system design or slice breakdown begins.

## Responsibilities

1. Clarify the problem, desired outcomes, and non-goals.
2. Capture stakeholders, users, constraints, and assumptions.
3. Identify initial capabilities or story candidates.
4. Produce repository-first planning artifacts without creating execution slices.

## Required Output

- `<feature_path>/discover.md`

Required companion output for canonical features that will continue into planning:

- `<feature_path>/user-stories.md`

Subfeatures do not own a separate story catalog. For subfeatures created by
`add-subfeature`, reference parent feature story IDs in `discover.md` and
`.subfeature-meta.json` instead of creating `<subfeature_path>/user-stories.md`.

For features or subfeatures created by bootstrap tooling, rough context may
exist in `draft.md`. Treat `draft.md` as input only: consume, replace, or
supersede it by authoring the real `discover.md`. Do not mark discovery ready
while only `draft.md` exists.

Older subfeatures may still contain a bootstrap `discover.md` marked by
`<!-- add-subfeature:discover-stub -->`. Replace that stub with the real
discovery packet instead of treating the placeholder as completed discovery.

Treat `user-stories.md` as the default, not the exception, when:

- the feature has multiple capabilities or story candidates
- later `design`, `breakdown`, or `slice-traceability` work is likely
- stable story IDs will help preserve traceability across subfeatures or slices

You may omit feature-level `user-stories.md` only when the discovery target is
genuinely too small or too corrective to benefit from stable story IDs. If you
omit it, record that choice explicitly in `discover.md` so downstream planning
does not have to guess whether the omission was intentional.

Resolve `<feature_path>` from the repository planning layout:

```text
<planning_dir>/<feature-slug>/
```

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.

## Discovery Rules

- Keep product thinking in the repository, not in slice-scoped execution artifacts.
- Record success criteria and constraints explicitly.
- Separate confirmed facts from assumptions and open questions.
- Name candidate stories in a way that later decomposition can preserve traceability.
- When the current feature or subfeature materially reshapes an existing
  workflow or planning surface, record what it supersedes, narrows, removes, or
  deliberately leaves additive and why.
- For workflow-shaping changes, identify any artifact movement or user-facing
  simplification expectations early instead of leaving them for review to infer.
- When `reference-research.md` exists for the current feature or subfeature,
  treat it as durable context for upstream-informed goals, constraints, and
  tradeoffs instead of re-deriving the same comparison in chat.
- Prefer writing explicit sections such as assumptions, resolved decisions,
  open questions, and candidate stories when they materially affect later
  design or breakdown work.

## Discovery quality bar

Prefer explicit headings whenever the feature is large enough to benefit from
them. For most canonical features, `discover.md` should cover:

- the problem and desired outcomes
- repository and reference context
- users, stakeholders, constraints, and risks
- scope boundaries and non-goals
- current workflow baseline and what the feature supersedes or narrows, when
  workflow shape is changing
- assumptions, open questions, and resolved decisions when they matter
- candidate stories and the next planning step

Do not treat that as a rigid required heading list. Small additive subfeatures
may use a reduced form as long as the discovery still gives downstream design
and breakdown enough durable context.

## Recommended `user-stories.md` usage

When the feature is expected to continue into `design` and `breakdown`, create
`user-stories.md` during discovery or immediately afterward. The goal is to
stabilize story IDs early enough that later artifacts do not have to invent
their own mapping.

Prefer:

- stable story IDs such as `FEATURE-001`
- concise user or system intent statements
- acceptance notes that can survive later decomposition
- enough scope to distinguish stories cleanly without turning the file into a
  slice plan

## Workflow

1. Resolve `<feature_path>` from `.skills/planning.json` when `planning_dir` is present; otherwise use `docs/features/<feature-slug>/`, then identify or create the feature planning folder.
2. Inspect the repository, existing docs, optional `reference-research.md`, and
   other relevant context.
3. Read any existing `draft.md` as rough input, then write `discover.md` with
   explicit problem framing, actors, goals, constraints, risks, and next-step
   guidance.
4. For canonical features, create `user-stories.md` with stable story
   identifiers unless the packet is intentionally too small for story-level
   planning; when omitting it, state why in `discover.md`. For subfeatures,
   reference parent story IDs instead of creating a subfeature-local story file.
5. For canonical features, run `sirius manage-planning sync-status <feature-selector> --through discovery_ready` so `.planning-meta.json` records that discovery is complete.
6. For subfeatures under `.../subfeatures/<subfeature-id>/`, do not try to force `discovery_ready` through `manage_planning.py`. Subfeature lifecycle stays in `.subfeature-meta.json`, authored discovery still leaves the raw subfeature at `draft`, and the next owner is typically `assess`.
7. Stop when the work is concrete enough for the next planning owner:
   - canonical feature: `design`
   - subfeature: usually `assess`

## Guardrails

- Do not create slice-scoped execution slices.
- Do not promote proposals into canonical feature folders; use `guide-planning` for that transition first.
- Do not move directly into implementation planning.
- Do not treat a missing `reference-research.md` as a discovery blocker when the
  current planning target does not need research.
- Do not leave downstream planning to infer whether story IDs, workflow
  supersession, or current-baseline assumptions were intentionally omitted.
- If the request is already architecture-focused, hand off to `design`.
