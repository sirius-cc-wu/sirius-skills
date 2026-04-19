# Slice Specification: Split local and packaged install targets

**Slice**: `sim-packaged-targets`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `split-install-modes / sim-packaged-targets`

## 1. Work Item Summary

- **Work Item**: Add explicit packaged install target names so the repo exposes separate command surfaces for local source-linked install and packaged install.
- **Source Story / Increment / Slice**: `SIM-02` / `I2` / `sim-packaged-targets`
- **Requested Outcome**: As a maintainer, I want explicit packaged target names so the local `install-local` workflow and the packaged workflow stop sharing the same conceptual command surface.
- **Why this matters**: The repo now has a local source-linked path, but the packaged path still looks like the default unnamed install contract. Explicit packaged target names are the first step toward a clearer migration.
- **Independent Test**: `Makefile` exposes `install-packaged` and `uninstall-packaged`, and `make -n` shows those targets running the existing packaged commands while `install-local` remains separate.

## 2. Acceptance Scenarios

1. **Given** a maintainer inspecting the `Makefile`, **When** they look at install targets, **Then** they can distinguish local source-linked targets from packaged targets by name.
2. **Given** the current packaged flow still needs to work unchanged, **When** the maintainer runs the explicit packaged targets, **Then** they see the same packaged sync and `npx skills` commands as before.
3. **Given** later migration work still depends on the old compatibility path, **When** this slice lands, **Then** `install` and `uninstall` can still remain available without breaking callers.

## 3. Functional Requirements

- **FR-001**: The system MUST add explicit `install-packaged` and `uninstall-packaged` `Makefile` targets for the packaged workflow.
- **FR-002**: The packaged targets MUST run the same packaged sync and registration commands as the current `install` and `uninstall` flow.
- **FR-003**: The slice MUST keep `install-local` and `uninstall-local` distinct from the packaged targets.
- **FR-004**: The slice MUST avoid breaking the current `install` and `uninstall` compatibility path.
- **FR-005**: The slice MUST provide a deterministic validation path for target selection, such as `make -n` or equivalent smoke inspection.

## 4. Key Entities

- **Local install targets**: `install-local` and `uninstall-local`, which manage source-linked symlinks.
- **Packaged install targets**: `install-packaged` and `uninstall-packaged`, which manage the self-contained packaged flow.
- **Compatibility targets**: `install` and `uninstall`, which remain available in this slice.

## 5. Edge Cases

- A maintainer invokes the new packaged target with `-n`; the rendered command list should still show sync plus packaged `npx skills` behavior.
- The repo adds new managed skills later; the explicit packaged targets should still reuse the shared managed skill list and packaged command logic.
- Later slices may change what `install` points to; this slice must not pre-empt that migration decision.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `sim-local-helper` already introduced a stable local install target surface.
- **A2**: Compatibility behavior for `install` and `uninstall` is still handled in the later `sim-packaged-compat` slice, so this slice should stay focused on naming and target shape.

### Dependencies

- **D1**: The existing packaged flow in `Makefile` remains the source of truth for the commands that `install-packaged` and `uninstall-packaged` should run.
- **D2**: The later compatibility slice will document or refine the remaining aliases once explicit packaged target names exist.

## 7. Success Criteria

- **SC-001**: `Makefile` contains explicit packaged install and uninstall target names.
- **SC-002**: `make -n install-packaged` and `make -n uninstall-packaged` show the expected packaged commands.
- **SC-003**: Existing `install-local` / `uninstall-local` and compatibility `install` / `uninstall` still exist after the slice.

## 8. Open Clarifications

- None.
