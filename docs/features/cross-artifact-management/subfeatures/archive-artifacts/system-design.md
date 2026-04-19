# System Design: Archive Artifacts

## 1. Scope

`archive-artifacts` adds an explicit archival surface for durable workflow
history. The first version should report archive candidates across proposals,
finalized subfeatures, and slices, and support safe apply mode for closed
execution slices through the existing execution owner helper.

The next retention step should treat archived slice folders as optional storage,
not as the only durable history layer. Once a closed slice has been summarized
into the owning feature or subfeature `system-design.md`, a maintainer may later
choose to prune the archived slice directory if it no longer provides enough
value to justify keeping the full execution packet on disk.

## 2. Design Goals

- Make candidate discovery read-only and reviewable.
- Reuse the execution layer's built-in slice archival behavior for actual moves.
- Keep v1 apply mode narrow and explicit.
- Preserve traceability by relying on owner-managed archive metadata where
  supported.
- Ensure the `system-design.md` summary block is self-contained enough that it
  remains meaningful after the archived slice folder is pruned.
- Leave room for a later prune flow that removes archived slice folders without
  being treated as accidental corruption by other artifact-management skills.

## 3. Proposed Shape

### 3.1 Candidate discovery

Candidate rules in v1:

- proposals with status `rejected`, `superseded`, or `promoted`
- subfeatures with status `finalized`
- slices with status `closed`

### 3.2 Apply mode

Apply mode in v1:

- requires both `--artifact-type slice` and `--artifact-id`
- archives that one closed slice through `manage_execution.archive_slice(...)`
- rejects unsupported apply combinations for other artifact types

### 3.3 Retention model after archival

The intended steady-state model should distinguish two historical layers:

1. **Retained planning history**
   - summary blocks copied into the owning feature or subfeature
     `system-design.md`
   - durable feature/subfeature story context and planning traceability
2. **Optional execution packet retention**
   - archived slice folders under `slices/.archived/`
   - useful while maintainers still want the original `brief.md`,
     `blueprint.md`, and checklists on disk

When the second layer is pruned intentionally, other workflow skills should
stop treating the missing archived directory as an error if the repo has already
preserved the summarized history and removed the slice from active reporting
surfaces.

### 3.4 Output

One result shape should power:

- candidate summaries by artifact type
- targeted candidate inspection
- apply-mode outcome for supported slice archival

## 4. CLI contract

```bash
python3 skills/archive-artifacts/scripts/archive_artifacts.py
python3 skills/archive-artifacts/scripts/archive_artifacts.py --artifact-type proposal
python3 skills/archive-artifacts/scripts/archive_artifacts.py --artifact-type slice --artifact-id rpt-artifact-state-report --apply
python3 skills/archive-artifacts/scripts/archive_artifacts.py --json
```

## 5. Validation strategy

- Fixture-driven tests should cover candidate discovery, unsupported apply
  combinations, and closed-slice archival through the owner helper.
- Full repo validation remains `pytest -q`.

## 6. Risks

- Users may assume candidate reporting implies apply support for all artifact
  layers, so the CLI must reject unsupported apply targets clearly.
- Archive moves must preserve execution traceability and registry integrity.
- If later prune behavior is added without corresponding audit/report changes,
  deleted archived slice folders will be mistaken for broken active state.
