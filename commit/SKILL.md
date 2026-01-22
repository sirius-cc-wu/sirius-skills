---
name: commit
description: Use this skill when requested to commit changes. It ensures commit messages follow project standards, follows the operational policy for character encoding (escaping backticks), and ensures code quality via verification steps.
---

# Commit Skill

This skill guides the process of committing code changes to the repository, ensuring consistency, quality, and adherence to the project's operational policies.

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

- **Summary Line:** Use the format `[Scope/ID]: [summary]`.
    - **Scope/ID:** Mandatory. Extract from the branch name (e.g., `123`, `feature`) or use a logical scope (e.g., `api`, `core`).
    - **Summary:** A concise, imperative summary of the change (e.g., "Refactor service handlers").
- **Body (Optional but Recommended):** A bulleted list of specific changes or a brief explanation of *why* the changes were made.
- **Character Encoding (CRITICAL):**
    - **NEVER** use emoji characters.
    - **ALWAYS escape backticks (`) with a backslash (\)`** if they include inline code, filenames, or any other content that uses backticks.
    - Example: `Update \`src/lib.rs\` to fix a bug.`

### 4. Executing the Commit
Run the `git commit` command with the crafted message.

```bash
git commit -m "Summary line

- Detailed bullet point 1
- Detailed bullet point 2 with escaped backticks: \`code_snippet\`"
```

## Examples

### Example 1: Refactoring a Service
**Request:** "Commit the changes where I refactored the module."
**Action:**
1. Check staged changes.
2. Run build verification.
3. Commit with extracted ID or scope.
