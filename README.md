# sirius-skills

`sirius-skills` is a generic-first skill collection for spec-driven development, planning, implementation support, and repository workflows.

## Installing skills

Use the repository `Makefile` to register the managed skill set:

```bash
make install
```

To remove the same managed skill set later:

```bash
make uninstall
```

The intended direction is:

- keep core workflow skills reusable across personal and company projects
- express project-specific conventions through local configuration
- isolate domain or company logic in project-local extensions instead of hardcoding it into the base skills

## Generic-first workflow

These core skills should remain tracker-agnostic by default:

- `skills/commit/`
- `skills/create-pr/`
- `skills/define/`
- `skills/planning-driver/`
- `skills/execution-driver/`
- `skills/plan/`
- `skills/review-planning/`
- `skills/review-execution/`
- `skills/close-track/`

If a project has no extra configuration, these skills should still work with generic conventions.

For the operational guide to using the skills together, see `SKILLS_METHODOLOGY.md`.

## Planning layer

For repositories that use repo-first planning and a separate execution tracker, the recommended short-name planning skills are:

- `skills/planning-driver/`
- `skills/discover/`
- `skills/design/`
- `skills/ui-flow/`
- `skills/breakdown/`
- `skills/review-planning/`
- `skills/track/`

These skills sit **before** the execution-track skills:

- planning layer: `planning-driver`, `discover`, `design`, `ui-flow`, `breakdown`, `review-planning`, `track`
- execution layer: `execution-driver`, `define`, `plan`, `review-execution`, `close-track`
- execution tracker: your task system or issue tracker

Recommended boundary:

- keep goals, design, stories, decomposition, and increment plans in repo documents
- keep executable tasks and dependency tracking in your task system
- bootstrap one execution track per executable task
- let `planning-driver` own feature-planning readiness and routing inside the planning layer
- let `execution-driver` own track readiness, while the execution tracker owns task execution state

Feature-local planning defaults to `docs/features/<feature-slug>/` unless
`.skills/planning.json` defines a different `planning_dir`.

Preferred repo workflow:

1. `planning-driver` resolves the feature planning folder, validates planning readiness, and routes to the right planning skill.
2. `discover` creates problem framing and initial story candidates.
3. `design` turns that into architecture, interfaces, and risks.
4. `ui-flow` adds optional UX or screen-flow artifacts.
5. `breakdown` turns repo stories into directly executable work items and groups those slices into small demonstrable increments.
6. `review-planning` reviews planning artifacts and task definitions before task-scoped track bootstrap.
7. `track` bootstraps a task-scoped execution track and hands off to `execution-driver`.
8. `execution-driver` routes task-scoped execution through `define` to capture task intent and acceptance, then through `plan` to produce the final execution artifact.
9. `review-execution` checks implementation and validation outcomes against the task-scoped execution artifacts before closure.
10. `close-track` closes completed execution tracks and can optionally publish a project-local summary.

In the repo-native flow, `planning-driver` owns feature-planning readiness and routing, `breakdown` owns repo-story decomposition, `review-planning` owns planning readiness review, `define` owns the task-scoped `brief.md`, `plan` owns the final task-scoped execution plan and validation checklist, and `review-execution` owns the final implementation-versus-brief review before closure.

Execution follows the same pattern: `execution-driver` owns routing, readiness, and registry state, while `define`, `plan`, `review-execution`, and `close-track` own their artifacts and outputs.

By default, new execution tracks are created under `tracks/` unless `.skills/execution.json` overrides the location.

When UML diagrams are useful, use **PlantUML**:

- `design` should produce feature-scoped system-design diagrams in `system-design.md`
- `plan` should produce task-scoped detailed-design diagrams in `plan.md`

## Execution track source of truth

The `execution-driver` workflow now keeps three complementary artifacts in sync:

- `<track_dir>/README.md` for a human-readable registry
- `<track_dir>/registry.json` for machine-readable registry/state
- `<track_path>/.track-meta.json` for per-track lifecycle metadata such as `created_at`, `updated_at`, and `closed_at`

The machine-readable metadata can also store explicit cross-track relations such as `supersedes`, `invalidates`, `narrows`, and `replaces_partially`, with reciprocal backlinks and optional soft selectors for story titles, requirement IDs, or freeform selectors.

