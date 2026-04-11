---
name: trace-artifacts
description: Traces durable lineage across proposals, features, subfeatures, planned slices, and execution slices.
---

# Trace Artifacts

Use this skill when a maintainer needs one read-only lineage view across
proposal staging, canonical planning, durable subfeatures, planned slices, and
execution slices.

## Responsibilities

1. Inventory the current repo artifacts through the shared artifact inventory.
2. Parse durable slice lineage from `slice-traceability.md` without rewriting it.
3. Build a typed lineage graph for proposals, features, subfeatures,
   planned slices, and execution slices.
4. Emit either a targeted lineage result or a broader lineage summary.

## Preferred Input

- no arguments for a full lineage summary
- `--artifact-type` and `--artifact-id` for a targeted lineage query

## Tooling

```bash
# Summarize the current lineage graph
python3 skills/trace-artifacts/scripts/trace_artifacts.py

# Trace one artifact
python3 skills/trace-artifacts/scripts/trace_artifacts.py \
  --artifact-type subfeature \
  --artifact-id replace-legacy-flow

# Trace one planned or execution slice
python3 skills/trace-artifacts/scripts/trace_artifacts.py \
  --artifact-type planned-slice \
  --artifact-id CAM-02-trace-artifact-lineage
python3 skills/trace-artifacts/scripts/trace_artifacts.py \
  --artifact-type slice \
  --artifact-id CAM-02-trace-artifact-lineage

# Emit machine-readable lineage output
python3 skills/trace-artifacts/scripts/trace_artifacts.py --json
```

## Output

- default: human-readable node and edge lineage
- `--json`: structured nodes, edges, and summary counts

Exit behavior:

- `0` when the trace succeeds
- `2` for missing targets, runtime errors, or invalid arguments

## Lineage Coverage

The first version traces:

- proposal links to target and promoted features
- subfeature links to parent features
- feature- or subfeature-local planned slice lineage from `slice-traceability.md`
- planned-slice to execution-slice lineage from `slice-traceability.md`
- execution slice relations stored in `.slice-meta.json`

## Guardrails

- Keep the trace read-only; do not repair or rewrite repo artifacts.
- Reuse owner-script metadata and the shared inventory instead of copying
  workflow state into a second state model.
- Only emit lineage edges supported by durable repo signals.
- Treat this skill as the lineage layer; audit, reporting, repair, and archive
  behaviors belong to their own capabilities.
