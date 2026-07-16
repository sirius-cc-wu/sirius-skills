# Slice Specification: Teach planning docs to cite research output

**Slice**: `rrs-research-consumers`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: "Teach planning docs to cite research output"

## 1. Work Item Summary

- **Work Item**: Update downstream planning guidance so `discover`, `design`,
  and `review-planning` treat `reference-research.md` as a durable input when it
  exists.
- **Source Story / Increment / Slice**: `RRS-03` / `I2` /
  `rrs-research-consumers`
- **Requested Outcome**: As a reviewer, when a feature or subfeature already has
  durable reference research, we want later planning phases to read it and
  preserve the chosen borrowing path instead of re-deriving the comparison from
  memory or chat history.
- **Why this matters**: It makes cross-reference decisions inspectable across
  planning phases and keeps the new research artifact valuable after it is
  written.
- **Independent Test**: Run the planned `rg` checks across
  `skills/discover/SKILL.md`, `skills/design/SKILL.md`,
  `skills/review-planning/SKILL.md`, and `SKILLS_METHODOLOGY.md` to confirm the
  docs mention `reference-research.md` and research-driven reuse.

## 2. Acceptance Scenarios

1. **Given** a feature or subfeature with `reference-research.md`, **When**
   `discover` or `design` guidance is followed, **Then** the guidance says to
   read that artifact and preserve the chosen borrowing path in the resulting
   planning docs.
2. **Given** a planning target without `reference-research.md`, **When**
   maintainers follow `discover` or `design`, **Then** the guidance still allows
   planning to continue without inventing a new readiness gate.
3. **Given** a planning packet with durable research conclusions, **When**
   `review-planning` checks readiness, **Then** the guidance tells reviewers to
   verify that relevant borrowing-path decisions remain preserved and coherent.

## 3. Functional Requirements

- **FR-001**: `discover` guidance MUST treat `reference-research.md` as a
  durable input when it exists for the current feature or subfeature.
- **FR-002**: `design` guidance MUST instruct authors to preserve the chosen
  borrowing path and tradeoffs from `reference-research.md` when those
  conclusions shape the solution.
- **FR-003**: `review-planning` guidance MUST instruct reviewers to check that
  relevant research conclusions are reflected coherently in planning artifacts.
- **FR-004**: Shared workflow guidance MUST describe `reference-research.md` as
  a reusable planning artifact rather than a chat-only note.
- **FR-005**: The consumer guidance MUST keep research advisory and MUST NOT
  introduce a new planning lifecycle state or an automatic blocker when the
  artifact is absent.

## 4. Key Entities

- **Reference research artifact**: `reference-research.md`, the durable local
  source for borrowing-path decisions.
- **Planning consumers**: `discover`, `design`, and `review-planning`, the
  skills that should read or verify research conclusions when relevant.
- **Borrowing path**: The preferred upstream pattern and tradeoff summary chosen
  during research.

## 5. Edge Cases

- A planning packet has no `reference-research.md`, so consumer guidance must
  stay optional rather than inventing a missing-artifact failure.
- Research conclusions exist but only some are relevant to the current
  discovery or design change, so the docs should preserve the meaningful parts
  without requiring wholesale repetition.
- Reviewers need to distinguish a real drift between research and planning from
  a benign omission where research was never required.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The dedicated `research` skill and its local artifact contract already
  exist from the earlier slices in this subfeature.
- **A2**: This slice teaches planning consumers to read the local artifact; wiki
  synthesis of reusable conclusions remains in the next slice.

### Dependencies

- **D1**: The reviewed design contract in
  `docs/features/planning-workflow/subfeatures/reference-research-synthesis/system-design.md`
  remains the source of truth for consumer behavior.
- **D2**: The completed `rrs-relevance-routing` slice already defined when
  research should be present as an input to later planning work.

## 7. Success Criteria

- **SC-001**: `discover`, `design`, and `review-planning` all mention
  `reference-research.md` as a durable planning input when relevant.
- **SC-002**: The shared methodology explains that later planning phases reuse
  research conclusions instead of re-deriving them.
- **SC-003**: The slice completes without adding a new readiness state or
  treating missing research as an automatic planning failure.
