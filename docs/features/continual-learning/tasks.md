# Task Board: Continual Learning Multi-Harness Plugin

Governing ADR: [ADR-001: Multi-Harness Continual Learning Plugin Architecture](../../decisions/adr-001-continual-learning-multi-harness-plugin.md)  
Governing Spec: [Specification: Multi-Harness Continual Learning Plugin](spec.md)

---

## Slice Breakdown (Vertical TDD Slices)

### Slice 1: Project Setup & Cadence Engine
- [x] **Task 1.1**: Initialize `plugins/continual-learning/package.json` (`"type": "module"`) and `tsconfig.json` configured for Node 24 native TypeScript execution.
- [x] **Task 1.2**: Author domain type definitions in `src/types/common.ts`, `src/types/antigravity.ts`, and `src/types/copilot.ts`.
- [x] **Task 1.3**: Implement `src/cadence.ts` with pure `evaluateCadence(state, config, currentMs)` logic supporting normal and trial mode thresholds.
- [x] **Task 1.4**: Author unit test `tests/cadence.test.ts` verifying Example Mapping Rules 1.1, 1.2, 1.3, and 1.4.

### Slice 2: Incremental Transcript Indexer
- [x] **Task 2.1**: Implement `src/indexer.ts` to inspect transcript directories, read modification times, filter unindexed/modified files, and prune deleted entries.
- [x] **Task 2.2**: Author unit test `tests/indexer.test.ts` verifying Example Mapping Rules 2.1, 2.2, and 2.3.

### Slice 3: In-Place AGENTS.md Memory Updater
- [x] **Task 3.1**: Implement `src/updater.ts` with surgical regex-based bullet replacement and categorized bullet append.
- [x] **Task 3.2**: Author unit test `tests/updater.test.ts` verifying Example Mapping Rules 3.1, 3.2, and 3.3 (ensuring unrelated headers and bullets remain byte-identical).

### Slice 4: Antigravity CLI Stop Hook Adapter
- [x] **Task 4.1**: Implement `src/antigravity-hook.ts` reading JSON from `stdin`, loading/saving cadence state, and writing `{"decision": "allow" | "continue"}` to `stdout`.
- [x] **Task 4.2**: Configure root `plugins/continual-learning/hooks.json` mapping `continual-learning.Stop` to `node --experimental-strip-types src/antigravity-hook.ts`.
- [x] **Task 4.3**: Author test verifying Rule 4.1 and Rule 4.2 input/output contract against mock stdin streams.

### Slice 5: Copilot CLI Adapter & Multi-Manifest Packaging
- [x] **Task 5.1**: Implement `src/copilot-hook.ts` handling `sessionEnd` lifecycle events.
- [x] **Task 5.2**: Configure `com.github.copilot/hooks/hooks.json` for Copilot CLI discovery.
- [x] **Task 5.3**: Author portable `skills/continual-learning/SKILL.md` and root `plugin.json`.
- [x] **Task 5.4**: Author `agents/agents-memory-updater.md` subagent prompt definition.

### Slice 6: Justfile Distribution & Dual Installation
- [x] **Task 6.1**: Add `install-antigravity-continual-learning` recipe to `sirius-skills/justfile` targeting `~/.gemini/config/plugins/continual-learning`.
- [x] **Task 6.2**: Add `install-copilot-continual-learning` recipe to `sirius-skills/justfile`.
- [x] **Task 6.3**: Add composite `install-continual-learning` recipe.
- [x] **Task 6.4**: Run `node --experimental-strip-types` and `npx tsc --noEmit` across all `.ts` files to ensure zero type or syntax errors.

---

## Slice 7: Qualification Remediation (Resolving UNVERIFIED Findings)
Governing Report: [Qualification Report (UNVERIFIED)](qualification-report.md)

- [x] **Task 7.1 (Extract Neutral State Module)**: Create `src/state.ts` containing `loadState`, `saveState`, and `loadCadenceConfigFromEnv`. Eliminate inverted dependency in `src/copilot-hook.ts` importing from `src/antigravity-hook.ts`.
- [x] **Task 7.2 (Bridge Core Engine via Runner)**: Create `src/runner.ts` exporting `runContinualLearningLoop(workspacePath, state, options)`. Connect `indexer.ts` (`syncTranscriptIndex`, `commitProcessedTranscripts`) and `updater.ts` (`patchAgentsMemory`) into an active production call path.
- [x] **Task 7.3 (Wire Copilot Hook & Authentic Tests)**: Wire `src/copilot-hook.ts` to execute `runContinualLearningLoop` on eligible cadence. Rewrite `tests/copilot-hook.test.ts` to assert observable disk side effects (verifying index file updates and `AGENTS.md` patching).
- [x] **Task 7.4 (Regex Sanitization)**: Implement regex metacharacter escaping (`escapeRegExp`) in `src/updater.ts` before creating dynamic `RegExp` objects to eliminate ReDoS vulnerabilities and runtime syntax crashes.
- [x] **Task 7.5 (Prune Dead Code)**: Remove or integrate orphaned `findTranscriptsInDirectory` in `src/indexer.ts`.
- [x] **Task 7.6 (Re-Run Dual Qualification)**: Verify 100% active call-paths and confirm all tests pass cleanly.

---

## Worker Handoff Checklist
- [x] Requirements Alpha $\to$ **Acceptable** (Example Mapping R1–R5 defined with concrete test cases, zero ambiguity).
- [x] Software System Alpha $\to$ **Architecture Selected** ([ADR-001](../../decisions/adr-001-continual-learning-multi-harness-plugin.md) binding contracts, SSDs, and interfaces established).
- [x] Software System Alpha $\to$ **Demonstrable / Usable** (Slice 7 Remediation completed; verified with authentic assertions and 100% active call paths).
- [x] Work Alpha $\to$ **Prepared** (Remediation tasks prioritized and mapped to finding IDs).

