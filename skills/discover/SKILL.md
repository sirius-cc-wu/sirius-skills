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

Optional companion output:

- `<feature_path>/user-stories.md`

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

## Workflow

1. Resolve `<feature_path>` from `.skills/planning.json` when `planning_dir` is present; otherwise use `docs/features/<feature-slug>/`, then identify or create the feature planning folder.
2. Inspect the repository, existing docs, optional `reference-research.md`, and
   other relevant context.
3. Write `discover.md` with problem framing, actors, goals, constraints, and risks.
4. If helpful, draft an initial `user-stories.md` with stable story identifiers.
5. Run `python3 skills/guide-planning/scripts/manage_planning.py sync-status <feature-selector> --through discovery_ready` so `.planning-meta.json` records that discovery is complete.
6. Stop when the work is concrete enough for `design`.

## Guardrails

- Do not create slice-scoped execution slices.
- Do not promote proposals into canonical feature folders; use `guide-planning` for that transition first.
- Do not move directly into implementation planning.
- Do not treat a missing `reference-research.md` as a discovery blocker when the
  current planning target does not need research.
- If the request is already architecture-focused, hand off to `design`.
