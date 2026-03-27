# Discover: Planning Workflow

## Problem

The repository offers a planning-layer workflow, but its value is distributed across multiple skills, scripts, templates, and methodology docs. Teams need a durable way to frame feature work, capture design decisions, and decompose repository stories into execution-ready slices without collapsing directly into slice-scoped execution slices.

## Goals

- Keep feature-level intent, scope, and architecture in repository artifacts.
- Route work through explicit planning readiness states before execution bootstrap.
- Preserve clear ownership boundaries between planning artifacts and execution artifacts.
- Produce planning outputs that are concrete enough for later review and slice bootstrap.

## Non-Goals

- Manage slice-scoped execution artifacts such as `brief.md` or `blueprint.md`.
- Replace the execution tracker with planning metadata.
- Encode tracker-specific behavior directly into the core planning skills.

## Primary Actors

- Feature lead starting a new planning folder.
- Technical designer producing feature architecture.
- Breakdown owner converting stories into slices and increments.
- Planning reviewer validating readiness for execution handoff.
- Slice tracker owner receiving execution-ready work items.

## Constraints

- Planning docs default to `docs/features/<feature-slug>/` unless `.skills/planning.json` overrides `planning_dir`.
- `planning-driver` owns planning readiness state only.
- `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, and `slice` must stay feature-scoped.
- Increments belong in planning artifacts, not execution-slice state.
- Core skills should remain generic-first and tracker-agnostic.

## Confirmed Signals in Repo

- `skills/planning-driver/scripts/manage_planning.py` manages planning registry and `.planning-meta.json`.
- `skills/discover/SKILL.md` defines `discover.md` as the starting artifact.
- `skills/design/SKILL.md` defines `system-design.md` with PlantUML diagrams.
- `skills/breakdown/SKILL.md` and its templates define `slice-planning.md` and `slice-traceability.md`.
- `README.md` and `SKILLS_METHODOLOGY.md` describe a planning-layer workflow ahead of execution.

## Success Criteria

- A maintainer can initialize a feature folder and move it through discovery, design, and breakdown with durable state.
- Planning artifacts are detailed enough that `review-planning` can assess them without side-channel context.
- Breakdown outputs produce execution-ready slices and demonstrable increments without inventing execution-slice state.

## Risks and Open Questions

- The boundary for when `ui-flow` is required still depends on user judgment.
- Story sizing and breakdown quality are guided by docs more than strict tooling enforcement.
- Planning review findings are durable only if maintainers feed them back into the repository artifacts.
