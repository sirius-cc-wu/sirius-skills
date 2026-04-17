---
name: audit-artifacts
description: Audits proposals, features, subfeatures, and slices for drift, missing files, broken links, and planning-versus-execution mismatches.
---

# Audit Artifacts

Use this skill when a maintainer needs one read-only view of artifact health
across proposals, canonical features, durable subfeatures, and execution slices.

## Responsibilities

1. Inventory the current proposal, planning, subfeature, and slice artifacts.
2. Reuse existing owner-script validators where available.
3. Surface registry drift, missing required files, invalid metadata, broken
   cross-artifact links, planning-to-execution handoff drift, subfeature
   traceability drift, and slice relation problems.
4. Emit findings without mutating repository artifacts.

## Preferred Input

- no arguments for a full audit
- optional artifact-type filtering when the user only wants one layer

## Tooling

```bash
# Audit all supported artifact types
python3 skills/audit-artifacts/scripts/audit_artifacts.py

# Limit the audit to selected artifact types
python3 skills/audit-artifacts/scripts/audit_artifacts.py \
  --artifact-type proposal \
  --artifact-type slice

# Emit machine-readable output
python3 skills/audit-artifacts/scripts/audit_artifacts.py --json
```

## Output

- default: grouped human-readable findings
- `--json`: structured findings with summary counts

Interpret warnings as audit evidence, not automatic state promotion:

- closed execution slices under a subfeature can mean its planning metadata is
  stale
- that does not mean the parent feature is fully implemented unless the rest of
  the feature artifacts agree

Exit behavior:

- `0` when no findings are present
- `3` when findings are present
- `2` for runtime or usage errors

## Audit Coverage

The first version audits:

- proposal registry and proposal metadata
- top-level planning registry plus canonical feature folders
- feature-local subfeature registries plus subfeature folders
- planning-to-execution handoff consistency for canonical features
- subfeature `slice-traceability.md` execution links versus actual slice state
- stale subfeature status or `affected_slice_ids` when all traced execution
  slices are already closed
- execution slice registry, slice metadata, and slice relation health

## Guardrails

- Keep the audit read-only; do not repair or rewrite registries or metadata.
- Reuse owner-script validation logic instead of copying lifecycle rules into a
  second state machine.
- Surface metadata read failures as findings instead of crashing on the first
  malformed artifact.
- Treat this skill as the inspection layer; repair, report, trace, and archive
  behaviors belong to their own capabilities.
