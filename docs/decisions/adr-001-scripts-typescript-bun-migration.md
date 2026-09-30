---
type: "Architecture Decision"
title: "ADR-001: Unification of Engineering Scripts and Test Harness on TypeScript and Bun"
description: "Migrates sirius-skills engineering scripts, skill validation, and evaluation harnesses from Python and Bash to TypeScript executed natively with Bun."
id: "ADR-001"
status: "accepted"
date: "2026-10-01"
---

# ADR-001: Unification of Engineering Scripts and Test Harness on TypeScript and Bun

Status: accepted

## Context
`sirius-skills` serves as the capability depot providing reusable, host-agnostic skills for agent workflows across the ecosystem. Currently, its local maintenance relies on a dual-stack setup:
1. Python 3 (`src/sirius_skills`, `tests/*.py`, `pyproject.toml`) for skill routing evaluation, installation management, and unit testing with `pytest`.
2. Bash (`scripts/validate_skills.sh`) for validating skill catalogs, frontmatter, and retirement ledgers.
3. `justfile` recipes requiring `env PYTHONPATH=...` prefixing and virtualenv management.

Meanwhile, companion projects like FoxPilot and Antigravity CLI agent harnesses have unified on TypeScript running natively on Bun. Maintaining Python alongside TypeScript creates toolchain fragmentation, slower test execution (~4.2s for 103 Python tests vs <50ms with `bun test`), and requires dual-runtime environments.

Notably, `sirius-skills`'s core package already has `dependencies = []` (zero runtime pip dependencies). Its standard algorithms, file operations, and validation routines can be expressed directly in idiomatic TypeScript with zero external npm dependencies using native Bun primitives (`Bun.$`, `Bun.file()`, `node:path`, `node:fs`).

## Decision
1. **Adopt TypeScript and Bun**:
   - Standardize all repository validation scripts, skill management commands, and evaluation harnesses on TypeScript executed natively by Bun.
   - Establish `package.json` (`"type": "module"`, `"private": true`, `"scripts": { "test": "bun test" }`) and `tsconfig.json` at repository root.
   - Strictly zero runtime npm packages, relying exclusively on Bun standard APIs (`Bun.$`, `Bun.file`, `node:path`, `node:fs`, `node:crypto`) and dev dependency `@types/bun`.
2. **Execute in 3 Staged Slices**:
   - **Slice 1**: Tooling scaffolding, migrating `scripts/validate_skills.sh` $\to$ `scripts/validate_skills.ts`, and porting installation/reference commands to TypeScript.
   - **Slice 2**: Core NLP evaluation engine (`evaluation.ts`, TF-IDF vector ranking, collision checking) and `scripts/run_evals.ts`.
   - **Slice 3**: Test suite cutover to `bun test` and deprecation of Python files and virtualenvs.
3. **Executable Shebang Invocation**:
   - Use `#!/usr/bin/env bun` headers and executable permissions (`chmod +x`) on script entrypoints.
   - Update `justfile` recipes to invoke `bun scripts/<name>.ts`.

## Invariants & Rules
- **Zero Runtime Dependencies**: No third-party npm libraries in production scripts or validation tooling.
- **Exact Algorithmic Parity**: The tokenization, stemming (`_stem`), and TF-IDF cosine ranking in TypeScript must match the Python implementation with float-level precision.
- **Strict Typing**: All TypeScript code must pass strict type-checking under `tsconfig.json` with no implicit `any`.
- **Equivalent CLI Contracts**: Command-line arguments, options, and output formats must remain backward-compatible with existing `justfile` targets and calling workflows.

## Consequences
- Unifies the entire agent skill ecosystem on a single, modern TypeScript + Bun runtime.
- Reduces full test and validation execution time from seconds to milliseconds.
- Replaces brittle bash shell scripts with type-safe, maintainable TypeScript.
