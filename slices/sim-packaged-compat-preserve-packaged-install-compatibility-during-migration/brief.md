# Slice Specification: Preserve packaged install compatibility during migration

**Slice**: `sim-packaged-compat`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `split-install-modes / sim-packaged-compat`

## 1. Work Item Summary

- **Work Item**: Document and preserve the interim packaged compatibility path now that `install-packaged` and `uninstall-packaged` exist.
- **Source Story / Increment / Slice**: `SIM-02` / `I2` / `sim-packaged-compat`
- **Requested Outcome**: As a maintainer, I want the repo to state clearly that `install-packaged` is the explicit packaged path while `install` and `uninstall` still exist as migration-time aliases.
- **Why this matters**: The command surface is now split, but the repo docs and source comments still describe the old packaged path as if it were the primary named interface.
- **Independent Test**: README, AGENTS, installation feature docs, and `Makefile` all describe `install-packaged` consistently while showing `install` / `uninstall` as compatibility aliases.

## 2. Acceptance Scenarios

1. **Given** a maintainer reading the README, **When** they look for the packaged path, **Then** they see `install-packaged` / `uninstall-packaged` as the explicit commands and `install` / `uninstall` as compatibility aliases.
2. **Given** an agent reading `AGENTS.md` or installation feature docs, **When** it reasons about install behavior, **Then** it sees the same compatibility story as the README.
3. **Given** a maintainer reading the `Makefile`, **When** they inspect `install` / `uninstall`, **Then** it is obvious those targets are aliases preserved during migration.

## 3. Functional Requirements

- **FR-001**: The README MUST present `install-packaged` and `uninstall-packaged` as the explicit packaged workflow.
- **FR-002**: The repo docs MUST state that `install` and `uninstall` remain migration-time compatibility aliases.
- **FR-003**: Agent-facing guidance and installation feature docs MUST describe the same compatibility policy as the README.
- **FR-004**: The `Makefile` MUST keep the compatibility aliases intact in this slice.
- **FR-005**: The slice MUST validate that the explicit packaged targets and compatibility aliases still render the expected packaged commands.

## 4. Key Entities

- **Explicit packaged targets**: `install-packaged` and `uninstall-packaged`.
- **Compatibility aliases**: `install` and `uninstall`.
- **Local source-linked targets**: `install-local` and `uninstall-local`.

## 5. Edge Cases

- A contributor only sees the README; it should still explain the migration state without needing the subfeature docs.
- A later slice may change what `install` points to; this slice should describe the current compatibility state without overcommitting to the later default flip.
- The packaged path must still be documented as running shared-runtime and shared-reference sync before `npx skills add`.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `sim-packaged-targets` already added working `install-packaged` and `uninstall-packaged` targets.
- **A2**: The default-path flip question remains intentionally unresolved in this slice.

### Dependencies

- **D1**: README, AGENTS, and installation feature docs remain the canonical durable guidance for install behavior.
- **D2**: The packaged `Makefile` targets continue to own the sync and `npx skills` flow that the docs describe.

## 7. Success Criteria

- **SC-001**: The packaged path is documented everywhere as `install-packaged` / `uninstall-packaged`.
- **SC-002**: `install` / `uninstall` are described consistently as compatibility aliases.
- **SC-003**: `make -n install-packaged uninstall-packaged install uninstall` still renders the packaged flow after the doc and comment updates.

## 8. Open Clarifications

- None.
