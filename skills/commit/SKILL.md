---
name: commit
description: Use this skill when requested to commit changes. It ensures commit messages follow project standards and ensures code quality via verification steps.
---

# Commit Skill

This skill guides the process of committing code changes to the repository, ensuring consistency, quality, and adherence to project standards.

## Workflow

### 1. Verify Staged Changes
Before committing, always verify exactly what is staged and what remains outside the commit.
- Use `git status`, `git diff --staged`, and `git diff --name-only --staged` to review the staged changes.
- Use `git diff` and `git status` to notice unstaged or untracked work without modifying it.
- Use `git log --oneline -10` to align the commit message with recent repository style.
- Ensure only relevant changes are staged.

### 2. Quality Assurance
Adhere to the project mandates (e.g. `AGENTS.md`):
- **Build and lint checks:** Run the repository's documented build, lint, type-check, or equivalent validation commands when available.
- **Tests pass:** Run the tests relevant to the staged changes. If no applicable validation command exists, state that explicitly before committing.
- **Formatter safety:** If you need to run a formatter or fixer before commit, scope it to the intended file set when the tool supports path arguments. If the formatter rewrites files outside that intended set, stop and treat that as spillover instead of silently committing unrelated cleanup.

### 3. Crafting the Commit Message
Follow these standards by default:

- **Default Summary Line:** Use the format `scope: summary`.
    - **Scope:** Mandatory. Use the crate name or module name (e.g., `api`, `core`).
    - **Summary:** A concise, imperative summary of the change (e.g., "Refactor service handlers").
- **Body (Optional but Recommended):** Start with a brief explanation of *why* the changes were made, then add a bulleted list of specific changes.
- **Prefer rationale over inventory:** Lead with the intent, tradeoffs, or reason the change exists, not just a second copy of the diff.
- **Good body content:** motivation, behavior change, constraints, compatibility notes, or why a refactor was necessary.
- **Avoid weak bodies:** bare file lists, vague "updated code" text, or a restatement of the summary line.

Examples:

```text
core: simplify retry handling

Reduces duplicate retry logic so backoff behavior stays consistent across API
and worker flows.
```

```text
ui: tighten empty-state copy

Clarifies the no-data state so users understand the page is waiting for input,
not broken.
```

### 3a. Optional Project-Specific Conventions
If the project defines `.skills/conventions.json`, follow that configuration instead of assuming the default format.

- Use `commit_format` when it is present.
- Common placeholders are `{ID}`, `{scope}`, and `{summary}`.
- If the configured format requires an ID, resolve it from:
  1. the current branch using `branch_extract_pattern`,
  2. direct user input.
- If `id_pattern` is present, validate any extracted or user-provided ID against it.
- Do **not** assume Jira, Azure DevOps, or any issue tracker unless the project config explicitly opts in.

Example project config:

```json
{
  "id_pattern": "^[A-Z][A-Z0-9]*-[0-9]+$",
  "branch_extract_pattern": "^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
  "commit_format": "{ID}: {summary}"
}
```

### 4. Executing the Commit
Use a message file and `git commit -F` when preparing a multi-line message. In agent workflows, create the message file with the available file-editing mechanism instead of shell heredocs when repository guidance forbids shell file writes.

Message file content for `/tmp/commit-msg.txt`:

```text
module: Summary line

- Explain why the change exists.
- Mention important behavior, compatibility, or validation notes.
```

Commit command:

```bash
git commit -F /tmp/commit-msg.txt
rm -f /tmp/commit-msg.txt
```

Fallback only when needed:

```bash
git commit -m 'module: Summary line' -m '- Detail bullet point'
```

## Examples

### Example 1: Refactoring a Service
**Request:** "Commit the changes where I refactored the module."
**Action:**
1. Inspect `git status`, `git diff --staged`, `git diff`, and recent commit style.
2. Run the repository's relevant documented verification commands.
3. Commit only the intended staged changes with crate or module scope.

### Example 2: Configured Ticket-Based Workflow
If `.skills/conventions.json` defines `commit_format` as `{ID}: {summary}` and the branch is `BSP-3313-buffer-fix`, use a summary line like:

```text
BSP-3313: Fix uds buffer bounds handling
```
