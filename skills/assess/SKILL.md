---
name: assess
description: Produces subfeature-scoped impact analysis for a durable child feature before design or breakdown continues.
---

# Assess

Use this skill after `add-subfeature` when an existing canonical feature has a
selected durable subfeature and you need explicit impact assessment before
subfeature-local design begins.

## Responsibilities

1. Resolve the target parent feature and selected subfeature.
2. Inspect parent planning artifacts under `docs/features/<feature-slug>/`.
3. Identify affected baseline artifacts, story IDs, planned slice IDs, and increment IDs.
4. Write `impact-analysis.md` inside the selected subfeature folder.
5. Synchronize the discovered impact lists back into `.subfeature-meta.json`.

## Preferred Input

- a parent feature slug, folder name, or path
- a subfeature ID, folder name, or path inside that feature's `subfeatures/` registry
- optional explicit artifact, story, or slice IDs when the automatic baseline scan needs manual additions

## Required Output

- `<subfeature_path>/impact-analysis.md`
- updated `<subfeature_path>/.subfeature-meta.json`

## Workflow

1. Resolve the active subfeature created by `add-subfeature`.
2. Inspect parent feature docs such as `discover.md`, `system-design.md`, `user-stories.md`, `slice-planning.md`, and `slice-traceability.md`.
3. Write `impact-analysis.md` with baseline files reviewed, candidate affected stories, increments, slices, and impact notes.
4. Persist the discovered artifact, story, and slice lists into the subfeature metadata.
5. Advance the subfeature to `impact_ready` when the artifact is complete.

## Tooling

```bash
# Analyze one subfeature and advance it to impact_ready
python3 skills/assess/scripts/analyze_impact.py "checkout" "replace-legacy-flow"

# Add manual impact hints when needed
python3 skills/assess/scripts/analyze_impact.py \
  "checkout" "replace-legacy-flow" \
  --story-id "CHK-299" \
  --slice-id "CHK-902" \
  --affected-artifact "docs/features/checkout/user-stories.md"
```

## Guardrails

- Do not use this skill for net-new canonical features; use `discover` for those.
- Do not treat impact analysis as execution-slice planning.
- Do not overwrite an existing `impact-analysis.md` unless the user is deliberately regenerating it.
- Keep the analysis tied to the selected subfeature, not the parent feature root.
