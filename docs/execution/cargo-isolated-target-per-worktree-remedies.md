---
title: "Execution Plan: Review Remedies for Isolated Cargo Target per Worktree"
status: "completed"
date: "2026-10-12"
---

# Review Remedies: Isolated Cargo Target per Worktree

Playbook: PB-5 Review Remediation. Base: branch `fix/cargo-isolated-target`
at `c253bb0`. Source of findings:
`docs/verification/qualification-cargo-isolated-target-per-worktree.md`,
section 5. Governing rules: `docs/execution/cargo-isolated-target-per-worktree.md`.

## 1. Selected Findings

Fix these findings: m-1, m-2, m-3, m-4, n-1, n-2, n-4, n-5.
Do not fix n-3. It is a refactor outside this remediation.

## 2. Rule Amendment

n-5 changes rule R6. The new R6 text is:

- **R6 — `env` does not export a target path.** `worktree env [n]` prints
  `export CARGO_BUILD_JOBS=<n>` as before. Then it prints
  `unset CARGO_TARGET_DIR CARGO_BUILD_TARGET_DIR CARGO_BUILD_BUILD_DIR`. It
  prints no path.

This text replaces R6 in the governing plan for this remediation.

## 3. Tasks

### Task R-1: Main checkout label (m-1)

Files: `scripts/worktree.ts`, `tests/worktree.test.ts`.

- In the R5 size report, label the first entry of `listWorktrees()` as
  `(main)`. `git worktree list --porcelain` always lists the main worktree
  first. Do not compare with `getRepoRoot()`.
- Add test `hygiene labels main checkout when run from a linked worktree`.
  Run `hygiene` with the current directory set to a linked worktree. Assert
  that the `(main)` line belongs to the main checkout and that the linked
  worktree line uses its branch name.
- Do not create `Cargo.toml` in this test. From a linked worktree, pool
  detection can select the temporary parent directory. This is an
  out-of-scope defect. Without `Cargo.toml`, no config file is written there.

### Task R-2: Exact R2 migration assertion (m-2)

Files: `tests/worktree.test.ts`.

- In `migrates legacy pool config and keeps jobs and user keys`, replace the
  `toContain` checks on the file content with one exact `toBe` comparison of
  the full migrated content. The expected value has the R1 header on the
  first line, CRLF line endings, and all other lines in the original order.

### Task R-3: Real R5 size assertion (m-3)

Files: `tests/worktree.test.ts`.

- In `hygiene reports target size for main checkout and worktree`, assert
  that the `(main)` line, the worktree line, and the `Total:` line each match
  `\d+\.\d GB`.
- Add a second worktree without `target/`. Assert that its branch name does
  not appear in the size report.

### Task R-4: Pool variable isolation in tests (m-4)

Files: `tests/worktree.test.ts`.

- In `beforeEach`, save and delete `WORKTREES_DIR`, `SIRIUS_WORKTREES_DIR`,
  and `FOXPILOT_WORKTREES_DIR`. In `afterEach`, restore the saved values.
  Delete a variable that was not set before.
- Keep the existing tests that set these variables. They must still work
  with the new `beforeEach` and `afterEach`.

### Task R-5: Unreachable checks (n-1)

Files: `scripts/worktree.ts`.

- Remove the `rawLines.length === 0` check.
- Compute `endsWith("\r")` for the first line once and reuse the value.
- Remove the `parts.length === 0` check in `getTargetSizeKb`.
- Keep behavior unchanged.

### Task R-6: Exact R6 output (n-2, n-5)

Files: `scripts/worktree.ts`, `tests/worktree.test.ts`,
`skills/cargo-worktree-hygiene/SKILL.md`.

- Change the `env` `unset` line to the amended R6 text.
- In `env prints jobs and unsets target overrides without a path`, assert
  the exact stdout lines in order with `toEqual`.
- Update the `unset` line in `SKILL.md` pillars 2 and 3 to the amended text.

### Task R-7: Skill wording (n-4)

Files: `skills/cargo-worktree-hygiene/SKILL.md`.

- Start the stale-artifact bullet with
  `When worktrees share one target directory,`.
- Change the `hygiene` description at line 40 to mention disk space, the
  worktree pool, Cargo target isolation, and target sizes.

## 4. Constraints

- Work on branch `fix/cargo-isolated-target`. Add one new commit. Do not
  amend `c253bb0`.
- Do not modify, create, or stage files under `docs/`.
- Stage with explicit paths only. Do not use `git add .`, `git add -A`, or
  wildcards.
- Follow the Task 4 test isolation requirements of the governing plan.

## 5. Verification

```bash
bun test tests/worktree.test.ts
bun test tests
git diff --stat c253bb0..HEAD
```

Acceptance:

- All tests pass.
- Each task R-1 to R-7 is visible in the diff.
- `git diff --stat c253bb0..HEAD` lists only `scripts/worktree.ts`,
  `tests/worktree.test.ts`, and `skills/cargo-worktree-hygiene/SKILL.md`.
