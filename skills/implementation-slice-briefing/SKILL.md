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

- Approved requirements and examples span more than one implementation
  increment, or need one traceable handoff with design and repository facts.
- A coding agent needs explicit scope, non-goals, verification, and stop
  conditions, or an existing brief may be stale.
- Do not use to elicit or approve requirements, create missing analysis or
  design, write production code, or execute the implementation workflow.

## Source and Authority Discipline

Treat approved requirements, examples, and decisions as the intended-behavior
oracle; repository inspection establishes current code facts only. Preserve
opaque IDs, exact revisions, statuses, approving roles, and supersession links.
A changed source makes the dependent brief stale until reconciled.

Do not promote `candidate`, `validated`, `contested`, superseded, or otherwise
unauthorized material into implementation expectations. Record it only as an
exclusion, dependency, risk, or stop condition. Preserve repository-specific
approval vocabulary and its authorization evidence.

Carry sensitivity, access, retention, and publication restrictions forward.
Copy only authorized sanitized requirements and examples.
Link to protected evidence without reproducing it. Mark the brief blocked when
an implementer cannot receive enough authorized information, and route the
access or publication decision to its owner.

## Readiness Gate

A slice is ready only when it has:

- an approved outcome, boundary, success and important failure behavior;
- approved examples, rules, constraints, quality expectations, and necessary
  design decisions;
- exact source status and revision links plus a fixed repository revision with
  verified entry points, tests, conventions, and commands; and
- no unresolved question that could materially change behavior, data handling,
  authorization, irreversible effects, or architecture.

If the feature fails this gate, shrink to a coherent actor- or business-visible
outcome. Otherwise issue a blocked brief or stop. A layer-only task such as
“add the schema” is not a vertical slice.

## Workflow

1. **Name the handoff.** State the implementer, observable outcome, repository
   boundary, and why a new or revised brief is needed.
2. **Inventory authoritative inputs.** List approved requirements, examples,
   non-goals, contracts, decisions, policies, and constraints with their IDs,
   revisions, statuses, authorities, and supersession links.
3. **Apply the readiness gate.** Trace every needed expectation to an authorized
   source. Classify gaps rather than filling them: missing evidence or business
   rules go to `requirements-synthesis-validation`; scope or feasibility to
   `inception`; black-box behavior to `use-case-modeling` or
   `operation-contracts`; architecture or responsibility decisions to the
   relevant design skill.
4. **Select one vertical slice.** Choose one observable outcome with its
   necessary success path, important failure behavior, rules, and constraints.
   Exclude unrelated or unresolved behavior and explain why the remainder is
   coherent and testable.
5. **Inspect the repository read-only.** Follow local governance. Record the
   exact revision, public boundaries, related code, tests, configuration,
   migrations, commands, and constraints. Separate facts from inference; do not
   change code.
6. **Assemble the behavior contract.** Restate approved in-scope behavior,
   examples, rules, qualities, and non-goals without changing their meaning.
   Link each expectation to its source ID, revision, and status.
7. **Package existing design inputs.** Include only approved decisions needed
   for the boundary. Stop and route any missing interface, ownership,
   persistence, security, or architecture decision.
8. **Define verification and stops.** Name independent approved oracles,
   established focused and regression commands, required evidence, and concrete
   conditions under which the coding agent must stop.
9. **Check freshness and hand off.** Verify source revisions, statuses, traces,
   and exclusions. Mark the brief `ready`, `blocked`, `stale`, or `superseded`;
   hand only a ready brief to `test-driven-implementation`.

## File Output

Apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Prefer an existing issue, work item, or feature artifact. Create a standalone
brief only for independent assignment, freshness, and completion.

For standalone Markdown, follow
[Markdown Artifact Frontmatter](../iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
and [Readable Technical Artifacts](../iterative-up-analysis-design/references/readable-technical-artifacts.md).
When a standalone brief is justified, read and adapt the
[Implementation Slice Brief Template](references/implementation-slice-brief-template.md).

Whether embedded or standalone, retain the source baseline fields
`Source | Revision | Status | Authority | Used for`, the instruction
`Stop and route to [owner]`, and independent-oracle, focused-verification,
regression-verification, readiness, exclusion, and dependency fields.

## Red Flags

- A layer, migration, or shell is called vertical without an observable outcome.
- Unauthorized material becomes in-scope behavior, or new rules are invented.
- Repository facts are confused with intended behavior or agent inference.
- Protected raw evidence is copied into a broadly visible brief.
- Missing architecture or design is invented to make a blocked brief executable.
- Revisions, approval, failure behavior, verification, or stops are omitted.
- Production or tests change while the task is only briefing.

## Verification

- [ ] One coherent observable outcome includes necessary failure behavior and constraints.
- [ ] Every expectation traces to an approved source ID, revision, status, and authority.
- [ ] Unauthorized material appears only as an exclusion, risk, dependency, or stop.
- [ ] No rule, threshold, architecture, or acceptance condition was invented.
- [ ] Repository facts, intended behavior, and inference remain distinct.
- [ ] Source handling restrictions remain enforceable without exposing raw evidence.
- [ ] Missing design blocks the brief and is routed instead of being invented.
- [ ] Verification names independent oracles and established commands without claiming results.
- [ ] Source-change and unresolved-decision stop conditions are concrete.
- [ ] Only the brief or existing owner changed; standalone Markdown follows repository guidance and has a reader-oriented opening.
