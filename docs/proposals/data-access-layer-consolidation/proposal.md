# Proposal: Data Access Layer Consolidation

## Problem

`sirius-skills` commands (such as `autoplan.py`, `scaffold_breakdown.py`, `ship.py`, etc.) are implicitly coupled through the files they access. Currently, these commands perform direct file I/O (using `Path.read_text`, `Path.write_text`, `json.loads`) and direct regex parsing/string manipulation on shared workspace files:

- `slice-traceability.md`
- `slice-planning.md`
- `system-design.md`
- registries (`registry.json`)
- metadata files (`.planning-meta.json`, `.subfeature-meta.json`, `.proposal-meta.json`)

This scatters formatting knowledge, schema structures, and extraction patterns across multiple standalone commands. If a file format or schema layout changes, it is difficult to determine which commands are affected, leading to fragile dependencies and implicit coupling that is hard to audit.

## Goals

- **Consolidate Data Access**: Move all direct file reads, writes, and formatting/regex parsers for workspace files out of standalone commands and into a unified Repository/Data Access Layer (DAL) in the `src/sirius_skills/lib/` package.
- **Provide Structured Contracts**: Ensure commands interact only with high-level Python dataclasses, schemas, or models (defined in `lib/`), rather than performing low-level string manipulation on markdown files or dictionaries.
- **Explicit Coupling Map**: Make file format dependencies transparent so that any developer can easily trace which command accesses or updates which workspace structures.
- **Enforce Separation of Concerns**: Isolate command files to executing business logic and argument orchestration, while data validation, parsing, and I/O are handled by the library.

## Non-Goals

- Change the physical layout or directory structure of workspace markdown files and registries.
- Combine the business logic of independent commands into a single monolithic script.
- Replace the existing CLI router or subcommand structure.

## Candidate Capability Areas

- **Markdown Data Repositories**
  - Implement a common reader/writer module for `slice-traceability.md`, `slice-planning.md`, and `system-design.md`.
  - Expose clean functions such as `load_traceability(path)` and `save_traceability(path, records)` to avoid duplicate regex parsing.

- **Registry & Metadata Repositories**
  - Consolidate all metadata json loads/dumps and schema validations in a single location under `lib/workflow_state/`.

- **Architectural Linting & Guardrails**
  - Establish a validation rule or build gate that detects and blocks direct workspace file reads/writes inside `commands/`.

## Constraints

- Maintain full backward compatibility with the existing `sirius` CLI interface and argument parsing.
- Preserve the exact behavior of existing workflow state check transitions and validator runs.

## Desired Outcomes

- Modifying markdown schemas or metadata keys requires updating only a single module in `lib/`, rather than updating multiple files in `commands/`.
- Code readability in commands is improved by removing boilerplate string indexing, regexes, and file system checking.
- The coupling between commands via data is documented explicitly by module imports.

## Success Criteria

- Command modules under `src/sirius_skills/commands/` do not perform direct file reading/writing or regex searches on shared workspace artifacts.
- All 312 workflow tests continue to execute and pass successfully.

## Why This Is Still A Proposal

- The work spans multiple commands, library modules, and requires a structured decoupling of existing data accesses.
- Keep speculative notes here until the team decides on the exact design contract for the new DAL.
