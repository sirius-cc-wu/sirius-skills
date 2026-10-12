---
title: "Phase 6 Qualification Report: Isolated Cargo Target Directory per Worktree"
status: "VERIFIED"
date: "2026-10-12"
commit: "5f335db281fb89bb81ce58beeae713fe7ba27f9b"
---

# Phase 6 Qualification Report: Isolated Cargo Target Directory per Worktree

## 1. Endeavor Summary

- **Plan**: `docs/execution/cargo-isolated-target-per-worktree.md` (PB-3 Scoped Fix).
- **Baseline commit**: `f8125a3` (`main`).
- **Delivery commits**: `c253bb0` (fix) and `5f335db` (review remedies) on
  branch `fix/cargo-isolated-target`.
- **Remediation plan**: `docs/execution/cargo-isolated-target-per-worktree-remedies.md`
  (PB-5). It amends R6: the `unset` line also clears `CARGO_BUILD_BUILD_DIR`.
- **Builder**: Gemini 3.8 Flash High (`agy`), isolated worktree.
- **Scope**: The pool config no longer sets `target-dir`. Legacy generated
  configs are migrated line by line. `hygiene` reports target isolation and
  target sizes. `env` no longer exports a target path. Skill and catalog text
  match the new behavior.
- **Changed files**: `scripts/worktree.ts`, `tests/worktree.test.ts`,
  `skills/cargo-worktree-hygiene/SKILL.md`, `catalog/skills.md`,
  `skills/assess-development-input/SKILL.md`. No other file changed.

## 2. Qualification Panel

Two reviewers ran in separate processes and separate contexts. Each reviewer
applied `spec-qualification`, `code-review-and-quality`, and an anti-phantom
call-path audit. Each reviewer had read-only access.

| Reviewer | Runner | Verdict |
| :--- | :--- | :--- |
| Reviewer 1 | `claude -p --model opus` (read and `git` read tools only) | **VERIFIED** |
| Reviewer 2 | `agy --mode plan --model gemini-3.8-flash-high` | **VERIFIED** |

Consensus: **VERIFIED**. No reviewer found a CRITICAL or MAJOR issue.

## 3. Rule Disposition Matrix

| Rule | Description | Evidence (`c253bb0`) | Status |
| :--- | :--- | :--- | :--- |
| **R1** | New pool config has the R1 header, `[build]`, and `jobs` only. | `scripts/worktree.ts:190-196`. Test `writes pool cargo config with jobs and without target-dir`. | **VERIFIED** |
| **R2** | Legacy migration replaces the header, removes `target-dir` lines, keeps other lines, writes a stderr notice, and is idempotent. | `scripts/worktree.ts:199-222`. Tests `migrates legacy pool config and keeps jobs and user keys`, `legacy migration is idempotent`. | **VERIFIED** |
| **R3** | User-authored configs are not modified. | `scripts/worktree.ts:225`. Test `does not modify user-authored pool config that sets target-dir`. | **VERIFIED** |
| **R4** | `hygiene` reports `isolated (checked: pool config, environment)` or `shared` with sources. | `scripts/worktree.ts:642-679`. Four `hygiene reports ...` tests. | **VERIFIED** |
| **R5** | `hygiene` reports target sizes for all checkouts, with `unknown` on `du` failure. | `scripts/worktree.ts:231-242`, `:683-704`. Test `hygiene reports target size for main checkout and worktree`. | **VERIFIED** |
| **R6** | `env` prints `CARGO_BUILD_JOBS` and the `unset` line, and no path. | `scripts/worktree.ts:732-733`. Test `env prints jobs and unsets target overrides without a path`. | **VERIFIED** |
| **R7** | Documentation matches behavior. | All Task 5 edits present. Section 6 `rg` matches are warnings, migration code, or R4 output only. | **VERIFIED** |

## 4. Call-Path Audit

| Function | Status | Production caller |
| :--- | :--- | :--- |
| `ensureCargoPoolConfig` | Changed | `getWorktreesDir` (`scripts/worktree.ts:162`, `:174`), reached from `createWorktree`, `removeWorktree`, and `hygiene`. |
| `getTargetSizeKb` | New | `main` `hygiene` branch (`scripts/worktree.ts:694`). |
| `runMainIsolated` | New, test only | Seven tests in `tests/worktree.test.ts`. |

No dead code, unused imports, or leftover variables were found.

## 5. First-Round Findings and Disposition

