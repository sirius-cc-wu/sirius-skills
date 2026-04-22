# Wiki Index

This wiki is the repository's synthesized knowledge layer. Read it before
re-deriving answers from raw planning artifacts or upstream references.

It is intentionally separate from `docs/features/`, `docs/proposals/`, and
`slices/`, which remain the canonical planning and execution sources of
truth.

## Features

| Page | Summary | Main sources |
|---|---|---|
| `features/planning-workflow.md` | Baseline planning lifecycle, ownership boundaries, and subfeature evolution map. | `docs/features/planning-workflow/*` |
| `features/execution-workflow.md` | Slice lifecycle model plus implemented multi-slice orchestration synthesis. | `docs/features/execution-workflow/*` |
| `features/installation-and-configuration.md` | Install/config ownership model plus split install mode implications. | `docs/features/installation-and-configuration/*` |
| `features/hierarchical-scope-support.md` | Scope-resolution design for root+nested planning/execution workspaces. | `docs/features/hierarchical-scope-support/*` |
| `features/cross-artifact-management.md` | Cross-artifact maintenance stack and parent-vs-child status delta. | `docs/features/cross-artifact-management/*` |
| `features/workflow-state-consistency.md` | Shared semantic reconciliation model and invariant hardening. | `docs/features/workflow-state-consistency/*` |
| `features/throughput-acceleration-workflow.md` | Optional accelerator layer for faster planning/execution loops. | `docs/features/throughput-acceleration-workflow/*` |

## Concepts

| Page | Summary | Main sources |
|---|---|---|
| `concepts/workflow-ownership-boundaries.md` | Cross-feature synthesis of planning, execution, and maintenance ownership boundaries. | planning/execution/consistency/throughput feature designs |
| `concepts/gstack-ship-reference.md` | Reference comparison of `gstack /ship` vs `sirius-skills ship` and adoptable improvements. | `gstack/ship` + `skills/ship*` |
| `concepts/agent-skills-reference.md` | Reference comparison of Addy Osmani's `agent-skills` and `sirius-skills` workflow model and UX implications. | `agent-skills` + `skills/autoplan*` + `skills/ship*` |
| `concepts/two-step-autonomy-roadmap.md` | Proposed design to run `sirius-skills` in two high-level steps (`autoplan`, then post-approval execution autopilot). | `skills/autoplan*` + `skills/ship*` |

## Notes

- Add feature pages as understanding changes or implementation completes.
- Add concept pages only when multiple feature pages need the same
  cross-cutting synthesis.
