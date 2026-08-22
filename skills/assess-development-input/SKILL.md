---
name: assess-development-input
description: Routes an incoming development request or artifact to the narrowest responsible Sirius skill, external add-on, repository-native process, or prerequisite. Use at task intake when the correct owner is unclear, several skills appear plausible, authority or readiness may block progress, or coordinated work must be distinguished from one localized specialist task. Preserve source meaning and select one initial route without executing it.
---

# Assess and Route Development Input

## Overview

Route an incoming development request or artifact to one initial owner. Base the
decision on content, authority, current uncertainty, and material risk. Do not
route by file name, lifecycle phase, or a mandatory skill sequence.

This skill owns entry routing. It does not execute the selected route.
`iterative-risk-driven-development` owns specialist selection after coordinated
iteration work begins.

## When to Use

- A task starts and its correct skill or process is unclear.
- Several skills appear plausible, but one owns the first material question.
- Requirements-shaped input may lack approval, evidence, behavior, or an
  independent verification oracle.
- It is unclear whether work needs one specialist, repository-native execution,
  or coordinated iteration across several boundaries.
- Do not use when the user selected a valid skill and supplied its entry
  conditions.
- Do not use to execute a handoff, rewrite source material, or coordinate an
  iteration.

## Task Discovery

Use this tree as a routing index, not a required lifecycle:

```text
Task arrives
├─ Requester intent is unclear
│  └─ external interview-me
├─ A candidate direction needs alternatives or MVP scope
│  └─ external idea-refine
├─ A confirmed direction needs an implementation specification
│  └─ external spec-driven-development
├─ Current behavior, architecture, deployment, or constraints lack evidence
│  └─ responsible external current-system recovery process
├─ Scope, actors, goals, or scenarios are unclear
│  └─ Requirements Analysis
├─ Domain vocabulary, system events, or state effects are unclear
│  └─ System Analysis
├─ Components, data owners, deployment, or quality trade-offs are unclear
│  └─ design-software-architecture
├─ Internal responsibilities, collaborations, structure, or variation are unclear
│  └─ Software/System Design specialists
├─ Target-language or runtime realization is unclear
│  └─ Detailed Design
├─ One bounded behavior has an approved independent oracle
│  └─ external test-driven-development or repository-native implementation
├─ A completed change needs formal review
│  └─ external code-review-and-quality or repository-native review
│     ├─ readability or local complexity → external code-simplification
│     ├─ established structural ownership → behavior-preserving-refactoring
│     └─ material boundary change → iterative-risk-driven-development
├─ A reader needs a paced explanation of a selected change
│  └─ walkthrough-me
├─ Prepared work needs Git or version guidance
│  └─ external git-workflow-and-versioning or repository-native Git workflow
├─ Committed work is ready for pull-request publication
│  └─ create-pr
├─ A consequential decision or durable context needs documentation
│  └─ external documentation-and-adrs or repository-native documentation
├─ Artifact existence or disposition is unclear
│  └─ select-technical-artifacts
├─ A justified artifact lacks a canonical home
│  └─ design-repository-artifact-layout
└─ Several analysis, design, implementation, verification, or commit boundaries
   require one coordinated objective
   └─ iterative-risk-driven-development
```

External Addy routes require the `all` installation. Otherwise, select the
repository-native workflow or report the responsible external prerequisite.

## Routing Principles

1. **Prefer the narrowest owner.** Select a specialist when one localized
   question blocks progress. Select the coordinator only when several material
   boundaries must advance together.
2. **Choose by meaning.** A specification, issue, feature file, pull request, or
   test does not prove readiness or determine its owner.
3. **Preserve authority.** Keep source references, revisions, approval state,
   non-goals, and open questions. Never upgrade candidate or inferred material
   into an approved decision.
4. **Surface uncertainty.** Keep missing information, conflicting information,
   and missing authority distinct. Stop instead of routing around a material
   prerequisite.
5. **Select one initial route.** Do not prescribe a full lifecycle. The selected
   owner may route feedback or request coordination after it begins.
6. **Do not execute implicitly.** Routing does not authorize artifact creation,
   implementation, commits, pushes, publication, or production changes.

## Assessment Modes

- **Direct task routing:** Classify an explicit request whose desired outcome is
  clear but whose owner is not. Return the route without demanding an input
  artifact or producing a readiness inventory.
- **Input readiness assessment:** Inspect an existing artifact or evidence set.
  Record what it establishes, the first material gap, and whether the selected
  route is ready.
- **Coordination decision:** Select `iterative-risk-driven-development` only
  when one approved objective requires several specialist questions, a
  boundary-sensitive change, or an iteration commit boundary.

## Workflow

1. **Identify the request.** State the requested outcome, source or selected
   change, explicit non-goals, and requested repository effects.
2. **Confirm authority.** Identify what is approved, candidate, inferred,
   contested, or unsupported. Treat code, tests, and observations as evidence,
   not automatically as intended behavior.
3. **Find the first material question.** Name the earliest unresolved question
   that would make the next owner guess or cross an unauthorized boundary.
4. **Check for a direct owner.** Use the discovery tree and quick reference.
   Prefer a specialist or repository-native process over coordination.
5. **Assess readiness.** For an existing input, mark the route `ready`,
   `needs prerequisite`, or `blocked`. For a direct task, report only material
   assumptions or stop conditions.
6. **Return one route.** Name one Sirius skill, external add-on,
   repository-native process, or responsible external prerequisite and explain
   why it owns the current question.
