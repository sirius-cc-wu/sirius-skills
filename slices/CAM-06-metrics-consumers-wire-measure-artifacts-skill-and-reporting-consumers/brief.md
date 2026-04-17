# Slice Specification: Wire measure-artifacts skill and reporting consumers

**Slice**: `CAM-06-metrics-consumers`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: `CAM-06-metrics-consumers`

## 1. Work Item Summary

- **Work Item**: Expose the new metrics foundation through a user-facing `measure-artifacts` skill and let `report-artifacts` reuse persisted metrics when they exist
- **Source Story / Increment / Slice**: `CAM-06` / `I2` / `CAM-06-metrics-consumers`
- **Requested Outcome**: As a maintainer, I want to run `measure-artifacts` directly for a completed feature or subfeature and see those persisted metrics appear in reporting output so workflow evidence becomes reusable instead of hidden behind internal helpers.
- **Why this matters**: The foundation slice creates the evidence model, but the capability is not yet usable or visible to maintainers until the CLI, skill definition, and first consumer are wired.
- **Independent Test**: Run the `measure-artifacts` and `report-artifacts` test modules and confirm the CLI emits text/JSON output, write mode persists the sidecar, and reporting includes the persisted metrics without mutating lifecycle ownership.

## 2. Acceptance Scenarios

1. **Given** a completed feature or subfeature, **When** a maintainer runs `measure-artifacts`, **Then** the command resolves the target, computes metrics from durable artifacts, and renders text or JSON output clearly.
2. **Given** a maintainer requests persistence, **When** `measure-artifacts` runs in write mode, **Then** it writes `implementation-metrics.json` deterministically beside the target packet.
3. **Given** persisted metrics exist for a feature or subfeature, **When** `report-artifacts` renders records, **Then** the report includes that evidence read-only without changing planning or execution metadata.

## 3. Functional Requirements

- **FR-001**: The system MUST expose a user-facing `measure-artifacts` command and skill definition for completed features and subfeatures.
- **FR-002**: The command MUST support human-readable text output and `--json` output from the same metrics result.
- **FR-003**: The command MUST support explicit persistence of `implementation-metrics.json` and avoid hidden mutation by default.
- **FR-004**: `report-artifacts` MUST read persisted metrics sidecars when they exist and preserve read-only behavior when they do not.
- **FR-005**: Reporting output MUST surface metrics in a form reusable by humans and later automation without inventing a new lifecycle model.
- **FR-006**: Repository docs and managed install surfaces MUST include the new skill once the user-facing wrapper exists.

## 4. Key Entities

- **Measure Artifacts CLI Result**: The rendered text or JSON payload returned by the new command for one completed target.
- **Persisted Metrics Sidecar**: The `implementation-metrics.json` file created by explicit write mode and reused later by reporting.
- **Report Record with Metrics**: An existing `report-artifacts` record enriched with optional implementation evidence for completed features or subfeatures.

## 5. Edge Cases

- A target is not implemented/finalized yet; the CLI must fail explicitly instead of writing partial metrics.
- A target has no persisted sidecar and the maintainer only runs reporting; `report-artifacts` must stay read-only and tolerate the missing metrics.
- Text output must remain readable when size or churn fields are unavailable.
- Report consumers must not assume archive-facing display or other downstream integrations that this slice intentionally defers.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The foundation engine and sidecar contract from `CAM-06-metrics-foundation` remain the internal source of truth for measurement logic.
- **A2**: Archive-facing metric display remains out of scope for this slice and should stay deferred.

### Dependencies

- **D1**: `skills/measure-artifacts/scripts/metrics_engine.py` and `metrics_store.py` already compute and persist the foundation record.
- **D2**: `skills/report-artifacts/` remains the first read-only consumer of persisted metrics.
- **D3**: Repository validation uses `pytest -q skills/measure-artifacts/tests/test_measure_artifacts.py && pytest -q skills/report-artifacts/tests/test_report_artifacts.py`.

## 7. Success Criteria

- **SC-001**: Maintainers can run `measure-artifacts` for a completed feature or subfeature and receive correct text or JSON output.
- **SC-002**: Explicit write mode persists a deterministic sidecar without changing owner metadata semantics.
- **SC-003**: `report-artifacts` includes persisted metrics when present and remains stable when metrics are absent.
