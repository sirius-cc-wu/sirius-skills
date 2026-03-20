# Tasks: [FEATURE NAME]

**Track**: `[ID-feature-name]`  
**Status**: Draft  
**Inputs**: `spec.md`, `plan.md`  
**Optional Inputs**: research notes, data model notes, interface notes, verification scenarios

## 1. Execution Strategy

- MVP scope:
- Sequencing rationale:
- Parallelization notes:
- Validation approach:
- Risk stop gates:
- Integration checkpoints:

## 2. Task Format

Use checklist items in this format:

- `[ ] T001 [Phase/Story] Concrete action with file path`
- `[ ] T002 [P] [Phase/Story] Parallel-safe action with file path`

Where:

- `T###` is a stable task ID
- `[P]` marks work that can run in parallel without touching the same files or dependencies
- `[Phase/Story]` identifies the execution packet, phase, or user story
- include exact file paths where practical and keep verification work as explicit checklist items

## 3. Setup / Shared Foundations

- [ ] T001 [Setup] [Replace with concrete shared setup task]
- [ ] T002 [Setup] [Replace with concrete shared setup or configuration task]

## 4. Execution Packets

### Packet P01 / Story [Identifier]

- Goal:
- Dependencies:
- Exact validation:
- Stop gate:
- Handoff / integration:

- [ ] T010 [P01] [Replace with a concrete implementation step and file path]
- [ ] T011 [P01] [Replace with the next dependent step]
- [ ] T012 [P01] [Replace with a validation or verification step]

### Packet P02 / Story [Identifier]

- Goal:
- Dependencies:
- Exact validation:
- Stop gate:
- Handoff / integration:

- [ ] T020 [P02] [Replace with a concrete implementation step and file path]
- [ ] T021 [P02] [Replace with the next dependent step]
- [ ] T022 [P02] [Replace with a validation or verification step]

## 5. Cross-Cutting / Finalization

- [ ] T900 [Polish] [Replace with documentation, cleanup, or cross-cutting validation work]

## 6. Dependencies & Parallel Work

- Packet order:
- Blocking prerequisites:
- Parallel-safe groups:
- Lane handoffs:
- Integration checkpoints:

## 7. Exit Criteria

- [ ] All required implementation tasks are listed
- [ ] Each requirement or packet maps to one or more tasks
- [ ] Validation work is represented with exact commands or concrete artifact checks
- [ ] Risk stop gates are called out where required
- [ ] The implementation agent can begin without major replanning
