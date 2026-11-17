# Playbook 3: Tier 3 Scoped Fix (Prove-It Defect Resolution)

**Trigger:** Defect fix, compiler/linter error, performance tuning, or local lint fix within existing contracts (zero specification or ADR overhead).
**Alpha Progression:** *Work* → *Prepared* & *Concluded*.

## Steps

1. **Frame the Defect**
   - Summarize the bug, failing log, or target fix in a concise 1-paragraph brief.
   - Identify affected repository paths and established contracts.

2. **Worktree Allocation**
   - Verify clean pre-dispatch state (`git status --porcelain`).
   - Create isolated worktree: `bun scripts/worktree.ts create fix-<slug> [base]`.

3. **Builder Dispatch (Mode B — Rule of Prove-It)**
   - Dispatch builder subagent into the worktree.
   - **Rule of Prove-It:** Builder must author a failing reproduction test *before* editing production code, apply the minimal surgical fix, simplify code, and verify all tests pass with zero warnings under fatal flags.
   - Builder commits via explicit paths (`<issue-key>: <summary>` or `fix: <summary>`) and opens a PR (`gh pr create`).

4. **CI & Gate 3 Verification**
   - Monitor PR checks and confirm a clean test run.
   - Pass the cross-cutting Gate 3 check (see `SKILL.md`) whenever a runtime verification harness exists or before cutting any release tag.
