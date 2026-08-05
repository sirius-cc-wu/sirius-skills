# sirius-skills

`sirius-skills` is a curated collection of repository workflow, software
discovery, iterative design, implementation, and evolution skills. Skills are
independently deployable; profiles provide convenient installations without
turning the catalog into a mandatory lifecycle.

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
| `iterative-design` | Requirements, analysis, object design, tested implementation, and refactoring |
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
`npx skills` for GitHub Copilot, Codex, Antigravity, and Antigravity CLI.

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

The [repository structure and skill-relationship comparison](catalog/agent-skill-repository-structures.md)
uses PlantUML views to show how two related projects organize skill authoring,
orchestration, distribution, runtime support, verification, and workflow
handoffs.

## Repository conventions

`commit` and `create-pr` can read `.skills/conventions.json` when a consuming
repository needs project-specific formatting. Supported fields include:

- `commit_format`
- `pr_title_format`
- `branch_extract_pattern`
- `id_pattern`

Shared skills remain generic; project-specific tracker and naming rules belong
in consuming-repository configuration.

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
behavioral evals. Behavioral execution is opt-in and never runs as part of
normal validation.

## Repository layout

- `skills/*/SKILL.md`: deployable agent workflows
- `skill-sets/*.txt`: canonical installation profiles
- `catalog/skills.md`: skill responsibilities and boundaries
- `catalog/agent-skill-repository-structures.md`: comparative PlantUML views of
  related skill repositories and their documented workflow handoffs
- `catalog/tracks/*.md`: optional workflow compositions
- `catalog/sources.md`: intellectual and repository provenance
- `evals/`: deterministic routing cases and opt-in behavioral evaluation data
- `docs/shared/`: canonical references copied into self-contained skills
- `docs/proposals/`: proposed, non-deployable capabilities
- `scripts/validate_skills.sh`: catalog and collection validation
- `src/sirius_skills/commands/sync_shared_references.py`: packaging helper

## Consolidation history

The iterative software design collection was consolidated into this repository
with its Git history preserved. Sirius's former spec-driven development runtime
and planning artifacts are not part of the active distribution; the annotated
tag `pre-consolidation-2026-08-04` preserves the repository immediately before
this consolidation.
