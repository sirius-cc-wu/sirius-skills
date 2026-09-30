---
title: "Execution Plan: Slice 01 — Tooling Scaffolding & Script Migration to TypeScript with Bun"
adr: "ADR-001"
status: "planned"
date: "2026-10-01"
---

# Slice 01 Plan: Tooling Scaffolding & Script Migration to TypeScript with Bun

## 1. Goal
Establish repository tooling on TypeScript and Bun (`package.json`, `tsconfig.json`), migrate `scripts/validate_skills.sh` to a type-safe `scripts/validate_skills.ts`, port `sync_shared_references.py` and `manage_installed_skills.py` to TypeScript, update `justfile` targets, and verify full behavioral and validation parity.

## 2. Inventory & Targets

| Source | Destination | Tests |
| :--- | :--- | :--- |
| *(new)* | `package.json` | `bun install` |
| *(new)* | `tsconfig.json` | TypeScript compiler / IDE check |
| `scripts/validate_skills.sh` | `scripts/validate_skills.ts` | `bun scripts/validate_skills.ts` (100% parity with shell script) |
| `src/sirius_skills/commands/sync_shared_references.py` | `scripts/sync_shared_references.ts` | `bun scripts/sync_shared_references.ts` |
| `src/sirius_skills/commands/manage_installed_skills.py` | `scripts/manage_installed_skills.ts` | `bun test tests/manage_installed_skills.test.ts` |
| `justfile` (recipes calling Python commands/bash) | `justfile` (recipes calling Bun scripts) | `just validate`, `just install-local` |

## 3. Incremental Execution Steps

1. **Step 1: Scaffolding Setup**:
   - Create `package.json` with:
     ```json
     {
       "name": "sirius-skills",
       "version": "0.3.0",
       "private": true,
       "type": "module",
       "scripts": {
         "test": "bun test",
         "validate": "bun scripts/validate_skills.ts"
       },
       "devDependencies": {
         "@types/bun": "latest"
       }
     }
     ```
   - Create `tsconfig.json` with strict settings tailored for Bun.
   - Run `bun install`.

2. **Step 2: Migrate `scripts/validate_skills.sh` $\to$ `scripts/validate_skills.ts`**:
   - Implement catalog, profile, frontmatter, retirement ledger, and budget validation in TypeScript.
   - Run both `bash scripts/validate_skills.sh` and `bun scripts/validate_skills.ts` side-by-side to verify exact output equivalence.
   - Add unit tests in `tests/validate_skills.test.ts`.

3. **Step 3: Migrate `sync_shared_references.py` $\to$ `scripts/sync_shared_references.ts`**:
   - Port copy logic of canonical references from `docs/shared/` to consuming skills.
   - Ensure `--check` flag works identically for dry-run verification.
   - Add test coverage in `tests/sync_shared_references.test.ts`.

4. **Step 4: Migrate `manage_installed_skills.py` $\to$ `scripts/manage_installed_skills.ts`**:
   - Port `link-profile`, `prune-local`, and state management commands.
   - Ensure CLI flags (`--profile`, `--source-dir`, `--target-dir`) match existing contracts.
   - Add test coverage in `tests/manage_installed_skills.test.ts`.

5. **Step 5: Update `justfile`**:
   - Update `install-local`, `sync-shared-references`, and `validate` recipes to use Bun scripts.
   - Run `just validate` to verify end-to-end green status.

## 4. Acceptance Criteria
- [ ] `bun scripts/validate_skills.ts` executes and passes cleanly with 0 errors.
- [ ] `just validate` completes successfully without invoking bash `validate_skills.sh`.
- [ ] `just install-local /tmp/test-target workflow` cleanly symlinks skills using `scripts/manage_installed_skills.ts`.
- [ ] Zero external npm runtime dependencies added.
