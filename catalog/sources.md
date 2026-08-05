# Source Catalog

This catalog records the intellectual provenance of the collection separately
from deployable skill packaging. A source may inform several skills, and a skill
may distill concepts from several sources.

## Distilled Sources

| Source | Skills informed | Concepts distilled |
|---|---|---|
| Sirius repository history and accumulated repository workflow practice | `simplify`, `commit`, `create-pr`, `governance-update` | Diff-scoped cleanup, intentional staging, convention-aware change publication, and evidence-based governance updates |
| Sirius active skill catalog and workflow boundary guidance | `assess-development-input` | Content-based readiness assessment, preservation of source status and uncertainty, and selection of the narrowest responsible downstream skill |
| Craig Larman, *Applying UML and Patterns* | `iterative-up-analysis-design`, `inception`, `use-case-modeling`, `domain-modeling`, `system-sequence-diagrams`, `operation-contracts`, `grasp-responsibility-design`, `use-case-realization`, `uml-class-diagram-design`, `design-pattern-application`, `software-design-language-adaptation`, `test-driven-implementation`, `behavior-preserving-refactoring` | Iterative Unified Process framing, inception, use cases, domain models, system sequence diagrams, operation contracts, GRASP, use-case realizations, design class diagrams, patterns, implementation, testing, and refactoring |
| Serge Demeyer, Stéphane Ducasse, and Oscar Nierstrasz, *Object-Oriented Reengineering Patterns* | All reverse-engineering skills | Question-driven reengineering, first contact, initial understanding, detailed model capture, tests as evidence, and bounded recovery |
| Rick Kazman, Liam O'Brien, and Chris Verhoef, *Architecture Reconstruction Guidelines, Third Edition* | `reverse-engineer-software-system`, `reconstruct-software-architecture`, `reconcile-recovered-design` | Extracting implementation facts, building successive abstractions, recovering as-built views, and checking as-built against as-designed |
| Paul Clements et al., *Documenting Software Architectures: Views and Beyond* | `reconstruct-software-architecture`, `reconcile-recovered-design` | Question-driven view selection, module and component-and-connector views, deployment, interfaces, behavior, and architecture review |
| Diomidis Spinellis, *Code Reading: The Open Source Perspective* | `survey-existing-system`, `recover-system-behavior`, `reconstruct-software-architecture` | Code-reading attack plans, project organization, control and data structures, mixed-language systems, search, and runtime tools |

The detailed concept-to-skill mapping is maintained in the
[Skill Catalog](skills.md).

## Proposed Sources

These sources inform the client-discovery proposal but have not yet been
distilled into deployable skills.

| Source | Candidate skills | Candidate concepts |
|---|---|---|
| James Robertson, Suzanne Robertson, and Adrian Reed, *Mastering the Requirements Process* | `stakeholder-requirements-elicitation`, `requirements-synthesis-validation` | Problem scope, stakeholder discovery, elicitation, fit criteria, and requirements quality |
| Steve Portigal, *Interviewing Users* | `stakeholder-requirements-elicitation` | Interview planning, contextual methods, evidence capture, and synthesis |
| Gojko Adzic, *Specification by Example* | `requirements-synthesis-validation`, `implementation-slice-briefing` | Collaborative examples, executable specifications, validation, and living documentation |
| Jeff Patton, *User Story Mapping* | `implementation-slice-briefing` | User journeys, coherent delivery slices, and release boundaries |
| Teresa Torres, *Continuous Discovery Habits* | A possible future continuous-discovery skill | Outcomes, recurring interviews, opportunities, assumptions, and experiments |

See the [client-discovery proposal](../docs/proposals/client-discovery-skills.md)
for the proposed boundaries and full reference links.

## Provenance Rules

- Record concepts as distilled agent behavior rather than reproducing source
  chapters.
- Keep source relationships many-to-many; do not make a book or author the
  filesystem owner of a skill.
- Mark a source as proposed until at least one implemented skill materially
  distills it.
- Keep detailed bibliography and design history here or in proposals, not in
  skill frontmatter.
