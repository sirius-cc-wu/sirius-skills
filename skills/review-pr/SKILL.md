---
name: review-pr
description: Review a GitHub pull request with structured five-axis review, present actionable findings for human approval, and optionally post selected comments with Mermaid diagrams.
---

# Review Pull Request

## Role

Orchestrates a read-only pull-request review separating analysis from publication:
1. Analyze the pull request in a read-only context.
2. Present structured findings to the user.
3. Post only user-selected findings to GitHub.

Uses `code-review-and-quality` practices for code review, while managing GitHub PR retrieval, policy checks, user selection, and comment publication. Does not prescribe a specific reviewer or model.

## When to Use

Use when asked to review a pull request (e.g., `Review PR #123`). Do not modify the worktree, branch, or pull request without explicit user consent.

## Workflow

### 1. Establish review context
- Fetch PR metadata, commits, diff, status checks, and existing comments:
  ```bash
  gh pr view <number> --json number,title,body,author,baseRefName,headRefName,commits,files,reviews,comments,statusCheckRollup
  gh pr diff <number>
  gh pr checks <number>
  ```
- Read project `AGENTS.md` and check governing specifications or ADRs.
- Keep operations strictly read-only.

### 2. Run read-only analysis
- Review tests before implementation; verify edge cases, error paths, and regression coverage.
- Evaluate across five dimensions: Correctness, Readability, Architecture, Security, Performance.
- Report only high-conviction, actionable findings backed by file/line evidence. Avoid style nits, speculative concerns, and praise.

### 3. Present findings before publication
Format findings for user review:
- **ID & Severity:** `R1` (`blocker`, `high`, `medium`, `low`).
- **Target:** File and line/range.
- **Details:** Problem, impact, evidence, and concise suggested solution.
- **Mermaid diagram (optional):** Only when it clarifies complex flow or state.

### 4. Ask for publication choices
Prompt the user to select which finding IDs to publish:
- Inline comments on changed lines.
- Summary review comment.
- No publication.

Never publish findings or approve/reject PRs without explicit user confirmation.

### 5. Publish selected comments
- Check existing comments to avoid duplicates.
- Include the review marker in published comments:
  ```text
  <!-- pr-review:<PR-number>:<finding-id> -->
  ```
- Post inline comments via `gh api` and summaries via `gh pr comment` or `gh pr review --comment`.

### 6. Report completion
Summarize:
- PR reviewed and reviewer used.
- Findings presented vs. published (with URLs).
- Unplaced findings or unresolved errors.

## Failure Handling

Stop and report errors if PR details, diff mapping, or write permissions are ambiguous or fail. Never perform unapproved writes.
