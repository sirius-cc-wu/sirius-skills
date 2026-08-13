---
name: behavior-driven-specification
description: Turns approved or explicitly candidate behavior into shared, example-based Given/When/Then scenarios and acceptance examples. Use when behavior needs stakeholder-readable examples, boundary cases, or traceable acceptance criteria before implementation.
---

# Behavior-Driven Specification

## Overview

Behavior-Driven Development (BDD) makes system behavior concrete through
shared examples. This skill turns a bounded behavior into observable scenarios
that stakeholders, analysts, developers, and testers can discuss consistently.

The scenarios may use Given/When/Then wording, plain Markdown, or an existing
repository format. BDD is a specification and collaboration practice, not a
requirement to install a Gherkin runner or replace the repository's test
framework.

## When to Use

- An approved or explicitly candidate requirement needs concrete examples.
- A feature brief or use case needs success, alternate, failure, or boundary
  scenarios before implementation.
- Stakeholders and implementers need a shared vocabulary for observable
  behavior.
- Existing examples are incomplete, ambiguous, duplicated, or not traceable to
  their source requirements.
- A testable acceptance boundary needs to be separated from implementation
  details.
- Do not use when stakeholder evidence, authority, or conflicting policies
  still need discovery or validation; use
  [`requirements-synthesis-validation`](../requirements-synthesis-validation/SKILL.md)
  or [`stakeholder-requirements-elicitation`](../stakeholder-requirements-elicitation/SKILL.md).
- Do not use when actors, goals, or the system boundary are missing; use
  [`use-case-modeling`](../use-case-modeling/SKILL.md).
- Do not use to specify non-trivial state effects; use
  [`operation-contracts`](../operation-contracts/SKILL.md).
- Do not use to implement behavior or create the test suite; use
  [`test-driven-implementation`](../test-driven-implementation/SKILL.md).
- Do not use to recover current as-built behavior from evidence; use
  [`recover-system-behavior`](../recover-system-behavior/SKILL.md).

## Design Inputs and Handoffs

- Preserve the source artifact's lifecycle, approval state, authority, open
  questions, non-goals, and unresolved uncertainty.
- Treat a scenario as a concrete example of a rule, not as permission to
  invent or approve the rule.
- Keep actor goals and system boundaries owned by use-case modeling.
- Keep state changes, created objects, associations, and postconditions owned
  by operation contracts when they need more precision than the scenario.
- Feed implementation discoveries back into the owning requirements or design
  artifact instead of silently changing a scenario's meaning.

## Workflow

1. **Read the source and repository guidance.** Identify the canonical
   requirements, use case, proposal, bug report, contract, or approved example
   and record its lifecycle and authority.
2. **Set the behavior boundary.** Name the actor or caller, system under
   discussion, trigger, observable output, and relevant external dependency.
   Do not describe private classes, database queries, or internal messages as
   scenario steps.
3. **Extract the rules and partitions.** Identify the main success case,
   meaningful alternate and failure paths, invalid inputs, boundary values,
   concurrency or retry cases, and important quality constraints. Select only
   the partitions justified by risk and scope.
4. **Write concrete examples.** Use one behavior per scenario:
   `Given` establishes relevant context, `When` names the actor or system
   action, and `Then` states observable outcomes. Use `And` only to extend the
   same phase. Prefer concrete values when they clarify the rule.
5. **Check scenario quality.** Ensure each scenario is deterministic enough to
   review, uses domain vocabulary, exposes the expected result or state, and
   does not prescribe an implementation. Split scenarios when different rules,
   outcomes, or failure causes are hidden behind one flow.
6. **Expose uncertainty.** Mark missing decisions, conflicting authorities,
   assumptions, and unverified examples. Ask for the owning decision rather
   than selecting a policy or promoting a candidate requirement to approved
   behavior.
7. **Trace the examples.** Link each scenario to its source rule, use case,
   contract, defect, or decision. Record the intended verification boundary
   and any scenario that remains unimplemented or human-owned.
8. **Choose the canonical location.** Apply the
   [Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
   Prefer the existing requirements brief, use case, acceptance section, or
   test file. Create a standalone scenario artifact only when it has distinct
   ownership, review value, and lifecycle.
9. **Hand off without overreaching.** Send approved scenarios to
   [`implementation-slice-briefing`](../implementation-slice-briefing/SKILL.md)
   or [`test-driven-implementation`](../test-driven-implementation/SKILL.md).
   Use [`operation-contracts`](../operation-contracts/SKILL.md) when examples
   reveal effects that require a precise contract.

## Scenario Template

When the repository does not already define a scenario format, use this shape
inside the canonical requirements or use-case artifact:

```markdown
### Scenario: [Observable outcome]

- Source: [requirement, rule, use case, contract, defect, or decision]
- Status: [candidate | approved | verified | blocked]

**Given** [relevant starting context]
**And** [additional context when needed]
**When** [actor or system action]
**Then** [observable outcome]
**And** [additional outcome when needed]
```

For a standalone Markdown artifact, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md):

```markdown
---
type: "Behavior Specification"
title: "[Behavior name]"
description: "[One sentence naming the observable behavior covered]"
id: "[Stable ID when cross-referenced]"
status: "[draft | candidate | approved | verified | blocked]"
tags: [requirements, behavior, acceptance]
---

# Behavior: [Behavior name]

## Boundary and Rule

- Actor or caller: [role]
- System: [system under discussion]
- Rule: [behavioral rule]

## Scenarios

### Scenario: [Observable outcome]

- Source: [traceable source]
- Status: [candidate | approved | verified | blocked]

**Given** [context]
**When** [action]
**Then** [observable result]

## Open Questions

- [Unresolved decision or missing example]
```

## BDD and Verification

BDD scenarios are an implementation-independent oracle when their expected
outcomes come from an authoritative source. They become executable evidence
only when a repository check, test runner, contract check, or other mechanical
verification actually evaluates them.

Use [`test-driven-implementation`](../test-driven-implementation/SKILL.md) to
turn approved scenarios into focused checks and production changes. Record
whether a scenario is merely specified, mechanically verified, or still
dependent on hardware, Docker, privileged services, or human review.

## Red Flags

- A scenario invents a business rule, resolves an authority conflict, or
  changes an approval state.
- Given/When/Then steps describe controllers, classes, SQL, mocks, or private
  method calls instead of observable behavior.
- One scenario hides several independent rules or failure causes.
- Only the happy path is covered when failure, boundary, retry, security, or
  concurrency behavior is material.
- A scenario uses vague outcomes such as "the system works" without a visible
  result, state, message, or error.
- Gherkin syntax is introduced as a tooling requirement when the repository has
  no scenario runner or the user did not request one.
- Scenarios duplicate a canonical requirements or use-case artifact without
  adding examples, traceability, or verification value.
- A passing scenario is treated as proof of implementation without executable
  or mechanical evidence.

## Verification

- [ ] The source, lifecycle, authority, and unresolved uncertainty are
  preserved.
- [ ] The actor, system boundary, trigger, and observable outcomes are clear.
- [ ] Main success, material alternate, failure, and boundary examples are
  covered at a risk-appropriate level.
- [ ] Each scenario expresses one behavior without prescribing internals.
- [ ] Each scenario traces to a requirement, rule, use case, contract, defect,
  or decision.
- [ ] Candidate, approved, verified, and blocked states are not conflated.
- [ ] The canonical artifact remains the source of truth or the standalone
  artifact has distinct ownership and lifecycle.
- [ ] Mechanical verification is distinguished from prose specification and
  human-owned validation.
- [ ] The handoff to requirements, contract, implementation, or test skills is
  explicit when further work is needed.
