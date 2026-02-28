---
name: simplify
description: Use this skill as a branch/PR cleanup pass to simplify recent code changes, remove code smells, and improve readability while preserving behavior.
---

# Simplify

Run this skill before opening a pull request or while refining an active pull request. It is a focused refactor pass over branch diffs and nearby context.

## When To Use

- "Run /simplify."
- "Make the code change, then simplify."
- "Clean up this PR before review."
- "Simplify this branch before I open a PR."
- "Simplify this branch with the current PR feedback."
- "Refactor this without changing behavior."

## Workflow

1. Inspect branch or PR scope first
- Review branch diff against base (or PR diff/comments if a PR exists).
- Prioritize recently changed files and review-critical paths before broad rewrites.

2. Lock behavior and constraints
- Identify invariants and external contracts that must stay stable.
- Check project conventions in `CLAUDE.md` (or closest equivalent guidance file) and align to them.

3. Apply targeted simplifications
- Remove duplicate or dead code.
- Remove commented-out or temporary "vibe-coding" artifacts.
- Inline single-use variables when clarity improves.
- Simplify nested conditionals and complex boolean expressions.
- Reduce unnecessary abstraction introduced during implementation.

4. Validate no behavior change
- Run relevant tests/lint/type checks for touched scope.
- If no tests exist for risky logic, add minimal focused tests before finalizing.

5. Produce PR-ready summary
- State what was simplified, what behavior was preserved, and what checks were run.
- If PR feedback exists, map simplifications to feedback themes.

## Guardrails

- Preserve external behavior unless the user explicitly asks for behavior changes.
- Keep scope tight to branch/PR diff unless the user requests broader cleanup.
- Avoid broad stylistic churn unrelated to simplification goals.
- If a simplification trades off extensibility, call it out explicitly.

## Output Checklist

1. Files/areas simplified (centered on branch/PR diff).
2. Simplifications applied (dedupe, conditional cleanup, inline/removal).
3. Invariants preserved.
4. Verification commands and outcomes.
