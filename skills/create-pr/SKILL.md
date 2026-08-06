---
name: create-pr
description: Creates GitHub pull requests with properly formatted titles. Use when creating PRs, submitting changes for review, or when the user says /pr or asks to create a pull request.
---

# Create Pull Request

Open GitHub PRs with the intended base, commits, title, and body.

## Title Rules

Default format: `<ID/Scope>: <summary>`.

Read the applicable `AGENTS.md` files and repository guidance for explicit
branch-identifier extraction, identifier validation, and pull-request title
rules.

- If an ID is invalid, or required but unavailable, stop and ask for a corrected ID or explicit title.
- Do not assume Jira or any other tracker without an explicit repository rule.

When no repository rule requires an ID, use a logical scope from the branch or changed area. Write the summary in imperative present tense, capitalize it, keep it concise, and omit the final period.

## Workflow

1. **Inspect state**:
   ```bash
   git status --short
   git status -sb
   git branch --show-current
   gh repo view --json defaultBranchRef
   ```
   Do not create a PR from a dirty worktree. Ask the user to commit, stash, or discard uncommitted work first.

2. **Resolve base, remote, and scope**:
   - Use an explicit user-provided base when given; otherwise use the GitHub default branch, then the upstream merge target as fallback.
   - Resolve the remote from the current upstream or repository remotes; use `origin` only when correct for the branch.
   - Fetch and review the PR contents:
     ```bash
     git fetch <remote> --prune
     git log <base-ref>..HEAD --oneline
     git diff --stat <base-ref>...HEAD
     ```
   - Stop if there are no commits ahead of the base.

3. **Check push state and duplicates**:
   ```bash
   git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
   git rev-list --left-right --count @{upstream}...HEAD
   gh pr list --head <current-branch> --state open --json number,title,url
   ```
   Run upstream commands only when an upstream exists. If an open PR already exists, report it instead of creating a duplicate unless explicitly requested. If no upstream exists, use `git push -u <remote> HEAD`; if only ahead, use `git push`; if behind or diverged, stop and ask.

4. **Prepare title and checks**:
   - Apply the title rules above after reading the repository guidance.
   - Derive the summary from commits and changed files, not just the branch name.
   - Review relevant project checklists when they exist; do not proceed with pending required items unless the user confirms the exception and the PR body explains it.

5. **Prepare the PR body**:
   Create a temporary body file outside the repository, or in a gitignored location, and pass it with `--body-file`. Do not use shell heredocs to construct the body.

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

   Remove placeholders, include testing evidence, mention relevant project records, and record any intentional checklist exception.

6. **Create the PR**:
   Use draft mode by default unless the user asks for ready-for-review.

   ```bash
   gh pr create --base <base-branch> --head <current-branch> --draft --title "<title>" --body-file <body-file>
   ```

   Return the PR URL plus base branch, included commits, validation, and draft/ready status.

## Validation

When no project-specific format is defined, the title should generally match `^[^:]+: [A-Z].+[^.]$`.

Before creating the PR, confirm the worktree is clean, base/head are correct, commits and diff match scope, no duplicate open PR exists unless requested, the body has no placeholders and includes testing evidence, and draft status matches the user request.
