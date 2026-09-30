---
title: "Execution Plan: Slice 04 Follow-up — Review Remedies for Evals & Fixtures"
status: "completed"
date: "2026-10-01"
---

# Slice 04 Follow-up: Review Remedies for Evals Modernization

## 1. Problem Statement
Commit `e2a0ffe7610` modernized fixtures and evaluations across active skills, but dual review by Gemini 3.8 Flash High and Claude Opus identified 3 Major and 4 Minor/Nit issues that require remediation:
1. `M-1`: `type-anchored-spec.json` prompt contradicts fixture state names (`Validated/Paid/Shipped` vs `Submitted/Approved/Fulfilled`) and omits target file path `docs/architecture/typestate-spec.md`.
2. `M-2`: Root `bun test` leaks test discovery into `evals/fixtures/refactor-boundary/tests/order.test.ts`.
3. `M-3`: `scripts/run_evals.ts` uses an array replacer in `JSON.stringify`, which drops nested object properties in dry-run CLI outputs.
4. `m-1`: `evals/fixtures/pr-scope-mismatch/docs/pr-context.md` describes test files that do not exist in the fixture.
5. `m-2`: `type-anchored-spec.json` dropped `prohibitions` without replacement.
6. `m-3`: `evals/fixtures/refactor-boundary/tests/order.test.ts` does not directly test `service.calculateTotalWithTax`.
7. `n-1`: Grammar typo in `evals/README.md#L52` ("an misplaced" -> "a misplaced").
8. `n-2`: `scripts/evals/routing.ts` does not verify fixture directory existence on disk during `validateEvaluations`.
9. `n-3`: `evals/cases/audit-pr-scope.json` expects a Mermaid diagram in expectations but omits it from rubric/controls.

## 2. Action Items & Concrete Changes

### Task 1: Fix `type-anchored-spec.json` (M-1, m-2)
- In `evals/cases/type-anchored-spec.json`:
  - Update `prompt` to reference `docs/approved-business-rules.md`, state progression `Draft -> Submitted -> Approved -> Fulfilled` (with `Rejected` from `Submitted`), and write destination `docs/architecture/typestate-spec.md`.
  - Restore `prohibitions`:
    ```json
    "prohibitions": [
      "Do not implement full runtime application logic",
      "Do not call unwrap() or expect() in spec definitions"
    ]
    ```

### Task 2: Isolate Root Test Discovery (M-2)
- In `package.json`:
  - Change `"test": "bun test"` to `"test": "bun test tests"`.
- In `justfile`:
  - Ensure `test` recipe runs `bun test tests`.

### Task 3: Fix `JSON.stringify` Property Stripping in `scripts/run_evals.ts` (M-3)
- In `scripts/run_evals.ts` (around lines 221, 239, 258):
  - Replace `console.log(JSON.stringify(plan, Object.keys(plan).sort(), 2));` with:
    ```typescript
    const sortedPlan = Object.fromEntries(
      Object.entries(plan).sort(([a], [b]) => a.localeCompare(b))
    );
    console.log(JSON.stringify(sortedPlan, null, 2));
    ```

### Task 4: Complete `pr-scope-mismatch` Fixture (m-1, n-3)
- In `evals/fixtures/pr-scope-mismatch/`:
  - Add stub test files `tests/cache.test.ts` and `tests/event_bus.test.ts` to fulfill the changed files listed in `docs/pr-context.md`.
  - In `evals/cases/audit-pr-scope.json`:
    - Add a criterion to `semantic_rubric` checking that vertical re-scoping includes a diagram or clean decoupling representation, and align controls.

### Task 5: Enhance `refactor-boundary` Test Coverage (m-3)
- In `evals/fixtures/refactor-boundary/tests/order.test.ts`:
  - Add explicit test case directly verifying `service.calculateTotalWithTax(order, 0.1)`.

### Task 6: Documentation and Validation Hardening (n-1, n-2)
- In `evals/README.md#L52`:
  - Change "an misplaced" to "a misplaced".
- In `scripts/evals/routing.ts`:
  - In `validateEvaluations`, check `fs.existsSync(path.join(root, "evals", "fixtures", fixture))` and report an error if missing.

## 3. Verification Criteria
- [x] `just validate` passes 100% green.
- [x] `just test` executes exactly 57 tests (no fixture tests leaked) and passes 100% green.
- [x] `just eval-behavior-dry-run audit-pr-scope audit-pr-scope-mismatch` outputs fully-populated nested properties (no empty `{}`).
- [x] `just eval-behavior-dry-run behavior-preserving-refactoring local-verified-transformation` runs cleanly.
- [x] `just eval-behavior-dry-run type-anchored-spec type-anchor-rules` outputs fully-populated file assertions.
- [x] `bun scripts/run_evals.ts --behavioral audit-pr-scope --case audit-pr-scope-mismatch --calibrate-judge --dry-run` outputs non-empty control objects.
