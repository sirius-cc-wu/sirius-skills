# Slice Specification: Add source-linked local install helper

**Slice**: `SIM-01-local-helper`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: `split-install-modes / SIM-01-local-helper`

## 1. Work Item Summary

- **Work Item**: Add a generic local install helper that symlinks the managed repo skills into a selected skill home without changing the existing packaged install flow.
- **Source Story / Increment / Slice**: `SIM-01` / `I1` / `SIM-01-local-helper`
- **Requested Outcome**: As a local contributor, I want one deterministic `install-local` / `uninstall-local` path so my repo checkout becomes the runtime source of truth for supported agent CLIs.
- **Why this matters**: Local contributors do not need copied installed skill snapshots, and a source-linked helper removes one major cause of repo-versus-installed drift during everyday development.
- **Independent Test**: Targeted helper tests confirm symlink creation, refresh, and managed-only cleanup in a temporary skill home, and a `make install-local` dry run or smoke invocation succeeds without touching the packaged install path.

## 2. Acceptance Scenarios

1. **Given** a clean temporary skill home, **When** the maintainer runs the local install helper, **Then** each managed skill appears as a symlink to the repo `skills/` directory.
2. **Given** an existing managed symlink and an unrelated personal skill in the same skill home, **When** the maintainer reruns local install or uninstall, **Then** the managed symlink is refreshed or removed and the unrelated skill is left untouched.
3. **Given** the existing packaged install flow is still the compatibility default, **When** the maintainer adds the new local helper entrypoints, **Then** `make install` and `make uninstall` keep their current packaged behavior in this slice.

## 3. Functional Requirements

- **FR-001**: The system MUST provide a local install helper that creates one symlink per managed skill from the repo `skills/` tree into a selected skill home.
- **FR-002**: The local install helper MUST be deterministic and idempotent when rerun against an existing managed local install.
- **FR-003**: The local uninstall helper MUST remove only the managed symlinks it owns and MUST NOT delete unrelated entries in the skill home.
- **FR-004**: The slice MUST expose repo-level entrypoints for the local helper without changing the existing packaged `make install` / `make uninstall` behavior yet.
- **FR-005**: The slice MUST include deterministic helper-focused validation using a temporary skill-home fixture rather than a real global install.

## 4. Key Entities

- **Managed skill set**: The curated list of `sirius-skills` skill directories that the repo installs and removes as one unit.
- **Skill home**: The filesystem directory where an agent CLI discovers installed skills, such as `~/.agents/skills/`.
- **Managed local symlink**: A symlink created by the local helper that points from the selected skill home to one repo-managed skill directory.
- **Unrelated skill entry**: Any non-managed file, directory, or symlink already present in the skill home that the helper must not remove.

## 5. Edge Cases

- A managed target already exists as a symlink to the correct repo path; rerun should succeed without churn.
- A managed target exists but points somewhere else or is a real directory; the helper should fail clearly rather than deleting ambiguous data silently.
- The skill home does not exist yet; the helper should create it.
- One repo-managed skill directory is missing; the helper should stop with an explicit error instead of creating a partial install.

## 6. Assumptions and Dependencies

### Assumptions

- **A1**: The first rollout can use a helper or `Makefile` override such as `SKILLS_HOME` for multi-CLI support without introducing a new durable repo config file.
- **A2**: The packaged install path remains the compatibility default until the later `SIM-02` slice explicitly splits and renames packaged targets.

### Dependencies

- **D1**: The managed skill list in `Makefile` remains the canonical source for which peer skill directories the helper should link.
- **D2**: `SIM-02-packaged-targets` will perform the later command-surface split; this slice only adds the local helper entrypoints it needs.

## 7. Success Criteria

- **SC-001**: A maintainer can run the new local install helper against a temporary skill home and get managed per-skill symlinks to the repo.
- **SC-002**: A matching local uninstall removes only managed symlinks and preserves unrelated skill-home entries.
- **SC-003**: Targeted helper tests pass and the existing packaged `make install` / `make uninstall` behavior is unchanged in this slice.

## 8. Open Clarifications

- None.
