---
name: review-planning
description: Reviews discovery, design, and breakdown artifacts for readiness before human approval, planning commit, and execution slice bootstrap, including durable subfeature planning.
---

# Review Planning

Use this skill after `discover`, `design`, or `breakdown` when the planning artifacts need an explicit readiness review before human approval, planning commit, and slice-scoped execution bootstrap.

It applies to both:

- canonical feature planning under `<planning_dir>/<feature-slug>/`
- a selected subfeature under `<planning_dir>/<feature-slug>/subfeatures/<subfeature-id>/`

Read these references when relevant:

- `references/config-surface-governance.md` when the planning touches configuration, startup, compatibility boundaries, environment injection, or test harness inputs

## Responsibilities

1. Review planning artifacts for intent clarity, scope, architecture fit, sequencing, and validation readiness.
2. Identify gaps, contradictions, unresolved risks, or oversized work that would make execution brittle.
3. Feed findings back into the existing planning docs rather than leaving critical decisions in side-channel notes.
4. Confirm whether the work is ready for human approval and later `slice` bootstrap or needs another planning pass first.

## Preferred Input

- `<feature_path>/discover.md`
- optional `<feature_path>/impact-analysis.md` when reviewing a subfeature
- `<feature_path>/system-design.md`
- optional `<feature_path>/ui-design.md`
- `<feature_path>/slice-planning.md`
- `<feature_path>/slice-traceability.md`
- linked backlog context when available

Resolve `<feature_path>` as either:

```text
<planning_dir>/<feature-slug>/
<planning_dir>/<feature-slug>/subfeatures/<subfeature-id>/
```

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.

## Required Output

- updated planning docs under `<feature_path>/`
- explicit review findings or a readiness note recorded in the planning docs

## Review Rules

- Confirm the business intent, constraints, and success criteria are still coherent across the planning artifacts.
- Check that the technical approach matches the stated architecture, repository boundaries, and non-functional constraints.
- Confirm that configuration and state ownership are coherent, especially when subfeatures inherit a parent feature that already defines typed control surfaces.
- Make sure every execution-ready slice is small enough for one execution slice and has a concrete validation path.
- Verify dependencies, sequencing, parallel-safe lanes, and integration checkpoints are explicit where they matter.
- Confirm `slice-traceability.md` keeps one planned slice per row whenever a
  story fans out, so later execution bootstrap can record execution slice IDs
  deterministically.
- Distinguish blocking findings from follow-up improvements so handoff decisions stay clear.
- For subfeatures, review the subfeature-local planning docs against `impact-analysis.md` and the intended child capability rather than treating the parent feature breakdown as the execution backlog.
- For subfeatures, confirm the planned slices represent only the new or amended work required by the subfeature and keep superseded parent slice IDs in notes or dependency references.
- Treat redundant control planes as blocking findings when the planning introduces new env vars, CLI flags, or globals for values that already have an owned typed carrier or documented parent-feature boundary.

## Workflow

1. Resolve whether the review target is canonical feature planning or a selected subfeature.
2. Read the current planning artifacts and any linked backlog context. For subfeatures, also read `impact-analysis.md` and the parent feature context needed to evaluate the child capability.
3. Compare discovery intent, design direction, and breakdown outputs for contradictions or missing handoff details, including duplicate configuration surfaces or parent/subfeature ownership drift.
4. Record findings directly in the planning docs already used by the team. For subfeatures, write those findings back into the subfeature-local docs.
5. Update the affected planning artifacts so the reviewed state is durable.
6. When the outcome is ready for approval, persist the readiness note in the planning docs and run `python3 skills/guide-planning/scripts/manage_planning.py sync-status <feature-selector> --through planning_reviewed --review-note "<readiness note>"`. If blockers remain, leave the metadata status unchanged.
7. Stop when the work is ready for human approval and planning commit, or return it to `discover`, `design`, or `breakdown` as needed.

## Guardrails

- Do not create slice-scoped execution slices directly; stop at reviewed planning and hand off to `slice` only after explicit approval and planning commit.
- Do not commit planning artifacts automatically from review output; the approval checkpoint comes first.
- Do not invent new lifecycle states for review; use findings and explicit readiness notes instead.
- Do not leave blocking review outcomes only in chat or transient notes.
- When reviewing a subfeature, do not move the review outcome into parent-feature `slice-planning.md` or `slice-traceability.md` unless that planning change intentionally belongs in the parent feature docs.
