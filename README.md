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
- `skills/close-track/`

If a project has no extra configuration, these skills should still work with generic conventions.

## Spec track source of truth

The `spec-driver` workflow now keeps three complementary artifacts in sync:

- `<spec_dir>/README.md` for a human-readable registry
- `<spec_dir>/registry.json` for machine-readable registry/state
- `<track_path>/.track-meta.json` for per-track lifecycle metadata such as `created_at`, `updated_at`, and `closed_at`

The machine-readable metadata can also store explicit cross-track relations such as `supersedes`, `invalidates`, `narrows`, and `replaces_partially`, with reciprocal backlinks and optional soft selectors for story titles, requirement IDs, or freeform selectors.

Closed tracks are retained in place. `sirius-skills` does not merge or delete the original `spec.md`/`plan.md` artifacts when a track closes; instead it records closure durably and leaves project-specific publishing or rollup logic to local extensions.

If a project wants a canonical rollup document, `skills/close-track/` can optionally publish closed-track summaries into a project-local history file such as `docs/spec-history.md`, driven by explicit command arguments or `.skills/plugins/spec-publish.json`.

The published entry can include:

- backlinks to the retained `spec.md` / `plan.md` / `tasks.md` artifacts
- explicit relation summaries such as which older track or story scope is superseded
- source issue links when `.track-meta.json` and `.skills/identity.json` provide them
- implementation verification highlights inferred from `plan.md` and `tasks.md`

For a starting point, see `skills/close-track/assets/spec-publish.example.json`.

To keep relation metadata healthy over time, `skills/spec-driver/scripts/manage_specs.py` also provides `audit-relations`, which checks for missing targets and missing reciprocal links.

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
