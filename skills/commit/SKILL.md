---
name: commit
description: Commit changes with scoped staging, repo checks, and convention-aware messages.
---

# Commit Skill

Use when the user asks to commit repository changes.

## Workflow

### 1. Review State
- Run `git status`, `git diff`, `git diff --staged`, and `git log --oneline -10`.
- Stage only intended files. Do not include unrelated work or formatter spillover.

### 2. Verify
- Follow repo guidance such as `AGENTS.md`.
- Run relevant build, lint, type-check, or tests when available.
- If no relevant validation exists, state that before committing.

### 3. Write Message
- Default summary: `scope: imperative summary`, e.g. `core: simplify retry handling`.
- When adding a body, start with a brief why, then add bullets for specific changes.
- Avoid vague bodies and restating the summary.

### 4. Apply Conventions
- If `.skills/conventions.json` exists, prefer `commit_format`.
- Supported placeholders: `{ID}`, `{id}`, `{scope}`, `{summary}`.
- When an ID is required, extract it with `branch_extract_pattern` or ask the user.
- Validate IDs with `id_pattern` when configured.
- Do not assume Jira, Azure DevOps, or another tracker unless configured.

### 5. Commit
- For multi-line messages, create a message file with the approved file-editing mechanism and run `git commit -F <file>`.
- Avoid shell heredocs when repo guidance forbids shell file writes.
- Fallback only when needed: `git commit -m 'scope: summary' -m 'Rationale or validation detail'`.

```text
scope: summary

Brief explanation of why the change exists.

- Specific change or behavior update.
- Validation, compatibility, or constraint note.
```
