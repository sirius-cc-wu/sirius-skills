---
name: correct
description: "Mine a target repository's history for mistakes agents keep repeating (2+ occurrences) and eliminate each class at the highest level that works: architecture first, then types, then a lint or CI check whose error names the fix, then behavioral tests or runtime verification harness proofs, and docs last. Proves each new check fails on a real past mistake and maintains a Rule-to-Enforcer table. User-invoked only: use for /correct; do not invoke automatically."
disable-model-invocation: true
---

# Correct (Structural Mistake Elimination)

The operator keeps correcting agents in a target repository for the same mistakes. Redesign that repository's environment and harness so the next agent cannot make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

Companion to `reflect`:
- **`correct`** mines **target-repo history** to structurally eliminate repeating mistake classes in that repository (code, types, lint/CI, tests, and runtime harness).
- **`reflect`** mines **one session transcript** to sharpen Thinker/shared skills, update target harness docs, and queue structural backlog items.

## 0. Resolve the target repository

Because `agy` runs in `thinker` while working on another repository, **never assume CWD (`/home/ccwu/thinker`) is the target repository**:

- Resolve `<TARGET_REPO_PATH>` explicitly from the operator's argument or current session context. If ambiguous, ask before mining history. Target `/home/ccwu/thinker` only when explicitly requested.
- Scope every read-only inspection command explicitly to `<TARGET_REPO_PATH>` (`git -C <TARGET_REPO_PATH> ...`, `gh ... --repo <owner/repo>`, reading `<TARGET_REPO_PATH>/docs/verification/`, `<TARGET_REPO_PATH>/AGENTS.md`, and `<TARGET_REPO_PATH>/docs/ui/surface-map/`).
- Provision Builder worktrees inside `<TARGET_REPO_PATH>`—never create target-repo worktrees inside `/home/ccwu/thinker`.

## 1. Find the mistake classes

Inspect `<TARGET_REPO_PATH>`'s recent commits, reverts, PR review comments (`git -C <TARGET_REPO_PATH> log`, `gh pr list`/`gh pr view`), Gate 2 qualification reports (`<TARGET_REPO_PATH>/docs/verification/`), Gate 3 harness logs (`<TARGET_REPO_PATH>/docs/ui/surface-map/`, `scripts/verify-*`), agent instruction files (`<TARGET_REPO_PATH>/AGENTS.md`/`CLAUDE.md`), and comments explaining workarounds.

Group recurring failures into **mistake classes**. A class counts once it has happened **at least twice** (or when the operator explicitly targets a known repeat mistake). Cite the exact commits, PRs, or reports for every class (ADR-005 evidence discipline).

## 2. Fix each class at the highest level that works

Evaluate each class strictly top-down—never stop at prose when a higher level can enforce the invariant:

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails to compile. Replace hand-synced lists with a single source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types, then lint or CI.** Make invalid states unrepresentable in the type system (see `type-anchored-spec` for Rust). If bad code still compiles, add a lint, pre-commit hook, or CI check whose error message **names the exact file, type, or function to use instead**. If the legacy pattern is already widespread, **ratchet** it: fail only when a change adds new occurrences.
3. **Test the behavior or lock it into the runtime harness.** Fix or delete any test that still passes when the behavior it checks breaks, or fails when only internals change. For repeating runtime/UI/CLI/device regressions, add a deterministic check to `<TARGET_REPO_PATH>`'s **Gate 3 verification harness** (`scripts/verify-*`, `docs/ui/surface-map/`, `.agents/skills/verify-*`, using `maintain-verification-harness` or `create-verification-harness` if drifted or absent).
4. **Write docs or agent rules last—only for judgment calls.** Nothing fails when an agent skips prose.

*Corollary:* If a structural fix works, apply only the structural fix. Adding another prose instruction is treating the symptom.

## 3. Plan, dispatch, and prove (Thinker/Builder Boundary)

Present the ranked mistake classes to the operator first, then execute approved classes according to Thinker's boundaries (Thinker never edits target-project application code or runs target build loops directly):

- **Level 1 (Architecture / new boundary)**: Route through **PB-1** (upfront ADR in `<TARGET_REPO_PATH>/docs/decisions/` + Gate 1) or **PB-9** (behavior-preserving structural refactor), then dispatch a Builder in an isolated worktree of `<TARGET_REPO_PATH>`.
- **Levels 2–3 (Types, lint/CI check, behavioral test, or runtime harness check)**:
  - For pure runtime harness drift (`docs/ui/surface-map/`, `scripts/verify-*`, `.agents/skills/verify-*`), route through **`maintain-verification-harness`**.
  - Otherwise package **one scoped PB-3 Builder task per mistake class** (one atomic commit per class) in an isolated worktree of `<TARGET_REPO_PATH>` with these mandatory Builder acceptance criteria:
    1. **Prove the check fails on a real past mistake** (reproduce against an earlier offending commit or minimal fixture showing the check/test/harness probe goes red before the fix and green on `HEAD`).
    2. **Same command locally and in CI** under fatal warning flags (`-D warnings`, `-Werror`, strict mode).
    3. **Bounded exceptions only**: any suppression goes on the offending line with a reason, an expiry date, and explicit human approval.
    4. Qualify deliverables via **Gate 2** (`code-review-and-quality` + `spec-qualification`)—and **Gate 3** when runtime surfaces changed—before merge.
- **Level 4 (Judgment-call docs only)**: Update target-owned `<TARGET_REPO_PATH>/AGENTS.md` / `CODING_STANDARDS.md` directly after operator approval (respecting ADR-003 Zero Repo Pollution—never create Thinker-only config files like `.thinker.yaml`).

## 4. Keep the Rule → Enforcer table

Maintain a compact table in `<TARGET_REPO_PATH>/AGENTS.md` (or `CLAUDE.md`) pairing each active rule with what enforces it:

```markdown
| Rule | Enforcer | Level |
|---|---|---|
| <invariant> | <compiler type / lint rule / CI job / test or harness probe / review-only> | <1-Arch \| 2-Type/Lint \| 3-Test/Harness \| 4-Doc> |
```

- When the operator corrects a mistake, fix the mistake and record or update its row.
- If the rule was already in the table with **no structural enforcer** (`4-Doc`), that is a repeat—escalate it to the highest working level in the same change.
- **Delete a rule from the table once its mistake can no longer happen** so `AGENTS.md` shrinks over time.

## 5. Reply format

Start by naming `<TARGET_REPO_PATH>`, then for each discovered mistake class report:
- **Class & Evidence**: concrete commits, reverts, PR comments, Gate 2 reports, or Gate 3 harness failures ($\ge 2$ occurrences).
- **Level Picked (1–4)** and **why every higher level did not work**.
- **Proposed Action**: exact PB-1/PB-3/PB-9 Builder brief (including the past-mistake proof target), `maintain-verification-harness` pass, or Level 4 doc update, awaiting operator approval.
