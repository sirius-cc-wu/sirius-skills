---
name: configure-project
description: Bootstraps `.skills/planning.json`, `.skills/execution.json`, and `.skills/conventions.json` for a repository. Use when a user asks to configure a project, initialize `sirius-skills` settings, apply generic defaults, or add Jira-oriented conventions.
---

# Configure Project

This skill configures the repository-local `.skills/` files used by `sirius-skills`.

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
- `slice_dir`: `slices`
- `preferred_workflow`: `TDD`

For `jira` mode, use these preset conventions unless the user supplies project-specific values:

- `issue_sliceer`: `jira`
- `id_pattern`: `^[A-Z][A-Z0-9]*-[0-9]+$`
- `branch_extract_pattern`: `^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$`
- `commit_format`: `{ID}: {summary}`
- `pr_title_format`: `{ID}: {summary}`
- `issue_url_template`: `https://jira.example.com/browse/{ID}`

If the user already gave a real Jira URL, use it instead of the placeholder.

### 3. Run the helper script

Use the bundled helper to create or update the files deterministically:

```bash
python3 skills/configure-project/scripts/configure_project.py --mode default
```

Jira mode:

```bash
python3 skills/configure-project/scripts/configure_project.py \
  --mode jira \
  --issue-url-template "https://jira.example.com/browse/{ID}"
```

If the user wants custom planning or execution layout, pass those values too:

```bash
python3 skills/configure-project/scripts/configure_project.py \
  --mode default \
  --planning-dir planning/features \
  --slice-dir specs \
  --workflow TDD
```

### 4. Validate the generated files

After running the helper:

- read back the written JSON files
- confirm the mode-specific values are present
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

In `default` mode, `.skills/conventions.json` may remain an empty object so the repo keeps its generic behavior explicit without inventing tracker-specific rules.

## Examples

### Example 1: Generic setup

Request: "Configure this repo for sirius-skills with the default setup."

Action:

1. Use `default` mode.
2. Apply the default planning and execution directories.
3. Create `.skills/conventions.json` as `{}` when it does not already exist.

### Example 2: Jira setup

Request: "Set this project up with Jira conventions."

Action:

1. Use `jira` mode.
2. Apply the Jira preset fields in `.skills/conventions.json`.
3. Use the real Jira browse URL if the user provided one.

### Example 3: Ambiguous request

Request: "Configure the project."

Action:

1. Use `ask` mode.
2. Ask the user whether they want `default` or `jira`.
3. Only write config after they choose.
