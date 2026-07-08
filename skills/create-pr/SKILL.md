---
name: create-pr
description: Creates GitHub pull requests with properly formatted titles. Use when creating PRs, submitting changes for review, or when the user says /pr or asks to create a pull request.
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

If the project defines `.skills/conventions.json`, use it to tighten title generation rules instead of hardcoding tracker behavior into the skill.

- Use `branch_extract_pattern` to extract an ID from the branch when present.
- Use `pr_title_format` when present.
- Use `id_pattern` to validate extracted or user-provided IDs when the project requires one.
- If no ID can be resolved, fall back to a logical scope unless the configured format explicitly requires an ID.
- Do **not** assume Jira or any other tracker unless the config says so.

Example project config:

```json
{
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

1. **Check repository and branch state**:
   ```bash
   git status --short
   git status -sb
   git branch --show-current
   gh repo view --json defaultBranchRef
   ```

   Do not create a PR from a dirty worktree. Ask the user to commit, stash, or discard uncommitted work first.

2. **Resolve the base branch and included commits**:
   - Use an explicit user-provided base branch when given.
   - Otherwise use the GitHub default branch from `gh repo view --json defaultBranchRef`.
   - Fall back to the current upstream merge target only when GitHub metadata is unavailable.
   - Resolve the remote from the current upstream or repository remotes; use `origin` only when that is the correct remote for the branch.
   - Review the included commits and changed files before creating the PR:
     ```bash
     git fetch <remote> --prune
     git log <base-ref>..HEAD --oneline
     git diff --stat <base-ref>...HEAD
     ```
   - Stop if there are no commits ahead of the base branch.

3. **Check branch tracking, push state, and existing PRs**:
   ```bash
   git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
   git rev-list --left-right --count @{upstream}...HEAD
   gh pr list --head <current-branch> --state open --json number,title,url
   ```

   Run the upstream comparison only when an upstream exists. If an open PR already exists for the branch, report it instead of creating a duplicate unless the user explicitly asks for another PR. If the branch has no upstream, push with `git push -u <remote> HEAD`. If it already tracks a remote and is only ahead, use `git push`. If it is behind or diverged, stop and ask before pushing.

4. **Read project-specific conventions**:
   - Read `.skills/conventions.json` when it exists before generating the title.
   - Use `branch_extract_pattern` to extract an ID from the current branch when configured.
   - Use `pr_title_format` when configured.
   - Validate extracted or user-provided IDs with `id_pattern` when configured.
   - If ID validation fails, stop and ask for a corrected ID or explicit title. Do not silently use an invalid ID.
   - If the configured title format requires `{ID}` or `{id}` and no valid ID is available, stop and ask for a valid ID or title.
   - If no configured format requires an ID, fall back to a logical scope from the branch or changed area.

5. **Analyze changes and write the title**:
   - Derive a concise summary from the commits and changed files.
   - Use imperative present tense, capitalize the first letter, and omit the final period.
   - Ensure the title describes the actual PR content, not just the branch name.

6. **Validate project checklists when applicable**:
   - Review relevant project checklists when they exist for the PR scope.
   - Do not create the PR with pending required checklist items unless the user explicitly confirms the exception and the PR body explains it.
   - If no applicable checklist is found, state that instead of blocking the PR.

7. **Prepare and validate the PR body**:
   Create a temporary PR body file outside the repository, or in a gitignored location, with the available file-editing mechanism and pass it with `--body-file`; do not use shell heredocs to construct the body.

   Body file content should include:

   ```text
   ## Description

   Describe what the PR changes and why.

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
   - [ ] I have updated relevant project records
   - [ ] New and existing unit tests pass locally with my changes
   - [ ] I have checked my code and corrected any misspellings
   ```

   Before creating the PR, remove placeholder text, include testing evidence, mention applicable project records, and record any intentional checklist exception.

8. **Create the PR**:
   Use draft mode by default unless the user asks for a ready-for-review PR.

   ```bash
   gh pr create --base <base-branch> --head <current-branch> --draft --title "<title>" --body-file <body-file>
   ```

   After creation, return the PR URL and summarize the base branch, included commits, validation, and draft/ready status.

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

If `.skills/conventions.json` provides stricter conventions, validate against those instead.

Before creating the PR, also confirm:

- The worktree is clean except for intentionally ignored temporary files.
- The base branch and head branch are correct.
- The commit list and diff match the intended PR scope.
- No duplicate open PR exists for the branch unless explicitly requested.
- The PR body has no placeholders and includes testing evidence.
- Draft versus ready-for-review status matches the user request.
