---
name: archive-artifacts
description: Reports archive candidates and safely archives one closed execution slice at a time.
---

# Archive Artifacts

Use this skill when a maintainer needs an explicit archival step that preserves
durable history without broad cleanup side effects.

## Responsibilities

1. Discover archive candidates across proposals, finalized subfeatures, and
   closed slices.
2. Keep candidate reporting read-only by default.
3. Archive one closed execution slice explicitly through the execution owner
   helper.
4. Reject unsupported non-slice apply requests clearly.

## Preferred Input

- no arguments for archive candidate discovery
- optional artifact-type filtering
- `--artifact-type slice --artifact-id <id> --apply` for slice archival

## Tooling

```bash
# Report archive candidates
python3 skills/archive-artifacts/scripts/archive_artifacts.py

# Filter to one artifact type
python3 skills/archive-artifacts/scripts/archive_artifacts.py --artifact-type proposal

# Archive one closed slice
python3 skills/archive-artifacts/scripts/archive_artifacts.py \
  --artifact-type slice \
  --artifact-id CAM-03-artifact-state-report \
  --apply

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
- Limit v1 apply mode to one closed execution slice at a time.
- Delegate slice archival to the execution owner helper instead of moving slice
  folders directly here.
- Treat proposal and subfeature archival as candidate-only in v1.
