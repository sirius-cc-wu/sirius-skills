# Discover: Data Access Layer Consolidation

## Problem

Workspace state is currently accessed directly inside multiple command modules. Planning, proposal, execution, and artifact-management commands each read and write markdown, JSON registries, and metadata files on their own, which spreads schema knowledge and parsing rules across the codebase.

That makes the repository harder to change safely. A file-format tweak or metadata-key rename can require coordinated edits in several commands, and the real coupling between commands is mostly implicit.

## Goals

- Consolidate shared workspace file access behind reusable library modules in `src/sirius_skills/lib/`.
- Move schema validation and normalization to the library boundary instead of repeating it in commands.
- Make data dependencies obvious through imports and dedicated repository helpers.
- Preserve current CLI behavior, file layout, and workflow state semantics.

## Non-Goals

- Change the on-disk layout of planning, proposal, execution, or registry files.
- Merge unrelated command behavior into one manager.
- Introduce a new workflow surface or a new registry format.

## Current Baseline

Representative command modules still perform direct I/O and parsing against shared artifacts such as:

- `slice-traceability.md`
- `slice-planning.md`
- `system-design.md`
- `registry.json`
- `.planning-meta.json`
- `.subfeature-meta.json`
- `.proposal-meta.json`

The current implementation also includes direct `json.load` / `json.dump` calls, `Path.read_text` / `Path.write_text`, ad hoc `open(...)` usage, and regex-based extraction in command code.

## Stakeholders

- Command maintainers who need predictable file access and fewer duplicated parsers.
- Planning owners who rely on stable metadata transitions.
- Execution owners who depend on traceability and registry consistency.
- Release and review maintainers who want easier auditing of data coupling.

## Constraints

- Keep the public `sirius` command interface stable.
- Preserve existing planning and execution readiness transitions.
- Keep the repo generic-first; the DAL should stay reusable rather than feature-specific.
- Avoid introducing parallel state stores or a second source of truth.

## Success Criteria

- Shared workspace file formats are read and written through central library helpers.
- Commands stop duplicating normalization, validation, and parsing rules.
- A maintainer can identify artifact coupling by following library imports instead of scanning for raw file access.
- Existing tests and CLI behavior continue to work without changing the workspace layout.

## Risks and Open Questions

- Some commands may need staged refactors because several file formats are coupled today.
- A central DAL needs clear ownership boundaries so it does not become a new monolith.
- It is still open how aggressive the repo should be about blocking direct file access in command modules.

## Candidate Stories

- `DALC-01`: centralize workspace markdown reads and writes.
- `DALC-02`: validate metadata at the library boundary.
- `DALC-03`: make command/data coupling explicit through imports.
- `DALC-04`: guard against direct filesystem writes in command modules.

## Next Step

Move into `design` to define the DAL boundaries, module structure, and the validation approach for the first pass.
