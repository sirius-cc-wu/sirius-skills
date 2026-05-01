# Slice Specification: Build metrics record and sidecar engine

**Slice**: `mea-metrics-foundation`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: `mea-metrics-foundation`

## 1. Work Item Summary

- **Work Item**: Establish the durable metrics record, derivation rules, and sidecar persistence model for `measure-artifacts`
- **Source Story / Increment / Slice**: `CAM-06` / `I1` / `mea-metrics-foundation`
- **Requested Outcome**: As a maintainer, I want completed features and subfeatures to produce a stable `implementation-metrics.json` record for story size, slice count, execution mode, and churn availability so later reporting can reuse high-confidence workflow evidence.
- **Why this matters**: The subfeature cannot compare guided and direct implementation or support later reporting unless the reusable evidence model exists first.
- **Independent Test**: Run `measure-artifacts` foundation tests against fixture planning and execution packets and confirm the computed sidecar content is deterministic, preserves unsupported or unavailable values explicitly, and writes the same normalized record on repeated runs.

## 2. Acceptance Scenarios

1. **Given** a completed feature or subfeature with durable planning traceability, **When** the foundation measurement flow computes metrics, **Then** it derives story-size points, planned slice count, linked slice IDs, and execution mode from repository artifacts without inventing a second lifecycle model.
2. **Given** a target without commit provenance or with unsupported story sizes, **When** the foundation flow computes metrics, **Then** it records churn as unavailable and surfaces unsupported sizes explicitly instead of silently guessing.
3. **Given** a caller chooses persistence, **When** the measurement result is written, **Then** `implementation-metrics.json` is stored deterministically beside the completed feature or subfeature packet and remains readable by later consumers.

## 3. Functional Requirements

- **FR-001**: The system MUST derive story-size points from durable planning traceability using the fixed weights `S=1`, `M=3`, and `L=5`.
- **FR-002**: The system MUST reject or surface `XL` and other unsupported sizes explicitly rather than folding them into the size score.
- **FR-003**: The system MUST derive planned slice count and linked slice identifiers from planning and execution artifacts already owned by the repository workflow.
- **FR-004**: The system MUST classify execution mode as `guided`, `direct`, `mixed`, or `unknown` from durable artifact evidence.
- **FR-005**: The system MUST represent missing commit provenance and other unavailable evidence explicitly in the metrics record rather than guessing values.
- **FR-006**: The system MUST read and write one normalized `implementation-metrics.json` sidecar per completed feature or subfeature without changing owner metadata semantics.

## 4. Key Entities

- **Implementation Metrics Record**: The normalized evidence payload persisted in `implementation-metrics.json`, including artifact identity, story-size metrics, slice metrics, execution mode, churn, and workflow outcome placeholders.
- **Measurement Target**: A completed feature or subfeature planning packet whose durable planning metadata, traceability, and linked execution artifacts provide the evidence inputs.
- **Evidence Sources**: Existing planning packets, subfeature metadata, slice registries, slice metadata, and optional explicit commit provenance used for reproducible derivation.

## 5. Edge Cases

- A target has no durable story-size source; the corresponding metric must remain unavailable.
- A target includes unsupported story sizes such as `XL`; the size computation must fail or surface the unsupported value clearly.
- A target has no linked execution slices; execution mode may still resolve to `direct` or `unknown`, but slice-linked evidence cannot be invented.
- A sidecar file already exists; rewriting it must stay deterministic instead of accumulating duplicate or reordered fields.
- Commit provenance is absent; churn fields must remain explicit null or unavailable values.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: `slice-traceability.md` is the canonical durable source for story-size and planned-slice derivation when it exists.
- **A2**: The first slice only establishes the metrics engine and sidecar contract; user-facing reporting integration belongs to the next slice.

### Dependencies

- **D1**: Existing planning and subfeature packets already provide the reviewed inputs for `CAM-06`.
- **D2**: Existing execution registry and slice metadata remain the source of truth for linked slice evidence.
- **D3**: Repository validation continues to use `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py` once the slice adds that test suite.

## 7. Success Criteria

- **SC-001**: A completed feature or subfeature can produce a deterministic metrics record with story-size points, planned slice count, linked slice IDs, and execution mode.
- **SC-002**: Unsupported sizes and missing provenance are preserved as explicit unavailable or unsupported values instead of inferred defaults.
- **SC-003**: Write mode persists a stable `implementation-metrics.json` sidecar that later read-only consumers can reuse without mutating planning or execution metadata.
