---
title: "Execution Plan: Slice 04 — Modernize Evals & Fixtures for Active Skills"
status: "completed"
date: "2026-10-01"
---

# Slice 04 Plan: Modernize Evals & Fixtures for Active Skills

## 1. Goal
Modernize the evaluation tier in `sirius-skills` end-to-end:
1. Prune legacy orphaned fixtures containing vestigial Python scripts (`host-safe-rust-refactoring`, `order-submission-contract`, `stateful-order`).
2. Build new, high-fidelity disposable fixtures tailored to active skills (`audit-pr-scope`, `behavior-preserving-refactoring`, `type-anchored-spec`).
3. Equip cases with semantic rubrics and calibrated positive/negative controls for LLM judge verification.
4. Rewrite `evals/README.md` to document the 17 active skills, new fixtures, and Bun-native workflows.
5. Ensure 100% green test passes across `just validate`, `just test`, and behavioral dry-runs.

## 2. Inventory & Targets

| Component | Current State | Target State |
| :--- | :--- | :--- |
| `evals/fixtures/` | 3 dead fixtures from retired Larman skills with Python scripts | Pruned; replaced with modern fixtures for active skills |
| `evals/cases/*.json` | 17 cases marked `provisional` with no fixtures or semantic rubrics | Key active skills upgraded with fixtures, assertions, and semantic controls |
| `evals/README.md` | Outdated documentation referencing retired skills and pytest commands | Fully rewritten for 17 active skills and Bun commands |
| `justfile` & CLI | `eval-behavior-dry-run` fails on active cases due to missing fixtures | Clean, working dry-runs and calibration plans |

## 3. Incremental Execution Steps

1. **Step 1: Prune Orphaned Fixtures**:
   - `git rm -r` legacy fixtures in `evals/fixtures/`.
2. **Step 2: Construct Modern Active Fixtures**:
   - `evals/fixtures/pr-scope-mismatch` for `audit-pr-scope`.
   - `evals/fixtures/refactor-boundary` (Bun/TS project with passing tests) for `behavior-preserving-refactoring`.
   - `evals/fixtures/typestate-workflow` for `type-anchored-spec`.
3. **Step 3: Upgrade Case JSON Definitions**:
   - Attach fixtures, file assertions, allowed/required mutations, and semantic rubrics & controls.
4. **Step 4: Rewrite `evals/README.md`**:
   - Update pilot coverage, command examples, and architecture documentation.
5. **Step 5: Verification**:
   - Run `just validate`, `just test`, dry-run evaluations, and calibration plan tests.

## 4. Acceptance Criteria
- [x] Zero Python files anywhere in `evals/fixtures/`.
- [x] At least 3 active skills have working, disposable fixtures and semantic controls.
- [x] `just eval-behavior-dry-run` runs cleanly on active fixture-backed skills.
- [x] Calibration dry-run outputs valid JSON execution plans.
- [x] `evals/README.md` accurately describes the 17 active skills.
- [x] `just validate` and `just test` pass 100% green.
