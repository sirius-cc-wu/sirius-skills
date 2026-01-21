---
name: plan
description: Technical implementation planning expert.
---

# Implementation Planning Skill

Use this skill to convert a `spec.md` into a step-by-step TDD implementation plan.

## Protocol
1. **Context Scan**: Analyze existing code and relevant interfaces in the target module.
2. **Phase Breakdown**:
   - **Phase 0**: Environment & Baseline (Tests that fail).
   - **Phase 1**: Core Implementation.
   - **Phase 2**: Refinement, Documentation, and Edge Case Tests.
3. **Atomic Steps**: Ensure every step is a discrete, verifiable unit of work.

## Validation
Before finalize the `plan.md`, check:
- Does every requirement in `spec.md` have a corresponding test step?
- Are file paths resolved according to the project structure?

## Execution Mandate
The `plan.md` is a live tracking document designed for the `implement` skill. The plan must:
1. Ensure steps are atomic enough for a single `implement` cycle.
2. Be maintained by the `implement` skill (marking `[x]` upon completion).
