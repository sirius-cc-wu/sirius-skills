# Slice Specification: Document rerun semantics and preflight behavior

**Slice**: `spi-operator-contracts`
**Created**: 2026-04-24  
**Status**: Draft
**Input**: "spi-operator-contracts Document rerun semantics and preflight behavior"

## 1. Work Item Summary

- **Work Item**: Update the ship skill and throughput-acceleration wiki pages so operators can understand what `ship` recomputes, what mutates, when preflight runs, and why it can stop before mutation.
- **Source Story / Increment / Slice**: `SPI-01`, `SPI-04` / `I3` / `spi-operator-contracts`
- **Requested Outcome**: The checked-in `ship` guidance and related wiki pages describe the shipped rerun contract in the same terms the implementation now uses: read-only recomputation, guarded mutation, delegated side effects, and local-only preflight timing.
- **Why this matters**: The code now has a real operator contract. Without aligned docs, maintainers still have to infer safe reruns and preflight behavior from implementation details.
- **Independent Test**: Artifact review that `skills/ship/SKILL.md`, `docs/wiki/concepts/two-step-autonomy-roadmap.md`, and `docs/wiki/features/throughput-acceleration-workflow.md` all match the current ship behavior.

## 2. Acceptance Scenarios

1. **Given** an operator reads `skills/ship/SKILL.md`, **When** they review the ship workflow and guardrails, **Then** they can tell which ship paths are read-only, which can mutate, and when preflight or approval matters.
2. **Given** an operator follows the two-step autonomy roadmap, **When** they read the wiki guidance, **Then** they can see when `ship --approve`, `ship --resume`, and optional preflight checks apply.
3. **Given** a reviewer checks the throughput-acceleration feature wiki, **When** they compare it against current ship behavior, **Then** the page reflects the implemented readiness/preflight contract rather than stale roadmap ideas.

## 3. Functional Requirements

- **FR-001**: The system documentation MUST describe `ship` rerun behavior as a typed contract that separates read-only recomputation from mutation-capable operations.
- **FR-002**: The ship skill and wiki guidance MUST explain that preflight is repo-configured under `accelerators.ship.preflight.mode` and currently supports `off` and `local_only`.
- **FR-003**: The docs MUST explain that local-only preflight can stop bootstrap or delegated resume before mutation while preserving canonical blocker codes.
- **FR-004**: The docs MUST preserve the boundary that `ship-slice` owns downstream execution stop-policy behavior after delegation starts.
- **FR-005**: The docs MUST stay consistent across `skills/ship/SKILL.md`, the two-step roadmap page, and the throughput-acceleration feature wiki.

## 4. Key Entities

- **Rerun contract**: The operator-facing description of which ship commands only recompute state and which can mutate execution artifacts or delegate work.
- **Preflight mode**: The repo-owned config surface under `accelerators.ship.preflight.mode` that determines whether preflight is off or local-only.
- **Delegation boundary**: The point where `ship` hands control to `ship-slice`, after which downstream stop-policy behavior is no longer owned by ship preflight.

## 5. Edge Cases

- Docs must not imply that every rerun is side-effect free.
- Docs must not claim that preflight creates new blocker kinds or overrides `ship-slice` review-boundary behavior.
- Docs must not suggest remote freshness or host-specific checks are already implemented.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The I1 and I2 slices are complete and represent the shipped contract that docs should now describe.
- **A2**: The operator-facing docs should reflect current behavior, not speculative future preflight modes.

### Dependencies

- **D1**: `spi-preflight-contract` established the typed preflight and readiness payload shape.
- **D2**: `spi-mutation-gating` established pre-mutation blocking with `stop_reason.phase=preflight` for ship-local guardrails.

## 7. Success Criteria

- **SC-001**: A maintainer reading the ship skill can distinguish read-only recomputation, guarded mutation, and delegated side effects.
- **SC-002**: The roadmap and feature wiki explain when preflight runs and what it can block without contradicting the implementation.
- **SC-003**: The three target docs describe one consistent operator contract.

