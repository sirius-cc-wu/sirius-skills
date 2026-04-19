# Slice Specification: Surface installed-vs-repo skill parity drift

**Slice**: `wsc-installed-parity`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `workflow-state-consistency / wsc-installed-parity`

## 1. Work Item Summary

- **Work Item**: Surface installed-vs-repo maintenance-skill parity drift through the shared workflow-state runtime and existing maintenance/reporting outputs.
- **Source Story / Increment / Slice**: `WSC-04` / `I3` / `wsc-installed-parity`
- **Requested Outcome**: As a repo owner, we want the active installed skills checked against the checked-in repo source so stale packaged behavior is visible before we trust a repair or audit result.
- **Why this matters**: The shared runtime now defines the canonical workflow-state interpretation, but maintainers still need a read-only way to tell when the installed maintenance skills no longer match the checked-in repository behavior they expect to be running.
- **Independent Test**: Targeted audit/report regression coverage and a stale-install parity fixture confirm that installed-vs-repo mismatches surface as structured parity findings while unchanged installs continue reporting clean parity.

## 2. Acceptance Scenarios

1. **Given** an environment where the installed maintenance-skill runtime no longer matches the checked-in repo source, **When** the maintainer runs the in-scope maintenance/reporting command, **Then** the output surfaces installed-vs-repo parity drift explicitly instead of silently assuming the install is current.
2. **Given** an environment where the installed maintenance-skill runtime matches the checked-in repo source, **When** the maintainer runs the same command, **Then** parity output stays clean and does not introduce unrelated warnings.
3. **Given** parity drift is present, **When** the maintainer reviews the result, **Then** the output remains read-only and points at the mismatch itself rather than mutating the installed skill or the repo source automatically.

## 3. Functional Requirements

- **FR-001**: The system MUST provide one shared installed-vs-repo parity inspection path for the in-scope maintenance skills rather than separate owner-local mismatch checks.
- **FR-002**: The affected maintenance/reporting outputs MUST surface parity drift as explicit structured findings so maintainers can distinguish stale installed behavior from repository workflow drift.
- **FR-003**: The parity path MUST remain read-only and MUST NOT modify installed skill files, repo source files, or maintenance output ownership boundaries directly.
- **FR-004**: Clean installed-vs-repo parity MUST remain low-noise so maintainers do not see mismatch warnings when the installed runtime matches the checked-in source.
- **FR-005**: The slice MUST preserve a deterministic validation path using the targeted audit/report tests plus a parity-specific stale-install scenario.

## 4. Key Entities

- **Parity finding**: A structured installed-vs-repo mismatch record describing which runtime file or skill surface differs from the checked-in repository source.
- **Installed runtime copy**: The active self-contained maintenance-skill code available through the installed skill set.
- **Repo source expectation**: The checked-in workflow-state or maintenance-skill source that represents the canonical behavior for the repository.
- **Parity-aware maintenance output**: The existing audit/report output surface extended to show parity findings without taking ownership of fixes.

## 5. Edge Cases

- The installed runtime matches the repo source; parity output should stay empty or clean rather than reporting soft differences.
- Only one synced shared-runtime file differs; the output should surface the specific mismatch instead of collapsing all parity into one generic warning.
- The installed copy is missing files that exist in the repo source; parity output should report the missing file explicitly.
- The repo source cannot be inspected normally; the command should continue surfacing explicit operational errors instead of disguising them as parity findings.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `wsc-maintenance-adoption` and `wsc-transition-guardrails` have already stabilized the shared runtime and skill-local sync flow enough that parity can compare meaningful installed-vs-repo expectations.
- **A2**: The first rollout should surface parity through existing maintenance commands and shared output fields rather than adding a dedicated parity-only command.

### Dependencies

- **D1**: `wsc-shared-library` remains the prerequisite canonical source for comparing installed copies with repo-local expectations.
- **D2**: The reviewed `workflow-state-consistency` design keeps parity reporting read-only and inside existing maintenance outputs for the initial rollout.

## 7. Success Criteria

- **SC-001**: In-scope maintenance/reporting output surfaces structured installed-vs-repo parity findings when the active installed copy is stale.
- **SC-002**: Clean parity remains low-noise and does not add mismatch output when the installed copy matches the checked-in repo source.
- **SC-003**: Targeted parity regression coverage continues to pass while exercising both clean and stale-install scenarios.

## 8. Open Clarifications

- None.
