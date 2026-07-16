# Implementation Plan: Create explicit research skill

**Slice**: `rrs-research-skill`  
**Date**: 2026-04-21  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice establishes the first explicit `research` skill in `sirius-skills`
and makes it capable of writing one local `reference-research.md` artifact for a
selected canonical feature or subfeature. The implementation stays focused on
the local artifact contract: target resolution, durable local research content,
and explicit recording of wiki follow-up status. Routing into the new skill and
downstream consumer updates stay in later planned slices.

## 2. Technical Context

- Current system context:
  - The repo already supports feature and subfeature planning resolution through
    `guide-planning`, `add-subfeature`, and shared scope-runtime helpers.
  - There is currently no `skills/research/` directory, no local
    `reference-research.md` artifact owner, and no reusable helper for this
    workflow.
  - The reviewed planning packet for
    `docs/features/planning-workflow/subfeatures/reference-research-synthesis/`
    already defines the local artifact contract and intentionally leaves routing
    and broader wiki integration to later slices.
- Target modules / files:
  - new `skills/research/SKILL.md`
  - new `skills/research/scripts/research.py`
  - new `skills/research/tests/test_research.py`
  - optional minimal repo docs touch only if needed to surface the new skill
  - slice artifacts under
    `slices/rrs-research-skill-create-explicit-research-skill/`
- Constraints:
  - keep this slice limited to the dedicated skill and local artifact contract
  - do not add a new planning lifecycle state
  - do not auto-bootstrap a wiki layer when it is absent
  - keep target resolution compatible with canonical feature and durable
    subfeature planning packets
- Assumptions:
  - checked-in repository references remain the default source set for the first
    implementation
  - a local artifact can record wiki follow-up status even before later slices
    implement reusable wiki-page updates
  - the existing planning registries and metadata are sufficient to resolve the
    target packet without new config
- Out of scope:
  - `guide-planning` routing updates for "when relevant" thresholds
  - downstream `discover`, `design`, and `review-planning` consumer updates
  - reusable wiki page generation and index/log mutation

## 3. Planning Gates

### Architecture / Constraints

- Decision: add one new `skills/research/` package with a Python helper script
  that resolves a planning target and writes `reference-research.md` into that
  folder.
- Result: PASS
- Notes: This keeps ownership explicit and aligns with existing skill-plus-script
  patterns without widening the slice into routing or consumer behavior.

### Risk / Compliance

- Decision: keep the new workflow local to repository files, avoid network
  behavior, and record wiki follow-up status without mutating the wiki layer in
  this slice.
- Result: PASS
- Notes: The main risk is writing the artifact into the wrong planning packet, so
  resolution must reuse the existing scope-aware planning helpers.

### Testability

- Decision: cover canonical feature and subfeature target resolution, local
  artifact generation, and missing-wiki behavior with focused pytest coverage.
- Result: PASS
- Notes: The helper should expose importable functions so tests can validate file
  output deterministically in temporary directories.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S002 | V001 |
| FR-002 | S002, S003 | V001, V002 |
| FR-003 | S003, S004 | V001, V002 |
| FR-004 | S004 | V001, V003 |
| FR-005 | S001, S005 | V001, V003 |

## 5. Execution Plan

### Packet P01: Create the research skill surface

- Scope: Add the dedicated skill directory and its user-facing workflow
  guidance.
- Target files:
  - `skills/research/SKILL.md`
- Dependencies: none
- Steps:
  - [ ] S001 Write the new `research` skill contract, including target
        resolution, required local artifact output, wiki-follow-up recording, and
        explicit guardrails against introducing a new planning state.
  - [ ] S002 Ensure the skill examples and terminology align with existing
        feature/subfeature planning layouts.
- Validation:
  - [ ] V001 Review the new skill guidance alongside the reviewed planning packet
        and confirm the required output is `reference-research.md`.
- Definition of Done: the repo has a dedicated `research` skill with explicit
  ownership and no ambiguity about the local artifact contract.
- Rollback / Mitigation: if the workflow wording starts to absorb later routing
  or consumer behavior, narrow the skill doc back to local artifact generation
  only.

### Packet P02: Implement target resolution and local artifact generation

- Scope: Build the Python helper that resolves a planning target and writes the
  local research artifact.
- Target files:
  - `skills/research/scripts/research.py`
