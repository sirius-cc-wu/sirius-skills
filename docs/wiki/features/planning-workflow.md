# Planning Workflow

## Snapshot

- Feature: `planning-workflow`
- Status: `planning_reviewed` (updated `2026-03-24`)
- Canonical scope: feature-scoped planning artifacts in `docs/features/<feature>/`

## What This Feature Establishes

`planning-workflow` defines the planning-layer lifecycle and ownership model:

- `guide-planning` owns planning readiness and planning registry updates.
- Authoring skills (`discover`, `design`, `ui-flow`, `breakdown`) own content artifacts.
- `slice` is the planning-to-execution handoff boundary.
- `implemented` is a planning metadata state, not an execution slice state.

The design keeps planning and execution concerns split while preserving a durable
planning packet that can be reviewed independently.

## Current Child Capability Map

| Subfeature | Status | Synthesis |
|---|---|---|
| `proposal-workflow` | `planning_reviewed` | Keeps speculative work in `docs/proposals/` until explicit promotion. |
| `subfeature-workflow` | `planning_reviewed` | Adds durable nested `subfeatures/` packets under an existing feature. |
| `change-to-subfeature-migration` | `planning_reviewed` | Defines deterministic migration from legacy `changes/` packets to `subfeatures/`. |
| `reference-research-synthesis` | `implemented` | Adds explicit research artifacts and reusable wiki synthesis without new planning states. |

## Key Tradeoffs

- Strength: explicit planning gates and durable artifacts make reviews auditable.
- Cost: semantic quality is still mostly review-driven rather than strongly
  enforced by strict schema validation.
- Strength: proposal and subfeature extensions avoid flattening all work into a
  single feature folder.

## Notable Delta

The parent feature remains `planning_reviewed` while one child capability
(`reference-research-synthesis`) is already `implemented`. The repo currently
uses child capabilities as the practical evolution path while parent packets
continue to describe the baseline planning model.

## Main Sources

- `docs/features/planning-workflow/discover.md`
- `docs/features/planning-workflow/system-design.md`
- `docs/features/planning-workflow/.planning-meta.json`
- `docs/features/planning-workflow/subfeatures/README.md`
- `docs/features/planning-workflow/subfeatures/*/{discover.md,system-design.md,.planning-meta.json}`
