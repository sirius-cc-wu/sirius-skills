# Slice Specification: Add preview-only semantic drift reporting

**Slice**: `WSC-03-semantic-preview`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `workflow-state-consistency / WSC-03-semantic-preview`

## 1. Work Item Summary

- **Work Item**: Extend repair and report maintenance output so semantic workflow-state drift is previewed separately from derived registry/readme rebuild work.
- **Source Story / Increment / Slice**: `WSC-03` / `I2` / `WSC-03-semantic-preview`
- **Requested Outcome**: As a maintainer, we want a safe preview path for semantic workflow drift so we can distinguish metadata reconciliation work from derived repair work before any owner-mediated write path runs.
- **Why this matters**: Later transition guardrails depend on one stable, reviewable semantic finding shape, and maintainers need to see those high-confidence semantic issues without conflating them with deterministic derived rebuild actions.
- **Independent Test**: Targeted repair and report regression coverage confirms that semantic drift is surfaced as a separate preview path while derived registry/readme rebuild output remains intact and read-only.

## 2. Acceptance Scenarios

1. **Given** a repository with semantic metadata drift and derived registry/readme drift, **When** a maintainer runs repair or report preview output, **Then** semantic drift is listed separately from derived rebuild actions.
2. **Given** a repository with high-confidence semantic workflow drift, **When** preview output is generated, **Then** the maintainer receives a read-only preview that can be reviewed safely before any lifecycle owner chooses to write metadata.
3. **Given** a repository with only derived registry/readme drift, **When** preview output is generated, **Then** the output does not invent semantic repair findings and continues to report only the derived maintenance work.

## 3. Functional Requirements

- **FR-001**: The system MUST surface high-confidence semantic workflow-state drift separately from derived registry/readme rebuild work in the affected maintenance outputs.
- **FR-002**: The semantic drift path MUST remain preview-only and MUST NOT mutate planning, subfeature, or execution metadata directly.
- **FR-003**: Repair and report outputs MUST present the same normalized semantic findings so maintainers can review one stable interpretation of semantic drift.
- **FR-004**: Preview output MUST make the semantic-versus-derived distinction explicit enough that later owner-mediated transition checks can reuse the same finding shape without redefining it.
- **FR-005**: The slice MUST preserve a deterministic validation path using the existing repair/report regression suites for the affected maintenance workflows.

## 4. Key Entities

- **Semantic drift preview**: A read-only summary of high-confidence workflow-state metadata inconsistencies that require review before any owner-mediated write path.
- **Derived repair action**: A deterministic registry/readme rebuild action derived from durable directories and valid metadata.
- **Maintenance preview output**: The repair or report result presented to maintainers for review.
- **Owner-mediated write path**: A later lifecycle command that may choose to mutate metadata after reviewing the preview output.

## 5. Edge Cases

- A repository has both semantic drift and derived drift; output must separate them instead of collapsing one into the other.
- A repository has only derived drift; semantic preview output should stay empty rather than inventing metadata findings.
- A repository has only semantic drift; preview output should still remain read-only and not imply that a derived rebuild would fix it.
- Artifact metadata is malformed; the maintenance output should continue surfacing explicit failures rather than disguising them as previewable semantic drift.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `WSC-02-maintenance-adoption` provides the shared workflow-state interpretation that repair and report should reuse for semantic preview findings.
- **A2**: The first rollout should preview only the highest-confidence semantic drift and leave any explicit metadata mutation path to later owner-specific work.

### Dependencies

- **D1**: `WSC-02-maintenance-adoption` is complete and remains the prerequisite shared semantic foundation for the repair/report preview behavior.
- **D2**: The reviewed `workflow-state-consistency` planning packet remains the source of truth for keeping semantic preview read-only and distinct from owner-mediated transition checks.

## 7. Success Criteria

- **SC-001**: Repair and report outputs show semantic workflow-state drift separately from derived registry/readme rebuild work.
- **SC-002**: Semantic preview output remains read-only and does not broaden write ownership in maintenance flows.
- **SC-003**: Targeted repair/report regression coverage continues to pass while exercising the new semantic preview shape.

## 8. Open Clarifications

- None.
