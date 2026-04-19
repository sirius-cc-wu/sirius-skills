# Slice Traceability

## Conventions

- Keep story IDs stable across planning docs.
- Use provisional slice IDs until execution bootstrap occurs.
- Treat this subfeature as planning-scoped even though it produces a migration
  script.

## Mapping Table

| Story ID | Story Size | Story Summary | Increments | Slice IDs | Slice Summary | Blocked By | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CTSM-01 | M | Detect legacy change packets in a feature or repo | I1 | ctsm-scan-legacy-layout | Scan old `changes/` directories and report candidates. |  | Foundation for all migration behavior |
| CTSM-02 | M | Preview writes before migration runs | I1 | ctsm-dry-run-reporting | Show target paths, conflicts, and no-op cases without modifying files. | ctsm-scan-legacy-layout | Keeps migration safe for existing repos |
| CTSM-03 | L | Convert old change packets into durable subfeatures | I2 | ctsm-metadata-conversion, ctsm-path-migration | Map metadata and move planning artifacts into the new structure. | ctsm-dry-run-reporting | Highest-risk data conversion step |
| CTSM-04 | M | Make the migration capability reusable and supported | I3 | ctsm-skill-docs-and-validation | Add the skill, install wiring, docs, and validation coverage. | ctsm-path-migration | Finishes the supported capability |

## Notes

- The migration slices are intentionally sequential because scan, conflict
  handling, metadata conversion, and path movement all operate on the same
  planning tree.
- If later versions need richer repair modes, add new slices rather than
  broadening the MVP migration semantics silently.
