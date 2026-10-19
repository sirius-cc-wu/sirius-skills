---
name: code-smell
description: "Diagnose function- and class-level code smells, primitive obsession, feature envy, data clumps, and branching complexity; identifies tactical refactoring opportunities and prescribes canonical Fowler transformations without modifying production code."
---

# Code Smell Diagnostic

## Overview

Diagnose implementation-level and intra-module code smells across functions, methods, classes, and types.
Grounding in the taxonomy of Martin Fowler and Kent Beck (*Refactoring: Improving the Design of Existing Code*, 2nd ed.) and Joshua Kerievsky (*Refactoring to Patterns*).

Identify tactical implementation pressures objectively and prescribe mechanical Fowler refactorings without modifying production code directly.

Read the [Code Smell Catalog](references/code-smell-catalog.md) for concrete symptoms, code patterns, and canonical refactoring remedies across all four smell pillars.

## When to Use

- **Implementation & TDD Refactoring**: Scan newly written or modified functions for local smells before marking a feature or fix complete.
- **Gate 2 Code Qualification**: Audit pull request diffs for micro-level code quality regressions, primitive obsession, or arrow anti-patterns.
- **Targeted Refactoring Prep**: Identify the specific method- or class-level transformation to execute under [`behavior-preserving-refactoring`](../behavior-preserving-refactoring/SKILL.md).
- **Legacy Function Cleanup**: Break down oversized legacy methods before adding new logic.
- **Do not use for**:
  - Subsystem boundaries, cyclic module dependencies, or architectural God modules (route to [`design-smell`](../design-smell/SKILL.md)).
  - Routine automated formatting, variable renames, or lint fixes (route to external `code-simplification` or repository linter).
  - Executing code modifications directly (diagnose only; hand off to [`behavior-preserving-refactoring`](../behavior-preserving-refactoring/SKILL.md)).

## Related Owners

- Use [`behavior-preserving-refactoring`](../behavior-preserving-refactoring/SKILL.md) to execute verified, behavior-preserving transformations behind passing tests.
- Use [`design-smell`](../design-smell/SKILL.md) when the smell spans multiple packages, involves cyclic dependencies, or compromises subsystem boundaries.
- Use [`type-anchored-spec`](../type-anchored-spec/SKILL.md) to replace primitive obsession or ad-hoc validation with compile-time type invariants.
- Use external `code-simplification` for routine line-level deletions, mechanical dead-code pruning, and syntax reduction.

## Workflow

1. **Establish the Analysis Scope.**
   - Focus on specific files, functions, or changesets under review (e.g., `src/service/order.ts` or a PR diff).
   - Read surrounding context to understand local invariants and existing test coverage.

2. **Audit for Bloaters & Parameter Smells.**
   - *Long Function*: Functions exceeding 30–50 lines or containing distinct stages separated by comments.
   - *Long Parameter List*: Functions accepting 4+ positional arguments instead of a cohesive options object.
   - *Primitive Obsession*: Raw primitives used in place of domain concepts with validation rules.
   - *Data Clumps*: Multiple fields repeatedly traveling together across parameters or data structures.

3. **Audit for Couplers & Envy.**
   - *Feature Envy*: Functions accessing data on a collaborator more than their own fields.
   - *Inappropriate Intimacy*: Tightly coupled access to internal fields across classes.
   - *Message Chains*: Law of Demeter violations navigating through chains of accessors (`a.getB().getC()`).

4. **Audit for Control-Flow & Branching Smells.**
   - *Switch / Conditional Obsession*: Repeated `switch` or `if/else` ladders matching on type tags or enums.
   - *Deep Nesting (Arrow Anti-Pattern)*: Code indented >3 levels deep with nested branches or loops.
   - *Temporary Field*: Fields that only hold meaningful state during specific operations.

5. **Audit for Dispensables & Redundancy.**
   - *Dead / Zombie Code*: Unreferenced functions, commented-out logic, unused variables.
   - *Speculative Generality*: Unused abstraction layers, unnecessary generics, or unneeded hooks.
   - *Comments as Deodorant*: Narrative comments explaining convoluted implementation mechanics instead of intent.
   - *Loose Casting*: Unsafe `as` casts or non-null assertions bypassing compiler checks.

6. **Formulate Canonical Fowler Refactorings.**
   - Pair each diagnosed smell with its mechanical remedy:
     - Long Function $\to$ Extract Function.
     - Long Parameter List / Data Clumps $\to$ Introduce Parameter Object / Extract Class.
     - Feature Envy $\to$ Move Function / Method.
     - Switch Obsession $\to$ Replace Conditional with Polymorphism / Discriminated Union.
     - Deep Nesting $\to$ Replace Nested Conditional with Guard Clauses.
     - Dead Code $\to$ Delete Unused Code.

7. **Synthesize the Code Smell Census.**
   - Deliver clear citations: file path, line numbers, and concrete code snippets.
   - Outline the ordered refactoring plan for execution.

## Output

Keep findings with the review notes or PR comments by default. Before creating a standalone artifact, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).

When a standalone report is justified, follow
[Markdown Artifact Frontmatter](../design-repository-artifact-layout/references/markdown-artifact-frontmatter.md)
and use this structure:

```markdown
---
type: "Code Smell Census"
title: "Code Smell Census: [Target File or Component]"
description: "[Identified implementation-level smells and targeted Fowler refactorings]"
status: "[identified | planned | remediated]"
tags: [refactoring, code-smells, clean-code]
---

# Code Smell Census: [Target File or Component]

## Scope
- Target: [file, function, or PR diff range]
- Baseline: [existing test suite status]

## Diagnosed Smells and Evidence

### 1. [Smell Name]: [Function or Identifier]
- **Category**: [Bloaters | Couplers | Control-Flow | Dispensables]
- **Location**: [file:line-range]
- **Symptom**: [Concrete pattern description and code quote]
- **Prescribed Refactoring**: [Fowler refactoring name, e.g., Extract Function, Replace Conditional with Guard Clauses]
- **Safety Precondition**: [Required test coverage before refactoring]

## Targeted Refactoring Sequence
1. [First mechanical step, e.g. Introduce Guard Clauses]
2. [Second mechanical step, e.g. Extract Parameter Object]
3. [Verification check command]
```

## Red Flags

- Escalating local function-level smells into sweeping architecture redesigns (keep local fixes local).
- Confusing architectural boundary leaks with local feature envy (route boundary issues to `design-smell`).
- Recommending refactorings without verifying adequate test coverage or characterization checks.
- Generating style/formatting nits that can be handled automatically by a linter or formatter.
- Attempting to modify production code directly without running verification.

## Verification

- [ ] Every identified smell cites exact file paths and line ranges.
- [ ] Smells are categorized under canonical Fowler categories (Bloaters, Couplers, Control-Flow, Dispensables).
- [ ] Each smell is paired with a specific Fowler/Kerievsky refactoring technique.
- [ ] Refactorings preserve observable behavior and do not alter public contracts.
- [ ] Any standalone record passes the artifact budget and uses the required frontmatter.
