---
title: "Execution Plan: Slice 02 — NLP TF-IDF Routing Engine & Routing Evals Migration to TypeScript with Bun"
adr: "ADR-001"
status: "planned"
date: "2026-10-01"
---

# Slice 02 Plan: NLP TF-IDF Routing Engine & Routing Evals Migration to TypeScript with Bun

## 1. Goal
Port the deterministic tokenization, suffix stemmer, TF-IDF vectorizer, and cosine similarity router from Python (`src/sirius_skills/evaluation.py`) to TypeScript (`scripts/evals/nlp.ts`, `scripts/evals/routing.ts`, `scripts/run_evals.ts`), verify all 17 routing case suites under `bun test` and achieve exact match with Python eval metrics (96/96 passing checks).

## 2. Inventory & Targets

| Source | Destination | Tests |
| :--- | :--- | :--- |
| `src/sirius_skills/evaluation.py` (NLP + TF-IDF) | `scripts/evals/nlp.ts`, `scripts/evals/routing.ts` | `bun test tests/nlp.test.ts`, `tests/routing.test.ts` |
| `src/sirius_skills/commands/run_evals.py` (Routing CLI) | `scripts/run_evals.ts` | `bun scripts/run_evals.ts --root .` (96/96 passing checks) |
| `evals/cases/*.json` (17 case files) | Consumed directly by TypeScript harness | Parity with Python routing eval harness |
| `justfile` `eval-routing` recipe | Updated to `bun scripts/run_evals.ts --root "{{repo_root}}"` | `just eval-routing`, `just validate` |

## 3. Incremental Execution Steps

1. **Step 1: NLP Foundation (`scripts/evals/nlp.ts`)**:
   - Port `_tokenize`, `_stem`, `TermFrequency`, `compute_idf`, `tfidf_vector`, and `cosine_similarity`.
   - Implement unit tests in `tests/nlp.test.ts` validating stemmer rules and cosine similarity.

2. **Step 2: Routing Classifier & Case Loader (`scripts/evals/routing.ts`)**:
   - Port skill profile loading, frontmatter description extraction, and TF-IDF index construction.
   - Implement query evaluation and rank-one matching logic.
   - Implement unit tests in `tests/routing.test.ts`.

3. **Step 3: CLI Runner (`scripts/run_evals.ts`)**:
   - Implement CLI handling for `--root`, `--routing`, and reporting.
   - Verify 96/96 checks pass with 96% rank-one accuracy.

4. **Step 4: Update `justfile`**:
   - Point `eval-routing` to `bun scripts/run_evals.ts`.
   - Run `just validate` to confirm end-to-end green status.

## 4. Acceptance Criteria
- [ ] `bun scripts/run_evals.ts` passes all 96 routing checks with 96% rank-one rate.
- [ ] `just eval-routing` and `just validate` run cleanly under Bun without Python.
- [ ] All unit tests pass in `bun test`.
- [ ] Zero external runtime npm dependencies.
