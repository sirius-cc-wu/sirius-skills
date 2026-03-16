---
name: plan
description: Technical implementation planning expert.
---

# Implementation Planning Skill

Use this skill to convert `spec.md` into a decision-complete implementation bundle.

## Required Outputs

Write planning artifacts into the active track directory resolved by `spec-driver` tooling.

1. `<track_path>/plan.md` (required)
2. `<track_path>/research.md` (required for unresolved constraints/tradeoffs)
3. `<track_path>/data-model.md` (required when feature includes data entities)
4. `<track_path>/contracts/` (required when feature exposes interfaces)
5. `<track_path>/quickstart.md` (required verification scenarios)

Use templates from `skills/plan/templates/`.

## Protocol
1. **Track Resolution**: Use `spec-driver` tooling to resolve the active track before planning.
2. **Context Scan**: Analyze existing code and relevant interfaces in the target module.
3. **Gates First**:
    - **Architecture/Constraints Gate**: Stack and structural constraints are explicit.
    - **Risk/Compliance Gate**: Security, data retention, and compliance risks are called out.
    - **Testability Gate**: Every requirement can be validated.
4. **Phase Breakdown**:
    - **Phase 0**: Baseline, environment, and unknown resolution.
    - **Phase 1**: Core implementation packets.
    - **Phase 2**: Refinement, docs, and edge-case coverage.
5. **Atomic Steps**: Every step is discrete, verifiable, and mapped to requirement IDs.

## Validation
Before finalizing, check:

1. Every requirement in `spec.md` maps to:
    - one or more implementation steps
    - one or more validation steps
2. File paths are resolved against the project structure and the active `<track_path>`.
3. All failed gates are either fixed or explicitly waived with rationale.
4. The plan is executable without extra design decisions.

## `plan.md` Requirements

`<track_path>/plan.md` must include:

1. Technical context and assumptions
2. Gate outcomes
3. FR-to-step traceability table
4. Execution packets with:
   - packet ID
   - scope
   - file targets
   - validation steps
   - definition of done
   - rollback/mitigation notes

## Execution Mandate
The planning bundle is a live implementation contract.

Agents must:
1. Reference `<track_path>/plan.md` at the start of each implementation session.
2. Mark steps as completed (`[x]`) in `<track_path>/plan.md` (and `<track_path>/tasks.md` if present) after verification.
3. Keep users informed using packet-level milestones.

## Implementation Capability Requirement

Implementation is assumed to run on coding agents with internal implementation capability.

Use that internal capability as the default execution path for all `<track_path>/plan.md` packets.
