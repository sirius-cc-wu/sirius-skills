---
name: measure-artifacts
description: Computes durable implementation metrics for completed features and subfeatures, and can persist a reusable sidecar for later reporting.
---

# Measure Artifacts

Use this skill when a maintainer wants reusable implementation metrics for a
completed feature or subfeature.

## Responsibilities

1. Resolve one completed feature or subfeature packet.
2. Compute story-size, slice-count, execution-mode, and churn-availability
   metrics from durable repository artifacts.
3. Render those metrics as text or JSON.
4. Persist `implementation-metrics.json` only when the caller explicitly asks
   for write mode.

## Preferred Input

- a feature slug, subfeature slug, or planning packet path
- optional `--scope <path>` when nested planning scopes are ambiguous

## Tooling

```bash
python3 skills/measure-artifacts/scripts/measure_artifacts.py <target>
python3 skills/measure-artifacts/scripts/measure_artifacts.py <target> --json
python3 skills/measure-artifacts/scripts/measure_artifacts.py <target> --write
python3 skills/measure-artifacts/scripts/measure_artifacts.py <target> --scope apps/payments
```

## Output

- default: human-readable metrics summary
- `--json`: machine-readable metrics payload plus sidecar path
- `--write`: persist `implementation-metrics.json` beside the target packet

## Guardrails

- Target artifacts must already be completed (`implemented` feature planning or
  finalized subfeature metadata).
- Do not mutate planning or execution owner metadata; only the dedicated metrics
  sidecar may be written.
- Keep unsupported story sizes and missing provenance explicit instead of
  silently guessing values.
- Treat archive-facing metric display as separate follow-on work.
