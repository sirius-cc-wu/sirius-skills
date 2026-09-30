---
title: "Execution Plan: Slice 03 — Behavioral Evals, LLM Judge Calibration & Complete Python Deprecation"
adr: "ADR-001"
status: "planned"
date: "2026-10-01"
---

# Slice 03 Plan: Behavioral Evals, LLM Judge Calibration & Complete Python Deprecation

## 1. Goal
Port the behavioral evaluation runner, dry-run planner, workspace snapshot/diff capture, assertion evaluator, Codex subprocess execution, and semantic judge calibration (`src/sirius_skills/behavioral_evaluation.py`) to TypeScript (`scripts/evals/behavioral.ts`, `scripts/evals/judge.ts`), wire up all `justfile` evaluation recipes to Bun, port remaining Python tests, and deprecate Python runtime files (`src/` and `pyproject.toml`).

## 2. Inventory & Targets

| Source | Destination | Tests |
| :--- | :--- | :--- |
| `src/sirius_skills/behavioral_evaluation.py` | `scripts/evals/behavioral.ts`, `scripts/evals/judge.ts` | `bun test tests/behavioral.test.ts`, `tests/judge.test.ts` |
| `justfile` (`eval-behavior-dry-run`, `eval-behavior`, `eval-behavior-judged`, `eval-judge-calibration`, `eval-judge-comparison`) | `justfile` recipes calling `bun scripts/run_evals.ts` | `just eval-behavior-dry-run` |
| `tests/test_*.py` | `tests/*.test.ts` | `bun test` replacing `pytest` |
| `src/sirius_skills/` & `pyproject.toml` | Deprecated / removed | Clean repo status with 0 Python dependencies |

## 3. Incremental Execution Steps

1. **Step 1: Workspace Sandbox & Assertions**:
   - Port workspace snapshotting, file mutation detection, and file/trace assertions.
   - Implement unit tests for workspace isolation and assertion verification.

2. **Step 2: Behavioral Runner & Codex Execution**:
   - Port dry-run plan generation and Codex CLI execution runner.
   - Implement unit tests for dry-run plans.

3. **Step 3: Judge Calibration & Model Comparison**:
   - Port semantic judge prompt formulation, response parsing, and calibration matrix.

4. **Step 4: Full Python Deprecation**:
   - Port all remaining Python unit tests to TypeScript.
   - Deprecate `pyproject.toml` and `src/sirius_skills/`.
   - Update `justfile` and documentation to declare TypeScript/Bun as single canonical runtime.

## 4. Acceptance Criteria
- [ ] `just eval-behavior-dry-run` runs cleanly without Python.
- [ ] 100% of test suites run via `bun test` in <500ms.
- [ ] Zero Python runtime dependencies remaining in repository.
- [ ] `just validate` passes 100% green.
