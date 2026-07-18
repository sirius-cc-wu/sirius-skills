---
name: behavior-preserving-refactoring
description: Improves internal code and design through small, verified transformations without intentionally changing observable behavior. Use when removing duplication, shortening or clarifying code, improving names, cohesion, coupling, responsibilities, or dependency structure behind an adequate passing test suite.
---

# Behavior-Preserving Refactoring

## Overview

Improve internal structure through one small transformation at a time and rerun relevant tests after every step. Preserve public contracts, observable results, state transitions, side effects, and error behavior unless a separate behavior change is explicitly requested.

## When to Use

- Remove duplication, clarify expressions or names, shorten long routines, replace unexplained literals, or simplify control flow.
- Improve responsibility placement, cohesion, coupling, dependency direction, or variation boundaries without changing required behavior.
- Prepare code for a later feature by making its structure easier to change safely.
- Do not mix a refactoring step with an intentional feature, contract, or defect-behavior change.

## Design Guidance

- Use [Test-Driven Implementation](../test-driven-implementation/SKILL.md) to add new behavior and to grow the executable safety net.
- Use [GRASP Responsibility Design](../grasp-responsibility-design/SKILL.md) when a smell indicates misplaced responsibility, low cohesion, or high coupling.
- Use [Design Pattern Application](../design-pattern-application/SKILL.md) only when a named design force justifies added indirection or variation; do not introduce a pattern merely as cleanup vocabulary.
- Use [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md) to choose idiomatic transformations and preserve language-specific ownership, lifecycle, error, and concurrency semantics.
- Update use-case realizations or design class diagrams when refactoring changes durable responsibilities, collaborations, public interfaces, or dependency direction. Do not update them for private local cleanup they intentionally omit.

## Workflow

1. **Define the invariant.** State the observable behavior and public contracts that must remain unchanged. Separate any desired behavior change into another task or test-driven increment.
2. **Inspect the repository and worktree.** Read governance, find established verification commands, and distinguish existing user changes from the intended refactoring.
3. **Establish a green baseline.** Run the focused tests that cover the behavior. If protection is inadequate, add characterization tests for current required behavior before restructuring it.
4. **Name one structural problem.** Identify concrete evidence such as duplication, a long routine, an unclear expression, a large responsibility cluster, high coupling, or an unstable dependency.
5. **Choose one small transformation.** Prefer a local move such as Rename, Extract Function/Method, Extract Constant, Introduce Explaining Variable, simplify a conditional, move one responsibility, or encapsulate one dependency.
6. **Apply only that transformation.** Keep the diff small enough to explain and reverse independently. Preserve behavior instead of redesigning multiple boundaries at once.
7. **Re-execute focused tests.** Run them immediately. If they fail, repair or undo only the current transformation before continuing; do not edit valid expectations to conceal a regression.
8. **Inspect the result.** Confirm that the named problem improved and that the change did not introduce unnecessary indirection, duplication, or semantic drift.
9. **Repeat in small steps.** Chain transformations only while each has a clear purpose and independently verified green state.
10. **Run broader verification.** Execute the relevant regression suite and repository-required static, formatting, lint, or type checks.
11. **Reconcile design artifacts.** Refine durable design records if responsibility, collaboration, interface, or dependency knowledge changed.
12. **Report evidence.** Summarize the preserved behavior, structural improvements, verification commands and results, and any intentionally deferred smell.

## Refactoring Record Template

```markdown
## Refactoring: [Structural outcome]

Behavior Preserved:
- [Public contract or observable result]

Baseline:
- [Focused test command and passing result]

Problem:
- [Concrete smell or design pressure]

Transformations:
1. [Small transformation] -> [focused test result]

Broader Verification:
- [Command and result]

Design Feedback:
- [none, or artifact/decision refined]
```

## Red Flags

- Refactoring begins without a passing baseline or adequate characterization of required behavior.
- A broad rewrite prevents individual transformations from being verified.
- Tests are changed to accept an accidental behavioral difference.
- A design pattern is introduced before its force and cost are stated.
- Generated indirection makes the code longer or harder to understand without improving a named pressure.
- Public interfaces, errors, side effects, ordering, ownership, or concurrency semantics drift unnoticed.
- UML or responsibility records remain stale after a durable structural design change.

## Verification

- [ ] The observable behavior to preserve is explicit.
- [ ] Relevant tests passed before the first transformation.
- [ ] Each transformation addressed one named structural problem.
- [ ] Focused tests ran after every transformation and broader checks passed at the end.
- [ ] No valid expectation was weakened to hide a regression.
- [ ] Language-specific behavior such as ownership, errors, ordering, and concurrency remains intact.
- [ ] Durable design artifacts were updated only when their represented design knowledge changed.
