# AGENTS.md

Default guidance for agents working in `sirius-skills`.

## Repository shape

- `skills/`: the four managed skills: `simplify`, `create-pr`, `commit`, and
  `governance-update`
- `docs/shared/`: canonical shared references copied into consuming skills
- `.github/`: repository guidance for GitHub tooling
- `src/` and `tests/`: helper package code and its verification
- `docs/features/`, `docs/wiki/`, and `slices/`: historical artifacts from the
  retired spec-driven development workflow
- top-level installation and usage docs such as `README.md`,
  `SKILLS_METHODOLOGY.md`, `PROMPT_GUIDE.md`, and `justfile`

## Core rules

### Keep the managed catalog focused

The supported catalog contains only `simplify`, `create-pr`, `commit`, and
`governance-update`. Do not reintroduce planning, execution, artifact-lifecycle,
or other spec-driven development skills without an explicit repository-level
decision.

### Keep shared skills generic

Do not hardcode company trackers, naming rules, or domain logic. Put
repository-specific conventions in `.skills/conventions.json` and preserve a
useful generic default.

### Keep documentation aligned

When changing a skill or install behavior:

- update the relevant `SKILL.md`
- update top-level docs and examples that describe the behavior
- update `managed_skills` and its focused tests when adding or retiring a skill
- keep historical SDD material clearly labeled as historical rather than
  current usage guidance

### Treat identifiers as opaque

Do not assume IDs are dates or sequence numbers. Preserve manual identifiers
and validate them only against configured conventions.

### Keep technical documentation approachable

Introduce project-specific concepts in plain language on first use. Name test
scenarios after the behavior being verified and retain exact identifiers only
where they help match code, configuration, or logs.

### Prefer backward-compatible changes

Favor additive changes, compatibility shims, and normalization over abrupt
breakage. Document intentional breaking behavior clearly.

## Working in this repository

Read the nearest `README.md`, `SKILL.md`, and nested `AGENTS.md` before changing
behavior. Keep skill instructions concise, explicit, and actionable. A skill
folder should contain its required `SKILL.md` plus only the scripts, references,
or assets needed to perform that skill.

Use `just install` and `just uninstall` for the supported packaged workflow.
`just install-packaged` and `just uninstall-packaged` remain aliases. Packaged
installation must register exactly the names in `managed_skills`.

Use `apply_patch` for file edits. Preserve unrelated work in a dirty tree, use
`rg` for searches, and run verification proportional to the changed behavior.

## Checklist

- Confirm only the intended skill packages and files changed.
- Keep shared references and their packaged copies synchronized.
- Update docs and focused tests with install-catalog changes.
- Run relevant validation and review the final diff before handoff.
