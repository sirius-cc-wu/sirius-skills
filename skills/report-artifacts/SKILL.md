---
name: report-artifacts
description: Reports operational workflow state across proposals, features, subfeatures, and slices.
---

# Report Artifacts

Use this skill when a maintainer needs concise, read-only operational summaries
instead of manually inspecting multiple workflow registries.

## Responsibilities

1. Reuse the shared artifact inventory and owner metadata.
2. Normalize one reporting-record shape for proposals, features, subfeatures,
   and slices.
3. Group report output by artifact type, lifecycle status, or parent feature.
4. Surface stale artifacts through an explicit threshold.

## Preferred Input

- no arguments for an overview report
- optional artifact-type filters
- optional grouping and stale-threshold overrides

## Tooling

```bash
# Overview report
python3 skills/report-artifacts/scripts/report_artifacts.py

# Group by lifecycle status
python3 skills/report-artifacts/scripts/report_artifacts.py --group-by status

# Group one artifact type by parent feature
python3 skills/report-artifacts/scripts/report_artifacts.py \
  --artifact-type subfeature \
  --group-by parent

# Emit machine-readable output with a custom stale threshold
python3 skills/report-artifacts/scripts/report_artifacts.py --stale-days 21 --json
```

## Output

- default: grouped human-readable report output
- `--json`: structured summary, groups, and records

Exit behavior:

- `0` when the report succeeds
- `2` for invalid arguments

## Guardrails

- Keep the report read-only; do not regenerate or rewrite artifact files.
- Preserve raw owner statuses and treat staleness as a separate derived signal.
- Reuse existing inventory and metadata readers instead of introducing a second
  workflow state model.
