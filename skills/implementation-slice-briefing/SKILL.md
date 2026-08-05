---
name: implementation-slice-briefing
description: Selects a coherent vertical behavior slice and packages its approved requirements, examples, decisions, repository facts, design inputs, source revisions, verification, non-goals, and stop conditions into a coding-agent-ready brief. Use when implementation knowledge already exists but an unfamiliar implementer needs a bounded, traceable handoff that must not invent missing business rules or architecture.
---

# Implementation Slice Briefing

## Overview

Assemble the smallest ready behavior slice an unfamiliar coding agent can
implement and verify without guessing. Preserve the meaning, approval state,
and revision of every source. Produce a handoff brief only; do not implement the
slice or manufacture the decisions needed to make it look ready.

## When to Use

- Approved requirements and examples exist, but they span more behavior than
  one implementation increment should own.
- Requirements, use cases, contracts, design decisions, and repository facts
  need one traceable implementation handoff.
- A coding agent needs explicit in-scope behavior, non-goals, verification, and
  conditions that require it to stop.
- A prior implementation brief may be stale because a source revision, status,
  decision, or repository boundary changed.
- Do not use to elicit or approve requirements, create missing analysis or
  design, write production code, or execute the implementation workflow.

## Source and Authority Discipline

Treat approved requirements, examples, and decisions as the oracle for intended
behavior. Treat repository inspection as evidence about the current codebase,
not client intent. Preserve opaque identifiers and exact source revisions or
commit IDs. Approval is revision-specific: a later source change makes the
dependent brief stale until it is reconciled.

Do not promote `candidate`, `validated`, `contested`, or superseded material to
an implementation expectation. It may appear only as an explicit exclusion,
dependency, risk, or stop condition. When approval vocabulary differs, record
the repository's original state and the evidence that it is authorized for the
slice.

Carry source sensitivity, access, retention, and publication restrictions into
the handoff. Copy only sanitized requirements and examples whose intended use
permits implementation briefing. Link to protected evidence without reproducing
raw participant, contractual, operational, or commercial details. If the brief
cannot expose enough authorized information for safe implementation, mark it
blocked and route the publication or access decision to its owner.

## Readiness Gate

A slice is ready only when all behavior it requires has:

- an approved outcome and system boundary;
- approved scenarios, examples, rules, constraints, and quality expectations
  needed to determine success and important failure behavior;
- the necessary analysis or design decisions for its implementation boundary;
- exact source status and revision links;
- a repository revision and verified current entry points, tests, conventions,
  and commands; and
- no unresolved question whose answer could materially change expected
  behavior, data handling, authorization, irreversible effects, or architecture.

If the larger feature fails this gate, shrink to a coherent ready slice when
one still produces a testable actor or business outcome. Otherwise issue a
blocked brief or stop without creating one. Never call a layer-only task such
as “add the schema” a vertical slice merely because it avoids the open rule.

## Workflow

1. **Name the handoff decision.** State the intended implementer, user or
   business outcome, repository boundary, and why a new or revised brief is
   needed.
2. **Inventory authoritative inputs.** List approved requirements, examples,
   non-goals, use cases, contracts, design decisions, policies, and quality
   constraints with exact IDs, revisions, statuses, approving roles, and known
   supersession links.
3. **Apply the readiness gate.** Trace every needed expectation to an authorized
   source. Classify gaps rather than filling them: missing evidence or business
   rules go to `requirements-synthesis-validation`; scope or feasibility to
   `inception`; black-box behavior to `use-case-modeling` or
   `operation-contracts`; architecture or responsibility decisions to the
   relevant design skill.
4. **Select one vertical behavior slice.** Choose an actor-visible or
   business-visible outcome with its necessary success path, important failure
   behavior, rules, and constraints. Exclude unrelated behavior and any portion
   that depends on an unresolved decision. Explain why the slice remains
   coherent and testable.
5. **Inspect the repository read-only.** Follow local governance. Record the
   exact revision, existing public boundaries, related code and tests,
   configuration, data migrations, verification commands, and current
   constraints. Label these as repository facts and separate inference. Do not
   change code while briefing.
6. **Assemble the behavior contract.** Restate only approved in-scope behavior,
   examples, rules, quality attributes, and non-goals without strengthening or
   weakening them. Link every expectation to its source ID, revision, and
   status.
7. **Package existing design inputs.** Include only decisions already needed
   and approved for the selected boundary. If implementation requires a missing
   interface, ownership, persistence, security, or architecture decision, stop
   and route it instead of proposing one in the brief.
