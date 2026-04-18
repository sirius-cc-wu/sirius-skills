# Slice Specification: Add high-confidence transition consistency checks

**Slice**: `WSC-01-transition-guardrails`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `workflow-state-consistency / WSC-01-transition-guardrails`

## 1. Work Item Summary

- **Work Item**: Add narrow shared transition guardrails to planning, subfeature, execution, and close/finalize owners so obvious workflow-state drift is surfaced during important state changes.
- **Source Story / Increment / Slice**: `WSC-01` / `I2` / `WSC-01-transition-guardrails`
- **Requested Outcome**: As a maintainer, we want state-changing skills to run narrow consistency checks after important transitions so stale subfeature or planning metadata is caught immediately.
- **Why this matters**: The shared preview work in WSC-03 now exposes one stable semantic finding shape, but maintainers still need owner scripts to surface that drift at the moment a transition would otherwise leave the repository in a stale or misleading state.
- **Independent Test**: Targeted guide-planning, add-subfeature, guide-execution, and close-slice regression coverage confirms that the affected owner flows surface the same high-confidence transition findings while still allowing clean transitions to complete.

## 2. Acceptance Scenarios

1. **Given** a planning or subfeature owner flow that would leave high-confidence workflow-state drift behind, **When** the transition completes, **Then** the owner surfaces the shared transition findings immediately and deterministically instead of silently accepting the stale state.
2. **Given** an execution or close/finalize owner flow with no high-confidence semantic drift, **When** the maintainer performs the transition, **Then** the transition still succeeds without adding new friction or duplicate output.
3. **Given** the same underlying semantic drift is visible in preview/report output, **When** a later owner script reaches its guarded transition point, **Then** the owner surfaces the same normalized finding class instead of inventing a second interpretation of the drift.

## 3. Functional Requirements

- **FR-001**: The system MUST run shared high-confidence workflow-state transition checks at the important transition points owned by `guide-planning`, `add-subfeature`, `guide-execution`, and `close-slice`.
- **FR-002**: The affected owner flows MUST surface transition findings using the shared semantic finding contract established by the workflow-state library instead of redefining owner-local drift logic.
- **FR-003**: Transition guardrails MUST remain narrow and deterministic so clean transitions continue to succeed without semantic false positives or broad workflow blocking.
- **FR-004**: The guardrails MUST preserve current ownership boundaries: owner scripts may surface or enforce findings, but the shared library MUST NOT directly mutate planning, subfeature, or execution metadata.
- **FR-005**: The slice MUST preserve a repeatable validation path using the existing owner test suites for planning, subfeature, execution, and close/finalize flows.

## 4. Key Entities

- **Transition guardrail**: A shared high-confidence workflow-state check run by an owning lifecycle script around an important status change.
- **Owner transition**: A planning, subfeature, execution, or close/finalize operation that remains the authoritative writer for the affected metadata.
- **Semantic finding contract**: The normalized workflow-state finding shape reused between preview/report maintenance output and transition-owner guardrails.
- **Clean transition**: An owner-mediated state change that does not introduce or preserve high-confidence workflow-state drift.

## 5. Edge Cases

- A transition touches a repository area with no high-confidence semantic drift; the guardrail should stay quiet and not block a clean change.
- A repository already has preview-visible semantic drift from the same finding class; the owner should surface that same normalized issue rather than inventing a second message shape.
- A lifecycle script encounters malformed metadata rather than a supported semantic-drift case; the flow should continue surfacing explicit owner errors instead of disguising them as guardrail findings.
- Different owners reach the same stale-state condition at different times; each owner should still use the same shared invariant interpretation for its guarded transition point.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `WSC-03-semantic-preview` provides the stable shared semantic finding contract that transition owners should reuse directly.
- **A2**: The first rollout should focus only on the high-confidence transition checks already identified in feature planning, leaving any broader policy tuning or configuration to later work if real repositories need it.

### Dependencies

- **D1**: `WSC-03-semantic-preview` is complete and remains the semantic prerequisite for owner-transition reuse.
- **D2**: The reviewed `workflow-state-consistency` planning packet remains the source of truth for which owners are in scope and for keeping guardrails narrow and deterministic.

## 7. Success Criteria

- **SC-001**: The targeted planning, subfeature, execution, and close/finalize owner flows surface shared high-confidence transition findings when they encounter the planned stale-state conditions.
- **SC-002**: Clean transitions in the affected owner flows continue to succeed without unrelated blocking or duplicate semantic output.
- **SC-003**: The targeted owner regression suites continue to pass while exercising the new guardrail behavior.

## 8. Open Clarifications

- None.
