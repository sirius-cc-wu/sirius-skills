# Implementation Plan: Build metrics record and sidecar engine

**Slice**: `mea-metrics-foundation`  
**Date**: 2026-04-18  
**Status**: Reviewed for close-slice  
**Spec**: `brief.md`

## 1. Summary

`mea-metrics-foundation` establishes the reusable evidence model behind the
future `measure-artifacts` capability. This slice should add the internal
measurement modules under `skills/measure-artifacts/`, derive story-size,
planned-slice, linked-slice, and execution-mode metrics from existing planning
and execution artifacts, persist deterministic `implementation-metrics.json`
sidecars, and ship fixture-driven tests that keep unavailable or unsupported
inputs explicit.

## 2. Technical Context

- Current system context:
  - `skills/audit-artifacts/scripts/artifact_inventory.py` already resolves the
    planning and execution roots and parses traceability records.
  - `skills/guide-planning/scripts/manage_planning.py`,
    `skills/add-subfeature/scripts/manage_subfeatures.py`, and
    `skills/guide-execution/scripts/manage_execution.py` already own canonical
    metadata and slice registry behavior.
  - no current module computes durable implementation metrics or writes an
    artifact-local sidecar for features or subfeatures.
- Target modules / files:
  - `skills/measure-artifacts/scripts/metrics_engine.py`
  - `skills/measure-artifacts/scripts/metrics_store.py`
  - `skills/measure-artifacts/tests/test_measure_artifacts.py`
  - optional support package files under `skills/measure-artifacts/scripts/`
- Constraints:
  - preserve owner metadata semantics; metrics must live in a separate sidecar
  - keep the first slice focused on reusable engine and persistence, not the
    final user-facing skill wrapper or reporting integration
  - derive values only from durable repository artifacts; avoid heuristics
  - keep missing provenance and unsupported sizes explicit instead of guessed
- Assumptions:
  - `slice-traceability.md` remains the best durable source for story-size and
    planned-slice derivation
  - linked execution-slice evidence can be resolved from `slices/registry.json`
    plus `.slice-meta.json`
  - churn stays unavailable until explicit commit provenance exists
- Out of scope:
  - a user-facing `measure-artifacts` CLI/skill definition
  - `report-artifacts` or `archive-artifacts` consumer integration
  - commit-provenance capture

## 3. Planning Gates

### Architecture / Constraints

- Decision: implement a small internal measurement package that reuses shared
  artifact inventory helpers and writes one dedicated sidecar file per target.
- Result: PASS
- Notes: this keeps the evidence model reusable for later slices while avoiding
  a parallel lifecycle store.

### Risk / Compliance

- Decision: treat unsupported sizes and missing provenance as explicit output
  states and keep sidecar writes deterministic.
- Result: PASS
- Notes: the main risk is letting low-confidence inference look authoritative;
  the engine should refuse that shortcut.

### Testability

- Decision: cover feature and subfeature fixtures, unsupported-size rejection,
  execution-mode classification, sidecar stability, and unavailable churn in a
  dedicated test module.
- Result: PASS
- Notes: fixture-driven tests can exercise the engine without depending on the
  later user-facing CLI.

## 4. Requirement Traceability

| Requirement | Implementation Steps | Validation |
| --- | --- | --- |
| FR-001 | S001, S003 | V001, V002 |
| FR-002 | S002, S003 | V002 |
| FR-003 | S001, S003 | V001, V003 |
| FR-004 | S003 | V003 |
| FR-005 | S003, S004 | V003, V004 |
| FR-006 | S001, S004 | V004, V005 |

## 5. Execution Plan

### Packet P01: Add target resolution and sidecar storage

- Scope: create the new internal skill package, resolve completed feature or
  subfeature targets through existing planning helpers, and read/write one
  deterministic `implementation-metrics.json` sidecar beside that packet.
- Target files:
  - `skills/measure-artifacts/scripts/metrics_store.py`
  - `skills/measure-artifacts/scripts/metrics_engine.py`
  - `skills/measure-artifacts/tests/test_measure_artifacts.py`
- Dependencies: planning and subfeature owner scripts; artifact inventory
- Steps:
  - [x] S001 Add target-resolution helpers that distinguish feature vs
        subfeature packets, load canonical metadata, and resolve the sidecar
        path without changing owner metadata files.
  - [x] S002 Define the normalized metrics-record shape and deterministic JSON
        read/write behavior for `implementation-metrics.json`.
  - [x] S003 Keep sidecar writes explicit and stable so repeated writes do not
        reorder fields or duplicate values.
- Validation:
  - [x] V001 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py -k target`
  - [x] V002 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py -k sidecar`
- Definition of Done: a completed feature or subfeature target can resolve to
  one stable metrics sidecar path and round-trip a normalized record.
- Rollback / Mitigation: keep the new package isolated under
  `skills/measure-artifacts/` so reverting it does not disturb current owner
  scripts.

### Packet P02: Derive the foundation metrics from durable artifacts

- Scope: compute story-size points, planned-slice and linked-slice metrics,
  execution mode, and unavailable churn from planning and execution evidence.
- Target files:
  - `skills/measure-artifacts/scripts/metrics_engine.py`
  - `skills/measure-artifacts/tests/test_measure_artifacts.py`
- Dependencies: P01
- Steps:
  - [x] S004 Reuse traceability parsing and registry readers to derive
        story-size points, planned slice count, and linked execution slice IDs.
  - [x] S005 Classify execution mode as `guided`, `direct`, `mixed`, or
        `unknown` from linked slice evidence.
  - [x] S006 Surface unsupported sizes and missing commit provenance explicitly
        without guessing churn values.
