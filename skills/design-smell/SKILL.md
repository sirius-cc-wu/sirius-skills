---
name: design-smell
description: "Diagnose architectural, modularization, encapsulation, abstraction, and hierarchy design smells across subsystems, packages, or component boundaries; identifies structural pressures and prescribes target architectural remedies before refactoring or during Gate 1 design reviews."
---

# Design Smell Diagnostic

## Overview

Diagnose structural, modularization, encapsulation, abstraction, and hierarchy design smells across subsystems, packages, or component boundaries.
Grounding in the taxonomy of Girish Suryanarayana, Ganesh Samarthyam, and Tushar Sharma (*Refactoring for Software Design Smells: Managing Technical Debt*).

Identify structural pressures objectively and prescribe target architectural remedies ("Code Judo" moves) without modifying production code.

Read the [Design Smell Catalog](references/design-smell-catalog.md) for concrete symptoms, code patterns, and canonical architectural remedies across all four smell pillars.

## When to Use

- **Gate 1 Design Review**: Audit candidate architecture, specifications, or proposed module boundaries against structural degradation before implementation.
- **Before Structural Refactoring**: Diagnose the exact structural pressure required by Step 3 of [`behavior-preserving-refactoring`](../behavior-preserving-refactoring/SKILL.md).
- **PR & Boundary Audit**: Evaluate pull requests that cross package boundaries, add ad-hoc dependencies, or threaten to introduce God modules or cyclic dependencies.
- **Subsystem Health Assessment**: Uncover architectural debt, hidden couplings, or leaky abstractions in unfamiliar codebases.
- **Do not use for**:
  - Local syntax, routine naming, or micro-level cleanup within a single function (route to external `code-simplification` or `code-smell`).
  - Intentional feature behavior changes or requirement additions (route to iterative design playbooks).
  - Executing code modifications directly (diagnose only; hand off to [`behavior-preserving-refactoring`](../behavior-preserving-refactoring/SKILL.md) or [`architecture-decision-records`](../architecture-decision-records/SKILL.md)).

## Related Owners

- Use [`behavior-preserving-refactoring`](../behavior-preserving-refactoring/SKILL.md) to implement verified structural changes once the target architecture is selected.
- Use [`architecture-decision-records`](../architecture-decision-records/SKILL.md) to record irreversible architectural boundary changes or invariant modifications.
- Use [`doubt-driven-development`](../doubt-driven-development/SKILL.md) for fresh-context adversarial review during Gate 1.
- Use [`type-anchored-spec`](../type-anchored-spec/SKILL.md) when the remedy requires compile-time typestate, phantom types, or sealed traits.
- Use [`design-rust-lifecycles`](../design-rust-lifecycles/SKILL.md) when the smell involves resource lifecycles, startup rollback, or cancellation boundaries.

## Workflow

1. **Establish the Analysis Boundary and Scope.**
   - Define the target subsystem, package boundary, or changeset (e.g. `src/domain/`, `crates/storage/`, or a PR diff).
   - Gather boundary facts: package import graphs, public interface exports, dependency flow directions, and file size distributions.

2. **Audit for Abstraction Smells.**
   - *Missing Abstraction*: Primitive obsession, raw strings/tuples representing domain concepts, scattered shape validations.
   - *Imperfect Abstraction*: Interfaces exposing operations misaligned with their named role, forcing callers into manual orchestration.
   - *Multifaceted Abstraction*: Components with multiple unrelated reasons to change (SRP violation, high fan-out).
   - *Duplicate Abstraction*: Parallel model hierarchies or duplicated domain representations across boundaries.

3. **Audit for Encapsulation Smells.**
   - *Leaky Encapsulation*: Exposing internal collections, locks, or database schemas directly through public interfaces.
   - *Missing Encapsulation*: Data structures with all public fields and zero invariant enforcement, manipulated procedurally by external modules.
   - *Unexploited Encapsulation*: Callers inspecting variant tags or type codes via ad-hoc `switch`/`if-else` branches.

