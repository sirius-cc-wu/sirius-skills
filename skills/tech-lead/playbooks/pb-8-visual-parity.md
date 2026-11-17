# Playbook 8: Visual Parity (Builder Mode C)

**Trigger:** UI component refactoring, design token migration, or CSS framework replacement with zero intended visual drift.
**Alpha Progression:** *Work* → *Concluded (Targeted)*.

## Steps

1. **Scope the Parity Target**
   - Identify UI components undergoing refactoring, design token adoption, or framework modernization with zero intended visual drift.

2. **Freeze Baseline Screenshots**
   - In the target project/worktree, capture golden baseline screenshots across all component states (`default`, `hover`, `focus`, `disabled`, `error`) and target viewports before altering production code.

3. **Builder Mode C Dispatch**
   - Provision isolated worktree via `bun scripts/worktree.ts create <branch> [base]`.
   - Dispatch builder with instructions to refactor components, run automated image diffs (Playwright/CDP) against frozen baselines, and loop until pixel diff is `0`.

4. **Parity & Gate 3 Qualification**
   - Verify the visual diff report (`0` pixel regression) and clean code diff via Gate 2 qualification before merging.
   - Pass the cross-cutting Gate 3 check (see `SKILL.md`) whenever a runtime verification harness exists or before cutting any release tag.
