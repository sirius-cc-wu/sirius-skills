---
name: archive-artifacts
description: Reports archive candidates and safely archives closed slices, including feature/subfeature scoped summarize-and-archive flows.
---

# Archive Artifacts

Use this skill when a maintainer needs an explicit archival step that preserves
durable history without broad cleanup side effects.

## Responsibilities

1. Discover archive candidates across proposals, features, subfeatures, and
   closed slices.
2. Keep candidate reporting read-only by default.
3. Archive one closed execution slice explicitly through the execution owner
   helper.
4. Summarize closed slices for one feature or subfeature into `system-design.md`
   before archiving them.

## Preferred Input

- no arguments for archive candidate discovery
- optional artifact-type filtering
- `--artifact-type slice --artifact-id <id> --apply` for one closed-slice archival
- `--artifact-type feature --artifact-id <feature-slug> --apply` to summarize
  and archive all closed planned slices for one feature
- `--artifact-type subfeature --artifact-id <subfeature-id-or-path> --apply` to
  summarize and archive all closed planned slices for one subfeature

## Tooling

```bash
# Report archive candidates
python3 skills/archive-artifacts/scripts/archive_artifacts.py

# Filter to one artifact type
python3 skills/archive-artifacts/scripts/archive_artifacts.py --artifact-type proposal

# Archive one closed slice
python3 skills/archive-artifacts/scripts/archive_artifacts.py \
  --artifact-type slice \
  --artifact-id rpt-artifact-state-report \
  --apply

# Summarize and archive closed slices for one feature
python3 skills/archive-artifacts/scripts/archive_artifacts.py \
  --artifact-type feature \
  --artifact-id execution-workflow \
  --apply

# Summarize and archive closed slices for one subfeature
python3 skills/archive-artifacts/scripts/archive_artifacts.py \
  --artifact-type subfeature \
  --artifact-id audit-artifacts \
  --apply

# Optional: preserve existing structural class/component diagrams too
python3 skills/archive-artifacts/scripts/archive_artifacts.py \
  --artifact-type subfeature \
  --artifact-id audit-artifacts \
  --apply \
  --include-structural-diagrams

# Emit machine-readable output
python3 skills/archive-artifacts/scripts/archive_artifacts.py --json
```

## Output

- default: human-readable candidate summary
- `--json`: structured candidates and optional apply outcome

Exit behavior:

- `0` when the archive command succeeds
- `2` for unsupported or invalid apply requests

## Guardrails

- Keep candidate discovery read-only.
- Delegate slice archival to the execution owner helper instead of moving slice
  folders directly here.
- For feature and subfeature apply mode, summarize slice history into
  `system-design.md` before archiving the targeted closed slices.
- Keep structural-diagram carry-forward opt-in and limited to preserving
  existing class/component-style PlantUML from blueprint or canonical
  `system-design.md`; do not synthesize new diagrams during archive.
- Keep archived slice summaries self-contained inside `system-design.md`; do
  not rely on source or archive path bullets to explain the result.
- Keep archival explicit and scoped; do not bulk archive across unrelated
  features by default.
- Do not treat archival as the default next step when the current user request
  is a new fix, regression, or follow-on capability for the same shipped
  feature; route that case back to `guide-planning`/`add-subfeature` unless the
  user explicitly asked to archive anyway.
