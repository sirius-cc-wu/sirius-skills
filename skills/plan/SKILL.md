---
name: plan
description: Technical implementation planning expert.
---

# Implementation Planning Skill

Use this skill to convert a `spec.md` into a step-by-step TDD implementation plan (`plan.md`).

## Protocol
1. **Context Scan**: Analyze existing code and relevant interfaces in the target module.
2. **Phase Breakdown**:
   - **Phase 0**: Environment & Baseline (Tests that fail).
   - **Phase 1**: Core Implementation.
   - **Phase 2**: Refinement, Documentation, and Edge Case Tests.
3. **Atomic Steps**: Ensure every step is a discrete, verifiable unit of work.

## Validation
Before finalizing the `plan.md`, check:
- Does every requirement in `spec.md` have a corresponding test step?
- Are file paths resolved according to the project structure?

## Execution Mandate
The `plan.md` is a live tracking document that serves as the direct input for the `implement` skill.

Agents must:
1. Reference the `plan.md` at the start of every implementation session.
2. Mark steps as completed (`[x]`) in `plan.md` as they are finished and verified. This is typically handled by the `implement` skill.
3. Keep the user informed of progress by referencing the plan's milestones.