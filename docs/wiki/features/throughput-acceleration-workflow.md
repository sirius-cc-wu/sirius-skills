# Throughput Acceleration Workflow

## Snapshot

- Feature: `throughput-acceleration-workflow`
- Status: `implemented` (updated `2026-04-22`)

## What This Feature Establishes

This feature adds an optional accelerator layer above the baseline planning and
execution workflows.

Implemented direction:

- `autoplan` composes planning steps while preserving approval boundaries.
- `ship` remains backlog orchestrator and can emit handoff payloads.
- `ship-slice` is a one-slice finisher for implementation through close/commit.
- `learn` manages durable workflow learnings.
- supplemental runtime artifacts (`.skills/runtime/*`, learnings JSONL) support
  resume/event logging without replacing repository artifacts as source of truth.

## Key Tradeoffs

- Strength: faster end-to-end flow without collapsing ownership boundaries.
- Cost: runtime/checkpoint state adds operational complexity and requires clear
  stale-state reconciliation.
- Strength: all accelerator behavior is optional and config-driven.

## Design Boundary To Preserve

The feature explicitly keeps `ship` independent for core backlog resolution and
positions `ship-slice` as optional delegation, not a required dependency.

## Main Sources

- `docs/features/throughput-acceleration-workflow/discover.md`
- `docs/features/throughput-acceleration-workflow/system-design.md`
- `docs/features/throughput-acceleration-workflow/.planning-meta.json`
