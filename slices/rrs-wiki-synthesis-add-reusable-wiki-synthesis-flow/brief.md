# Slice Specification: Add reusable wiki synthesis flow

**Slice**: `rrs-wiki-synthesis`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: "Add reusable wiki synthesis flow"

## 1. Work Item Summary

- **Work Item**: Extend the `research` workflow so reusable conclusions can be
  written into the derived wiki root, including the selected wiki page plus
  `index.md` and `log.md`.
- **Source Story / Increment / Slice**: `RRS-02` / `I2` / `rrs-wiki-synthesis`
- **Requested Outcome**: As a maintainer, when a repository already has a wiki
  layer and a research run produces reusable conclusions, we want the research
  workflow to update one focused wiki page and the wiki index/log instead of
  leaving reuse status only in the local planning artifact.
- **Why this matters**: It makes cross-feature research conclusions easier to
  find and reuse while still keeping feature-local decisions anchored in
  `reference-research.md`.
- **Independent Test**: Run `pytest -q skills/research/tests/test_research.py`
  and confirm wiki-page, `index.md`, and `log.md` updates happen only when the
  derived wiki root exists and wiki synthesis is explicitly requested.

## 2. Acceptance Scenarios

1. **Given** a feature or subfeature research run with reusable conclusions and
   an existing derived wiki root, **When** the workflow records wiki status as
   written, **Then** it writes or updates the requested wiki page and keeps
   `index.md` and `log.md` in sync.
2. **Given** a repository without the derived wiki root, **When** the workflow
   runs, **Then** it records deferred wiki status locally and does not
   auto-bootstrap wiki files.
3. **Given** a repeated research run that targets the same wiki page, **When**
   the workflow updates the reusable conclusion, **Then** the focused wiki page
   is updated in place and the log records another append-only entry.

## 3. Functional Requirements

- **FR-001**: The `research` workflow MUST update a requested wiki page when
  reusable synthesis is explicitly recorded as written and the derived wiki root
  exists.
- **FR-002**: The `research` workflow MUST maintain the wiki `index.md` and
  `log.md` alongside a written wiki page update.
- **FR-003**: The wiki synthesis path MUST remain rooted in the derived wiki
  directory and MUST NOT auto-bootstrap the wiki layer when the root is absent.
- **FR-004**: The local `reference-research.md` artifact MUST still record wiki
  follow-up status and page location alongside any reusable wiki update.
- **FR-005**: The wiki synthesis flow MUST stay focused on one page per run and
  MUST keep the wiki update linked back to the local planning artifact.

## 4. Key Entities

- **Derived wiki root**: The `<planning-parent>/wiki` directory associated with
  the current planning scope.
- **Wiki page**: The focused reusable synthesis destination chosen for the
  current research run.
- **Wiki index and log**: `index.md` and `log.md`, the durable discovery and
  chronology entrypoints for the wiki layer.

## 5. Edge Cases

- The wiki root exists but `index.md` or `log.md` do not, so the workflow must
  create or update those files inside the existing wiki layer.
- The requested wiki page path points outside the derived wiki root, so the
  workflow must reject it instead of writing outside the wiki layer.
- The wiki root is absent, so the workflow must keep the synthesis local and
  explicitly deferred.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The local `reference-research.md` artifact remains the first durable
  home for feature-local conclusions even when reusable wiki output is written.
- **A2**: A repository with an existing wiki root expects `index.md` and
  `log.md` to be the discoverability surfaces for reusable conclusions.

### Dependencies

- **D1**: The earlier `rrs-research-skill` slice already defined the local
  artifact and wiki-status contract in `research.py`.
- **D2**: The reviewed subfeature design and wiki rules in `AGENTS.md` remain
  the source of truth for append-only `log.md` behavior and content-oriented
  `index.md` entries.

## 7. Success Criteria

- **SC-001**: A research run with a valid wiki root can write one focused wiki
  page plus `index.md` and `log.md`.
- **SC-002**: A research run without a wiki root still succeeds locally and
  records deferred wiki synthesis instead of bootstrapping the wiki layer.
- **SC-003**: The resulting wiki content stays linked to the local
  `reference-research.md` artifact and remains constrained to one page per run.
