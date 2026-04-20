# Implementation Plan: Add reusable wiki synthesis flow

**Slice**: `rrs-wiki-synthesis`  
**Date**: 2026-04-21  
**Status**: Draft  
**Spec**: `brief.md`

## 1. Summary

This slice extends the existing `research` helper so a run can write reusable
wiki output when a derived wiki root already exists and the caller explicitly
marks the wiki update as written. The implementation keeps the local
`reference-research.md` artifact primary, then adds one focused wiki page plus
`index.md` and append-only `log.md` updates inside the existing wiki layer.

## 2. Technical Context

- Current system context:
  - `skills/research/scripts/research.py` already resolves planning targets,
    derives the wiki root from `planning_dir`, writes `reference-research.md`,
    and records wiki status locally.
  - The helper currently rejects `--wiki-status written` when the wiki root does
    not exist, but it does not yet write the wiki page or maintain `index.md`
    and `log.md`.
  - `AGENTS.md` defines the wiki conventions that matter here: keep
    `index.md` content-oriented and `log.md` append-only with
    `## [YYYY-MM-DD] operation | subject` headings.
- Target modules / files:
  - `skills/research/SKILL.md`
  - `skills/research/scripts/research.py`
  - `skills/research/tests/test_research.py`
  - `slices/rrs-wiki-synthesis-add-reusable-wiki-synthesis-flow/`
- Constraints:
  - never auto-bootstrap the wiki root when it is absent
  - keep all wiki writes confined to the derived wiki root
  - keep one wiki page per run
  - keep `reference-research.md` as the durable feature-local source of truth
- Assumptions:
  - creating `index.md` or `log.md` inside an already-existing wiki root is part
    of maintaining the wiki layer, not bootstrapping it
  - the caller provides a focused `--wiki-page` when reusable synthesis is
    written
  - repeated updates to the same wiki page should update the page in place while
    appending a new log entry
- Out of scope:
  - changing the route-into-research threshold
  - adding multi-page wiki synthesis in one run
  - creating a wiki root when it is missing

## 3. Planning Gates

### Architecture / Constraints

- Decision: extend `research.py` with wiki write helpers that run only when
  `--wiki-status written` is used and the derived wiki root already exists.
- Result: PASS
- Notes: This reuses the current helper and keeps all wiki behavior behind the
  existing wiki-status contract.

### Risk / Compliance

- Decision: validate that the requested wiki page stays under the derived wiki
  root, create or update only wiki-local files, and preserve append-only log
  behavior.
- Result: PASS
- Notes: The main risk is writing outside the wiki layer; path validation should
  fail loudly when that happens.

### Testability

- Decision: extend the existing research tests with a wiki-root-present case and
  a repeated-update case, while preserving the no-wiki-root failure case.
- Result: PASS
- Notes: The current temp-dir fixtures already model planning roots and can be
  extended to cover wiki content.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S003 | V001 |
| FR-002 | S002, S003 | V001 |
| FR-003 | S001, S004 | V001, V002 |
| FR-004 | S003 | V001, V002 |
| FR-005 | S001, S002, S003 | V001 |

## 5. Execution Plan

### Packet P01: Extend the research contract for wiki writes

- Scope: Update the skill guidance and helper contract so wiki synthesis is
  explicit and rooted in the existing wiki layer.
- Target files:
  - `skills/research/SKILL.md`
  - `skills/research/scripts/research.py`
- Dependencies: none
- Steps:
  - [ ] S001 Validate the requested wiki page path against the derived wiki root
        and refuse writes outside that root.
  - [ ] S002 Add helper behavior that writes or updates one focused wiki page
        plus `index.md` and append-only `log.md` when wiki status is written.
  - [ ] S003 Keep `reference-research.md` recording wiki status and page details
        while linking the wiki page back to the local research artifact.
  - [ ] S004 Preserve the current no-wiki-root behavior by failing written wiki
        updates when the root is absent instead of bootstrapping it.
- Validation:
  - [ ] V001 Review the helper behavior against the brief and confirm all wiki
        writes stay under the derived wiki root.
- Definition of Done: a single research run can update the local artifact and
  the existing wiki layer together when reusable synthesis is requested.
- Rollback / Mitigation: if wiki content generation becomes too broad, narrow it
  back to one focused page and minimal index/log maintenance.

### Packet P02: Lock wiki synthesis behavior with tests

- Scope: Extend the focused research tests to cover wiki-page, index, and log
  writes.
- Target files:
  - `skills/research/tests/test_research.py`
- Dependencies: P01
- Steps:
  - [ ] S005 Add assertions that a written wiki update creates or updates the
        wiki page plus `index.md` and `log.md`.
  - [ ] S006 Add a repeated-update test proving the wiki page updates in place
        while `log.md` stays append-only.
- Validation:
  - [ ] V002 Run `pytest -q skills/research/tests/test_research.py`
- Definition of Done: wiki-root-present and repeated-update scenarios are
  covered by deterministic tests.
- Rollback / Mitigation: if the page/update fixture grows too large, keep one
  representative repeated-write test and one absent-root test.

## 6. Supporting Notes

### Detailed Design Diagrams (PlantUML)

- Diagram purpose: show how one research run now updates both the local artifact
  and the existing wiki layer when reusable synthesis is requested.
- Diagram type: sequence

```plantuml
@startuml
skinparam backgroundColor white

actor Maintainer
participant "research.py" as Helper
file "reference-research.md" as LocalArtifact
folder "derived wiki root" as WikiRoot
file "wiki page" as WikiPage
file "index.md" as WikiIndex
file "log.md" as WikiLog

Maintainer -> Helper : run with --wiki-status written --wiki-page ...
Helper -> LocalArtifact : write local research artifact
Helper -> WikiRoot : validate root + page path
Helper -> WikiPage : write/update reusable synthesis
Helper -> WikiIndex : upsert page summary entry
Helper -> WikiLog : append timestamped log entry
Helper --> Maintainer : success
@enduml
```

### Research Decisions

- Decision: keep wiki content generation lightweight and link back to
  `reference-research.md` instead of duplicating the entire planning packet.
- Rationale: the local artifact stays the durable source of feature-local
  detail, while the wiki page captures reusable conclusions.
- Alternative considered: update only the local artifact and leave wiki files to
  manual edits.

### Interface Notes

- Interface: `skills/research/scripts/research.py`
- Inputs / outputs:
  - inputs: existing research arguments plus `--wiki-status written` and
    `--wiki-page`
  - outputs: `reference-research.md`, optional wiki page, optional `index.md`,
    optional append-only `log.md`
- Error states / compatibility notes:
  - `--wiki-status written` still requires an existing wiki root
  - `--wiki-page` must resolve inside the derived wiki root
  - repeated writes may update the page but should only append to `log.md`

### Verification Scenarios

- Happy path: wiki root exists, a reusable page is written, and `index.md` plus
  `log.md` update with it.
- Edge case: wiki root missing still fails written wiki output and leaves the
  local artifact behavior unchanged.
- Regression checks: repeated writes update the page content in place while the
  log keeps multiple dated entries.

## 7. Delivery Notes

- Sequencing rationale: finish the local artifact and consumer guidance first,
  then add reusable wiki synthesis as the final layer of the subfeature.
- Risks to monitor:
  - writing outside the derived wiki root
  - turning wiki maintenance into implicit wiki bootstrap
  - duplicating too much local-artifact detail in the wiki page
- Handoff notes for implementation:
  - keep the wiki content format simple, linked, and reusable
  - preserve the existing CLI contract where possible
  - stop once the research tests cover wiki-root-present and repeated-update
    behavior