Closed tracks are retained in place. `sirius-skills` does not merge or delete the original `brief.md`/`plan.md` artifacts when a track closes; instead it records closure durably and leaves project-specific publishing or rollup logic to local extensions.

If a project wants a canonical rollup document, `skills/close-track/` can optionally publish closed-track summaries into a project-local history file such as `docs/track-history.md`, driven by explicit command arguments or `.skills/plugins/spec-publish.json`.

The published entry can include:

- backlinks to the retained `brief.md` / `plan.md` artifacts, plus any legacy `tasks.md`
- explicit relation summaries such as which older track or story scope is superseded
- source issue links when `.track-meta.json` and `.skills/conventions.json` provide them
- implementation verification highlights inferred from `plan.md` and any legacy `tasks.md`

For a starting point, see `skills/close-track/assets/spec-publish.example.json`.

To keep relation metadata healthy over time, `skills/execution-driver/scripts/manage_execution.py` also provides `audit-relations`, which checks for missing targets and missing reciprocal links.
## Optional project configuration

Projects can add `.skills/planning.json` in the repository root to configure planning-layer layout.

Example:

```json
{
  "planning_dir": "planning/features"
}
```

Projects can add `.skills/conventions.json` in the repository root to describe their local conventions.

Projects can add `.skills/execution.json` in the repository root to configure execution-track layout for `execution-driver`.

Example:

```json
{
  "track_dir": "tracks",
  "preferred_workflow": "TDD"
}
```

Example:

```json
{
  "issue_tracker": "jira",
  "id_pattern": "^[A-Z][A-Z0-9]*-[0-9]+$",
  "branch_extract_pattern": "^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
  "commit_format": "{ID}: {summary}",
  "pr_title_format": "{ID}: {summary}",
  "issue_url_template": "https://jira.example.com/browse/{ID}"
}
```

Current Phase 1 usage:

- planning-layer skills resolve `<feature_path>` from `.skills/planning.json` field `planning_dir` when the file is present, otherwise they default to `docs/features/<feature-slug>/`
- `skills/planning-driver/scripts/manage_planning.py` reads `.skills/planning.json` for `planning_dir` and maintains planning readiness metadata under `<feature_path>/.planning-meta.json`
- `skills/breakdown/scripts/scaffold_breakdown.py` uses `.skills/planning.json` field `planning_dir` during scaffolding when the file is present
- `skills/execution-driver/scripts/manage_execution.py` reads `.skills/execution.json` for `track_dir` and `preferred_workflow`
- `skills/execution-driver/scripts/manage_execution.py` uses `branch_extract_pattern` during `add` when the file is present
- `skills/commit/SKILL.md` documents how `commit_format` can override the generic default
- `skills/create-pr/SKILL.md` documents how `pr_title_format`, `branch_extract_pattern`, and `id_pattern` can define stricter PR conventions

If the file is absent, the generic defaults remain in effect.

## Project-local extensions

Use `.skills/plugins/` as the project-local area for company or domain add-ons.

Important: this is currently a **convention**, not an automatically loaded plugin system. Nothing in `sirius-skills` scans or executes `.skills/plugins/` by itself today.

Current usage model:

- put project-local helper configs or scripts in `.skills/plugins/`
- have a specific skill or script read them explicitly
- document that behavior in the relevant skill

Today, the project-local files that are actually consumed automatically are `.skills/planning.json`, `.skills/conventions.json`, and `.skills/execution.json`.

Examples:

- `.skills/plugins/jira-validator.json`
- `.skills/plugins/jira-backlog-analyzer.py`
- `.skills/plugins/iso14229-reviewer.py`

Example of how to use the convention today:

- a future `create-pr` implementation could read `.skills/plugins/jira-validator.json`
- a future `review-pr` or `review-bsp-uds-code` implementation could import `.skills/plugins/iso14229-reviewer.py`
- a future planning skill could read `.skills/plugins/jira-backlog-analyzer.py`

Core skills should only rely on these extensions when a project explicitly opts in. This keeps `sirius-skills` reusable while still allowing company overlays.
