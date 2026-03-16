---
name: create-pr
description: Creates GitHub pull requests with properly formatted titles. Use when creating PRs, submitting changes for review, or when the user says /pr or asks to create a pull request.
allowed-tools: Bash(git:*), Bash(gh:*), Read, Grep, Glob
---

# Create Pull Request

Creates GitHub PRs with clear, descriptive titles.

## PR Title Format

Default format:

```
<ID/Scope>: <summary>
```

### ID/Scope

The ID is extracted from the current branch name or a logical scope is used.

**Examples:**
| Branch Name | ID |
|-------------|----|
| `3916-optimize-init` | `3916` |
| `feature/add-new-feature` | `feature` |
| `fix/memory-leak` | `fix` |

### Optional Project-Specific Conventions

If the project defines `.skills/identity.json`, use it to tighten title generation rules instead of hardcoding tracker behavior into the skill.

- Use `branch_extract_pattern` to extract an ID from the branch when present.
- Use `pr_title_format` when present.
- Use `id_pattern` to validate extracted or user-provided IDs when the project requires one.
- If no ID can be resolved, fall back to a logical scope unless the configured format explicitly requires an ID.
- Do **not** assume Jira or any other tracker unless the config says so.

Example project config:

```json
{
  "issue_tracker": "jira",
  "id_pattern": "^[A-Z][A-Z0-9]*-[0-9]+$",
  "branch_extract_pattern": "^([A-Z][A-Z0-9]*-[0-9]+)-(.+)$",
  "pr_title_format": "{ID}: {summary}"
}
```

### Summary Rules

- Use imperative present tense: "Add" not "Added"
- Capitalize first letter
- No period at the end
- Be concise but descriptive

## Steps

1. **Check current state**:
   ```bash
   git status
   git diff --stat
   git log origin/main..HEAD --oneline
   ```

2. **Determine ID**:
   - Attempt to extract an ID from the current branch name.
   - If no ID is strictly present, use the branch type (feature, fix) or project scope.

3. **Analyze changes** to determine:
   - Summary: What does the change do?

4. **Validate Execution Checklist Completion**:
   - Locate the relevant `tasks.md` (usually in `specs/<ID>-<name>/tasks.md`).
   - For legacy tracks without `tasks.md`, fall back to `plan.md`.
   - Check if all checklist items in the execution artifact are marked as completed (`[x]`).
   - **MANDATORY**: A PR should not be created if there are pending `[ ]` items in `tasks.md` (or the legacy `plan.md`) unless explicitly justified.

5. **Push branch if needed**:
   ```bash
   git push -u origin HEAD
   ```

6. **Create PR** using gh CLI:
   ```bash
   gh pr create --draft --title "${ID}: <summary>" --body "$(cat <<'EOF'
   ## Description

   <Describe what the PR does and how to test. Photos and videos are recommended.>

   ## Type of change

   - [ ] Bug fix
   - [ ] New feature
   - [ ] Improvement
   - [ ] Breaking change

   ## How Has This Been Tested?

   - [ ] Unit tests
   - [ ] Integration tests
   - [ ] Manual testing

   ## Checklist:

   - [ ] My code follows the style guidelines of this project
   - [ ] I have performed a self-review of my own code
   - [ ] I have commented my code, particularly in hard-to-understand areas
   - [ ] I have made corresponding changes to the documentation
   - [ ] I have updated the execution checklist (`tasks.md`, or `plan.md` for legacy tracks)
   - [ ] New and existing unit tests pass locally with my changes
   - [ ] I have checked my code and corrected any misspellings
   EOF
   )"
   ```

## PR Body Guidelines

### Description Section
- Describe what the PR does
- Explain how to test the changes
- Include screenshots/videos for UI changes

### Type of Change
Select the appropriate type:
- Bug fix - Fixes an issue
- New feature - Adds new functionality
- Improvement - Enhances existing functionality
- Breaking change - Changes that break backward compatibility

### Testing Section
Describe how the changes were tested

### Checklist
All items should be addressed before merging

## Validation

When no project-specific format is configured, the PR title should generally match this pattern:
```
^[^:]+: [A-Z].+[^.]$
```

If `.skills/identity.json` provides stricter conventions, validate against those instead.
