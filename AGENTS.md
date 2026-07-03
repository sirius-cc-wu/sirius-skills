# AGENTS.md

Default guidance for agents working in `sirius-skills`.

## Repo Shape

`sirius-skills` has three main areas:

- `skills/`: reusable skill definitions and helper scripts
- `.github/`: repository guidance for GitHub tooling
- `docs/wiki/`: synthesized, durable knowledge pages derived from repo artifacts
- top-level docs and install helpers such as `README.md`, `SKILLS_METHODOLOGY.md`, and `Makefile`

## External References

Use these upstream repositories as reference inputs when their patterns are
relevant to current work:

Local tooling note:
- `http://127.0.0.1:8080` hosts a reachable PlantUML server for diagram rendering during local work.
- When writing UML, validate correctness by checking the diagram against the local PlantUML server when practical.

- `gstack`
  - upstream: `https://github.com/garrytan/gstack`
  - local sibling clone (when present): `../gstack/`
- `agent-skills` (Addy Osmani)
  - upstream: `git@github.com:addyosmani/agent-skills.git`
- `treehouse`
  - upstream: `git@github.com:kunchenguid/treehouse.git`
  - local submodule: `references/treehouse/`

Treat them as references, not source-of-truth replacements for this repo's
artifact ownership and workflow boundaries.

The `references/` tree is for checked-in upstream reference inputs only. Do not
write implementation changes, planning artifacts, generated docs, or workflow
state inside `references/`; copy or synthesize relevant lessons into this
repo's owned surfaces instead.

## Core Rules

### Keep shared skills generic

Core skills should stay reusable across projects. Do not hardcode company
trackers, naming rules, or domain logic unless the repo explicitly documents
that behavior.

### Prefer configuration to hardcoding

Project-specific behavior should normally live in:

- `.skills/planning.json`
- `.skills/conventions.json`
- `.skills/execution.json`
- `.skills/plugins/`

If you add configurable behavior, document the config surface and preserve a
useful generic default.

When bootstrap scaffolds a wiki, keep the wiki root aligned with the planning
layout: derive it from the parent directory of `planning_dir` (for example,
`docs/features` -> `docs/wiki`, `planning/features` -> `planning/wiki`) instead
of hardcoding `docs/wiki` for every repository.

When documenting or demonstrating first-time repository setup for
`sirius-skills`, treat `bootstrap` as the starting step and request wiki
scaffolding in the same run so `.skills/` config, the derived wiki root, and
the related `AGENTS.md` guidance land together from the start.

### Keep wiki content synthesized

Treat the wiki as a maintained knowledge layer, not as planning state or a
replacement for canonical workflow artifacts.

Rules:

- keep feature-planning and execution truth in `docs/features/`, `docs/proposals/`, and `slices/`
- keep `docs/wiki/index.md` content-oriented with discoverable page summaries
- keep `docs/wiki/log.md` append-only and chronological using `## [YYYY-MM-DD] operation | subject`
- prefer feature-scoped synthesis pages under `docs/wiki/features/`
- use `docs/wiki/concepts/` for cross-cutting knowledge shared by multiple features
- capture conclusions, tradeoffs, and deltas; do not copy raw source text into wiki pages

### Preserve ownership boundaries

Do not mix workflow responsibilities:

- `guide-planning` owns planning readiness and registry state
- `guide-execution` owns execution-slice readiness and registry state
- the execution layer owns slice lifecycle state within the repository

Do not duplicate registry states inside execution-slice artifacts.

### Treat IDs as opaque

Do not assume IDs are dates or sequence numbers. If a helper defines an ID
algorithm, follow that helper. Preserve manual IDs exactly.

### Keep docs aligned with behavior

When you change a skill or helper:

- update the relevant `SKILL.md`
- update any top-level docs that describe the behavior
- remove stale examples in the same change when practical

### Reconcile before archive

When a feature or subfeature has completed all planned slices and is about to be
archived:

- reconcile the final implementation against the canonical `system-design.md`
- record that review durably in an `execution-reconciliation` block inside
  `system-design.md`
- do not archive closed slices until that reconciliation block declares
  `Status: aligned` and names the reviewed planned slice IDs

### Prefer backward-compatible changes

Favor additive changes, compatibility shims, and normalization over abrupt
breaking changes. If you must break behavior, document it clearly.

### Prefer action-oriented skill names

Use short, imperative skill names by default.

Rules:

- prefer a verb when one clear verb exists
- prefer short names over long noun phrases
- use verb-noun forms only when the noun is needed for clarity, such as `add-subfeature` or `close-slice`
- avoid noun-only skill names when the skill is performing an action

Examples:

- good: `propose`, `discover`, `design`, `assess`
- acceptable when needed: `add-subfeature`, `guide-planning`, `review-planning`
- avoid for skill names: `proposal`, `impact-analysis`

Artifact and storage names may stay noun-based when they describe durable
repository objects rather than actions.

Examples:

- `docs/proposals/`
- `proposal_dir`
- `impact-analysis.md`
- `.proposal-meta.json`

### Keep workflow naming boundaries clear

- skills should sound like actions an agent takes
- files, directories, registries, and metadata should sound like objects the workflow stores

## Working In This Repo

### Skills

Each skill should live in its own directory and usually include:

- `SKILL.md`
- any scripts or assets the skill references

When editing skills:

- keep instructions explicit and actionable
- do not document behavior the repo does not actually implement
- prefer simple interfaces over clever indirection

### Installation

Use `just install` and `just uninstall` for the supported packaged workflow.
`just install-packaged` and `just uninstall-packaged` remain explicit aliases to
the same packaged path.

Packaged installs use the centralized `sirius` CLI and shared Python support
under `src/sirius_skills/lib/`. When a skill needs shared runtime behavior,
import it from the package instead of copying runtime folders into the skill.

Keep repo-level guidance agent-agnostic unless a specific integration requires
otherwise.

## Agent Checklist

- Read the nearest `README.md`, `SKILL.md`, and nested `AGENTS.md` before
  changing behavior.
- Keep edits small and aligned with the repo's generic-first design.
- If you change config semantics, update docs and examples together.
- If you touch `guide-execution`, keep `slices/`, registry behavior, and `.skills/`
  configuration consistent.