Status after `5f335db`: m-1 to m-4, n-1, n-2, n-4, and n-5 are RESOLVED by
remediation tasks R-1 to R-7. n-3 is DEFERRED by decision. It is a refactor.

| ID | Severity | Location | Finding | Source |
| :--- | :--- | :--- | :--- | :--- |
| **m-1** | Minor | `scripts/worktree.ts:688` | `hygiene` labels the current checkout `(main)` when it runs from a linked worktree. Label `items[0]` instead. | Reviewer 1 |
| **m-2** | Minor | `tests/worktree.test.ts:335-341` | The R2 test uses `toContain`. It does not prove line order, CRLF preservation, or the header position. Assert the exact content. | Reviewer 1 |
| **m-3** | Minor | `tests/worktree.test.ts:508-510` | The R5 test checks labels only. It passes if every size is `unknown`. Assert `\d+\.\d GB` and assert that a checkout without `target/` is not listed. | Reviewer 1 |
| **m-4** | Minor | `tests/worktree.test.ts:27-46` | Tests do not clear `WORKTREES_DIR`, `SIRIUS_WORKTREES_DIR`, or `FOXPILOT_WORKTREES_DIR`. With one of these set, tests can fail and the R5 test can leave a worktree in a real pool. | Reviewer 1 |
| **n-1** | Nit | `scripts/worktree.ts:201-203`, `:207`, `:236` | Unreachable `length === 0` checks and a repeated `endsWith("\r")` call. | Reviewers 1 and 2 |
| **n-2** | Nit | `tests/worktree.test.ts:521-524` | The R6 test does not check exact output or line order. | Reviewer 1 |
| **n-3** | Nit | `scripts/worktree.ts:642-679` | R4 detection is inline in `main`. An extracted function would be easier to test. | Reviewer 1 |
| **n-4** | Nit | `skills/cargo-worktree-hygiene/SKILL.md:40`, `:55` | The stale-artifact bullet does not name the shared-directory condition. The `hygiene` description omits isolation and sizes. | Reviewer 1 |
| **n-5** | Nit | Plan R6 | R4 detects `CARGO_BUILD_BUILD_DIR`, but the R6 `unset` line does not clear it. This is a plan gap, not a code defect. | Reviewer 1 |

## 6. Re-Qualification (`5f335db`)

The same two reviewers ran again in separate processes with read-only access.

| Reviewer | Verdict | Result |
| :--- | :--- | :--- |
| Reviewer 1 (`claude -p --model opus`) | **VERIFIED** | R-1 to R-7 RESOLVED. R1 to R7 hold with amended R6. n-3 untouched. 5 NITs. |
| Reviewer 2 (`agy --mode plan`, Gemini 3.8 Flash High) | **VERIFIED** | R-1 to R-7 RESOLVED. No regression. 0 findings. |

`5f335db` changes only `scripts/worktree.ts`, `tests/worktree.test.ts`, and
`skills/cargo-worktree-hygiene/SKILL.md`. It changes nothing under `docs/`.

Open NITs (non-blocking, Reviewer 1):

| ID | Location | Finding |
| :--- | :--- | :--- |
| **n-6** | `tests/worktree.test.ts:562-575` | The R-1 test does not assert `Repository Root:` is the linked worktree. |
| **n-7** | `tests/worktree.test.ts:568-571` | Duplicate assertions on `Cargo Target Sizes:`. |
| **n-8** | `tests/worktree.test.ts:110-126` | Always-true guard and repeated restore blocks for pool variables. |
| **n-9** | `scripts/worktree.ts:628-636` | Existing defect: `Active Worktrees:` still compares with `getRepoRoot()`. Track with the pool-detection defect. |
| **n-10** | `tests/worktree.test.ts:88-107` | Existing defect: tests do not isolate global git config keys such as `sirius.worktreesDir`. Use `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`. |

## 7. Verification Evidence

- Builder report at `c253bb0`: `bun test tests` passed 102 of 102 tests.
- Builder report at `5f335db`: `bun test tests/worktree.test.ts` passed 26 of
  26 tests. `bun test tests` passed 103 of 103 tests across 13 files.
- Reviewers did static review only. They did not run the test suite.
- `git diff --stat main...HEAD` at `c253bb0`: 5 files changed, 447
  insertions, 44 deletions. Only the files named in the plan changed.
- `git diff --stat c253bb0..5f335db`: 3 files changed, 90 insertions, 28
  deletions.
- Both reviewer runs left the worktree clean (`git status --porcelain` empty).
