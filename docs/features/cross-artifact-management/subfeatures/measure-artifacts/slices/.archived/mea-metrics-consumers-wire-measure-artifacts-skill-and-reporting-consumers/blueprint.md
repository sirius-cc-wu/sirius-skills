# Implementation Plan: Wire measure-artifacts skill and reporting consumers

**Slice**: `mea-metrics-consumers`  
**Date**: 2026-04-18  
**Status**: Reviewed for close-slice  
**Spec**: `brief.md`

## 1. Summary

`mea-metrics-consumers` turns the foundation measurement engine into a usable
repository capability. This slice should add the user-facing
`measure-artifacts` skill and CLI, expose text/JSON plus explicit write mode,
enrich `report-artifacts` with optional persisted metrics, and wire the new
skill into repo install/docs surfaces.

## 2. Technical Context

- Current system context:
  - `skills/measure-artifacts/scripts/metrics_engine.py` and
    `metrics_store.py` already resolve completed targets and derive/persist the
    foundation metrics record.
  - `skills/report-artifacts/scripts/report_data.py` already normalizes report
    records across proposals, features, subfeatures, and slices.
  - `skills/report-artifacts/scripts/report_artifacts.py` already renders text
    and JSON from one shared report result.
- Target modules / files:
  - `skills/measure-artifacts/SKILL.md`
  - `skills/measure-artifacts/scripts/measure_artifacts.py`
  - `skills/measure-artifacts/tests/test_measure_artifacts.py`
  - `skills/report-artifacts/scripts/report_data.py`
  - `skills/report-artifacts/scripts/report_artifacts.py`
  - `skills/report-artifacts/tests/test_report_artifacts.py`
  - `README.md`
  - `Makefile`
- Constraints:
  - keep reporting read-only; only `measure-artifacts` write mode may persist
    the sidecar
  - keep archive-facing metric display out of this slice
  - preserve the existing report record model instead of inventing a new report
    lifecycle state
- Assumptions:
  - the foundation metrics record remains stable enough to surface directly in
    JSON output and summarized text output
  - user-facing output should stay useful even when churn or size fields are
    unavailable
- Out of scope:
  - archive-facing metric display
  - richer workflow-outcome signals beyond the current placeholders
  - commit-provenance capture

## 3. Planning Gates

### Architecture / Constraints

- Decision: add one thin CLI/skill wrapper over the existing metrics engine and
  reuse the persisted sidecar in `report-artifacts` as an optional enrichment.
- Result: PASS
- Notes: this keeps the measurement core separate from read-only consumers and
  avoids duplicating derivation logic.

### Risk / Compliance

- Decision: require explicit write mode for sidecar persistence and keep report
  reads tolerant of missing sidecars.
- Result: PASS
- Notes: the main risk is accidentally making reporting mutate state or treating
  optional metrics as required metadata.

### Testability

- Decision: extend the measure/report test modules to cover CLI rendering, write
  mode, and metrics-enriched reports, then run the full repo suite.
- Result: PASS
- Notes: fixture repos from the foundation tests can be reused for CLI cases.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S006 | V001, V004 |
| FR-002 | S001, S002 | V001, V002 |
| FR-003 | S002, S003 | V001, V002 |
| FR-004 | S004, S005 | V003 |
| FR-005 | S004, S005 | V003, V004 |
| FR-006 | S006, S007 | V004 |

## 5. Execution Plan

### Packet P01: Add the measure-artifacts skill wrapper and CLI

- Scope: expose the foundation engine through a command with text/JSON output,
  explicit write mode, and a packaged `SKILL.md`.
- Target files:
  - `skills/measure-artifacts/SKILL.md`
  - `skills/measure-artifacts/scripts/measure_artifacts.py`
  - `skills/measure-artifacts/tests/test_measure_artifacts.py`
- Dependencies: foundation engine and metrics store
- Steps:
  - [x] S001 Add CLI argument parsing for target selection, optional `--scope`,
        `--json`, and explicit persistence mode.
  - [x] S002 Render human-readable and JSON output from one metrics result and
        keep writes behind an explicit flag.
  - [x] S003 Author `skills/measure-artifacts/SKILL.md` with usage, output, and
        guardrails.
- Validation:
  - [x] V001 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py -k cli`
  - [x] V002 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py -k sidecar`
- Definition of Done: maintainers can run `measure-artifacts` directly and
  choose between preview and persistence.
- Rollback / Mitigation: keep the CLI thin so later output changes do not force
  engine rewrites.

### Packet P02: Reuse persisted metrics in report-artifacts

- Scope: enrich feature/subfeature report records with optional implementation
  metrics and surface them in text/JSON output without changing report
  ownership.
- Target files:
  - `skills/report-artifacts/scripts/report_data.py`
  - `skills/report-artifacts/scripts/report_artifacts.py`
  - `skills/report-artifacts/tests/test_report_artifacts.py`
