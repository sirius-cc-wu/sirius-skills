# AGENTS.md

Default guidance for agents working in `sirius-skills`.

## Repository shape

- `skills/`: independently deployable repository workflow, reverse-engineering,
  iterative-design, implementation, and evolution skills
- `skill-sets/`: canonical installation profiles; `all.txt` lists every active
  skill exactly once and `workflow.txt` defines the default install
- `catalog/`: skill boundaries, provenance, workflow tracks, and relationship
  guidance; `retired-skills.tsv` is the append-only retirement ledger
- `docs/shared/`: canonical shared references copied into consuming skills
- `docs/proposals/`: proposed capabilities that are not deployable skills
- `.github/`: repository guidance for GitHub tooling
- `src/` and `tests/`: the shared-reference packaging helper and repository
  verification
- top-level installation and usage docs such as `README.md`,
  `SKILLS_METHODOLOGY.md`, `PROMPT_GUIDE.md`, and `justfile`

## Core rules

### Keep the active catalog profile-driven

Every deployable skill belongs to `skill-sets/all.txt` and the skill catalog.
Add it to the smallest user-facing profiles that represent its responsibility;
profile membership expresses convenient composition, not a mandatory
lifecycle. Preserve `workflow` as the no-argument install default and keep
`applying-uml-and-patterns` equivalent to `iterative-design` for compatibility.

Do not restore the retired Sirius spec-driven runtime, command catalog, or
planning state model without a separate repository-level decision. The active
iterative-design skills produce durable artifacts but do not depend on that
retired runtime.

### Make skill retirement durable

Treat a deprecated skill as active until it is actually retired: keep it in
`skills/`, `skill-sets/all.txt`, the catalog, and every applicable profile while
its replacement or migration guidance remains available. To retire it, remove
those active surfaces and append its name plus a full Git evidence revision to
`catalog/retired-skills.tsv`. Do not reuse or delete a retired name; correct bad
evidence explicitly without erasing the tombstone.

Profile files remain the source of truth for active install membership. The
host-local managed-skill state is only an ownership receipt written after a
successful installation; it must not become another active profile. Normal
install and uninstall operations may automatically remove only installed names
present in both that state and the retirement ledger. Cleanup by historical
name alone requires the explicit legacy migration command because old generic
names can collide with skills installed from another repository.

### Keep shared skills generic

Do not hardcode company trackers, naming rules, or domain logic. Put
repository-specific conventions in the nearest applicable `AGENTS.md`, avoid a
parallel convention-file control plane, and preserve a useful generic default.

### Keep documentation aligned

When changing a skill or install behavior:

- update the relevant `SKILL.md`
- update top-level docs and examples that describe the behavior
- update `skill-sets/all.txt`, affected profiles, the skill catalog, and focused
  tests when adding or retiring a skill
- update the owning workflow track when a normal handoff or boundary changes

### Treat identifiers as opaque

Do not assume IDs are dates or sequence numbers. Preserve manual identifiers
and validate them only against explicit rules in the applicable `AGENTS.md`.

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

Use `just install` and `just uninstall` for the default workflow profile, or
pass a profile name for another collection. `just install-packaged` and
`just uninstall-packaged` remain aliases with the same profile parameter.
Profile files are the single ownership surface for install and uninstall
membership; do not add a parallel hard-coded managed-skill list. Use
`just prune-retired` for ownership-verified cleanup. Use
`just prune-retired-legacy` only after reviewing the reported unowned names on
a computer whose Sirius installation predates host-local ownership state.

Use `apply_patch` for file edits. Preserve unrelated work in a dirty tree, use
`rg` for searches, and run verification proportional to the changed behavior.

## Checklist

- Confirm only the intended skill packages and files changed.
- Keep `all.txt`, named profiles, the catalog, and discovered skill directories
  consistent.
- Add a retirement tombstone when removing a previously installable skill, and
  keep active names disjoint from retired names.
- Keep shared references and their packaged copies synchronized.
- Preserve the default workflow profile and documented compatibility aliases.
- Update docs, tracks, and focused tests with install-catalog changes.
- Run relevant validation and review the final diff before handoff.
