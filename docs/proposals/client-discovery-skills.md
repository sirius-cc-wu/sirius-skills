# Client Discovery Skills for Coding-Agent Handoffs

The missing area is best described as **stakeholder-driven requirements
discovery**, not merely prompt writing.

The existing pipeline starts after useful client knowledge already exists:

- [`inception`](../../skills/inception/SKILL.md) frames vision, scope, feasibility,
  and risks.
- [`use-case-modeling`](../../skills/use-case-modeling/SKILL.md) expresses actor goals
  and system behavior.
- [`test-driven-implementation`](../../skills/test-driven-implementation/SKILL.md)
  expects approved examples, requirements, or contracts and explicitly avoids
  guessing missing business rules.

Therefore, the missing loop is:

```text
Stakeholders
    ↓ interviews, observation, workshops
Evidence
    ↓ synthesis and client playback
Validated requirements and examples
    ↓ select a bounded slice
Coding-agent brief
    ↓
Design, tests, and implementation
    ↓
Stakeholder feedback
```

## Recommended Skill Family

Initially, this could be a family of three skills.

| Possible skill | Responsibility | Main output | Important boundary |
|---|---|---|---|
| `stakeholder-requirements-elicitation` | Identify the right participants and learn how their work actually operates through interviews, observation, workshops, document review, and prototypes | Stakeholder map, elicitation plan, evidence notes, open questions, conflicts | Records evidence; does not silently convert every client statement into a requirement |
| `requirements-synthesis-validation` | Turn evidence into goals, workflows, rules, constraints, quality attributes, scenarios, assumptions, and decisions; play these back to stakeholders | Discovery brief, candidate requirements, validated examples, decision/conflict log | Routes results into inception, use cases, domain models, and supplementary requirements; does not design software |
| `implementation-slice-briefing` | Select a sufficiently understood behavior slice and assemble its approved sources into a coding-agent-ready brief | Bounded implementation brief with traceable acceptance conditions | Packages existing decisions; never invents missing business rules or architecture |

If the first skill becomes too large, it could later split into
`stakeholder-analysis` and `requirements-elicitation`. That split should wait
until actual usage demonstrates the need.

## What an Agent-Ready Brief Should Contain

The final brief should be more like a requirements contract than a polished
natural-language prompt:

- Business or user outcome
- Actor and system boundary
- Current problem and supporting evidence
- Exact in-scope behavior
- Main, alternate, and failure scenarios
- Concrete acceptance examples
- Business rules and data definitions
- Relevant quality attributes and constraints
- Explicit non-goals
- Dependencies and already-made decisions
- Open questions, confidence, and approval state
- A rule telling the coding agent when to stop rather than guess
- Links or stable IDs tracing every expectation to its source
- Required verification
- Repository context discovered from the codebase, kept distinct from
  client-provided facts

That distinction matters: an interview transcript is evidence, not
automatically a specification. A requested feature may be a proposed solution
rather than the underlying need, and the paying client may not represent
operators, end users, compliance staff, or support personnel.

## Recommended References

### Overall Requirements Process

If choosing one comprehensive foundation, use **Mastering the Requirements
Process, 4th Edition** by James Robertson, Suzanne Robertson, and Adrian Reed.
It covers problem scoping, stakeholder discovery, prototypes, functional and
non-functional requirements, measurable fit criteria, stories, and iterative
requirements work. It is probably the strongest backbone for all three
proposed skills.

- [Mastering the Requirements Process — Pearson](https://www.pearson.com/en-us/subject-catalog/p/mastering-the-requirements-process-getting-requirements-right/P200000011135/9780137969500)

For a smaller, checklist-oriented foundation, **Software Requirements
Essentials** by Karl Wiegers and Candase Hokanson is especially suitable for
skill distillation. Its twenty practices span problem definition, stakeholder
identification, elicitation, analysis, specification, validation, and change
management.

- [Software Requirements Essentials — InformIT](https://www.informit.com/store/software-requirements-essentials-core-practices-for-9780138190149)

### Skill-Specific References

- **Interviewing Users, 2nd Edition** by Steve Portigal is a practical source
  for research planning, contextual methods, interviewing behavior,
  documentation, synthesis, and communicating findings. It is a strong
  foundation for `stakeholder-requirements-elicitation`.
  [Rosenfeld Media](https://rosenfeldmedia.com/books/interviewing-users-second-edition/)

- **Specification by Example** by Gojko Adzic explains how to turn stakeholder
  conversations into concrete examples, validate them collaboratively, and
  connect requirements to executable verification. It is a strong foundation
  for `requirements-synthesis-validation`.
  [Manning](https://www.manning.com/books/specification-by-example)

- **User Story Mapping** by Jeff Patton helps preserve the user's overall
  journey while selecting coherent delivery slices instead of creating a
  disconnected backlog. It is useful for `implementation-slice-briefing`.
  [Author's overview](https://jpattonassociates.com/story-mapping/)

- **Continuous Discovery Habits** by Teresa Torres is useful if the collection
  should support ongoing product discovery rather than only project-based
  client intake. It emphasizes outcomes, recurring interviews, opportunities,
  assumptions, and experiments.
  [Product Talk](https://www.producttalk.org/continuous-discovery-habits/)

- **Writing Effective Use Cases** by Alistair Cockburn remains a strong source
  for the existing use-case skill and for converting elicited knowledge into
  disciplined behavioral scenarios.
  [Pearson](https://www.pearson.com/en-us/subject-catalog/p/writing-effective-use-cases/P200000009217/9780321605801)

## Suggested Starting Stack

1. *Mastering the Requirements Process* for the overall model.
2. *Interviewing Users* for evidence acquisition.
3. *Specification by Example* for validation and executable handoff.
4. *User Story Mapping* when designing the delivery-slice skill.

The central design principle should be:

> Coding agents receive validated decisions plus visible uncertainty—not a
> prompt that makes uncertainty disappear.
