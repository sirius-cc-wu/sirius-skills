---
name: repair-artifacts
description: Previews and repairs active workflow registries from durable directories and valid metadata.
---

# Repair Artifacts

Use this skill when a maintainer needs a conservative remediation path after
audit finds registry or readme drift.

## Responsibilities

1. Reuse the shared inventory to discover active artifact directories.
2. Rebuild normalized registry rows from valid metadata.
3. Preview repair actions and manual follow-up suggestions by default.
4. Apply registry/readme regeneration only when the maintainer explicitly asks.

## Preferred Input

- no arguments for a full dry-run repair plan
- optional artifact-type filters
- `--apply` to perform the selected repair writes

## Tooling

```bash
# Preview a full repair plan
python3 skills/repair-artifacts/scripts/repair_artifacts.py

# Preview selected artifact layers
python3 skills/repair-artifacts/scripts/repair_artifacts.py \
  --artifact-type proposal \
  --artifact-type slice

# Apply the selected repairs
python3 skills/repair-artifacts/scripts/repair_artifacts.py --apply

# Emit machine-readable output
python3 skills/repair-artifacts/scripts/repair_artifacts.py --json
```

## Output

- default: human-readable dry-run or apply summary, plus preview-only repair suggestions
- `--json`: structured actions, suggestions, and skipped artifacts

Exit behavior:

- `0` when the repair plan or apply run succeeds

## Guardrails

- Default to dry-run; do not write unless `--apply` is present.
- Keep apply mode limited to derived registry/readme artifacts.
- Preview metadata or traceability follow-up without guessing or silently rewriting those files.
- Leave malformed metadata as manual follow-up instead of guessing corrections.
- Reuse owner registry writers instead of copying registry formatting logic.
