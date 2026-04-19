# Slice Specification: Scope shared-runtime sync to packaged installs

**Slice**: `sim-runtime-scope`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `split-install-modes / sim-runtime-scope`

## 1. Work Item Summary

- **Work Item**: Lock the shared-runtime sync boundary so it remains part of the packaged flow and not the local source-linked flow.
- **Source Story / Increment / Slice**: `SIM-03` / `I3` / `sim-runtime-scope`
- **Requested Outcome**: As a maintainer, I want deterministic verification that local install does not run shared-runtime sync while packaged install still does.
- **Why this matters**: The repo has already split local and packaged install behavior, but that boundary is still implicit. A later edit to the `Makefile` could accidentally re-couple local install to packaged sync without a targeted regression test.
- **Independent Test**: Targeted tests inspect `make -n` output and confirm `install-local` omits sync while `install-packaged` and its compatibility alias still render sync commands.

## 2. Acceptance Scenarios

1. **Given** a maintainer renders `make -n install-local`, **When** they inspect the output, **Then** it shows only the local helper command and no shared-runtime or shared-reference sync commands.
2. **Given** a maintainer renders `make -n install-packaged`, **When** they inspect the output, **Then** they still see shared-runtime sync and shared-reference sync before the packaged `npx skills add` flow.
3. **Given** compatibility aliases remain in place, **When** a maintainer renders `make -n install`, **Then** it still reflects the packaged sync behavior.

## 3. Functional Requirements

- **FR-001**: The repo MUST keep shared-runtime sync scoped to the packaged install path.
- **FR-002**: The repo MUST keep local source-linked install free of shared-runtime sync and shared-reference sync.
- **FR-003**: The packaged compatibility alias MUST still reflect the packaged sync behavior in the current rollout.
- **FR-004**: The slice MUST add deterministic regression coverage for the target-surface boundary.
- **FR-005**: The slice MUST avoid broadening scope into parity or migration-guidance behavior changes.

## 4. Key Entities

- **Local install path**: `install-local`.
- **Packaged install path**: `install-packaged`.
- **Compatibility alias**: `install`.
- **Shared-runtime sync commands**: `scripts/sync_shared_skill_runtime.py` and `scripts/sync_shared_skill_references.py`.

## 5. Edge Cases

- The local helper command itself changes later; the test should assert the absence of packaged sync, not overfit every command detail unnecessarily.
- The packaged path may add more commands later; the test should focus on the required sync boundary and packaged registration behavior.
- Compatibility aliases may render slightly differently from direct packaged targets, but they must still reflect packaged sync semantics.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `sim-packaged-compat` has already clarified that `install-packaged` is the explicit packaged path and `install` remains an alias.
- **A2**: The current `Makefile` behavior already matches the intended boundary, so this slice can mostly codify it with regression coverage.

### Dependencies

- **D1**: `Makefile` remains the source of truth for the install-path command boundary.
- **D2**: `scripts/sync_shared_skill_runtime.py` and `scripts/sync_shared_skill_references.py` remain the packaged sync steps that the boundary must preserve.

## 7. Success Criteria

- **SC-001**: Targeted regression tests prove `install-local` omits packaged sync.
- **SC-002**: The same tests prove `install-packaged` and `install` still include packaged sync.
- **SC-003**: No unrelated install or parity behavior changes are introduced in this slice.

## 8. Open Clarifications

- None.
