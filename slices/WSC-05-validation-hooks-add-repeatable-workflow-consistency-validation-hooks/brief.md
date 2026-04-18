# Slice Specification: Add repeatable workflow consistency validation hooks

**Slice**: `WSC-05-validation-hooks`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `workflow-state-consistency / WSC-05-validation-hooks`

## 1. Work Item Summary

- **Work Item**: Add one repeatable validation entrypoint that reuses the stabilized workflow-state checks so maintainers and CI can rerun the same fixture-backed consistency coverage on demand.
- **Source Story / Increment / Slice**: `WSC-05` / `I3` / `WSC-05-validation-hooks`
- **Requested Outcome**: As a repo owner, we want one repeatable validation hook for workflow consistency so automation and manual reruns can fail fast when parity or transition guardrail behavior regresses.
- **Why this matters**: The shared runtime, semantic preview, transition guardrails, and installed parity checks now exist, but maintainers still need one stable automation surface that reruns the reviewed drift cases without rebuilding that coverage ad hoc each time.
- **Independent Test**: A single repo-level validation entrypoint runs the reviewed workflow-state regression suites and fails when a fixture-backed parity or transition consistency regression is reintroduced.

## 2. Acceptance Scenarios

1. **Given** a clean repository checkout with the reviewed workflow-state implementation, **When** a maintainer runs the repeatable validation entrypoint, **Then** it completes successfully by rerunning the curated workflow-state regression coverage.
2. **Given** a regression in one of the reviewed fixture-backed workflow consistency paths, **When** CI or a maintainer runs the same entrypoint, **Then** it fails non-zero and surfaces the failing validation without requiring a separate ad hoc command list.
3. **Given** the validation entrypoint is rerun multiple times, **When** the underlying workflow-state checks remain unchanged, **Then** the entrypoint stays read-only and deterministic across reruns.

## 3. Functional Requirements

- **FR-001**: The repository MUST provide one repeatable workflow consistency validation entrypoint suitable for both CI and maintainer reruns.
- **FR-002**: The validation entrypoint MUST rerun the reviewed workflow-state regression coverage that protects installed parity and transition guardrail behavior.
- **FR-003**: The validation entrypoint MUST fail clearly when any underlying workflow consistency regression fails.
- **FR-004**: The validation entrypoint MUST remain read-only and MUST NOT mutate workflow artifacts, installed skills, or repo metadata as part of validation.
- **FR-005**: The validation entrypoint MUST be discoverable from the repo’s normal maintainer surfaces so rerunning it does not require reconstructing the command sequence from planning docs.

## 4. Key Entities

- **Workflow consistency validation entrypoint**: The repeatable repo-level hook maintainers or CI invoke to rerun the curated workflow-state checks.
- **Fixture-backed drift regression**: A deterministic test case that reproduces parity or transition consistency drift and should fail when the shared behavior regresses.
- **Read-only workflow-state checks**: The existing audit/report/owner validation paths that inspect drift without mutating artifacts.

## 5. Edge Cases

- One underlying workflow-state regression suite fails; the validation entrypoint should fail immediately and preserve the underlying failure output.
- The entrypoint is rerun after no code changes; the result should remain deterministic instead of depending on transient local state.
- The validation surface runs from CI or a maintainer shell with no installed skill refresh; it should validate the reviewed repo-local behavior rather than attempting to repair installs automatically.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `WSC-01-transition-guardrails` and `WSC-04-installed-parity` already define the workflow consistency behaviors that this slice must keep repeatably validated.
- **A2**: The first rollout can use a curated repo-level validation hook over existing deterministic regression coverage rather than introducing a new long-lived validation service or daemon.

### Dependencies

- **D1**: The reviewed workflow-state regression suites for audit/report parity and owner transition guardrails remain the source of truth for fixture-backed consistency coverage.
- **D2**: Repo-level maintainer guidance such as `Makefile` or adjacent usage docs remains the correct surface for exposing the repeatable validation hook.

## 7. Success Criteria

- **SC-001**: Maintainers can rerun one documented workflow consistency validation entrypoint without reconstructing the suite list manually.
- **SC-002**: The validation entrypoint fails non-zero when fixture-backed parity or transition consistency behavior regresses.
- **SC-003**: The validation entrypoint stays read-only and deterministic across repeated reruns.
