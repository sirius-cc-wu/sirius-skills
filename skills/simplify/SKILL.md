---
name: simplify
description: Simplify branch/PR changes without altering behavior; use before opening a PR, while refining one, or after review feedback.
---

# Simplify

Run this skill as a focused cleanup pass on branch/PR diffs.

Read these references when relevant:

- `references/config-surface-governance.md` when the diff touches configuration, startup, compatibility boundaries, environment injection, or test harness inputs

## Workflow (3 phases, 3 perspectives)

1. Phase 1: Scope

- Start with `git diff HEAD` (or PR diff/comments).
- Focus on changed files and critical paths.
- Lock invariants/contracts and follow `AGENTS.md`.
- When the diff touches startup, configuration, compatibility, or tests, inspect the governing planning docs first so the cleanup pass preserves the intended ownership of configuration and state.

2. Phase 2: Review

- **Code Reuse:** duplicate logic, missed helper/utility reuse, dead code.
- **Code Quality:** redundant state, parameter sprawl, copy-paste variants, leaky abstractions, stringly types.
- **Efficiency:** unnecessary `await`/work, missed parallelization, hot-path bloat, TOCTOU, memory leaks, overly broad operations.
- **Architecture fit / control surfaces:** redundant env vars, CLI flags, singleton reads, or compatibility shims when an existing typed owner already exists.
- Keep only actionable findings in changed scope.

3. Phase 3: Fix and verify

- Apply high-signal fixes; skip false positives/low-value items.
- Preserve external behavior unless asked otherwise.
- When simplifying only part of a Rust diff, check for other dirty Rust files
  before formatting. If unrelated Rust work is already dirty, prefer
  `rustfmt <touched-files>` over repo-wide `cargo fmt`.
- Run relevant tests/lint/type checks for touched scope.
- End with a short summary of fixes, skips, and checks (or confirm code is already clean).

## Guardrails

- Preserve external behavior unless the user explicitly asks for behavior changes.
- Keep scope tight to branch/PR diff unless the user requests broader cleanup.
- Avoid broad stylistic churn unrelated to simplification goals.
- If a simplification trades off extensibility, call it out explicitly.
- Treat new process-global configuration surfaces as suspicious unless they are required by an external compatibility boundary and converted immediately into typed state.
- If the diff adds another way to configure an existing value, prefer collapsing it into the already-owned typed configuration surface.

## Output Checklist

1. Files/areas simplified.
2. Changes by perspective (reuse, quality, efficiency, architecture fit).
3. Invariants preserved and skipped items.
4. Verification commands and outcomes.
