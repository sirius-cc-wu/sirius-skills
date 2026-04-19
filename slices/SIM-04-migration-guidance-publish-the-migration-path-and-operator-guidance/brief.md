# Slice Specification: Publish the migration path and operator guidance

**Slice**: `SIM-04-migration-guidance`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `split-install-modes / SIM-04-migration-guidance`

## 1. Work Item Summary

- **Work Item**: Publish a clear migration guide for contributors and maintainers moving from the old one-path install model to the new local-versus-packaged split.
- **Source Story / Increment / Slice**: `SIM-04` / `I3` / `SIM-04-migration-guidance`
- **Requested Outcome**: As a contributor, I want one place that tells me which command to use now, what old commands still work, and how packaged parity checks fit into the new model.
- **Why this matters**: The repo now has explicit local and packaged install modes plus opt-in packaged parity, but the migration story is still spread across multiple slices and assumptions.
- **Independent Test**: README and durable planning docs provide a consistent command map, alias policy, and packaged-parity guidance that matches the implemented behavior.

## 2. Acceptance Scenarios

1. **Given** a contributor used to `make install`, **When** they read the migration guidance, **Then** they can map that old habit to the new local or packaged command intentionally.
2. **Given** a maintainer validating packaged installs, **When** they read the guidance, **Then** they can find the explicit packaged-parity flag instead of assuming parity is always part of local report output.
3. **Given** a planner reviewing the subfeature docs, **When** they inspect the final state, **Then** the migration guidance aligns with the actual implemented command surface and parity behavior.

## 3. Functional Requirements

- **FR-001**: The repo guidance MUST provide a concise command map from old install habits to the new local and packaged commands.
- **FR-002**: The guidance MUST state that `install` / `uninstall` are still compatibility aliases to the packaged path in the current rollout.
- **FR-003**: The guidance MUST explain that packaged parity checks are now opt-in through `--check-packaged-parity`.
- **FR-004**: Durable planning docs for `split-install-modes` MUST reflect the current implemented migration state.
- **FR-005**: The slice MUST avoid changing install or parity behavior; it is guidance-only.

## 4. Key Entities

- **Local source-linked workflow**: `make install-local` / `make uninstall-local`.
- **Explicit packaged workflow**: `make install-packaged` / `make uninstall-packaged`.
- **Compatibility aliases**: `make install` / `make uninstall`.
- **Packaged parity flag**: `--check-packaged-parity` on audit and report maintenance commands.

## 5. Edge Cases

- A contributor only reads the README; the migration map must still be sufficient there.
- A maintainer still uses `install` / `uninstall`; the guidance should explain that those aliases remain valid today.
- A local user expects packaged parity in default report output; the guidance should now point them to the explicit parity flag instead.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: All prior slices in `split-install-modes` are complete, so the command surface and parity behavior are now stable enough to document as the current migration state.
- **A2**: The later default flip of `install` away from the packaged alias is still unresolved and should remain framed as future follow-up rather than current behavior.

### Dependencies

- **D1**: README and installation feature docs remain the main durable guidance surfaces.
- **D2**: The explicit packaged parity flag added in `SIM-03-parity-scope` is the authoritative operator contract for parity validation.

## 7. Success Criteria

- **SC-001**: The migration guidance gives a correct command map for local, packaged, and alias behavior.
- **SC-002**: The guidance tells users how to run packaged parity checks explicitly.
- **SC-003**: No guidance contradicts the current `Makefile` targets or audit/report flags.

## 8. Open Clarifications

- None.
