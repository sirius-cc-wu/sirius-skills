# Slice Contract: Implement Markdown and Artifact Repositories

**Slice**: `dalc-repo-markdown`  
**Created**: 2026-06-25  
**Status**: Draft  
**Input**: `data-access-layer-consolidation / dalc-repo-markdown`

## 1. Summary

- **Work Item**: Move markdown/table parsing and artifact summary writes behind shared repository helpers.
- **Source Story / Increment / Slice**: `DALC-01`, `DALC-03` / `I3` / `dalc-repo-markdown`
- **Requested Outcome**: Commands no longer own the markdown parsing/writing details for traceability, reconciliation, and archive summaries.
- **Why this matters**: The DAL consolidation only finishes when markdown-backed artifact access is shared instead of scattered across commands.
- **Independent Test**: `pytest`

## 2. Acceptance Scenarios

1. **Given** the shared markdown repository, **When** code reads traceability tables or updates reconciliation blocks, **Then** the repository owns that markdown logic.
2. **Given** the current ship/archive/report workflows, **When** they run, **Then** behavior remains compatible.
3. **Given** malformed markdown tables or summaries, **When** repository parsing runs, **Then** it fails predictably instead of silently corrupting content.

## 3. Functional Requirements

- **FR-001**: The system MUST provide shared repository helpers for markdown-backed artifact parsing and writing.
- **FR-002**: The repository helpers MUST own traceability table parsing and markdown summary/appendix updates.
- **FR-003**: The command modules MUST delegate markdown parsing/writing responsibilities to the shared repository layer.
- **FR-004**: The slice MUST preserve current ship, archive, inventory, and reporting behavior.
- **FR-005**: Markdown repository helpers MUST remain deterministic and filesystem-local.

## 4. Edge Cases

- Traceability tables may contain optional columns or multiple rows.
- Markdown appendices and reconciliation blocks must remain well-formed after updates.
- Existing archive summary sections on feature and subfeature design docs must still be discoverable.
- Commands that only read markdown should not be forced to rewrite it.

## 5. Assumptions and Dependencies

### Assumptions

- **A1**: The current markdown table formats are stable enough to centralize without redesigning them.
- **A2**: Inventory/reporting can consume shared markdown helpers without altering the data model.

### Dependencies

- **D1**: The storage and metadata repository foundation slices are already complete.
- **D2**: The direct-write guardrail remains in place to prevent new command-owned markdown writes.

## 6. Success Criteria

- **SC-001**: Markdown table parsing and update helpers live in the shared repository layer.
- **SC-002**: Ship/archive/report/inventory paths use the repository helpers for moved markdown access.
- **SC-003**: The relevant pytest suite passes without changing CLI outputs or artifact formats.

## 7. Open Clarifications

- None.
