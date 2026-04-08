# Slice Traceability

## Conventions

- Keep story IDs stable across planning docs.
- Use provisional slice IDs until execution bootstrap occurs.
- Treat this subfeature as planning-scoped even though it produces a migration
  script.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Summary | Blocked By | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CTSM-01 | M | Detect legacy change packets in a feature or repo | I1 | CTSM-01-scan-legacy-layout | Scan old `changes/` directories and report candidates. |  | Foundation for all migration behavior |
| CTSM-02 | M | Preview writes before migration runs | I1 | CTSM-02-dry-run-reporting | Show target paths, conflicts, and no-op cases without modifying files. | CTSM-01-scan-legacy-layout | Keeps migration safe for existing repos |
| CTSM-03 | L | Convert old change packets into durable subfeatures | I2 | CTSM-03-metadata-conversion, CTSM-03-path-migration | Map metadata and move planning artifacts into the new structure. | CTSM-02-dry-run-reporting | Highest-risk data conversion step |
| CTSM-04 | M | Make the migration capability reusable and supported | I3 | CTSM-04-skill-docs-and-validation | Add the skill, install wiring, docs, and validation coverage. | CTSM-03-path-migration | Finishes the supported capability |

## Notes

- The migration slices are intentionally sequential because scan, conflict
  handling, metadata conversion, and path movement all operate on the same
  planning tree.
- If later versions need richer repair modes, add new slices rather than
  broadening the MVP migration semantics silently.