- Validation:
  - [x] V003 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py -k derive`
  - [x] V004 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py -k unavailable`
- Definition of Done: the engine returns a normalized metrics record with
  explicit unsupported or unavailable fields and no invented lifecycle state.
- Rollback / Mitigation: keep derivation logic in a pure data module so future
  CLI and reporting surfaces can change independently.

### Packet P03: Prove the foundation with feature and subfeature fixtures

- Scope: verify the new engine across both target types and lock in the
  deterministic sidecar contract with targeted tests plus repo validation.
- Target files:
  - `skills/measure-artifacts/tests/test_measure_artifacts.py`
- Dependencies: P01, P02
- Steps:
  - [x] S007 Build fixture repos for completed feature and subfeature targets
        with planning and execution evidence.
  - [x] S008 Add assertions for write/read stability, execution-mode outcomes,
        and explicit null churn behavior.
- Validation:
  - [x] V005 `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py`
  - [x] V006 `pytest -q`
- Definition of Done: the foundation engine is covered by slice-specific tests
  and the repo test suite stays green.
- Rollback / Mitigation: keep fixtures local to the new test module to avoid
  coupling unrelated skill tests to the new metric model.

## 6. Supporting Notes

### Detailed Design Diagrams (PlantUML)

- Diagram purpose: show how the foundation engine resolves one completed target,
  derives evidence from planning and execution artifacts, and optionally writes
  the sidecar.
- Diagram type: sequence

```plantuml
@startuml
actor Maintainer
participant "metrics_engine.py" as Engine
participant "artifact_inventory.py" as Inventory
participant "manage_planning.py /\nmanage_subfeatures.py" as PlanningOwners
participant "manage_execution.py" as Execution
participant "metrics_store.py" as Store
database "planning packet" as PlanningPacket
database "slice registry + metadata" as SliceData
file "implementation-metrics.json" as Sidecar

Maintainer -> Engine: measure completed target
Engine -> PlanningOwners: resolve target + metadata
PlanningOwners --> Engine: completed feature/subfeature packet
Engine -> Inventory: parse traceability records
Inventory --> Engine: story sizes + planned/execution slice ids
Engine -> Execution: load linked slice evidence
Execution --> Engine: execution statuses + metadata
Engine -> Engine: derive score, counts, mode, unavailable churn
Engine -> Store: normalize record [optional write]
Store -> Sidecar: write deterministic JSON
Store --> Engine: normalized record
Engine --> Maintainer: metrics record
@enduml
```

### Research Decisions

- Decision: reuse `artifact_inventory.py` for traceability parsing instead of
  copying markdown-table parsing into a second module.
- Rationale: the inventory helper already understands the current traceability
  table shape and keeps cross-artifact tooling aligned.
- Alternative considered: build a brand-new parser inside
  `skills/measure-artifacts/`; rejected because it would drift from existing
  artifact readers immediately.

### Data Model Notes

- **Measurement target**
  - Fields / relationships:
    - `artifact_type`
    - `artifact_id`
    - `artifact_path`
    - `status`
    - optional `parent_feature`
  - Validation rules:
    - target must be a completed feature or subfeature packet
    - target path must resolve inside the active planning scope

- **Implementation metrics record**
  - Fields / relationships:
    - identity (`artifact_type`, `artifact_id`, `computed_at`, `status`)
    - `story_size`
    - `slices`
    - `execution_mode`
    - `implementation_churn`
    - optional workflow outcome placeholders
  - Validation rules:
    - story-size weights stay fixed at `S=1`, `M=3`, `L=5`
    - unsupported sizes are preserved explicitly
    - churn stays unavailable unless provenance exists

### Interface Notes

- Interface: internal Python helpers under `skills/measure-artifacts/scripts/`
- Inputs / outputs:
  - input: a completed feature or subfeature selector plus optional explicit
    write intent
  - output: one normalized metrics record and, in write mode, one
    `implementation-metrics.json` sidecar
- Error states / compatibility notes:
  - missing targets or non-completed targets should fail explicitly
  - unsupported sizes should surface clearly rather than being dropped
  - the foundation slice should not yet depend on a user-facing CLI contract

### Verification Scenarios

- Happy path:
  - derive metrics for a completed subfeature with linked execution slices and
    write a deterministic sidecar
- Edge case:
  - keep churn unavailable when no commit provenance exists
  - surface unsupported story sizes explicitly
- Regression checks:
  - feature and subfeature targets both resolve correctly
  - repeated sidecar writes stay byte-stable apart from recomputed timestamps

## 7. Delivery Notes

- Sequencing rationale: establish target resolution and the sidecar contract
  first, then derive the foundation metrics, then lock the behavior with
  feature/subfeature fixtures.
- Risks to monitor: conflating planned-slice identifiers with lifecycle state,
  silently inferring churn without provenance, or letting sidecar writes drift
  from deterministic ordering.
- Handoff notes for implementation: keep the new package pure and reusable so
  the next slice can add the user-facing CLI and reporting consumers without
  restructuring the core engine.

## 8. Execution Review Outcome

- Outcome: ready for `close-slice`
- Review classification:
  - brief-to-implementation gap: none
  - intent-to-brief gap: none
  - follow-up outside the active slice: none; user-facing CLI and reporting
    integration remain intentionally queued in `mea-metrics-consumers`
- Durable artifact note:
  - `mea-metrics-foundation` adds `skills/measure-artifacts/` internal
    foundation modules for target resolution, metrics derivation, and sidecar
    persistence, and extends shared traceability parsing with optional
    `story_size` support.
- Validation evidence:
  - `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py`
  - `pytest -q`
