# Implementation Plan: Teach planning docs to cite research output

**Slice**: `rrs-research-consumers`  
**Date**: 2026-04-21  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice teaches the downstream planning skills to reuse
`reference-research.md` when it exists. The implementation remains guidance-only
and consumer-focused: `discover`, `design`, and `review-planning` should read or
verify the durable research artifact when it matters, while `SKILLS_METHODOLOGY.md`
should explain that later planning phases reuse those conclusions instead of
re-deriving them.

## 2. Technical Context

- Current system context:
  - `skills/research/` already writes `reference-research.md` into a feature or
    subfeature packet.
  - `skills/discover/SKILL.md`, `skills/design/SKILL.md`, and
    `skills/review-planning/SKILL.md` currently describe their own inputs and
    review responsibilities without yet treating research as a durable consumer
    input.
  - `SKILLS_METHODOLOGY.md` now explains when to run `research`, but it still
    needs to explain how later planning phases should use the resulting artifact.
- Target modules / files:
  - `skills/discover/SKILL.md`
  - `skills/design/SKILL.md`
  - `skills/review-planning/SKILL.md`
  - `SKILLS_METHODOLOGY.md`
  - `slices/rrs-research-consumers-teach-planning-docs-to-cite-research-output/`
- Constraints:
  - keep this slice limited to planning-consumer guidance
  - do not add a new planning readiness state or missing-artifact blocker
  - do not absorb wiki synthesis behavior that belongs to the next slice
  - preserve the skill-specific boundaries: `discover` frames work, `design`
    records architecture, `review-planning` checks readiness
- Assumptions:
  - the reviewed design contract already defines `reference-research.md` as the
    durable local source for borrowing-path decisions
  - not every planning packet will have a research artifact, so the docs must
    describe optional consumption rather than mandatory gating
  - the planned `rg` validations are the correct proof for this doc-driven slice
- Out of scope:
  - changes to `research.py`
  - reusable wiki page synthesis
  - changes to planning metadata or lifecycle tooling

## 3. Planning Gates

### Architecture / Constraints

- Decision: update only the planning-consumer skill docs and shared methodology
  so each phase knows how to use `reference-research.md`.
- Result: PASS
- Notes: The behavior belongs in consumer guidance, not in registry state or
  code-level planning transitions.

### Risk / Compliance

- Decision: keep the artifact advisory and optional, while making borrowing-path
  preservation explicit when research exists and is relevant.
- Result: PASS
- Notes: The main risk is overcorrecting into a hard blocker; the docs should
  state clearly that missing research does not invent a new readiness failure.

### Testability

- Decision: use the planned `rg` checks to confirm both the artifact name and
  the research-consumption language appear in the intended docs.
- Result: PASS
- Notes: This slice is guidance-only, so content checks are the most direct
  validation path.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S004 | V001, V002 |
| FR-002 | S002, S004 | V001, V002 |
| FR-003 | S003, S004 | V001, V002 |
| FR-004 | S004 | V001, V002 |
| FR-005 | S001, S002, S003, S004 | V001, V002 |

## 5. Execution Plan

### Packet P01: Teach discover and design to reuse research

- Scope: Update discovery and design guidance so those planning phases read
  `reference-research.md` when it exists and preserve the chosen borrowing path
  when relevant.
- Target files:
  - `skills/discover/SKILL.md`
  - `skills/design/SKILL.md`
- Dependencies: none
- Steps:
  - [ ] S001 Add discovery guidance that treats `reference-research.md` as an
        optional durable input rather than a new readiness requirement.
  - [ ] S002 Add design guidance that preserves the chosen borrowing path and
        tradeoffs from `reference-research.md` when those decisions shape the
        architecture.
- Validation:
  - [ ] V001 Confirm both files mention `reference-research.md` and research
        reuse with `rg`.
- Definition of Done: `discover` and `design` make research reuse explicit
  without requiring it for every planning packet.
- Rollback / Mitigation: if either file starts to describe wiki synthesis or new
  gating logic, trim it back to optional artifact consumption only.

### Packet P02: Teach review-planning and shared methodology to verify reuse

- Scope: Update review and workflow guidance so maintainers know to check for
  preserved borrowing-path decisions when research exists.
