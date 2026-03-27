---
name: review-planning
description: Reviews discovery, design, and breakdown artifacts for readiness before execution slice bootstrap.
---

# Review Planning

Use this skill after `discover`, `design`, or `breakdown` when the planning artifacts need an explicit readiness review before bootstrapping slice-scoped execution slices.

## Responsibilities

1. Review planning artifacts for intent clarity, scope, architecture fit, sequencing, and validation readiness.
2. Identify gaps, contradictions, unresolved risks, or oversized work that would make execution brittle.
3. Feed findings back into the existing planning docs rather than leaving critical decisions in side-channel notes.
4. Confirm whether the work is ready for `slice` or needs another planning pass first.

## Preferred Input

- `<feature_path>/discover.md`
- `<feature_path>/system-design.md`
- optional `<feature_path>/ui-design.md`
- `<feature_path>/slice-planning.md`
- `<feature_path>/slice-traceability.md`
- linked backlog context when available

Resolve `<feature_path>` from the repository planning layout:

```text
<planning_dir>/<feature-slug>/
```

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.

## Required Output

- updated planning docs under `<feature_path>/`
- explicit review findings or a readiness note recorded in the planning docs

## Review Rules

- Confirm the business intent, constraints, and success criteria are still coherent across the planning artifacts.
- Check that the technical approach matches the stated architecture, repository boundaries, and non-functional constraints.
- Make sure every execution-ready slice is small enough for one execution slice and has a concrete validation path.
- Verify dependencies, sequencing, parallel-safe lanes, and integration checkpoints are explicit where they matter.
- Distinguish blocking findings from follow-up improvements so handoff decisions stay clear.

## Workflow

1. Read the current planning artifacts and any linked backlog context.
2. Compare discovery intent, design direction, and breakdown outputs for contradictions or missing handoff details.
3. Record findings directly in the planning docs already used by the team.
4. Update the affected planning artifacts so the reviewed state is durable.
5. Stop when the work is ready for `slice` or return it to `discover`, `design`, or `breakdown` as needed.

## Guardrails

- Do not create slice-scoped execution slices directly; hand off to `slice` when ready.
- Do not invent new lifecycle states for review; use findings and explicit readiness notes instead.
- Do not leave blocking review outcomes only in chat or transient notes.
