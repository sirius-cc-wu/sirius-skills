# Slice Planning

Use this file to decompose repo stories into execution-ready slices before bootstrapping execution slices.

## Slice ID Naming

- Default naming: `<scope-prefix>-<capability-slug>`
- Use a short lowercase alias derived from the owning feature slug for
  feature-scoped breakdown.
- Use a short lowercase alias derived from the owning subfeature ID for
  subfeature-scoped breakdown.
- Avoid meaningless generic prefixes such as bare `slice-*` unless a
  repository-specific convention explicitly requires them.

## 1. Planning Scope

- Feature: data-access-layer-consolidation
- Planning sources:
  - `discover.md`
  - `system-design.md`
  - `ui-design.md` (if applicable)
  - `user-stories.md`
- Execution system: repository-managed slices
- Execution mode: `single-agent` | `multi-agent`
- Notes:

## 2. Story Decisions

| Story ID | Story Size | Story Risk | Decision | Reason | Output Slice Count |
| --- | --- | --- | --- | --- | --- |
| DALC-01 | M | medium | keep | Consolidate markdown accesses into a single markdown repository | 1 |
| DALC-02 | M | medium | keep | Encapsulate metadata validation at the library repository boundary | 1 |
| DALC-03 | M | high | split | Touches many command modules; split into foundation/repositories and command integrations | 2 |
| DALC-04 | S | low | keep | AST-based test checking for direct writes/open/json in commands | 1 |

Decision rules:

- `keep` means the story is already small enough to map to one executable slice.
- `split` means the story fans out into multiple execution-ready slices.
- `defer` means the story is not ready and should not be executed yet.
- split any `XL` story before slice bootstrap
- `S`/`M`/`L` stories may also split when risk, validation shape, coupling, or handoff complexity would make one packet brittle
- record the main reason for the decision, not just the size label

Risk rubric:

- `low`: one cohesive packet with one clear validation path
- `medium`: some coupling, multiple touchpoints, or moderate sequencing/handoff risk
- `high`: cross-subsystem impact, migration/reconciliation, compatibility risk, or materially different validation paths

## 3. Increment Plan

Use increments to group related slices into small, demonstrable outcomes. Increment 1 should usually be the simplest end-to-end usable path.

| Increment | Goal / User-Visible Value | Included Story IDs | Planned Slice IDs | Demo / Verification Outcome | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | Core DAL foundation, Scope runtime relocation, and AST guardrail | DALC-03, DALC-04 | dalc-foundation-storage, dalc-foundation-guardrail | All existing tests pass, scope_runtime is relocated, and AST test validates commands against an ignore list | Foundation phase |
| I2 | Registry and Metadata Repositories | DALC-02, DALC-03 | dalc-repo-metadata | Feature/proposal/subfeature/execution status commands migrate to repositories, thinned commands, guardrail passes | Metadata and registry phase |
| I3 | Markdown and Artifact Repositories | DALC-01, DALC-03 | dalc-repo-markdown | Markdown table/regex parsing and writing thinned from commands/inventory, guardrail ignore list empty | Final consolidation |

Rules:

- keep increments feature-scoped planning artifacts, not execution slices
- each increment should be demonstrable without requiring the full project to be complete
- an increment can include one or many execution-ready slices
- planned slices and execution slices remain slice-scoped even when they belong to the same increment

## 4. Execution Slice Backlog

| Slice ID | Story ID | Title | Summary | Target Area | Lane | Validation | Planned Action | Depends On | Slice Ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dalc-foundation-storage | DALC-03 | Implement Storage/Models and relocate Scope Runtime | Create storage.py, define models.py, move scope_runtime.py from commands/ to lib/workflow_state/ | `lib/workflow_state` | primary | `pytest tests/test_workflow_runtime.py` | create slice | | yes |
| dalc-foundation-guardrail | DALC-04 | Add AST-based Direct I/O Guardrail Test | Implement pytest to analyze commands AST for open/write/json imports with an ignore list | `tests` | primary | `pytest tests/test_direct_io_guardrails.py` | create slice | dalc-foundation-storage | yes |
| dalc-repo-metadata | DALC-02, DALC-03 | Implement Registry and Metadata Repositories | Implement planning/proposal/subfeature/execution repositories, migrate command writes | `lib/workflow_state`, `commands` | primary | `pytest` | create slice | dalc-foundation-guardrail | yes |
| dalc-repo-markdown | DALC-01, DALC-03 | Implement Markdown and Artifact Repositories | Implement markdown_repository, migrate table and template writes (ship, archive_data, inventory) | `lib/workflow_state`, `commands` | primary | `pytest` | create slice | dalc-repo-metadata | yes |

## 5. Dependency Notes

- Critical path: Storage/Models/Scope Relocation -> AST Guardrail -> Metadata Repositories -> Markdown Repositories
- Explicit blockers: None
- Parallel-safe slices: None (sequential refactoring is safer to prevent conflict)
- Increment ordering: I1 -> I2 -> I3
- Lane owners and handoffs: N/A
- Integration checkpoints: Run full pytest suite after each slice to verify command thinnings.

## 6. Bootstrap Order

1. dalc-foundation-storage
2. dalc-foundation-guardrail
3. dalc-repo-metadata
4. dalc-repo-markdown

## 7. Open Questions / Stop-and-Ask Items

- None (all resolved).

## Notes

- This file is feature-scoped planning, not slice-scoped execution.
- Keep increment definitions here, not in execution-slice artifacts.
- Once planned slices are created, record the actual slice IDs in `slice-traceability.md`.
- Keep slice IDs stable enough that they can be cross-referenced from traceability notes and planning discussion.
