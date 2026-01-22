---
name: plan
description: Technical implementation planning expert.
---

# Implementation Planning Skill

Use this skill to convert a `spec.md` into a step-by-step TDD implementation plan. This is the bridge between requirements and execution.

## Step-by-Step TDD Protocol
1. **Context Scan**: Analyze existing code and relevant interfaces in the target module.
2. **Phase Breakdown**:
   - **Phase 0**: Environment & Baseline (Define tests that *should* fail initially).
   - **Phase 1**: Core Implementation (Small, discrete logic units).
   - **Phase 2**: Refinement, Documentation, and Edge Case Tests.
3. **Atomic Steps**: Ensure every step is a discrete, verifiable unit of work.

## Validation Checklist
Before finalizing `plan.md`, verify:
- Does every requirement in `spec.md` have a corresponding test step?
- Are file paths resolved according to the project structure?
- Is the plan formatted as a checklist that `implement` can track?

## Handoff
Once the `plan.md` is approved, the lifecycle transitions to `implement`.