- Dependencies: P01
- Steps:
  - [ ] S003 Reuse the existing planning resolution helpers to locate a canonical
        feature or durable subfeature path from a selector.
  - [ ] S004 Generate `reference-research.md` with stable sections for research
        scope, sources reviewed, borrowing-path decision, lower-priority
        alternatives, and wiki follow-up status.
  - [ ] S005 Record missing-wiki behavior as an explicit deferred state in the
        local artifact instead of trying to bootstrap or mutate the wiki layer.
- Validation:
  - [ ] V002 Run the research helper against a canonical feature fixture and a
        subfeature fixture, then inspect the resulting local artifact.
- Definition of Done: a maintainer can run the helper for a valid planning
  target and get `reference-research.md` in the correct folder.
- Rollback / Mitigation: if scope-aware target resolution is brittle, keep the
  selector contract narrower and require explicit planning-packet paths for the
  first slice rather than guessing.

### Packet P03: Lock behavior with focused tests

- Scope: Add regression coverage for the new helper and artifact behavior.
- Target files:
  - `skills/research/tests/test_research.py`
- Dependencies: P02
- Steps:
  - [ ] S006 Add canonical-feature and subfeature tests for target resolution and
        local artifact creation.
  - [ ] S007 Add a missing-wiki test proving the artifact records deferred wiki
        synthesis without failing the local research step.
- Validation:
  - [ ] V003 Run `pytest -q skills/research/tests/test_research.py`
- Definition of Done: the new helper behavior is covered by deterministic tests
  and the planned slice validation path is real.
- Rollback / Mitigation: if one fixture setup is too large, keep the tests closer
  to the helper functions with minimal planning metadata and one representative
  end-to-end CLI path.

## 6. Supporting Notes

### Detailed Design Diagrams (PlantUML)

- Diagram purpose: show how the new helper resolves one planning packet and
  writes only the local research artifact in this slice.
- Diagram type: sequence

```plantuml
@startuml
skinparam backgroundColor white

actor Maintainer
participant "research skill" as ResearchSkill
participant "research.py" as Helper
participant "planning resolution" as PlanningLookup
file "reference-research.md" as ResearchArtifact
folder "derived wiki root" as WikiRoot

Maintainer -> ResearchSkill : invoke with feature/subfeature target
ResearchSkill -> Helper : run target-aware research workflow
Helper -> PlanningLookup : resolve planning packet path
PlanningLookup --> Helper : feature or subfeature folder
Helper -> ResearchArtifact : write local research synthesis
Helper -> WikiRoot : inspect presence only
Helper --> ResearchSkill : success + wiki follow-up status
ResearchSkill --> Maintainer : local artifact written
@enduml
```

### Research Decisions

- Decision: keep wiki behavior in this slice to presence detection and deferred
  status recording only.
- Rationale: the local artifact contract must stabilize first before later slices
  update the derived wiki root or downstream planning-doc consumers.
- Alternative considered: implement wiki page generation in the same slice.

### Interface Notes

- Interface: `skills/research/scripts/research.py`
- Inputs / outputs:
  - inputs: feature slug, subfeature slug, or explicit planning-packet path
  - outputs: zero exit on success plus `reference-research.md` in the target
    planning folder
- Error states / compatibility notes:
  - fail explicitly when the selector cannot be resolved to one planning packet
  - do not silently write to the wrong scope or to a repo-global scratch file
  - do not require the wiki layer to exist

### Verification Scenarios

- Happy path: run the helper for a canonical feature and confirm the local
  research artifact is created with the required sections.
- Edge case: run the helper for a subfeature and confirm the artifact is written
  into the subfeature-local planning folder.
- Regression checks: run without a wiki layer and confirm the artifact records
  deferred wiki synthesis instead of failing or bootstrapping the wiki.

## 7. Delivery Notes

- Sequencing rationale: establish the dedicated skill and local artifact first so
  later routing, consumer, and wiki-synthesis slices can reuse one stable
  contract.
- Risks to monitor:
  - ambiguous target resolution across feature and subfeature scopes
  - accidental expansion into routing or consumer changes that belong to later
    planned slices
  - drift between the implemented helper behavior and the slice-scoped artifact
    contract
- Handoff notes for implementation:
  - keep the first slice tightly scoped to `skills/research/` and its tests
  - prefer explicit target resolution errors over permissive guessing
  - stop after the local artifact contract and tests are real
