---
type: "Architecture Decision"
title: "ADR-001: Multi-Harness Continual Learning Plugin Architecture"
description: "Authoritative architectural decision for continual learning plugin supporting Antigravity CLI and Copilot CLI via a typed Core Engine and thin CLI Hook Adapters in sirius-skills."
id: "ADR-001"
status: "accepted"
date: "2026-09-24"
tags: [architecture, decision, continual-learning, plugins, antigravity, copilot]
owner_loop: spec-validate
phase_profile: design
---

# ADR-001: Multi-Harness Continual Learning Plugin Architecture

Status: accepted

Date: 2026-09-24

## Context

Operator Sirius requires an autonomous, continual learning capability that updates `AGENTS.md` incrementally based on actual user corrections and project decisions captured across CLI sessions. The capability originated as a Cursor-specific plugin (`cursor-plugins/continual-learning`), but must now operate seamlessly across both **Antigravity CLI** and **GitHub Copilot CLI**.

Both CLI hosts adhere to the emerging agent customization standards (`plugin.json`, `skills/<name>/SKILL.md`), but differ in runtime lifecycle hooks, event schemas, payload delivery methods, and transcript locations:
- **Antigravity CLI**: Invokes commands declared in `hooks.json` under event names such as `Stop`. Context is passed as camelCase JSON over `stdin` (providing `conversationId`, `transcriptPath`, `workspacePaths`), and the process responds with JSON on `stdout` (`{ "decision": "allow" | "continue" }`).
- **Copilot CLI**: Discovers hooks declared under `com.github.copilot/hooks/hooks.json` (or root `hooks.json`) for lifecycle events such as `sessionEnd` or `stop`.
- **Runtime Environment**: Host runs Node.js v24.16+, enabling direct execution of modern TypeScript without a dedicated compile or build step via `node --experimental-strip-types`.

## Decision

1. **Repository Placement**:
   The multi-harness continual learning capability is authored, versioned, and maintained in `sirius-skills` under `plugins/continual-learning/`. The `thinker` repository remains dedicated to the Spec–Validate loop and maintains zero internal plugin implementations.

2. **Core Engine & Thin Adapter Architecture**:
   - The capability is decoupled into a shared, pure **TypeScript Core Engine** and two thin **CLI Hook Adapters**.
   - **Core Engine (`src/cadence.ts`, `src/updater.ts`)**: Evaluates turn count and elapsed time against configurable thresholds (supporting trial mode), indexes processed transcripts by modification timestamp (`continual-learning-index.json`), and updates `AGENTS.md` in-place while strictly preserving non-matching sections.
   - **Antigravity Adapter (`src/antigravity-hook.ts`)**: Ingests `AntigravityStopHookInput` from `stdin`, executes cadence evaluation, emits Antigravity `Stop` instructions, and outputs `AntigravityStopHookOutput` to `stdout`.
   - **Copilot Adapter (`src/copilot-hook.ts`)**: Ingests Copilot `sessionEnd` context, locates active session state, triggers the core updater, and terminates cleanly.

3. **Execution Runtime & Typing**:
   - Implementation uses pure TypeScript (`.ts`) executed directly by Node.js using `--experimental-strip-types`.
   - All hook payloads and state models are typed with strict interfaces (`AntigravityStopHookInput`, `CopilotSessionEndInput`, `ContinuousLearningState`).

4. **Multi-Target Manifest Packaging**:
   `plugins/continual-learning/` packages both host manifests:
   - Root `plugin.json` and portable `skills/continual-learning/SKILL.md`.
   - Root `hooks.json` for Antigravity CLI discovery.
   - `com.github.copilot/hooks/hooks.json` for Copilot CLI discovery.

5. **Runtime State Storage**:
   State is stored in `.gemini/state/continual-learning.json` or `.copilot/state/continual-learning.json` depending on host, or defaulted to `.agent/hooks/state/continual-learning.json` within target workspaces.

## Consequences

- **Capabilities & Guarantees**: A single, version-controlled codebase in `sirius-skills` serves both Antigravity CLI and Copilot CLI with zero duplicated business logic.
- **Invariants**:
  - `AGENTS.md` edits must always be in-place modifications to existing matching bullet items or non-destructive additions to designated learning sections.
  - The hook must execute synchronously within the CLI timeout limit (30 seconds default).
  - Transcript indexing must be strictly monotonic using file mtimes to prevent re-processing identical turns.
  - Type-checking must pass cleanly with `tsc --noEmit`.

## Trace

- Requirements & Examples: [`docs/features/continual-learning/spec.md`](../features/continual-learning/spec.md)
- Work Slicing & Task Board: [`docs/features/continual-learning/tasks.md`](../features/continual-learning/tasks.md)
