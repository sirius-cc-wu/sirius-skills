# sirius-skills

`sirius-skills` is a curated collection of development-input assessment,
proposal authoring, repository workflow, software discovery, iterative design,
implementation, and evolution skills. Skills are independently deployable;
profiles provide convenient installations without turning the catalog into a
mandatory lifecycle.

## Install

Install the four generic repository workflow skills by default:

```bash
just install
```

Install a named profile:

```bash
just install iterative-design
just install reverse-engineering
just install all
```

Available profiles are defined in [`skill-sets/`](skill-sets/):

| Profile | Purpose |
|---|---|
| `workflow` | Simplification, scoped commits, pull requests, and durable governance updates |
| `iterative-design` | External-input assessment, proposal authoring, requirements, analysis, object design, tested implementation, and refactoring |
| `applying-uml-and-patterns` | Compatibility alias for `iterative-design` |
| `reverse-engineering` | Evidence-driven system survey, behavior and architecture recovery, and reconciliation |
| `all` | Every active skill in the catalog |

Remove the default or a named profile later:

```bash
just uninstall
just uninstall iterative-design
```

The `install-packaged` and `uninstall-packaged` aliases accept the same optional
profile. Installation refreshes shared references from the checkout and uses
`npx --yes skills` so the CLI can bootstrap noninteractively for GitHub Copilot,
Codex, Antigravity, and Antigravity CLI. The upstream CLI stores these shared
global skills in `~/.agents/skills`, while Antigravity CLI discovers global
skills in `~/.gemini/config/skills`. Installation therefore creates a
per-skill compatibility symlink in the Antigravity directory without replacing
unrelated entries already there. Uninstall and retired-skill cleanup remove
only symlinks that still point to their expected Sirius installation.

A successful installation also records its skill names in host-local state at
`$XDG_STATE_HOME/sirius-skills/managed-skills.txt`, or
`~/.local/state/sirius-skills/managed-skills.txt` when `XDG_STATE_HOME` is not
set.

## Skill lifecycle and retired installations

A deprecated skill remains in the active catalog and profiles until users have
migration guidance. Once retired, its name is removed from those active
surfaces and appended to the [retirement ledger](catalog/retired-skills.tsv).
The ledger currently records 50 local skills recovered by intersecting Git
history for former installer manifests with historical `skills/*/SKILL.md`
packages. External skills once installed alongside Sirius were excluded.

Every normal install and uninstall first prunes installed skill names that are
both in the retirement ledger and in this computer's Sirius ownership state.
You can run that safe cleanup directly:

```bash
just prune-retired
```

Installations made before ownership state existed cannot be attributed safely:
`npx skills` currently reports their names and paths but no source repository.
The safe command reports matching unowned names without deleting them. After
checking that those names are old Sirius copies rather than same-named skills
from another project, remove them explicitly:

```bash
just prune-retired-legacy
```

The legacy command removes matching global skills by name, so review its
candidates first. Each computer must run updated repository tooling at least
once; one computer cannot remove installations on another computer.

## Catalog and workflow tracks

The [Skill Catalog](catalog/skills.md) describes every skill's responsibility
and boundary. Common compositions are documented as workflow tracks:

- [Repository Workflow](catalog/tracks/repository-workflow.md)
- [Reverse Engineering](catalog/tracks/reverse-engineering.md)
- [Iterative Analysis and Design](catalog/tracks/iterative-analysis-design.md)
- [Implementation and Evolution](catalog/tracks/implementation-evolution.md)
- [Client to Code](catalog/tracks/client-to-code.md), from stakeholder evidence
  through validated requirements to a traceable implementation slice brief

The [Skill Relationships](catalog/skill-relationships.md) views summarize
normal handoffs and optional feedback paths. Select the smallest set of skills
that addresses the current risk or outcome.

Use `assess-development-input` when requirements-shaped material comes from an
external or mixed workflow and its Sirius entry point is unclear. It evaluates
the content and recommends one next Sirius skill without rewriting the source
or automatically executing the handoff.

Use `author-software-proposal` when technical discussions, findings, incidents,
or candidate changes need a decision-seeking artifact. For one focused,
consequential choice it prefers a proposed decision record or ADR; broader
exploration keeps a software proposal. It separates current evidence from
proposed behavior and stops before approval, implementation, commit, or
publication unless those actions are separately authorized. It preserves an
established decision or proposal location; otherwise, the
[artifact layout guidance](skills/iterative-up-analysis-design/references/artifact-layouts.md#proposal-placement)
selects the repository location according to how reviewers navigate it.

The [repository structure and skill-relationship comparison](catalog/agent-skill-repository-structures.md)
uses PlantUML views to show how two related projects organize skill authoring,
orchestration, distribution, runtime support, verification, and workflow
handoffs.

## Repository conventions

`commit` and `create-pr` follow explicit repository-specific message, title,
identifier, and tracker rules from the nearest applicable `AGENTS.md`. Without
such rules, both skills use their documented generic defaults. Shared skills
remain generic; consuming repositories own their local conventions in
`AGENTS.md`.

## Design artifacts and sources

The iterative-design collection treats use cases, domain models, system
sequence diagrams, contracts, realizations, and design class diagrams as
durable knowledge refined across iterations. It preserves established
repository layouts and applies an artifact-selection budget before creating a
new standalone document. The budget prefers executable evidence and existing
canonical artifacts, and requires new files to demonstrate value, distinct
ownership, and an independent lifecycle. Layout and Markdown guidance lives in
the references owned by `iterative-up-analysis-design`.

The original analysis and design skills distill workflows from Craig Larman's
*Applying UML and Patterns*. Reverse-engineering skills also draw from software
reengineering, architecture reconstruction, architecture documentation, and
code-reading sources. See the [Source Catalog](catalog/sources.md) for
provenance.

## Validation

Validate skill structure, profile membership, shared references, catalogs, and
collection-specific contracts. This also runs the free deterministic routing
evals:

```bash
just validate
pytest -q
```

Run only the routing evals while authoring skill descriptions or eval cases:

```bash
just eval-routing
```

See [Skill Evals](evals/README.md) for the case format, current pilot coverage,
and the boundary between deterministic routing checks and model-executed
behavioral evals. Behavioral execution, its optional non-gating semantic judge,
and judge calibration are opt-in and never run as part of normal validation.

## Repository layout

- `skills/*/SKILL.md`: deployable agent workflows
- `skill-sets/*.txt`: canonical installation profiles
- `catalog/skills.md`: skill responsibilities and boundaries
- `catalog/retired-skills.tsv`: append-only retired-name tombstones with Git
  evidence revisions
- `catalog/agent-skill-repository-structures.md`: comparative PlantUML views of
  related skill repositories and their documented workflow handoffs
- `catalog/tracks/*.md`: optional workflow compositions
- `catalog/sources.md`: intellectual and repository provenance
- `evals/`: deterministic routing cases and opt-in behavioral evaluation data
- `docs/shared/`: canonical references copied into self-contained skills
- `docs/proposals/`: capability proposals, implementation rationale, and
  historical iteration records
- `scripts/validate_skills.sh`: catalog and collection validation
- `src/sirius_skills/commands/sync_shared_references.py`: packaging helper
- `src/sirius_skills/commands/manage_installed_skills.py`: host ownership,
  Antigravity compatibility links, and retired-installation reconciliation

## Consolidation history

The iterative software design collection was consolidated into this repository
with its Git history preserved. Sirius's former spec-driven development runtime
and planning artifacts are not part of the active distribution; the annotated
tag `pre-consolidation-2026-08-04` preserves the repository immediately before
this consolidation.