8. **Define verification and stops.** Identify approved examples or contracts
   that can serve as independent oracles, established repository commands, and
   required focused and regression evidence. State concrete conditions under
   which the coding agent must stop rather than guess.
9. **Check freshness and hand off.** Verify every source still has the recorded
   revision and status, every trace resolves, and no excluded issue leaks into
   scope. Mark the brief `ready`, `blocked`, `stale`, or `superseded`, then hand
   a ready brief to `test-driven-implementation`.

## File Output

Before creating a document, apply
[Artifact Selection Budget](../iterative-up-analysis-design/references/artifact-selection-budget.md).
Prefer an existing issue, work item, or feature artifact when it can own the
same bounded contract and lifecycle. A standalone brief is justified when an
implementation slice needs independent assignment, freshness, and completion.

For standalone Markdown, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
Use this proportionate shape, omitting empty sections:

```markdown
---
type: "Implementation Slice Brief"
title: "Implementation Slice: [Observable Outcome]"
description: "[Behavior delivered and important boundary]"
id: "[Stable opaque brief ID when cross-referenced]"
status: "[ready | blocked | stale | superseded]"
tags: ["implementation", "brief"]
---

# Implementation Slice: [Observable Outcome]

## Outcome and Boundary

- Actor or business outcome: [approved result]
- In scope: [coherent behavior]
- Non-goals: [explicit exclusions]
- Slice rationale: [why this is vertical, testable, and appropriately sized]

## Source Baseline

| Source | Revision | Status | Authority | Used for |
|---|---|---|---|---|

## Approved Behavior and Examples

1. [Main behavior or approved concrete example]
2. [Important alternate or failure behavior]

## Rules, Constraints, and Quality Expectations

- [approved rule or constraint with source]

## Existing Design Inputs

- [approved boundary, responsibility, interface, or decision with source]

## Repository Context

- Revision: [commit or other stable revision]
- Existing boundaries and files: [verified repository facts]
- Related verification: [tests, commands, and conventions]
- Inferences: [clearly labeled, or none]

## Traceability

| Brief expectation | Source ID | Revision and status | Notes |
|---|---|---|---|

## Verification Handoff

- Independent oracle: [approved example, use case, contract, invariant]
- Focused verification: [established boundary and command]
- Regression verification: [established command]

## Coding-Agent Stop Conditions

- Stop and route to [owner] if [material missing or changed condition].

## Readiness

- Status: [ready | blocked | stale | superseded]
- Remaining exclusions and dependencies: [items not authorized for this slice]
```

## Red Flags

- Calling a feature, UI shell, database migration, or service layer a vertical
  slice without an observable outcome.
- Copying candidate, contested, or superseded material into in-scope behavior.
- Writing new acceptance criteria, examples, rules, thresholds, or non-goals
  that no source approved.
- Mixing repository facts with client-provided requirements or treating current
  code as proof of desired behavior.
- Copying protected raw evidence into a broadly visible implementation brief.
- Proposing architecture, interfaces, schemas, or component ownership to make a
  blocked brief appear executable.
- Omitting source revisions, approval state, important failure behavior,
  verification, or coding-agent stop conditions.
- Modifying production or test files while the task is only to create a brief.

## Verification

- [ ] The slice produces one coherent actor-visible or business-visible outcome
      and includes its necessary failure behavior and constraints.
- [ ] Every in-scope expectation traces to an approved source ID, exact
      revision, status, and appropriate authority.
- [ ] Candidate, contested, superseded, and stale material appears only as an
      exclusion, risk, dependency, or stop condition.
- [ ] Approved examples and rules retain their original meaning; no thresholds,
      business rules, architecture, or acceptance conditions were invented.
- [ ] Repository facts are revision-fixed and distinguishable from intended
      behavior and agent inference.
- [ ] Source sensitivity, access, retention, and publication restrictions
      remain enforceable without copying protected raw evidence.
- [ ] Existing design inputs are sufficient for the slice or the brief is
      blocked and routed to the appropriate design skill.
- [ ] Verification names an independent oracle and established focused and
      regression commands without claiming unexecuted results.
- [ ] Source-change and unresolved-decision stop conditions are concrete.
- [ ] Only the brief or its existing owner changed; implementation was not
      performed.
- [ ] A standalone brief has one frontmatter block and a reader-oriented
      opening.