- Target files:
  - `skills/review-planning/SKILL.md`
  - `SKILLS_METHODOLOGY.md`
- Dependencies: P01
- Steps:
  - [ ] S003 Add review guidance that checks whether relevant research
        conclusions remain coherent in the planning packet.
  - [ ] S004 Update shared methodology so later planning phases reuse
        `reference-research.md` instead of re-deriving the comparison.
- Validation:
  - [ ] V002 Confirm both files mention `reference-research.md` and research
        reuse with `rg`.
- Definition of Done: reviewers and maintainers can see how research feeds
  discovery, design, and planning review.
- Rollback / Mitigation: if methodology starts to absorb wiki behavior or repeat
  entire skill contracts, cut it back to one concise consumer-oriented note.

### Packet P03: Run the planned content checks

- Scope: Execute the planned validation commands for this documentation slice.
- Target files:
  - `skills/discover/SKILL.md`
  - `skills/design/SKILL.md`
  - `skills/review-planning/SKILL.md`
  - `SKILLS_METHODOLOGY.md`
- Dependencies: P02
- Steps:
  - [ ] S005 Run the planned `rg` checks for both `reference-research.md` and
        general research-consumption wording.
- Validation:
  - [ ] V003 Run `rg -n "reference-research\\.md" skills/discover/SKILL.md skills/design/SKILL.md skills/review-planning/SKILL.md SKILLS_METHODOLOGY.md && rg -n "research" skills/discover/SKILL.md skills/design/SKILL.md skills/review-planning/SKILL.md SKILLS_METHODOLOGY.md`
- Definition of Done: the expected consumer guidance is present in all planned
  files.
- Rollback / Mitigation: if the checks pass because of stray or misleading
  wording, tighten the content so each reference is meaningful and phase-scoped.

## 6. Supporting Notes

### Detailed Design Diagrams (PlantUML)

- Diagram purpose: show how the local research artifact becomes an input to
  later planning phases instead of a side-channel note.
- Diagram type: sequence

```plantuml
@startuml
skinparam backgroundColor white

participant "research" as Research
file "reference-research.md" as Artifact
participant "discover" as Discover
participant "design" as Design
participant "review-planning" as ReviewPlanning

Research -> Artifact : write chosen borrowing path
Discover -> Artifact : read when present and relevant
Design -> Artifact : preserve decisions and tradeoffs
ReviewPlanning -> Artifact : verify coherence in planning packet
@enduml
```

### Research Decisions

- Decision: consumer guidance should reuse `reference-research.md` only when the
  artifact exists and is relevant to the current planning change.
- Rationale: this keeps research durable without inventing a new planning
  checkpoint.
- Alternative considered: require later planning phases to always regenerate or
  restate the full comparison directly.

### Interface Notes

- Interface: `skills/discover/SKILL.md`, `skills/design/SKILL.md`,
  `skills/review-planning/SKILL.md`
- Inputs / outputs:
  - inputs: planning packets that may include `reference-research.md`
  - outputs: clearer guidance for how later planning phases consume or review
    research conclusions
- Error states / compatibility notes:
  - missing `reference-research.md` should not imply a lifecycle failure
  - only relevant conclusions should be preserved; avoid requiring blanket copy

### Verification Scenarios

- Happy path: all consumer docs mention `reference-research.md` and explain how
  to reuse it.
- Edge case: the guidance still allows planning to proceed when research was not
  required and no artifact exists.
- Regression checks: the planned `rg` validations pass against the intended
  files only.

## 7. Delivery Notes

- Sequencing rationale: consumer guidance should land before wiki synthesis so
  the local research artifact is already valuable across the planning layer.
- Risks to monitor:
  - turning optional research reuse into a hard planning gate
  - duplicating entire research conclusions in every later skill instead of
    pointing back to the durable artifact
  - letting methodology drift from the skill-level guidance
- Handoff notes for implementation:
  - keep edits constrained to the three consumer skills plus
    `SKILLS_METHODOLOGY.md`
  - mention `reference-research.md` explicitly in each planned file
  - stop once the planned `rg` validations pass and the lifecycle remains
    unchanged
