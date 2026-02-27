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

- **Summary Line:** Use the format `[scope]: [summary]`.
    - **Scope:** Mandatory. Use the crate name or module name (e.g., `api`, `core`).
    - **Summary:** A concise, imperative summary of the change (e.g., "Refactor service handlers").
- **Body (Optional but Recommended):** A bulleted list of specific changes or a brief explanation of *why* the changes were made.

### 4. Executing the Commit
Use a message file and `git commit -F` when preparing a multi-line message.

```bash
cat > /tmp/commit-msg.txt <<'EOF'
[module]: Summary line

- Detailed bullet point 1
- Detailed bullet point 2 with `code_snippet`
EOF

git commit -F /tmp/commit-msg.txt
rm -f /tmp/commit-msg.txt
```

Fallback only when needed:

```bash
git commit -m '[module]: Summary line' -m '- Detail bullet point'
```

## Examples

### Example 1: Refactoring a Service
**Request:** "Commit the changes where I refactored the module."
**Action:**
1. Check staged changes.
2. Run build verification.
3. Commit with crate or module scope.