7. **Stop at the handoff.** Do not invoke the route or create its output unless
   the user separately requests that work.

## Quick Reference

| Group | Condition | Initial owner |
|---|---|---|
| Define | One requester's intended outcome is unclear | External `interview-me` |
| Define | A candidate direction needs alternatives, assumption testing, or MVP scope | External `idea-refine` |
| Define | A confirmed direction needs an implementation specification | External `spec-driven-development` |
| Requirements Analysis | Vision, feasibility, project scope, or major business risk is unclear | `inception` |
| Requirements Analysis | Actors, goals, system boundary, scenarios, or extensions are unclear | `use-case-modeling` |
| System Analysis | Business concepts, vocabulary, associations, or attributes are unclear | `domain-modeling` |
| System Analysis | Actor-system events or system operations are unclear | `system-sequence-diagrams` |
| System Analysis | Non-trivial state changes, preconditions, or postconditions are unclear | `operation-contracts` |
| Software/System Design | Major components, services, processes, data owners, architectural boundaries, deployment topology, or quality trade-offs are unclear | `design-software-architecture` |
| Software/System Design | Native responsibility, cohesion, coupling, coordination, or dependency direction is unclear | `grasp-responsibility-design` |
| Software/System Design | Internal collaboration for one selected scenario is unclear | `use-case-realization` |
| Software/System Design | Stable object-oriented structure needs a summary | `uml-class-diagram-design` |
| Software/System Design | Demonstrated creation, structural, communication, or variation pressure needs a pattern decision | `design-pattern-application` |
| Detailed Design | Language-neutral design needs target-language adaptation | `software-design-language-adaptation` |
| Detailed Design | Approved Rust behavior has material ownership, startup, rollback, cancellation, or cleanup risk | `design-rust-lifecycles` |
| Implementation and Evolution | Bounded approved behavior has an independent oracle and needs no Sirius coordination | External `test-driven-development` or repository-native implementation and verification |
| Review | A completed change needs correctness, architecture, security, performance, or merge review | External `code-review-and-quality` or repository-native review |
| Review | Protected behavior needs routine naming, extraction, duplication, control-flow, or recent-code clarity work | External `code-simplification` or repository-native cleanup |
| Review | Protected behavior needs an established responsibility, dependency, variation, or configuration-ownership change | `behavior-preserving-refactoring` |
| Repository Workflow | A reader needs a paced, read-only change tour | `walkthrough-me` |
| Integrate and ship | Prepared work needs standalone Git, branch, worktree, release, or version guidance | External `git-workflow-and-versioning` or repository-native Git workflow |
| Integrate and ship | Committed work is ready for pull-request publication | `create-pr` |
| Integrate and ship | A consequential architecture choice or durable engineering context needs documentation | External `documentation-and-adrs` or repository-native documentation |
| Cross-cutting Support | Candidate knowledge needs create, update, embed, keep, omit, or defer disposition | `select-technical-artifacts` |
| Cross-cutting Support | A justified artifact needs a canonical home, lifecycle separation, or migration | `design-repository-artifact-layout` |
| Iterative Coordination | One approved objective crosses several analysis, design, implementation, verification, or commit boundaries | `iterative-risk-driven-development` |
| External prerequisite | Current-system claims lack sufficient evidence | Responsible external recovery process |
| External prerequisite | Stakeholder evidence, validation, approval, or another authority is missing | Responsible external owner |

## Output

Use this concise conversational form:

```markdown
Request or input:
- [task, source, artifact, selected change, or revision]

Intended outcome:
- [what the route should enable]

Readiness: [ready | needs prerequisite | blocked]

Established:
- [material approved fact, evidence, or none needed for direct routing]

Material uncertainty:
- [gap, conflict, missing authority, assumption, or none]

Recommended initial route: `[one owner]`

Rationale:
- [why this owner matches the first material question]

Prerequisite or stop condition:
- [what must be resolved before proceeding, or none]
```

## File Output

Keep routing conversational unless a durable cross-session or cross-team
handoff is justified. Before creating a standalone record, apply the
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style.

```markdown
---
type: "Development Input Assessment"
title: "Assessment: [Request or input]"
description: "[Readiness and recommended initial owner]"
status: "[active | blocked | completed]"
tags: [intake, routing]
---
```

## Red Flags

- Routing every task through a fixed lifecycle or mandatory artifact sequence.
- Selecting by a file name, tool, syntax, or development phase instead of the
  first material question.
- Sending every task to `iterative-risk-driven-development` when one specialist
  or repository-native process is sufficient.
- Using this skill after the user already selected a valid direct owner.
- Inventing requirements, approval, current-system facts, or verification
  evidence to make a route appear ready.
- Returning a roadmap of many skills instead of one initial owner.
- Executing the selected route without separate authority.

## Verification

- [ ] The requested outcome, source or selected change, and requested effects
      are explicit.
- [ ] The route follows content, authority, uncertainty, and risk rather than a
      mandatory phase sequence.
- [ ] The first material question and exactly one initial owner are named.
- [ ] A specialist is preferred over coordination when one localized question
      owns the gap.
- [ ] Established information remains distinct from assumptions, conflicts,
      unsupported claims, and missing authority.
- [ ] External add-on availability and repository-native fallback are explicit
      when relevant.
- [ ] No route was executed and no effect was implied without separate user
      authority.
- [ ] Any standalone assessment passes the artifact budget and uses the
      required frontmatter.
