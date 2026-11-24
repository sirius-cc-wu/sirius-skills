---
name: correct
description: "Mine repository history for mistakes agents keep repeating (2+ occurrences) and eliminate each class at the highest level that works: architecture first, then types, then a lint or CI check whose error names the fix, then a behavioral test, and docs last. Proves each new check fails on a real past mistake and maintains a Rule-to-Enforcer table. User-invoked only: use for /correct; do not invoke automatically."
disable-model-invocation: true
---

# Correct (Structural Mistake Elimination)

The operator keeps correcting agents in this repository for the same mistakes. Redesign the repository environment so the next agent cannot make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

Companion to `reflect`:
- **`correct`** mines **repo history** to structurally eliminate repeating mistake classes in a target repository.
- **`reflect`** mines **one session transcript** to sharpen skills and trigger descriptions.

## 1. Find the mistake classes

Inspect recent commits, reverts, PR review comments (`git log`, `gh pr list`/`gh pr view`), Gate 2 qualification reports (`docs/verification/`), agent instruction files (`AGENTS.md`/`CLAUDE.md`), and comments explaining workarounds.

Group recurring failures into **mistake classes**. A class counts once it has happened **at least twice** (or when the operator explicitly targets a known repeat mistake). Cite the exact commits, PRs, or reports for every class (ADR-005 evidence discipline).

## 2. Fix each class at the highest level that works

Evaluate each class strictly top-down—never stop at prose when a higher level can enforce the invariant:

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails to compile. Replace hand-synced lists with a single source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types, then lint or CI.** Make invalid states unrepresentable in the type system (see `type-anchored-spec` for Rust). If bad code still compiles, add a lint, pre-commit hook, or CI check whose error message **names the exact file, type, or function to use instead**. If the legacy pattern is already widespread, **ratchet** it: fail only when a change adds new occurrences.
3. **Test the behavior.** Fix or delete any test that still passes when the behavior it checks breaks, or fails when only internals change.
4. **Write docs or agent rules last—only for judgment calls.** Nothing fails when an agent skips prose.

*Corollary:* If a structural fix works, apply only the structural fix. Adding another prose instruction is treating the symptom.

## 3. Plan, dispatch, and prove (Thinker/Builder Boundary)

Present the ranked mistake classes to the operator first, then execute approved classes according to Thinker's boundaries (Thinker never edits target-project application code or runs target build loops directly):

- **Level 1 (Architecture / new boundary)**: Route through **PB-1** (upfront ADR in `docs/decisions/` + Gate 1) or **PB-9** (behavior-preserving structural refactor), then dispatch a Builder in an isolated worktree (`bun scripts/worktree.ts create`).
- **Levels 2–3 (Types, lint/CI check, behavioral test)**: Package **one scoped PB-3 Builder task per mistake class** (one atomic commit per class) in an isolated worktree with these mandatory Builder acceptance criteria:
  1. **Prove the check fails on a real past mistake** (reproduce against an earlier offending commit or minimal fixture showing the check/test goes red before the fix and green on `HEAD`).
  2. **Same command locally and in CI** under fatal warning flags (`-D warnings`, `-Werror`, strict mode).
  3. **Bounded exceptions only**: any suppression goes on the offending line with a reason, an expiry date, and explicit human approval.
  4. Qualify deliverables via **Gate 2** (`code-review-and-quality` + `spec-qualification`) before merge.
- **Level 4 (Judgment-call docs only)**: Update target-owned `AGENTS.md` / `CODING_STANDARDS.md` directly after operator approval (respecting ADR-003 Zero Repo Pollution—never create Thinker-only config files like `.thinker.yaml`).

## 4. Keep the Rule → Enforcer table

Maintain a compact table in the target repo's agent instruction file (`AGENTS.md` / `CLAUDE.md`) pairing each active rule with what enforces it:

```markdown
| Rule | Enforcer | Level |
|---|---|---|
| <invariant> | <compiler type / lint rule / CI job / behavioral test / review-only> | <1-Arch \| 2-Type/Lint \| 3-Test \| 4-Doc> |
```

- When the operator corrects a mistake, fix the mistake and record or update its row.
- If the rule was already in the table with **no structural enforcer** (`4-Doc`), that is a repeat—escalate it to the highest working level in the same change.
- **Delete a rule from the table once its mistake can no longer happen** so `AGENTS.md` shrinks over time.

## 5. Reply format

For each discovered mistake class, report:
- **Class & Evidence**: concrete commits, reverts, PR comments, or Gate 2 reports ($\ge 2$ occurrences).
- **Level Picked (1–4)** and **why every higher level did not work**.
- **Proposed Action**: exact PB-1/PB-3/PB-9 Builder brief (including the past-mistake proof target) or Level 4 doc update, awaiting operator approval.
