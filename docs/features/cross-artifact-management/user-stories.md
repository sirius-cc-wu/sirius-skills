# User Stories: Cross-Artifact Management

## Feature Stories

| Story ID | Title | Description | Initial Capability |
|---|---|---|---|
| CAM-01 | Audit artifact health | As a maintainer, I want the repo to identify broken links, missing required files, and stale lifecycle packets so I can repair artifact drift before it causes workflow confusion. | `audit-artifacts` |
| CAM-02 | Trace artifact lineage | As a maintainer, I want to trace how a slice or feature relates to upstream proposals and downstream execution artifacts so I can understand scope and history quickly. | `trace-artifacts` |
| CAM-03 | Report artifact state | As a maintainer, I want concise summaries of active, reviewed, stale, and completed artifacts so I can see workflow load and bottlenecks without manual folder inspection. | `report-artifacts` |
| CAM-04 | Repair artifact drift | As a maintainer, I want supported repair flows for registry and metadata drift so the repo can recover from merges, manual edits, or partial automation. | `repair-artifacts` |
| CAM-05 | Archive durable history safely | As a maintainer, I want to archive superseded or completed artifacts without losing traceability so the active workflow stays readable while history remains durable. | `archive-artifacts` |
| CAM-06 | Measure workflow evidence | As a maintainer, I want durable implementation metrics and execution-outcome evidence for completed features and subfeatures so I can understand when workflow steps such as `guide-execution` were useful or unnecessary. | `measure-artifacts` |
