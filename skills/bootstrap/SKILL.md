---
name: bootstrap
description: Bootstraps `.skills/planning.json`, `.skills/execution.json`, and `.skills/conventions.json` for a repository, and can also scaffold a wiki knowledge layer next to the planning feature directory. Use when a user asks to configure a project, initialize `sirius-skills` settings, apply generic defaults, add Jira-oriented conventions, or bootstrap the repo's wiki skeleton.
---

# Bootstrap

This skill configures the repository-local `.skills/` files used by `sirius-skills`.

When requested, it also scaffolds a lightweight wiki layer with `features/`,
`concepts/`, `concepts/architecture/`, `index.md`, and `log.md`. The wiki root
is derived from the parent directory of `planning_dir`, so it stays next to the
feature planning tree. When the target repository already has an `AGENTS.md`,
bootstrap also patches it with a small wiki-architecture guidance block derived
from that same wiki root.

It supports three modes:

- `default`: write the supported config files with generic defaults
- `jira`: write the supported config files plus Jira-oriented conventions
- `ask`: ask the user which mode to use before writing any config

## Mode selection

Choose the mode from the user request:

- If the user explicitly asks for a generic setup, use `default`.
- If the user explicitly asks for Jira support or ticket-based conventions, use `jira`.
- If the user says "configure the project" or is otherwise ambiguous, use `ask` and stop to ask which mode they want.

Do not silently assume Jira. The only time this skill should ask the user to choose a mode is the explicit `ask` path.

## Workflow

### 1. Inspect the current repository config

Read these files when they exist:

- `.skills/planning.json`
- `.skills/execution.json`
- `.skills/conventions.json`

Preserve unrelated keys in existing JSON files. This skill should only update the supported configuration surface it owns.

### 2. Resolve the config values

Use these defaults unless the user asked for different values:

- `planning_dir`: `docs/features`
- `proposal_dir`: `docs/proposals`
- `design_diagram_mode`: `embedded`
- `slice_dir`: `slices`
- `preferred_workflow`: `TDD`
- `auto_start_implementation`: `true`

In both `default` and `jira` mode, seed `.skills/conventions.json` with these
generic slice-ID defaults unless the repo already overrides them:

- `slice_id_style`: `scope_prefix`
- `slice_id_format`: `{scope_prefix}-{capability_slug}`
- `slice_id_scope_precedence`: `subfeature_then_feature`
- `slice_id_prefix_source`: `slug_alias`
- `slice_id_prefix_guidance`: `Use a short lowercase alias derived from the feature or subfeature slug and avoid bare 'slice-*' IDs.`

For `jira` mode, use these preset conventions unless the user supplies project-specific values:

- `id_pattern`: `^[A-Z][A-Z0-9]*-[0-9]+$`
- `branch_extract_pattern`: `^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$`
- `commit_format`: `{ID}: {summary}`
- `pr_title_format`: `{ID}: {summary}`
- `issue_url_template`: `https://jira.example.com/browse/{ID}`

If the user already gave a real Jira URL, use it instead of the placeholder.

If the user also wants a wiki scaffold, derive the wiki root from the parent
directory of `planning_dir`.

Examples:

- `planning_dir = docs/features` -> wiki root `docs/wiki`
- `planning_dir = planning/features` -> wiki root `planning/wiki`

The scaffold layout under that derived root is:

- wiki root: `<planning-parent>/wiki`
- architecture pages: `<planning-parent>/wiki/concepts/architecture`
- feature synthesis pages: `<planning-parent>/wiki/features`
- cross-cutting concept pages: `<planning-parent>/wiki/concepts`
- wiki index: `<planning-parent>/wiki/index.md`
- append-only log: `<planning-parent>/wiki/log.md`
- repository guidance patch: `AGENTS.md` gains or refreshes a bootstrap-managed
  section pointing architecture pages at the derived wiki root when `AGENTS.md`
  already exists