4. **Audit for Modularization Smells.**
   - *Broken Modularization*: Cohesive data and operations split across modules, causing Shotgun Surgery across unrelated directories.
   - *Cyclic Dependencies*: Bidirectional or circular imports coupling module lifecycles.
   - *Insufficient Modularization (God Module / Blob)*: Files crossing 1,000+ lines centralizing all logic while surrounding modules remain passive.
   - *Hub-like Modularization*: Central clearinghouse modules with high fan-in and fan-out creating systemic ripple effects.

5. **Audit for Hierarchy and Coupling Smells.**
   - *Speculative Hierarchy*: Complex trait/inheritance layers with only a single implementation.
   - *Deep Hierarchy*: Excessively nested wrapper chains (>3 levels) creating reader indirection without value.
   - *Rebellious Hierarchy*: Subtypes throwing on or violating parent contracts (LSP violation).
   - *Multipath Coupling*: Redundant channels of communication between two components causing race conditions.

6. **Prescribe Architectural Remedies ("Code Judo").**
   - For each confirmed smell, formulate the simplest structural reframing that removes the complexity rather than shifting it around.
   - Map each finding to a concrete remedy (e.g., Dependency Inversion, Vertical Slice Decomposition, Encapsulate Boundary, Discriminated Union Dispatch).

7. **Synthesize the Design Smell Diagnostic.**
   - Prioritize findings by severity and blast radius: Presumptive Blockers (Modularization & Boundary leaks) $\to$ Abstraction & Hierarchy $\to$ Local coupling.
   - Deliver clear evidence citations: line numbers, import statements, and structural measurements.

## Output

Keep findings with the review summary by default. Before creating a standalone artifact, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).

When a standalone report is justified, follow
[Markdown Artifact Frontmatter](../design-repository-artifact-layout/references/markdown-artifact-frontmatter.md)
and use this structure:

```markdown
---
type: "Design Smell Diagnostic"
title: "Design Smell Diagnostic: [Target Subsystem or PR]"
description: "[Identified architectural and structural smells with prescribed remedies]"
status: "[identified | planned | remediated]"
tags: [architecture, design-smells, refactoring]
---

# Design Smell Diagnostic: [Target Subsystem or PR]

## Scope and Boundary
- Target: [path, subsystem, or PR range]
- Focus: [Abstraction | Encapsulation | Modularization | Hierarchy]

## Diagnosed Smells and Evidence

### 1. [Smell Name]: [Affected Component or Boundary]
- **Category**: [Abstraction | Encapsulation | Modularization | Hierarchy]
- **Severity**: [Blocker | High | Moderate]
- **Evidence**: [file, line numbers, import cycles, or metric citations]
- **Structural Pressure**: [Why this compromises maintainability, cohesion, or evolvability]
- **Prescribed Remedy**: [Concrete architectural move, e.g. Ports & Adapters, Vertical Decomposition]

## Recommended Refactoring Sequence
1. [First structural transformation to eliminate cyclic dependency or God module]
2. [Subsequent boundary encapsulation]
3. [Durable ADR or specification updates required]
```

## Red Flags

- Flagging localized naming, small functions, or formatting nits as "design smells" (route to `code-simplification`).
- Recommending complex new abstraction layers for hypothetical future requirements (violates the Speculative Hierarchy rule).
- Diagnosing a smell without providing the concrete architectural remedy.
- Proposing code edits directly without passing through a verified refactoring gate or ADR.
- Treating working but brittle spaghetti code as acceptable merely because existing tests pass.

## Verification

- [ ] Every identified smell cites concrete evidence (file paths, lines, import paths, or fan-in/fan-out metrics).
- [ ] Smells are categorized under the four canonical pillars (Abstraction, Encapsulation, Modularization, Hierarchy).
- [ ] Each smell is paired with a specific, actionable architectural remedy ("Code Judo" move).
- [ ] Findings clearly separate macro-architectural smells from localized code-level issues.
- [ ] Prescribed remedies preserve system invariants and identify necessary ADR or boundary updates.
- [ ] Any standalone record passes the artifact budget and uses the required frontmatter.
