# System Design: Report Artifacts

## 1. Scope

`report-artifacts` adds a read-only reporting layer on top of the durable repo
artifacts already inventoried by `audit-artifacts` and linked by
`trace-artifacts`. It should summarize operational state instead of introducing
new persistent report files.

## 2. Design Goals

- Reuse the shared inventory and existing owner metadata instead of duplicating
  discovery logic.
- Support concise overview reporting plus grouped report modes.
- Surface stale packets through an explicit threshold parameter.
- Keep the output reusable for humans and future automation.

## 3. Proposed Shape

### 3.1 Shared data flow

1. Load the shared artifact inventory.
2. Normalize proposal, feature, subfeature, and slice rows into one reporting
   record shape.
3. Enrich those records with:
   - artifact type
   - artifact ID
   - status
   - updated timestamp
   - parent feature when applicable
   - stale classification based on the configured threshold
4. Build grouped summaries and optional detail rows from the same record set.

### 3.2 Report record model

Each record should include:

- `artifact_type`
- `artifact_id`
- `status`
- `path`
- `updated_at`
- `parent_feature`
- `is_stale`

### 3.3 Supported report modes

- `overview`: counts by artifact type plus stale counts
- `status`: counts grouped by lifecycle status
- `parent`: counts grouped by parent feature

Optional artifact-type filtering should apply before grouping so both text and
JSON stay consistent.

## 4. CLI contract

```bash
python3 skills/report-artifacts/scripts/report_artifacts.py
python3 skills/report-artifacts/scripts/report_artifacts.py --group-by status
python3 skills/report-artifacts/scripts/report_artifacts.py --group-by parent --artifact-type subfeature
python3 skills/report-artifacts/scripts/report_artifacts.py --stale-days 21 --json
```

## 5. Validation strategy

- Fixture-driven tests should cover overview reporting, grouping by status,
  grouping by parent feature, and stale classification.
- Full repo validation remains `pytest -q`.

## 6. Risks

- Different artifact owners use different lifecycle vocabularies, so the report
  layer must group raw statuses rather than inventing a universal state machine.
- Parent grouping must preserve slice feature ownership and subfeature parent
  ownership without conflating them.
