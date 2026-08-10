# Requirements Discovery Brief Template

Use this template only after a standalone discovery brief passes the
artifact-selection budget. Preserve repository-defined frontmatter and headings
when they exist; otherwise adapt this shape and omit empty sections.

```markdown
---
type: "Requirements Discovery Brief"
title: "Requirements Discovery: [Problem or Decision]"
description: "[Synthesis scope and important unresolved consequence]"
id: "[Stable opaque ID when cross-referenced]"
status: "[active | completed | completed-with-gaps | blocked | superseded]"
tags: ["requirements", "validation"]
---

# Requirements Discovery: [Problem or Decision]

## Purpose and Boundary

- Decision informed: [decision]
- Evidence set: [source IDs and revisions]
- Coverage limits: [known gaps]
- Non-goals: [what this synthesis does not decide]

## Synthesized Understanding

- Goal or outcome: [source-linked synthesis]
- Current workflow: [source-linked synthesis]
- Material constraints and quality attributes: [source-linked synthesis]

## Candidate Requirements

### [Opaque requirement ID]: [Short name]

- Kind: [goal | workflow | rule | constraint | quality attribute | scenario | decision]
- Statement: [precise, solution-neutral where possible]
- Status: [candidate | validated | approved | contested | superseded]
- Source evidence IDs: [supporting and contradicting IDs]
- Applies to: [actors, scenarios, data, or boundary]
- Example or fit criterion: [concrete behavior or measurable result]
- Validation and approval: [role, authority, revision, outcome, date if known]
- Limits and open questions: [uncertainty and responsible resolver]

## Validation and Decision Log

| Requirement | Revision | Participant role | Authority | Outcome | Correction or rationale |
|---|---|---|---|---|---|

## Conflicts and Open Questions

- [conflict, consequence, responsible role, and next evidence or decision]

## Handoffs

- [accepted knowledge, canonical owner, and status]
```
