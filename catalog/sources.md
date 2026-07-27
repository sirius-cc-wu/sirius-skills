# Source Catalog

This catalog records the intellectual provenance of the collection separately
from deployable skill packaging. A source may inform several skills, and a skill
may distill concepts from several sources.

## Distilled Sources

| Source | Skills informed | Concepts distilled |
|---|---|---|
| Craig Larman, *Applying UML and Patterns* | All currently implemented skills | Iterative Unified Process framing, inception, use cases, domain models, system sequence diagrams, operation contracts, GRASP, use-case realizations, design class diagrams, patterns, implementation, testing, and refactoring |

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