- Dependencies: P01, foundation sidecar contract
- Steps:
  - [x] S004 Load persisted `implementation-metrics.json` sidecars for feature
        and subfeature report records when they exist.
  - [x] S005 Extend report text/JSON output to surface the optional metrics while
        keeping absent sidecars non-fatal and read-only.
- Validation:
  - [x] V003 `pytest -q skills/report-artifacts/tests/test_report_artifacts.py -k metrics`
- Definition of Done: report consumers can see persisted workflow evidence
  without changing the raw report lifecycle model.
- Rollback / Mitigation: keep metrics enrichment optional and local to report
  record rendering.

### Packet P03: Ship repo wiring and end-to-end validation

- Scope: register the new skill in repo docs and managed install surfaces, then
  validate the slice-specific and full-repo suites.
- Target files:
  - `README.md`
  - `Makefile`
  - `skills/measure-artifacts/tests/test_measure_artifacts.py`
  - `skills/report-artifacts/tests/test_report_artifacts.py`
- Dependencies: P01, P02
- Steps:
  - [x] S006 Add `measure-artifacts` to the managed install list and top-level
        skill inventory in repo docs.
  - [x] S007 Confirm the slice-specific and repo-wide validation commands remain
        green after the new skill ships.
- Validation:
  - [x] V004 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py && pytest -q skills/report-artifacts/tests/test_report_artifacts.py`
  - [x] V005 `pytest -q`
- Definition of Done: the new skill is documented, installable, and validated
  together with its first report consumer.
- Rollback / Mitigation: localize docs/install edits to the new skill so the
  rest of the managed skill set remains unchanged if reverted.

## 6. Supporting Notes

### Detailed Design Diagrams (PlantUML)

- Diagram purpose: show how the user-facing measurement CLI reuses the internal
  engine and how reporting consumes persisted sidecars read-only.
- Diagram type: sequence

```plantuml
@startuml
actor Maintainer
participant "measure_artifacts.py" as MeasureCli
participant "metrics_engine.py" as Engine
participant "metrics_store.py" as Store
participant "report_data.py" as ReportData
file "implementation-metrics.json" as Sidecar

Maintainer -> MeasureCli: run measure-artifacts [--json] [--write]
MeasureCli -> Engine: build metrics record
Engine --> MeasureCli: normalized record
MeasureCli -> Store: write sidecar [when --write]
Store -> Sidecar: persist deterministic JSON
MeasureCli --> Maintainer: text or JSON output

Maintainer -> ReportData: build report result
ReportData -> Store: read sidecar [optional]
Store -> Sidecar: load metrics if present
ReportData --> Maintainer: report records enriched with optional metrics
@enduml
```

### Research Decisions

- Decision: let `report-artifacts` read the sidecar through the shared metrics
  store normalization instead of duplicating JSON-shape parsing.
- Rationale: the sidecar contract is part of the measure-artifacts capability,
  so report consumers should reuse that normalization rather than drift.
- Alternative considered: parse raw JSON directly inside `report_data.py`;
  rejected because a second parser would make the sidecar contract harder to
  evolve safely.

### Interface Notes

- Interface: `python3 skills/measure-artifacts/scripts/measure_artifacts.py`
- Inputs / outputs:
  - input: feature/subfeature selector plus optional `--scope`, `--json`, and
    explicit write mode
  - output: human-readable text or JSON metrics for one completed target
- Error states / compatibility notes:
  - non-completed targets should fail explicitly
  - report consumers must tolerate a missing sidecar and remain read-only
  - archive-facing surfaces stay untouched in this slice

### Verification Scenarios

- Happy path:
  - run `measure-artifacts` for a completed target and persist the sidecar
- Edge cases:
  - render text output when churn is unavailable
  - build report output when some records have metrics and others do not
- Regression checks:
  - the CLI and report consumer both reuse the same normalized metrics contract
  - `pytest -q` stays green

## 7. Delivery Notes

- Sequencing rationale: expose the CLI first, then reuse the persisted sidecar
  in reporting, then ship docs/install wiring.
- Risks to monitor: accidentally mutating state from report consumers, or
  over-formatting text output so unavailable metrics become confusing.
- Handoff notes for implementation: keep the new CLI thin, keep report
  enrichment optional, and keep archive-facing display deferred.

## 8. Execution Review Outcome

- Outcome: ready for `close-slice`
- Review classification:
  - brief-to-implementation gap: none
  - intent-to-brief gap: none
  - follow-up outside the active slice: none; archive-facing metric display
    remains intentionally deferred outside the current reviewed scope
- Durable artifact note:
  - `mea-metrics-consumers` adds the user-facing `measure-artifacts` skill
    and CLI, enriches `report-artifacts` with optional persisted metrics, and
    wires the new capability into the managed install and README surfaces.
- Validation evidence:
  - `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py`
  - `pytest -q skills/report-artifacts/tests/test_report_artifacts.py`
  - `pytest -q`
