# Iterative Software Design Skills

This collection provides agent skills for recovering existing software
knowledge and moving iteratively from product scope and behavioral requirements
through design, tested implementation, and refactoring. It uses evidence-driven
reverse engineering, use cases, domain modeling, UML, responsibility-driven
design, and patterns where they help.

## Installing Skills

Install all managed skills globally for GitHub Copilot, Codex, Antigravity, and Antigravity CLI:

```bash
just install
```

Install only one curated skill set by passing its filename without the `.txt`
extension:

```bash
just install applying-uml-and-patterns
```

Available sets are defined in [`skill-sets/`](skill-sets/). The default managed
set is defined by [`skill-sets/all.txt`](skill-sets/all.txt). The installer and
validator consume these files, so adding or retiring a skill requires one
membership update.

Remove the managed skills later with:

```bash
just uninstall
```

## Validation

Validate the collection structure and skill metadata:

```bash
just validate
```

## Workflow Tracks

Skills remain independently deployable and can be composed through different
tracks:

- [Client to Code](catalog/tracks/client-to-code.md) describes the proposed
  path from stakeholder evidence to a bounded coding-agent brief.
- [Reverse Engineering](catalog/tracks/reverse-engineering.md) recovers
  evidence-backed behavior and as-built architecture from existing systems,
  then reconciles them with documents, decisions, tests, and history.
- [Iterative Analysis and Design](catalog/tracks/iterative-analysis-design.md)
  sequences the current requirements, analysis, responsibility, and object
  design skills.
- [Implementation and Evolution](catalog/tracks/implementation-evolution.md)
  covers verified behavior changes and behavior-preserving structural
  improvement.

The tracks express dependencies and common handoffs, not a requirement to
create every artifact. Select skills according to the current risk, learning
goal, and behavior slice.

## Sources

The original analysis and design skills distill agent workflows from Craig
Larman's *Applying UML and Patterns*. Reverse-engineering skills also draw from
software reengineering, architecture reconstruction, architecture
documentation, and code-reading sources. New sources and candidate skill
boundaries remain tracked separately so deployable skill directories are
organized by capability rather than by book. See the
[Source Catalog](catalog/sources.md) and [Skill Catalog](catalog/skills.md).

## Artifact Durability and Layouts

The iterative UP coordinator distinguishes durable design knowledge from
iteration history:

- Use cases, domain models, SSDs, contracts, realizations, and design class
  diagrams are canonical artifacts refined across iterations.
- Iteration records retain goals, risks, selected scope, exit criteria, and
  results without copying the canonical artifacts.
- Decision records preserve cross-cutting choices and explicitly supersede
  earlier decisions when needed.

The coordinator preserves an established repository layout. When no convention
exists, it selects the smallest suitable structure rather than imposing one
taxonomy:

| Layout | Best fit |
|---|---|
| Feature-iteration hybrid, flat variant | Small repositories and one-page features |
| Feature-iteration hybrid, package variant | Cohesive features with independently changing artifacts |
| Artifact-oriented | Shared models spanning many features |
| Product-area oriented | Stable subsystems with area ownership |
| Iteration-first | Audit-focused repositories with snapshots plus a canonical `current/` index |

See [Artifact Durability and Repository Layouts](skills/iterative-up-analysis-design/references/artifact-layouts.md)
for selection criteria, tradeoffs, linking rules, and migration guidance.

When a skill persists a standalone Markdown artifact, it uses OKF-aligned YAML
frontmatter for discovery metadata such as artifact type, title, description,
stable ID, and lifecycle state. Narrative content, diagrams, rationale, and
evidence remain in the Markdown body. See [Markdown Artifact Frontmatter](skills/iterative-up-analysis-design/references/markdown-artifact-frontmatter.md)
for the shared rules, artifact types, aggregate-file handling, and reserved
`index.md`/`log.md` behavior.

## Files

- `skills/*/SKILL.md` contains the agent-facing workflows.
- `skills/*/agents/openai.yaml` optionally provides user-facing skill metadata.
- `catalog/skills.md` maps concepts, artifacts, and skill boundaries.
- `catalog/sources.md` records intellectual provenance without making source
  books filesystem owners.
- `catalog/tracks/*.md` describes ways to compose skills.
- `skill-sets/*.txt` defines curated installation groups; `all.txt` is the
  canonical managed set.
- `docs/proposals/` contains design proposals that are not deployable skills.
- `skills/iterative-up-analysis-design/references/artifact-layouts.md` describes supported persistence layouts.
- `skills/iterative-up-analysis-design/references/markdown-artifact-frontmatter.md` defines metadata for generated Markdown artifacts.
- `scripts/validate_skills.sh` performs lightweight structure validation.
- `justfile` installs, removes, and validates the managed skills.
