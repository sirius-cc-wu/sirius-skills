---
name: assess
description: Produces change-scoped impact analysis for an existing feature change packet before design or breakdown continues.
---

# Assess

Use this skill after `evolve-feature` when an existing canonical feature has an active change packet and you need explicit impact assessment before change-local design begins.

## Responsibilities

1. Resolve the target canonical feature and selected change packet.
2. Inspect canonical planning artifacts under `docs/features/<feature-slug>/`.
3. Identify affected baseline artifacts, story IDs, planned slice IDs, and increment IDs.
4. Write `impact-analysis.md` inside the selected change packet.
5. Synchronize the discovered impact lists back into `.feature-change-meta.json`.

## Preferred Input

- a canonical feature slug, folder name, or path
- a change ID, folder name, or path inside that feature's `changes/` registry
- optional explicit artifact, story, or slice IDs when the automatic baseline scan needs manual additions

## Required Output

- `<change_path>/impact-analysis.md`
- updated `<change_path>/.feature-change-meta.json`

## Workflow

1. Resolve the active change packet created by `evolve-feature`.
2. Inspect canonical feature docs such as `discover.md`, `system-design.md`, `user-stories.md`, `slice-planning.md`, and `slice-traceability.md`.
3. Write `impact-analysis.md` with baseline files reviewed, candidate affected stories, increments, slices, and impact notes.
4. Persist the discovered artifact, story, and slice lists into the change metadata.
5. Advance the change to `impact_ready` when the artifact is complete.

## Tooling

```bash
# Analyze one feature change and advance it to impact_ready
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
- Keep the analysis tied to the selected change packet, not the canonical feature root.
