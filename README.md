# sirius-skills

`sirius-skills` is a generic-first skill collection for spec-driven development, planning, implementation support, and repository workflows.

The intended direction is:

- keep core workflow skills reusable across personal and company projects
- express project-specific conventions through local configuration
- isolate domain or company logic in project-local extensions instead of hardcoding it into the base skills

## Generic-first workflow

These core skills should remain tracker-agnostic by default:

- `skills/commit/`
- `skills/create-pr/`
- `skills/spec-driver/`
- `skills/specify/`
- `skills/plan/`
- `skills/tasks/`

If a project has no extra configuration, these skills should still work with generic conventions.

## Planning layer

For repositories that use repo-first planning and `sb-tracker` for execution work, the recommended short-name planning skills are:

- `skills/discover/`
- `skills/design/`
- `skills/ui-flow/`
- `skills/breakdown/`
- `skills/track/`

These skills sit **before** the execution-track skills:

- planning layer: `discover`, `design`, `ui-flow`, `breakdown`, `track`
- execution layer: `spec-driver`, `specify`, `plan`, `tasks`
- execution tracker: `sb-tracker`

Recommended boundary:

- keep goals, design, stories, and decomposition in repo documents
- use `sb-tracker` for executable tasks and dependency tracking
- bootstrap one spec track per executable `sb` task
- let `spec-driver` own track readiness, while `sb-tracker` owns task execution state

Preferred repo workflow:

1. `discover` creates problem framing and initial story candidates.
2. `design` turns that into architecture, interfaces, and risks.
3. `ui-flow` adds optional UX or screen-flow artifacts.
4. `breakdown` turns repo stories into directly executable tracker work.
5. `track` bootstraps a task-scoped execution track and hands off to `spec-driver`.
6. `spec-driver` routes task-scoped execution through `specify`, `plan`, and `tasks` as needed.

In the repo-native flow, `breakdown` owns repo-story decomposition and `tasks` owns the final task-scoped, machine-checkable execution checklist.

## Optional project configuration

Projects can add `.skills/identity.json` in the repository root to describe their local conventions.

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

- `skills/spec-driver/scripts/manage_specs.py` uses `branch_extract_pattern` during `add` when the file is present
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

Today, the only project-local file that is actually consumed automatically is `.skills/identity.json`.

Examples:

- `.skills/plugins/jira-validator.json`
- `.skills/plugins/jira-backlog-analyzer.py`
- `.skills/plugins/iso14229-reviewer.py`

Example of how to use the convention today:

- a future `create-pr` implementation could read `.skills/plugins/jira-validator.json`
- a future `review-pr` or `review-bsp-uds-code` implementation could import `.skills/plugins/iso14229-reviewer.py`
- a future planning skill could read `.skills/plugins/jira-backlog-analyzer.py`

Core skills should only rely on these extensions when a project explicitly opts in. This keeps `sirius-skills` reusable while still allowing company overlays.
