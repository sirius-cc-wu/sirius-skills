---
name: research
description: Captures checked-in reference comparison in a durable local planning artifact and records wiki follow-up status.
---

# Research

Use this skill when a canonical feature or durable subfeature needs explicit
reference-project comparison recorded durably in the repository.

## Responsibilities

1. Resolve exactly one feature or subfeature planning packet.
2. Review the relevant checked-in references, repo docs, and local planning
   packet.
3. Write `<feature_path>/reference-research.md` with the chosen borrowing path.
4. Record whether reusable wiki synthesis was written, skipped as non-reusable,
   or deferred because the wiki layer is absent.
5. When reusable synthesis is written into an existing wiki layer, update one
   focused wiki page plus that wiki root's `index.md` and `log.md`.

## Required Output

- `<feature_path>/reference-research.md`

Resolve `<feature_path>` as either:

- `<planning_dir>/<feature-slug>/`
- `<planning_dir>/<feature-slug>/subfeatures/<subfeature-id>/`

- If `.skills/planning.json` defines `planning_dir`, use that as `<planning_dir>`.
- Otherwise default to `docs/features`.

## Workflow

1. Resolve the target feature or subfeature using the existing planning
   registry.
2. Inspect the relevant checked-in references and the local planning packet.
3. Choose the preferred borrowing path and note lower-priority alternatives.
4. Run the helper with concrete research inputs so the result is written
   deterministically into `reference-research.md`.
5. If a derived wiki root already exists and the conclusion is reusable, record
   `--wiki-status written` plus one focused `--wiki-page` so the helper updates
   that page and the wiki `index.md` / `log.md`.
6. Stop after the local artifact and any requested wiki-layer updates are
   written. Downstream routing into `discover`, `design`, or
   `review-planning` belongs to later workflow steps.

## Tooling

```bash
python3 skills/research/scripts/research.py \
  docs/features/planning-workflow/subfeatures/reference-research-synthesis \
  --question "Which upstream pattern should own durable reference synthesis?" \
  --source "references/build-your-own-openclaw/: tutorial baseline" \
  --source "references/OpenHarness/: stronger workflow ownership patterns" \
  --chosen-reference "references/OpenHarness/" \
  --decision "Borrow the explicit skill-and-artifact pattern while keeping wiki updates optional." \
  --alternative "references/build-your-own-openclaw/: useful background, but too tutorial-shaped as the primary owner" \
  --wiki-status deferred \
  --wiki-note "Local artifact is written first; reusable wiki-page mutation lands in a later slice."
```

If the repository already has a derived wiki root and the reusable synthesis was
written there, record that explicitly and let the helper update the wiki page,
index, and log:

```bash
python3 skills/research/scripts/research.py \
  planning-workflow \
  --question "Which proposal-management pattern should we reuse?" \
  --source "references/proposals/: current baseline" \
  --chosen-reference "references/proposals/" \
  --decision "Reuse the existing proposal lifecycle and extend it with local evidence." \
  --wiki-status written \
  --wiki-page "docs/wiki/concepts/proposal-research-patterns.md"
```

## Guardrails

- Do not create a new planning lifecycle state for research.
- Do not auto-bootstrap a wiki layer when it is absent.
- Do not write wiki pages outside the derived wiki root.
- Do not write to a repository-global scratch file instead of the resolved
  planning packet.
- Do not silently guess across ambiguous scopes; require explicit `--scope`
  when needed.
- Do not absorb downstream discovery, design, or review changes into this skill
  unless the user explicitly asks for those later steps.
