# Slice Specification: Route research only when relevant

**Slice**: `rrs-relevance-routing`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: "Route research only when relevant"

## 1. Work Item Summary

- **Work Item**: Define and document when planning should route into the new
  `research` skill and when it should skip that step.
- **Source Story / Increment / Slice**: `RRS-04` / `I1` /
  `rrs-relevance-routing`
- **Requested Outcome**: As a repository adopter, when planning work overlaps
  checked-in references in a way that can change solution shape, we want
  `guide-planning` and methodology guidance to require `research`; otherwise we
  want low-overlap repo-local work to continue without extra ceremony.
- **Why this matters**: It keeps the new `research` capability useful and
  durable without turning every local-only planning task into process overhead.
- **Independent Test**: Run `pytest -q skills/guide-planning/tests/test_manage_planning.py`
  and confirm routing guidance distinguishes research-worthy work from direct
  `discover` or `design` paths.

## 2. Acceptance Scenarios

1. **Given** a planning request where the user explicitly asks for
   reference-project research or discovery/design depends on choosing between
   multiple upstream patterns, **When** `guide-planning` resolves the next step,
   **Then** the maintained guidance routes to `research`.
2. **Given** a small repo-local planning change whose shape does not depend on
   checked-in references, **When** `guide-planning` resolves the next step,
   **Then** the maintained guidance keeps the work on direct planning paths
   instead of adding a mandatory research detour.
3. **Given** a feature or subfeature that overlaps checked-in `references/`
   patterns but already has a durable `reference-research.md`, **When**
   maintainers consult the workflow guidance, **Then** they can see that
   research is conditional on missing or materially changed comparison work
   rather than always repeating the step.

## 3. Functional Requirements

- **FR-001**: The workflow MUST define concrete conditions that make
  `research` the next planning step.
- **FR-002**: The workflow MUST define counterexamples where `research` should
  be skipped because the work is repo-local and does not depend on upstream
  comparison.
- **FR-003**: `guide-planning` guidance and shared methodology guidance MUST
  describe the same routing threshold so maintainers do not get conflicting
  instructions.
- **FR-004**: The routing guidance MUST treat an existing
  `reference-research.md` artifact as prior work that can reduce or eliminate
  the need for a new research step unless the decision scope has materially
  changed.
- **FR-005**: The routing guidance MUST keep `research` advisory within the
  existing planning lifecycle and MUST NOT add a new planning readiness state.

## 4. Key Entities

- **Routing threshold**: The decision rule that determines whether the next
  step is `research` or direct planning work.
- **Reference overlap**: Evidence that a feature or subfeature materially
  depends on checked-in upstream patterns or comparisons.
- **Local-only change**: Planning work whose solution shape can be decided from
  the repo itself without meaningful upstream comparison.

## 5. Edge Cases

- The user explicitly asks for reference-project research even if the overlap
  signal is otherwise weak.
- A planning packet already has `reference-research.md`, so the guidance must
  avoid forcing duplicate work by default.
- A change touches planning docs but still does not depend on upstream
  comparison, so documentation-only scope should not be treated as automatic
  research relevance.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The dedicated `research` skill from `rrs-research-skill` is already
  available as the concrete destination when routing says research is relevant.
- **A2**: This slice sets the routing threshold and examples only; downstream
  planning-doc consumers of `reference-research.md` remain in later slices.

### Dependencies

- **D1**: The reviewed design contract in
  `docs/features/planning-workflow/subfeatures/reference-research-synthesis/system-design.md`
  remains the source of truth for the routing threshold.
- **D2**: Later slices `rrs-research-consumers` and `rrs-wiki-synthesis` depend
  on this slice keeping the research step scoped and non-ceremonial.

## 7. Success Criteria

- **SC-001**: Maintainers can identify when `research` is required versus when
  planning should continue directly.
- **SC-002**: The repo’s `guide-planning` and methodology docs stay aligned on
  the same routing threshold.
- **SC-003**: The slice completes without widening the workflow into a new
  planning state or mandatory research for every local planning change.
