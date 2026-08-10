# Implementation Slice Brief Template

Use this template only after a standalone brief passes the artifact-selection
budget. Preserve repository-defined frontmatter and headings when they exist;
otherwise adapt this shape and omit empty sections.

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
