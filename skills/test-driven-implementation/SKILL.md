---
name: test-driven-implementation
description: Implements scoped behavior through a test-first red-green-refactor loop. Use when adding or changing production behavior from use cases, operation contracts, use-case realizations, design classes, acceptance examples, or bug reports and executable verification can drive the implementation.
---

# Test-Driven Implementation

## Overview

Implement one observable behavior at a time: demonstrate its absence with a focused test, make that test pass with the smallest production change, then improve the structure while the tests stay green. Use discoveries from executable examples to clarify interfaces and refine implementation-facing design.

## When to Use

- Add or change behavior whose expected result can be expressed as an executable example.
- Translate an operation contract, realized collaboration, design operation, acceptance example, or bug report into production code.
- Clarify a detailed interface by exercising it from a caller's perspective before implementing it.
- Do not use test-first mechanics to guess at missing business rules; resolve material requirement ambiguity first.

## Design Inputs and Feedback

- Start from the smallest available source of expected behavior. Do not require every upstream artifact for a small change.
- Use [Operation Contracts](../operation-contracts/SKILL.md) when domain state changes need precise postconditions.
- Use [GRASP Responsibility Design](../grasp-responsibility-design/SKILL.md), [Use-Case Realization](../use-case-realization/SKILL.md), and [UML Class Diagram Design](../uml-class-diagram-design/SKILL.md) when responsibility, collaboration, or interface ownership is unclear.
- Use [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md) to express the design and tests with native language constructs.
- Feed discoveries back into durable contracts, realizations, or design class diagrams when implementation changes their externally relevant postconditions, responsibilities, collaborations, or interfaces.

## Workflow

1. **Inspect the repository.** Read governance and neighboring tests; identify the established test framework, commands, naming, fixtures, and test level.
2. **Select one behavior.** State one concrete input, action, and observable result traceable to the requirement, contract, design artifact, or defect.
3. **Choose a stable test boundary.** Prefer the narrowest boundary that proves the behavior without coupling the test to private structure. Use a broader test when the behavior crosses a meaningful integration boundary.
4. **Write one focused test.** Arrange the relevant context, invoke the intended public surface, and assert the observable result. Include only the setup needed for this behavior.
5. **Observe a meaningful failure.** Run the focused test and confirm that it fails because the behavior is absent or incorrect. Fix test setup errors until the failure demonstrates the intended gap; reconsider a test that already passes.
6. **Make the smallest production change.** Implement enough behavior to pass the test. Defer speculative generalization and unrelated cleanup.
7. **Return to green.** Run the focused test, then the smallest relevant regression set. Diagnose failures rather than weakening valid expectations.
8. **Improve structure safely.** Remove immediate duplication or clarify names and expressions while green. For non-trivial cleanup, use [Behavior-Preserving Refactoring](../behavior-preserving-refactoring/SKILL.md).
9. **Repeat incrementally.** Add the next behavior, boundary case, or failure mode one test at a time; do not write the entire test suite before implementing any behavior.
10. **Reconcile design knowledge.** Update affected durable design artifacts only when the executable design changes information those artifacts are meant to preserve.
11. **Report verification.** Record the behavior covered, focused and regression commands run, results, and any design feedback or remaining gap.

## Behavior Slice Template

```markdown
## Behavior: [Concise outcome]

Source:
- [Use case step, contract postcondition, design operation, acceptance example, or defect]

Example:
- Given: [initial context]
- When: [action]
- Then: [observable result]

Test Boundary:
- [Public surface and test level]

Red Evidence:
- [Command and expected failure reason]

Green Evidence:
- [Focused and regression commands with results]

Design Feedback:
- [none, or artifact/decision to refine]
```

## Red Flags

- Production code is written before any test demonstrates the behavioral gap.
- A test fails because of broken setup, compilation, or infrastructure rather than the intended missing behavior.
- Tests assert private calls, internal fields, or exact collaboration structure without a contractual reason.
- Every production class or public method receives a test mechanically, regardless of meaningful behavior.
- Mocks replace simple collaborators or duplicate implementation logic in expectations.
- A large batch of tests is written before any one behavior is made to pass.
- A passing test is weakened to accommodate an unintended production result.

## Verification

- [ ] Each increment traces to a requirement, contract, design decision, example, or defect.
- [ ] Each new test was observed failing for the intended reason before production behavior was added.
- [ ] Tests exercise observable behavior through a stable boundary.
- [ ] The smallest relevant regression set passes after each increment.
- [ ] Structural cleanup occurred only while protected by passing tests.
- [ ] Design artifacts were refined when durable responsibilities, collaborations, interfaces, or postconditions changed.
- [ ] Final verification commands and results are reported.