Do not assume the wiki should be created unless the user asked for it.

### 3. Run the helper script

Use the bundled helper to create or update the files deterministically:

```bash
sirius bootstrap --mode default
```

Add `--wiki` when the user also wants the wiki scaffold:

```bash
sirius bootstrap --mode default --wiki
```

Jira mode:

```bash
sirius bootstrap \
  --mode jira \
  --issue-url-template "https://jira.example.com/browse/{ID}"
```

If the user wants custom planning or execution layout, pass those values too:

```bash
sirius bootstrap \
  --mode default \
  --wiki \
  --planning-dir planning/features \
  --proposal-dir planning/proposals \
  --design-diagram-mode linked_svg \
  --slice-dir specs \
  --workflow TDD \
  --auto-start-implementation
```

### 4. Validate the generated files

After running the helper:

- read back the written JSON files
- confirm the mode-specific values are present
- when `--wiki` was used, confirm `<wiki-root>/index.md`,
  `<wiki-root>/log.md`, `<wiki-root>/features/`,
  `<wiki-root>/concepts/architecture/`, and
  `<wiki-root>/concepts/` exist
- when `AGENTS.md` already exists, confirm it now mentions the derived
  `<wiki-root>/concepts/architecture/` path without duplicating the bootstrap
  guidance block on reruns
- summarize the result for the user

If the helper reports invalid existing JSON, surface that error instead of overwriting the file blindly.

## Ask mode

When the request does not choose `default` or `jira`, ask the user which mode to apply before running the helper.

Recommended choices:

- `default`
- `jira`

Once the user chooses, continue with the matching workflow above.

## Output expectations

Successful runs should leave the repository with:

- `.skills/planning.json`
- `.skills/execution.json`
- `.skills/conventions.json`

When `--wiki` is used, successful runs should also leave the repository with:

- `<wiki-root>/index.md`
- `<wiki-root>/log.md`
- `<wiki-root>/features/`
- `<wiki-root>/concepts/architecture/`
- `<wiki-root>/concepts/`
- an updated `AGENTS.md` wiki-architecture section when `AGENTS.md` already
  exists

The generated wiki scaffold is intentionally generic. Bootstrap now adds a small
default `AGENTS.md` guidance block when that file already exists, and
repositories can refine the rest of their wiki rules later without changing the
bootstrap defaults.

When `.skills/planning.json` includes `design_diagram_mode: "linked_svg"`, planning/design skills should place diagram source and generated SVGs under `<feature_path>/figures/`, link the SVGs from `system-design.md`, and keep the figures on an explicit white background using `skinparam backgroundColor white` plus a white SVG canvas rect.

## Examples

### Example 1: Generic setup

Request: "Configure this repo for sirius-skills with the default setup."

Action:

1. Use `default` mode.
2. Apply the default planning and execution directories.
3. Create `.skills/conventions.json` with the generic scope-prefixed slice-ID defaults when it does not already exist.

### Example 2: Default setup with wiki

Request: "Configure this repo for sirius-skills and scaffold the wiki."

Action:

1. Use `default` mode.
2. Run the helper with `--wiki`.
3. Confirm the wiki scaffold uses the directory derived from the parent of
   `planning_dir` (for the default layout, `docs/wiki/features/`,
   `docs/wiki/concepts/`, and `docs/wiki/concepts/architecture/`).
4. Confirm an existing `AGENTS.md` now points architecture pages at the same
   derived wiki root.

### Example 3: Jira setup

Request: "Set this project up with Jira conventions."

Action:

1. Use `jira` mode.
2. Apply the Jira preset fields in `.skills/conventions.json`.
3. Use the real Jira browse URL if the user provided one.

### Example 4: Ambiguous request

Request: "Configure the project."

Action:

1. Use `ask` mode.
2. Ask the user whether they want `default` or `jira`.
3. Only write config after they choose.
