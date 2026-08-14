# AGENTS.md

Default guidance for agents working in `sirius-skills`.

## Repository shape

- `skills/`: independently deployable skills for repository workflow, reverse
  engineering, iterative design, implementation, and evolution
- `skill-sets/`: canonical installation profiles. `all.txt` lists every active
  skill once. `workflow.txt` defines the default installation.
- `catalog/`: skill boundaries, provenance, workflow tracks, and relationship
  guidance. `retired-skills.tsv` is the append-only retirement ledger.
- `docs/shared/`: canonical shared references copied into consuming skills
- `docs/ideas/`: candidate-direction one-pagers from the `idea-refine`
  workflow
- `docs/proposals/`: legacy Sirius proposals and their historical iteration
  records; these are not deployable skills
- `.github/`: GitHub repository guidance
- `src/` and `tests/`: shared-reference packaging and repository verification
- Top-level installation and usage documentation, including `README.md`,
  `SKILLS_METHODOLOGY.md`, `PROMPT_GUIDE.md`, and `justfile`

## Core rules

### Keep the active catalog profile-driven

Put every deployable skill in `skill-sets/all.txt` and the skill catalog. Add it
to the smallest user-facing profiles that represent its responsibility. Profile
membership expresses convenient composition. It does not define a mandatory
lifecycle.

Keep `workflow` as the no-argument installation default. Keep
`applying-uml-and-patterns` equivalent to `iterative-design` for compatibility.

Do not restore the retired Sirius spec-driven runtime, command catalog, or
planning state model without a separate repository-level decision. Active
iterative-design skills produce durable artifacts. They do not depend on that
retired runtime.

### Make skill retirement durable

Keep a deprecated skill active until you retire it. Keep it in `skills/`,
`skill-sets/all.txt`, the catalog, and every applicable profile until its
replacement or migration guidance is available. To retire a skill, remove it
from those active surfaces and append its name and a full Git evidence revision
to `catalog/retired-skills.tsv`.

Do not reuse or delete a retired name. Correct bad evidence explicitly. Do not
erase the tombstone.

Profile files are the source of truth for active installation membership.
Host-local managed-skill state is only an ownership receipt written after a
successful installation. Do not treat it as another active profile.

Normal install and uninstall operations may automatically remove only installed
names that appear in both the ownership state and the retirement ledger.
Cleanup by historical name alone requires the explicit legacy migration command.
Old generic names can collide with skills from another repository.

### Keep installed skills generic

Skills under `skills/` are installed into other repositories. Keep them free of
company-specific and consumer-repository-specific trackers, naming rules, and
domain logic. Put those rules in the consuming repository's nearest
`AGENTS.md`. Do not create a parallel convention-file control plane.

### Keep documentation aligned

When you change a skill or installation behavior:

- update the relevant `SKILL.md`;
- update top-level documentation and examples that describe the behavior;
- update `skill-sets/all.txt`, affected profiles, the catalog, and focused tests
  when you add or retire a skill; and
- update the owning workflow track when a normal handoff or boundary changes.

### Treat identifiers as opaque

Treat IDs as opaque. Do not assume that they contain dates or sequence numbers.
Preserve manual identifiers. Validate them only against explicit rules in the
applicable `AGENTS.md`.

### Write all artifacts in STE-style

Write all project artifacts in STE-style. Use short, direct, unambiguous
sentences and consistent terminology. Preserve exact identifiers, normative
meaning, evidence, lifecycle, and traceability.

### Keep technical documentation approachable

Introduce project-specific concepts in plain language on first use. Name test
scenarios after the behavior they verify. Keep exact identifiers when they
help readers match code, configuration, or logs.

### Prefer backward-compatible changes

Prefer additive changes, compatibility shims, and normalization over abrupt
breakage. Document intentional breaking behavior clearly.

## Working in this repository

Before changing behavior, read the nearest `README.md`, `SKILL.md`, and nested
`AGENTS.md`. Keep skill instructions concise, explicit, and actionable. A skill
folder should contain its required `SKILL.md` and only the scripts, references,
or assets that the skill needs.

Use `just install` and `just uninstall` for the default workflow profile. Pass a
profile name for another collection. `just install-packaged` and
`just uninstall-packaged` are aliases with the same profile parameter.

Profile files own installation and uninstallation membership. Do not add a
parallel hard-coded managed-skill list. Use `just prune-retired` for
ownership-verified cleanup. Use `just prune-retired-legacy` only after reviewing
reported unowned names on a computer whose Sirius installation predates
host-local ownership state.

Use `apply_patch` for file edits. Preserve unrelated work in a dirty tree. Use
`rg` for searches. Run verification proportional to the changed behavior.

## Checklist

- Confirm that only the intended skill packages and files changed.
- Keep `all.txt`, named profiles, the catalog, and discovered skill directories
  consistent.
- Add a retirement tombstone when removing a previously installable skill.
  Keep active names disjoint from retired names.
- Keep shared references and their packaged copies synchronized.
- Preserve the default workflow profile and documented compatibility aliases.
- Update documentation, tracks, and focused tests for install-catalog changes.
- Run relevant validation and review the final diff before handoff.
