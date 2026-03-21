# AGENTS.md

Default guidance for agents working in `sirius-skills`.

## Repo Shape

`sirius-skills` has three main areas:

- `skills/`: reusable skill definitions and helper scripts
- `.github/`: repository guidance for GitHub tooling
- top-level docs and install helpers such as `README.md`, `SKILLS_METHODOLOGY.md`, and `Makefile`

## Core Rules

### Keep shared skills generic

Core skills should stay reusable across projects. Do not hardcode company
trackers, naming rules, or domain logic unless the repo explicitly documents
that behavior.

### Prefer configuration to hardcoding

Project-specific behavior should normally live in:

- `.skills/identity.json`
- `.skills/plugins/`
- `.specs/config.json`

If you add configurable behavior, document the config surface and preserve a
useful generic default.

### Preserve ownership boundaries

Do not mix workflow responsibilities:

- `spec-driver` owns spec track readiness and registry state
- the execution tracker owns task lifecycle

Do not duplicate execution-tracker lifecycle states inside spec track state.

### Treat IDs as opaque

Do not assume IDs are dates or sequence numbers. If a helper defines an ID
algorithm, follow that helper. Preserve manual IDs exactly.

### Keep docs aligned with behavior

When you change a skill or helper:

- update the relevant `SKILL.md`
- update any top-level docs that describe the behavior
- remove stale examples in the same change when practical

### Prefer backward-compatible changes

Favor additive changes, compatibility shims, and normalization over abrupt
breaking changes. If you must break behavior, document it clearly.

## Working In This Repo

### Skills

Each skill should live in its own directory and usually include:

- `SKILL.md`
- any scripts or assets the skill references

When editing skills:

- keep instructions explicit and actionable
- do not document behavior the repo does not actually implement
- prefer simple interfaces over clever indirection

### Installation

Use `make install` to install or refresh skills and `make uninstall` to remove
the managed skill set. Keep repo-level guidance agent-agnostic unless a
specific integration requires otherwise.

## Agent Checklist

- Read the nearest `README.md`, `SKILL.md`, and nested `AGENTS.md` before
  changing behavior.
- Keep edits small and aligned with the repo's generic-first design.
- If you change config semantics, update docs and examples together.
- If you touch `spec-driver`, keep `.specs/`, `specs/`, and `.skills/`
  behavior consistent.
