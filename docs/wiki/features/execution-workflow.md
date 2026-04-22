# Execution Workflow

## Snapshot

- Feature: `execution-workflow`
- Status: `planning_reviewed` (updated `2026-03-24`)
- Canonical scope: slice-scoped execution under `slices/`

## What This Feature Establishes

`execution-workflow` defines a one-slice-at-a-time lifecycle:

- `guide-execution` owns slice readiness states and registry transitions.
- `brief` and `blueprint` own execution intent and plan artifacts.
- `review-execution` and `close-slice` own closure quality and durable closeout.
- Closure is non-destructive; historical context remains available for later
  audit and archival tooling.

## Current Child Capability Map

| Subfeature | Status | Synthesis |
|---|---|---|
| `multi-slice-execution` | `implemented` | Adds `ship` orchestration to traverse planned slices sequentially while preserving one active slice and one commit checkpoint per completed slice. |

## Key Tradeoffs

- Strength: deterministic slice lifecycle and durable metadata improve
  traceability.
- Cost: throughput can be slower without higher-level orchestration.
- Strength: `multi-slice-execution` improves throughput without replacing
  existing execution owners.

## Notable Delta

The parent packet remains `planning_reviewed`, but its multi-slice child is
`implemented`. In practice, the execution model is baseline single-slice plus an
optional orchestration layer.

## Main Sources

- `docs/features/execution-workflow/discover.md`
- `docs/features/execution-workflow/system-design.md`
- `docs/features/execution-workflow/.planning-meta.json`
- `docs/features/execution-workflow/subfeatures/multi-slice-execution/discover.md`
- `docs/features/execution-workflow/subfeatures/multi-slice-execution/system-design.md`
