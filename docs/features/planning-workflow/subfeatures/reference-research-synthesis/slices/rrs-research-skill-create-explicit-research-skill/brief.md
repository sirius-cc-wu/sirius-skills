# Slice Specification: Create explicit research skill

**Slice**: `rrs-research-skill`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: "Create explicit research skill"

## 1. Work Item Summary

- **Work Item**: Create a dedicated `research` skill that owns checked-in
  reference comparison and writes one local `reference-research.md` artifact for
  the target feature or subfeature.
- **Source Story / Increment / Slice**: `RRS-01` / `I1` / `rrs-research-skill`
- **Requested Outcome**: As a planner, when a feature or subfeature depends on
  upstream reference comparison, we want one explicit skill that captures the
  chosen borrowing path durably in the planning packet.
- **Why this matters**: It makes reference comparison reusable and reviewable
  instead of scattering the reasoning across chat history or unrelated planning
  docs.
- **Independent Test**: Run `pytest -q skills/research/tests/test_research.py`
  and confirm a target planning packet receives a valid
  `reference-research.md`.

## 2. Acceptance Scenarios

1. **Given** a reviewed feature or subfeature whose design depends on checked-in
   references, **When** the maintainer runs the `research` skill for that target,
   **Then** the skill writes a `reference-research.md` artifact in the planning
   folder with the chosen borrowing path and comparison notes.
2. **Given** a target with a feature or subfeature planning path, **When** the
   skill resolves the target, **Then** it records the research scope against the
   correct local planning packet instead of a repository-global scratch note.
3. **Given** a repository that does not yet have a wiki layer, **When** the
   skill completes local research, **Then** the local artifact still records
   whether reusable wiki synthesis was deferred.

## 3. Functional Requirements

- **FR-001**: The system MUST provide a dedicated `research` skill for
  checked-in reference comparison.
- **FR-002**: The system MUST resolve either a canonical feature path or a
  subfeature path and write `reference-research.md` into that target folder.
- **FR-003**: The system MUST capture the research scope, reviewed sources,
  chosen borrowing path, and lower-priority alternatives in the local artifact.
- **FR-004**: The system MUST record the status of reusable wiki follow-up in
  the local artifact, including when wiki synthesis is intentionally deferred.
- **FR-005**: The system MUST keep the local research artifact as a planning
  artifact and not introduce a new planning lifecycle state.

## 4. Key Entities

- **Research skill**: The execution target for this slice; it owns the workflow
  guidance and local artifact generation for reference comparison.
- **Reference research artifact**: `reference-research.md`, the durable local
  planning document that records comparison scope, sources, and borrowing-path
  conclusions.
- **Planning target**: A canonical feature or durable subfeature folder that
  receives the local research artifact.

## 5. Edge Cases

- The target has no wiki layer yet, so reusable conclusions must stay local and
  explicitly marked as deferred.
- The reviewed references disagree, so the artifact must preserve the chosen
  source and the rejected alternatives.
- The skill is run for a subfeature, so the artifact must live in the
  subfeature-local planning folder rather than the parent feature root.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: Checked-in references under the repository remain the default input
  set for this first slice.
- **A2**: This slice establishes the local artifact contract first; downstream
  routing and wiki integration can build on it in later slices.

### Dependencies

- **D1**: The reviewed planning packet for
  `docs/features/planning-workflow/subfeatures/reference-research-synthesis/`
  remains the source of truth for scope and acceptance.
- **D2**: Later slices (`rrs-relevance-routing`, `rrs-research-consumers`,
  `rrs-wiki-synthesis`) depend on this slice defining the stable local artifact
  shape.

## 7. Success Criteria

- **SC-001**: A maintainer can run one explicit `research` skill and obtain
  `reference-research.md` in the selected planning folder.
- **SC-002**: The generated local artifact records the chosen borrowing path,
  reviewed sources, and reusable wiki follow-up status.
- **SC-003**: The slice completes without introducing a new planning lifecycle
  state or moving the research decision into transient chat-only context.
