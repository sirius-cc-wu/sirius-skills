# Discover: Installation and Configuration

## Problem

The repository is designed as a reusable skill collection, but successful adoption depends on a clear install path and well-separated configuration surfaces. Teams need a predictable way to register the managed skills, configure planning and execution layout, and apply project-specific naming conventions without hardcoding company logic into the shared skills.

## Goals

- Provide a managed installation and uninstallation path for the skill set.
- Keep project-specific behavior in config rather than hardcoded into core skills.
- Separate planning layout, execution layout, and naming conventions into distinct config files.
- Allow optional project-local extensions without requiring a full plugin loader.

## Non-Goals

- Auto-load arbitrary plugin code from `.skills/plugins/`.
- Collapse all configuration into one generic catch-all file.
- Force tracker-specific setup for repositories that want generic defaults.

## Primary Actors

- Maintainer installing the shared skill set.
- Project owner configuring planning, execution, and naming behavior.
- Extension author adding project-local helper configs or scripts.
- Contributors relying on the configured skill behavior in day-to-day work.

## Constraints

- Managed installation goes through the repository `Makefile`.
- Config files live under `.skills/`.
- `.skills/plugins/` is a convention that must be read explicitly by a specific skill.
- Core skills must work with generic defaults when config files are absent.

## Confirmed Signals in Repo

- `Makefile` defines `make install` and `make uninstall` using `npx skills add/remove`.
- `README.md` documents generic-first workflow and config surfaces.
- `AGENTS.md` emphasizes configuration over hardcoding and preserving ownership boundaries.
- `skills/commit/`, `skills/create-pr/`, `skills/planning-driver/`, and `skills/execution-driver/` all consume configuration in controlled ways.

## Success Criteria

- A maintainer can install or remove the managed skill set through one documented entrypoint.
- A project can configure planning, execution, and conventions independently without modifying core skills.
- Optional project-local extensions remain opt-in and explicitly documented.

## Risks and Open Questions

- Configuration naming can drift over time if layer and owner boundaries are not kept consistent.
- Plugin conventions are documented but not auto-discovered, so users may expect more automation than exists.
- Installation can silently diverge if new managed skills are added but `Makefile` guidance is not updated.
