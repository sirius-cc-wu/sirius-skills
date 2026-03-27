---
name: commit
description: Use this skill when requested to commit changes. It ensures commit messages follow project standards and ensures code quality via verification steps.
---

# Commit Skill

This skill guides the process of committing code changes to the repository, ensuring consistency, quality, and adherence to project standards.

## Workflow

### 1. Verify Staged Changes
Before committing, always verify exactly what is staged.
- Use `git status` and `git diff --staged` (or `get_changed_files`) to review the changes.
- Ensure only relevant changes are staged.

### 2. Quality Assurance
Adhere to the project mandates (e.g. `AGENTS.md`):
- **No Compilation Warnings:** Run build checks (e.g. `cargo check`, `npm run lint`) to ensure the code compiles without warnings.
- **Tests Pass:** Ensure all relevant tests pass.

### 3. Crafting the Commit Message
Follow these standards for all commit messages:

- **Default Summary Line:** Use the format `scope: summary`.
    - **Scope:** Mandatory. Use the crate name or module name (e.g., `api`, `core`).
    - **Summary:** A concise, imperative summary of the change (e.g., "Refactor service handlers").
- **Body (Optional but Recommended):** A bulleted list of specific changes or a brief explanation of *why* the changes were made.

### 3a. Optional Project-Specific Conventions
If the project defines `.skills/conventions.json`, follow that configuration instead of assuming the default format.

- Use `commit_format` when it is present.
- Common placeholders are `{ID}`, `{scope}`, and `{summary}`.
- If the configured format requires an ID, resolve it from:
  1. the current branch using `branch_extract_pattern`,
  2. the active execution slice ID, or
  3. direct user input.
- Do **not** assume Jira, Azure DevOps, or any issue tracker unless the project config explicitly opts in.

Example project config:

```json
{
  "issue_sliceer": "jira",
  "branch_extract_pattern": "^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
  "commit_format": "{ID}: {summary}"
}
```

### 4. Executing the Commit
Use a message file and `git commit -F` when preparing a multi-line message.

```bash
cat > /tmp/commit-msg.txt <<'EOF'
module: Summary line

- Detailed bullet point 1
- Detailed bullet point 2 with `code_snippet`
EOF

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
1. Check staged changes.
2. Run build verification.
3. Commit with crate or module scope.

### Example 2: Configured Ticket-Based Workflow
If `.skills/conventions.json` defines `commit_format` as `{ID}: {summary}` and the branch is `BSP-3313-buffer-fix`, use a title like:

```text
BSP-3313: Fix uds buffer bounds handling
```
