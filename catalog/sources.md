# Source Catalog

This catalog records the intellectual provenance of the collection separately
from deployable skill packaging. A source may inform several skills, and a skill
may distill concepts from several sources.

## Distilled Sources

| Source | Skills informed | Concepts distilled |
|---|---|---|
| Sirius repository history and accumulated repository workflow practice | `behavior-preserving-refactoring`, `create-pr`, `walkthrough-me` | Configuration ownership, verified structural improvement, convention-aware change publication, and revision- or snapshot-fixed code-change comprehension |
| Matt Pocock's [`grilling`](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/productivity/grilling/SKILL.md) at revision `8b78b531` | `walkthrough-me` | Agent-owned fact finding, explicit user checkpoints, and user-controlled interactive pacing, adapted from decision interviewing to a section-by-section code-change tour |
| Sirius active skill catalog and workflow boundary guidance | `assess-development-input` | Content-based readiness assessment, preservation of source status and uncertainty, and selection of the narrowest responsible downstream skill |
| Addy Osmani's `interview-me` and `idea-refine` at revision [`5a1b82d`](https://github.com/addyosmani/agent-skills/tree/5a1b82d6445d1e2f0abeea1072851419a50c0e5c) | `assess-development-input`, `design-repository-artifact-layout` | Optional requester-intent clarification and candidate-direction refinement; the confirmed idea remains candidate input |
| Martin Fowler, [*Architecture Decision Record*](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html) | `record-architecture-decision` | Short one-decision records, inverted-pyramid presentation, proposed/accepted/superseded lifecycle, rationale and forces, serious alternatives, consequences, confidence, reconsideration triggers, advice, repository proximity, and linked supersession |
| Sirius durable-artifact and risk-driven delivery practice | `select-technical-artifacts`, `design-repository-artifact-layout`, `iterative-risk-driven-development` | Value, ownership, and lifecycle selection gates; executable-first dispositions; repository-first convention discovery; artifact lifecycle separation; minimal layouts; canonical paths; linking; migration; risk-driven objective selection; boundary-sensitive refactoring gates; native responsibility, ownership, and verification coordination; parent-outcome reconciliation; validation; Rust lifecycle pressure; and authorized commit boundaries |
| Craig Larman, *Applying UML and Patterns* | Larman-derived analysis and object-design skills in [`applying-uml-and-patterns.txt`](../skill-sets/applying-uml-and-patterns.txt) | Iterative phase framing, inception, use cases, domain models, system sequence diagrams, operation contracts, GRASP responsibility reasoning adapted to language-native owners, use-case realizations, design class diagrams, patterns, implementation, testing, and refactoring |
| Rust ownership conventions and accumulated Sirius Rust design practice | `software-design-language-adaptation`, `design-rust-lifecycles` | Native responsibility realization, ownership and capability transfer, consuming transitions, RAII and explicit shutdown, staged startup, rollback, async cancellation, supervision, vertical verification retention, and evidence-driven abstraction |
| Serge Demeyer, Stéphane Ducasse, and Oscar Nierstrasz, *Object-Oriented Reengineering Patterns* | All reverse-engineering skills | Question-driven reengineering, first contact, initial understanding, detailed model capture, tests as evidence, and bounded recovery |
| Rick Kazman, Liam O'Brien, and Chris Verhoef, *Architecture Reconstruction Guidelines, Third Edition* | `reverse-engineer-software-system`, `reconstruct-software-architecture`, `reconcile-recovered-design` | Extracting implementation facts, building successive abstractions, recovering as-built views, and checking as-built against as-designed |
| Paul Clements et al., *Documenting Software Architectures: Views and Beyond* | `reconstruct-software-architecture`, `reconcile-recovered-design` | Question-driven view selection, module and component-and-connector views, deployment, interfaces, behavior, and architecture review |
| Diomidis Spinellis, *Code Reading: The Open Source Perspective* | `survey-existing-system`, `recover-system-behavior`, `reconstruct-software-architecture` | Code-reading attack plans, project organization, control and data structures, mixed-language systems, search, and runtime tools |

The detailed concept-to-skill mapping is maintained in the
[Skill Catalog](skills.md).

## External skill add-ons

The `all` installation fetches these upstream skills without copying them into
the Sirius active catalog:

| Source | Pinned revision | Installed names | Installation surface |
|---|---|---|---|
| Addy Osmani's [`agent-skills`](https://github.com/addyosmani/agent-skills/tree/5a1b82d6445d1e2f0abeea1072851419a50c0e5c) | `5a1b82d6445d1e2f0abeea1072851419a50c0e5c` | `interview-me`, `idea-refine`, `code-review-and-quality`, `code-simplification`, `git-workflow-and-versioning` | `just install <target-project> all` or `just install-global all` only |

## Proposed Sources

This remaining source informs a possible future client-discovery capability but
has not been materially distilled into a deployable skill.

| Source | Candidate skills | Candidate concepts |
|---|---|---|
| Teresa Torres, *Continuous Discovery Habits* | A possible future continuous-discovery skill | Outcomes, recurring interviews, opportunities, assumptions, and experiments |

See the [client-discovery idea](../docs/ideas/client-discovery-skills.md)
for the implemented boundaries, design rationale, and full reference links.

## Provenance Rules

- Record concepts as distilled agent behavior rather than reproducing source
  chapters.
- Keep source relationships many-to-many; do not make a book or author the
  filesystem owner of a skill.
- Mark a source as proposed until at least one implemented skill materially
  distills it.
- Keep detailed bibliography and design history here or in legacy proposal
  records, not in skill frontmatter.
