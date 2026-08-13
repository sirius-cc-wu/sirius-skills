# Source Catalog

This catalog records the intellectual provenance of the collection separately
from deployable skill packaging. A source may inform several skills, and a skill
may distill concepts from several sources.

## Distilled Sources

| Source | Skills informed | Concepts distilled |
|---|---|---|
| Sirius repository history and accumulated repository workflow practice | `simplify`, `commit`, `create-pr` | Diff-scoped cleanup, intentional staging, and convention-aware change publication |
| Sirius active skill catalog and workflow boundary guidance | `assess-development-input` | Content-based readiness assessment, preservation of source status and uncertainty, and selection of the narrowest responsible downstream skill |
| Addy Osmani's `interview-me` and `idea-refine` at revision [`5a1b82d`](https://github.com/addyosmani/agent-skills/tree/5a1b82d6445d1e2f0abeea1072851419a50c0e5c) | `assess-development-input`, `design-repository-artifact-layout` | Optional requester-intent clarification, candidate-direction refinement, and idea/proposal lifecycle equivalence |
| Martin Fowler, [*Architecture Decision Record*](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html) | `record-architecture-decision` | Short one-decision records, inverted-pyramid presentation, proposed/accepted/superseded lifecycle, rationale and forces, serious alternatives, consequences, confidence, reconsideration triggers, advice, repository proximity, and linked supersession |
| Sirius durable-artifact and repository-navigation practice | `select-technical-artifacts`, `design-repository-artifact-layout`, `iterative-up-analysis-design` | Value, ownership, and lifecycle selection gates; executable-first dispositions; repository-first convention discovery; artifact lifecycle separation; minimal layouts; canonical paths; linking; migration; and durable current knowledge versus historical iteration records |
| Sirius iterative delivery practice and active specialist boundaries | `run-development-iteration` | One-objective iteration execution, question-driven specialist selection, artifact budgeting, validation, authorized commit boundaries, and language-neutral extensibility |
| Craig Larman, *Applying UML and Patterns* | Larman-derived analysis and object-design skills in [`applying-uml-and-patterns.txt`](../skill-sets/applying-uml-and-patterns.txt) | Iterative Unified Process framing, inception, use cases, domain models, system sequence diagrams, operation contracts, GRASP, use-case realizations, design class diagrams, patterns, implementation, testing, and refactoring |
| Rust ownership conventions and accumulated Sirius Rust design practice | `software-design-language-adaptation`, `design-rust-lifecycles` | Ownership and capability transfer, consuming transitions, RAII and explicit shutdown, staged startup, rollback, async cancellation, supervision, and evidence-driven abstraction |
| James Robertson, Suzanne Robertson, and Adrian Reed, *Mastering the Requirements Process* | `stakeholder-requirements-elicitation`, `requirements-synthesis-validation` | Problem scope, stakeholder discovery, elicitation methods, evidence quality, requirements synthesis, measurable fit criteria, and validation |
| Steve Portigal, *Interviewing Users* | `stakeholder-requirements-elicitation` | Interview planning, contextual methods, neutral questioning, evidence capture, and responsible reporting |
| Gojko Adzic, *Specification by Example* | `requirements-synthesis-validation`, `behavior-driven-specification`, `implementation-slice-briefing` | Collaborative examples, concrete playback, validation, traceable requirement knowledge, example-based acceptance specifications, and executable handoff |
| Jeff Patton, *User Story Mapping* | `implementation-slice-briefing` | User journeys, coherent vertical delivery slices, and explicit release boundaries |
| Serge Demeyer, Stéphane Ducasse, and Oscar Nierstrasz, *Object-Oriented Reengineering Patterns* | All reverse-engineering skills | Question-driven reengineering, first contact, initial understanding, detailed model capture, tests as evidence, and bounded recovery |
| Rick Kazman, Liam O'Brien, and Chris Verhoef, *Architecture Reconstruction Guidelines, Third Edition* | `reverse-engineer-software-system`, `reconstruct-software-architecture`, `reconcile-recovered-design` | Extracting implementation facts, building successive abstractions, recovering as-built views, and checking as-built against as-designed |
| Paul Clements et al., *Documenting Software Architectures: Views and Beyond* | `reconstruct-software-architecture`, `reconcile-recovered-design` | Question-driven view selection, module and component-and-connector views, deployment, interfaces, behavior, and architecture review |
| Diomidis Spinellis, *Code Reading: The Open Source Perspective* | `survey-existing-system`, `recover-system-behavior`, `reconstruct-software-architecture` | Code-reading attack plans, project organization, control and data structures, mixed-language systems, search, and runtime tools |

The detailed concept-to-skill mapping is maintained in the
[Skill Catalog](skills.md).

## Proposed Sources

This remaining source informs a possible future client-discovery capability but
has not been materially distilled into a deployable skill.

| Source | Candidate skills | Candidate concepts |
|---|---|---|
| Teresa Torres, *Continuous Discovery Habits* | A possible future continuous-discovery skill | Outcomes, recurring interviews, opportunities, assumptions, and experiments |

See the [client-discovery proposal](../docs/proposals/client-discovery-skills.md)
for the implemented boundaries, design rationale, and full reference links.

## Provenance Rules

- Record concepts as distilled agent behavior rather than reproducing source
  chapters.
- Keep source relationships many-to-many; do not make a book or author the
  filesystem owner of a skill.
- Mark a source as proposed until at least one implemented skill materially
  distills it.
- Keep detailed bibliography and design history here or in proposals, not in
  skill frontmatter.
