---
name: test-driven-implementation
description: Implements scoped behavior through risk-calibrated, test-first verification. Use when adding or changing production behavior from use cases, operation contracts, use-case realizations, design classes, acceptance examples, or bug reports and executable examples, properties, invariants, or other mechanical checks can anchor the implementation.
---

# Test-Driven Implementation

## Overview

Implement a risk-sized slice of observable behavior: establish an implementation-independent oracle, demonstrate that its checks discriminate missing or incorrect behavior, make the smallest coherent production change, then improve the structure while verification stays green. Prefer short feedback loops without forcing every related test through its own isolated red-green cycle.

## When to Use

- Add or change behavior whose expected result can be expressed as an executable example, property, invariant, or other mechanical constraint.
- Translate an operation contract, realized collaboration, design operation, acceptance example, or bug report into production code.
- Clarify a detailed interface by exercising it from a caller's perspective before implementing it.
- For a trivial mechanical change already protected by adequate checks, use the existing verification instead of manufacturing a new failing test.
- Do not use test-first mechanics to guess at missing business rules; resolve material requirement ambiguity first.

## Design Inputs and Feedback

- Start from the smallest available source of expected behavior. Derive expected outcomes from requirements, contracts, approved examples, or independent reference behavior rather than from the production logic under test.
- Treat a prose specification as design input, not executable evidence, until a tool can mechanically check it.
- Use [Operation Contracts](../operation-contracts/SKILL.md) when domain state changes need precise postconditions.
- Use [GRASP Responsibility Design](../grasp-responsibility-design/SKILL.md), [Use-Case Realization](../use-case-realization/SKILL.md), and [UML Class Diagram Design](../uml-class-diagram-design/SKILL.md) when responsibility, collaboration, or interface ownership is unclear.
- Use [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md) to express the design and tests with native language constructs.
- Feed discoveries back into durable contracts, realizations, or design class diagrams when implementation changes their externally relevant postconditions, responsibilities, collaborations, or interfaces.

## Calibrate the Slice

- Use a narrow behavior slice for ambiguous requirements, novel algorithms, defect reproduction, security or financial rules, concurrency, irreversible effects, and other high-risk work.
- Use a small coherent group of examples or properties for a well-specified vertical behavior whose checks share one stable boundary and implementation change.
- Use existing regression and static checks for a low-risk mechanical change when a new failing test would add no discriminatory evidence.
- Shrink the slice when failures would be hard to localize or the implementation would span unrelated responsibilities. Do not default to a comprehensive test suite followed by a whole-module implementation.

## Workflow

1. **Inspect the repository.** Read governance and neighboring tests; identify the established framework, commands, naming, fixtures, test levels, and non-test verification tools.
2. **Define the oracle.** State the inputs, action, expected results, postconditions, properties, or invariants and trace them to a source independent of the production implementation.
3. **Size the behavior slice.** Use risk, uncertainty, reversibility, and failure locality to choose one example, a small coherent group, or existing verification.
4. **Choose a stable verification boundary.** Prefer the narrowest public boundary that proves the behavior without coupling checks to private structure. Use a broader boundary when the behavior crosses a meaningful integration.
5. **Write focused checks.** Express the oracle with the most suitable combination of example tests, properties, invariants, differential comparisons, type constraints, or static analysis.
6. **Demonstrate discrimination.** Before adding behavior, obtain evidence that the checks can detect its absence or an incorrect result. Prefer an intended behavioral failure; use a negative control, mutation, or reference comparison when an ordinary red run is not informative. Do not count incidental setup or compilation failure as behavioral evidence.
7. **Make the smallest coherent production change.** Implement enough behavior to satisfy the slice. Defer speculative generalization and unrelated cleanup.
8. **Return to green.** Run the focused checks, then the smallest relevant regression set. Run the broader repository suite at an appropriate checkpoint. Diagnose failures rather than weakening valid expectations.
9. **Improve structure safely.** Remove immediate duplication or clarify names and expressions while green. For non-trivial cleanup, use [Behavior-Preserving Refactoring](../behavior-preserving-refactoring/SKILL.md).
10. **Repeat incrementally.** Add the next behavior slice, boundary case, or failure mode. Split work further whenever feedback becomes ambiguous or slow.
11. **Reconcile design knowledge.** Update affected durable design artifacts only when the executable design changes information those artifacts are meant to preserve.
12. **Report verification.** Record the oracle source, slice-size rationale, discrimination evidence, focused and regression commands, results, and any design feedback or remaining gap.

## Behavior Slice Template

```markdown
## Behavior: [Concise outcome]

Risk and Slice Size:
- [risk/uncertainty and why this increment is appropriately sized]

Oracle:
- Source: [use case, contract, design operation, approved example, invariant, reference, or defect]
- Expected: [observable result, property, or mechanical constraint]

Checks:
- [stable boundary and example/property/static mechanism]

Discrimination Evidence:
- [command, negative control, mutation, or comparison and detected gap]

Green Evidence:
- [Focused and regression commands with results]

Design Feedback:
- [none, or artifact/decision to refine]
```

## Red Flags

- Expected results are copied from or calculated with the production logic under test.
- A prose specification is treated as verification without an executable or mechanical check.
- A setup, compilation, or infrastructure failure is accepted as proof of semantic behavior.
- A comprehensive suite and whole-module implementation obscure which check detects which behavioral gap.
- Every related test is forced through an isolated red cycle without adding discriminatory evidence.
- Tests assert private calls, internal fields, or exact collaboration structure without a contractual reason.
- Every production class or public method receives a test mechanically, regardless of meaningful behavior.
- Mocks replace simple collaborators or duplicate implementation logic in expectations.
- A passing test is weakened to accommodate an unintended production result.

## Verification

- [ ] Each behavior slice traces to a requirement, contract, approved example, invariant, reference, or defect.
- [ ] The oracle is derived independently from the production implementation.
- [ ] Slice size is justified by risk, uncertainty, reversibility, and failure locality.
- [ ] Each new behavior has evidence that its checks discriminate an absent or incorrect implementation; individual tests need not each receive an isolated red run.
- [ ] Checks exercise observable behavior through a stable boundary and use non-test verification where it adds confidence.
- [ ] Focused checks and the smallest relevant regression set pass after each slice; broader verification passes at the chosen checkpoint.
- [ ] Structural cleanup occurred only while protected by passing tests.
- [ ] Design artifacts were refined when durable responsibilities, collaborations, interfaces, or postconditions changed.
- [ ] Final verification commands and results are reported.
