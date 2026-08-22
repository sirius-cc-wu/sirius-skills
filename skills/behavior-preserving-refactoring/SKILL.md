---
name: behavior-preserving-refactoring
description: Improves responsibility, dependency, and configuration structure through risk-calibrated, verified transformations without changing observable behavior. Use when moving a cohesive responsibility to an existing owner, correcting coupling or dependency direction, or consolidating configuration ownership behind adequate checks; route routine clarity cleanup to external code-simplification and boundary-sensitive redesign to iterative coordination.
---

# Behavior-Preserving Refactoring

## Overview

Improve established design structure without changing observable behavior.
Preserve public contracts, results, state transitions, side effects, errors,
ordering, ownership, and concurrency semantics.

Read [Configuration Surface Governance](references/config-surface-governance.md)
when work touches configuration, startup, compatibility boundaries, environment
injection, or test harness inputs.

## When to Use

- Resolve a review finding or direct request by moving a cohesive
  responsibility to an existing owner.
- Correct coupling, dependency direction, or variation ownership when the
  intended boundaries are already established.
- Consolidate raw configuration translation into an existing typed owner.
- Reconcile durable design knowledge after one of these structural changes.
- Do not use for an intentional behavior, contract, or defect change.

## Related Owners

- Use external `code-review-and-quality` with the `all` installation for formal
  review. Route its routine naming, extraction, duplication, control-flow, or
  recent-code clarity findings to external `code-simplification`. Otherwise,
  use repository-native review and cleanup.
- Use external `test-driven-development` with the `all` installation for new
  behavior or a larger executable safety net. Otherwise, follow repository
  implementation and verification guidance.
- Use [GRASP Responsibility Design](../grasp-responsibility-design/SKILL.md)
  when the intended responsibility owner is unresolved.
- Use [Design Pattern Application](../design-pattern-application/SKILL.md) only
  when a demonstrated force justifies new indirection or variation.
- Use
  [Software Design Language Adaptation](../software-design-language-adaptation/SKILL.md)
  when language semantics constrain a safe transformation.
- Use `iterative-risk-driven-development` when work creates or moves a material
  test seam, composition root, backend, entrypoint, process-global dependency,
  runtime owner, readiness condition, resource lifecycle, or cleanup boundary.

## Workflow

1. **Fix the invariant and scope.** State the behavior to preserve. Read
   repository governance and separate unrelated work.
2. **Establish a green baseline.** Run focused checks. Add characterization
   checks for required current behavior when protection is inadequate.
3. **Name one structural pressure.** Cite evidence of misplaced responsibility,
   high coupling, unstable dependency direction, a parallel configuration
   control plane, or a variation boundary with the wrong owner.
4. **Classify boundary impact.** Route boundary-sensitive work to
   `iterative-risk-driven-development`. Do not hide system redesign inside a
   local refactoring.
5. **Choose one transformation.** Move one responsibility to its established
   owner, encapsulate a dependency behind an existing boundary, consolidate
   configuration translation, or align dependency direction with established
   design. Batch only homogeneous mechanical edits that share one rule and
   verification boundary.
6. **Apply and verify.** Run focused checks after each transformation or bounded
   batch. Repair or undo a failing step without weakening valid expectations.
7. **Run broader checks.** Execute the relevant regression, static, formatting,
   lint, and type checks. Retain a material integration or end-to-end oracle.
8. **Reconcile durable knowledge.** Update existing design artifacts only when
   represented responsibility, collaboration, interface, dependency, ownership,
   or verification knowledge changed.
9. **Report evidence.** Summarize the invariant, structural pressure,
   transformation, verification, completion boundary, and deferred risk.

## Output

Keep evidence with the changed code and checks by default. Before creating a
separate record, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).

When a standalone record is justified, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use this compact shape:

```markdown
---
type: "Refactoring Record"
title: "Refactoring: [Structural outcome]"
description: "[Verified responsibility, dependency, or configuration change]"
status: "[planned | verified | blocked]"
tags: [refactoring, verification]
---

# Refactoring: [Structural outcome]

- Behavior preserved: [invariant]
- Structural pressure: [evidence]
- Transformation: [bounded change]
- Verification: [focused and broader commands and results]
- Design feedback: [updated owner or none]
```

## Red Flags

- Routine clarity cleanup is routed here instead of to `code-simplification` or
  repository-native cleanup.
- Work starts without a passing baseline or adequate characterization.
- A batch combines semantic or independently changing edits.
- Tests are weakened to accept a behavioral difference.
- A boundary-sensitive change is treated as local.
- Configuration gains a second control plane instead of one typed owner.
- Durable design knowledge remains stale after structural ownership changes.

## Verification

- [ ] The preserved behavior and structural pressure are explicit.
- [ ] Focused checks passed before and after each transformation or bounded
      batch.
- [ ] The change follows one established responsibility, dependency, variation,
      or configuration boundary.
- [ ] Boundary-sensitive work returned to coordinated development.
- [ ] No valid expectation or observable behavior changed.
- [ ] Broader checks and any material end-to-end oracle pass.
- [ ] Configuration retains one typed owner and control plane.
- [ ] Durable design artifacts changed only when their represented knowledge
      changed.
- [ ] Any standalone record passes the artifact budget and uses the required
      frontmatter.
