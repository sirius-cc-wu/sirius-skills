# Client Discovery Skills for Coding-Agent Handoffs

This historical record describes the retired
`stakeholder-requirements-elicitation`, `requirements-synthesis-validation`, and
`implementation-slice-briefing` capabilities as they existed at revision
`f544d48bf5e1b0d836e0cb39f8122a767bdbae0f`. Existing artifacts remain valid at
their recorded revisions. The active migration is documented in the
[Client to Code track](../../catalog/tracks/client-to-code.md). This document
preserves the problem, design rationale, safeguards, and delivery history.

The gap they fill is best described as **stakeholder-driven requirements
discovery**, not merely prompt writing.

The existing pipeline starts after useful client knowledge already exists:

- External `idea-refine` prepares a candidate direction or business-case
  hypothesis. [`define-project-vision`](../../skills/define-project-vision/SKILL.md)
  guides grounded input toward an authority-approved project vision; the
  responsible external product or portfolio process owns feasibility and
  investment decisions.
- [`use-case-modeling`](../../skills/use-case-modeling/SKILL.md) expresses actor goals
  and system behavior, while
  [`specify-quality-constraints`](../../skills/specify-quality-constraints/SKILL.md)
  owns measurable quality requirements and binding constraints.
- External or repository-native implementation starts from approved examples,
  requirements, or contracts and must not guess missing business rules.

The implemented loop is:

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

## Relationship to Generic Input Assessment

The deployable
[`assess-development-input`](../../skills/assess-development-input/SKILL.md)
skill now owns generic entry routing. Its readiness mode can still assess intent
statements, specifications, proposals, BDD scenarios, story maps, brainstorm
notes, and other requirements-shaped inputs from any method. It selects one
initial owner from content, authority, uncertainty, and risk.

That router does not implement this proposal. It does not identify or interview
stakeholders, turn evidence into validated requirements, assemble an
implementation-ready slice, or execute the selected handoff. A readiness
assessment may therefore route an input back to an external authority instead
of making incomplete material look ready.

## Representative Path

A sponsor asks for a dashboard. An operator interview reveals that the real
problem is reconciling records from several systems, while a compliance review
shows that some records must not be exported. The original request, the
operator's workflow, and the compliance constraint are all evidence; none is
automatically the specification.

The elicitation skill records the participants, observations, sources, and
conflict. The synthesis skill plays back candidate workflows and rules until
the relevant decision-makers validate them. The briefing skill then selects
only an approved behavior slice and tells the coding agent to stop if a missing
retention or authorization rule would require guessing.

## Related Skill Collections

The
[agent-skill repository comparison](../../catalog/agent-skill-repository-structures.md)
shows two useful neighboring approaches:

- Addy Osmani's collection clarifies one requester's intent, refines ideas,
  writes an approved specification, and breaks it into vertical implementation
  slices with acceptance criteria.
- gstack challenges demand, status quo, target user, and the narrowest valuable
  wedge before producing an approved design document and a repository-grounded,
  executable issue.

These are strong precedents for explicit restatement, non-goals, approval,
verified repository context, bounded slices, and pass/fail acceptance
conditions. They do not replace the implemented skills: neither collection
owns a generic workflow for selecting multiple stakeholders, acquiring
evidence through several methods, preserving conflicts and provenance, or
validating requirements with the people authorized to decide them.

Two patterns should not become the evidence standard here. A leading guess can
accelerate clarification with an empowered requester but can bias a research
interview. Likewise, agent confidence or spec-executability scores can expose
ambiguity but cannot substitute for stakeholder coverage, source evidence, or
approval authority.

## Decision

Keep three independently deployable skills. Their artifact boundaries matter
more than forcing every engagement through a mandatory sequence. A low-risk
change with one authoritative requester may compose elicitation and synthesis
in one conversation, but it should still keep source evidence distinct from
candidate requirements and decisions.

## Delivery History

The family was implemented through risk-driven increments rather than authoring
all three skills at full detail before any had been exercised:

1. Validated `stakeholder-requirements-elicitation` against contradictory
   sponsor, operator, and compliance evidence.
2. Built `requirements-synthesis-validation` against evidence shaped by the
   first skill, including conflicts and approval authority.
3. Built `implementation-slice-briefing` against approved requirements plus
   the smallest necessary downstream analysis and design artifacts.
4. Reconciled the complete handoff against the proposal, active catalog,
   profiles, routing and behavioral evaluations, and focused handoff tests.

Each skill graduated independently with focused routing and behavioral
evaluations. The order below records implementation history, not a mandatory
lifecycle for skill users:

- [Validate Stakeholder Evidence Elicitation](iterations/client-discovery-elicitation-e1.md)
- [Validate Requirements Synthesis and Playback](iterations/client-discovery-synthesis-e2.md)
- [Validate Implementation Slice Briefing](iterations/client-discovery-briefing-e3.md)
- [Reconcile the Client Discovery Handoff](iterations/client-discovery-integration-e4.md)

## Implemented Skill Family

The active family contains three independently deployable skills.

| Skill | Responsibility | Main output | Important boundary |
|---|---|---|---|
| `stakeholder-requirements-elicitation` | Identify the right participants and learn how their work actually operates through interviews, observation, workshops, document review, and prototypes | Stakeholder Evidence Record with coverage, plan, sources, conflicts, and open questions | Records evidence; does not silently convert every client statement into a requirement |
| `requirements-synthesis-validation` | Turn evidence into goals, workflows, rules, constraints, quality attributes, scenarios, assumptions, and decisions; play these back to stakeholders | Requirements Discovery Brief with candidates, validated examples, and decision/conflict log | Routes candidate direction to external `idea-refine`, durable project vision to `define-project-vision`, business decisions to the responsible external owner, and technical knowledge to use cases, domain models, and supplementary requirements; does not design software |
| `implementation-slice-briefing` | Select a sufficiently understood behavior slice and assemble its approved sources into a coding-agent-ready brief | Implementation Slice Brief with approved examples, traceability, verification, and stop conditions | Packages existing decisions; never invents missing business rules or architecture |

If the first skill becomes too large, it could later split into
`stakeholder-analysis` and `requirements-elicitation`. That split should wait
until actual usage demonstrates the need.

## Shared Evidence and Decision Model

The skills use a small compatible model so that information does not lose its
origin as it moves toward implementation. Identifiers are opaque and may be
assigned manually; their format must follow repository conventions rather than
assuming dates or sequence numbers. Evidence claims reused the then-active
[Recovery Evidence and Confidence](https://github.com/sirius-cc-wu/sirius-skills/blob/f544d48bf5e1b0d836e0cb39f8122a767bdbae0f/skills/reverse-engineer-software-system/references/recovery-evidence.md)
vocabulary where it fit instead of creating a competing confidence model.

This compatibility contract does not require a separately packaged shared
reference. Each owning skill defines the fields it produces or consumes, and
the focused
[client-discovery handoff tests](../../tests/test_client_discovery_handoffs.py)
guard the source-ID, authority, status, freshness, and track-link boundaries.

An evidence record should preserve:

- Stable source ID
- Acquisition method, such as interview, observation, workshop, document
  review, prototype, or repository inspection
- Source or stakeholder role and relevant decision authority
- Capture date, document revision, or observation conditions
- The statement, quote, observation, or repository fact
- Claim status such as observed, corroborated, inferred, contradicted, or
  unknown
- Confidence, open questions, and conflicting evidence
- Sensitivity, retention, and publication constraints

A candidate requirement, example, or decision should preserve:

- Stable ID and precise statement
- Status such as candidate, validated, approved, contested, or superseded
- Source evidence IDs
- Applicable actors, scenarios, rules, constraints, and quality attributes
- Concrete examples or measurable fit criteria
- Decision-maker or approving role and approval date
- Unresolved questions and the person or group responsible for resolving them

Raw notes remain evidence. Synthesis creates traceable candidate requirements;
it does not rewrite the notes to make later decisions appear inevitable.

## Skill Entry, Exit, and Stop Rules

### `stakeholder-requirements-elicitation`

Enter when the relevant people, current work, underlying need, or decision
authority is not sufficiently understood.

The skill should:

- identify sponsors, operators, end users, support, compliance, and other
  affected roles without assuming the paying client represents all of them;
- choose proportionate methods and prepare an elicitation plan;
- ask neutral questions during evidence discovery and label researcher or
  agent hypotheses separately;
- capture observed work, statements, documents, prototypes, open questions,
  disagreements, and missing participants as evidence records; and
- distinguish what a participant experiences from the solution they request.

Exit when the planned evidence has been captured or the remaining coverage gap
is explicit. Stop rather than claiming adequate coverage when a material
stakeholder is unavailable, consent is missing, or contradictory evidence
cannot yet be investigated.

### `requirements-synthesis-validation`

Enter with an identified evidence set, including known limitations and
conflicts.

The skill should:

- synthesize goals, current workflows, rules, constraints, quality attributes,
  scenarios, assumptions, and candidate decisions without erasing their source;
- turn important behavior into concrete examples that stakeholders can confirm
  or correct;
- play the synthesis back to the relevant stakeholders and record validation,
  rejection, approval, abstention, and unresolved conflict; and
- route candidate direction to external `idea-refine`, durable project vision
  to `define-project-vision`, business decisions to the responsible external
  owner, and accepted technical knowledge to use cases, domain models,
  supplementary requirements, or other owning artifacts.

Exit with a discovery brief whose statements have explicit status and source
links. Stop before software design, and do not resolve a conflict merely
because one participant is more available or more senior unless that person
has the documented authority to decide it.

### `implementation-slice-briefing`

Enter when a coherent behavior slice has approved requirements and the
downstream analysis or design decisions needed to implement it.

The skill should:

- select a vertical behavior slice that produces a testable outcome;
- assemble approved requirements, examples, decisions, non-goals, repository
  evidence, and required verification without changing their meaning;
- identify the exact source revision or status on which the brief depends; and
- make every remaining uncertainty and coding-agent stop condition visible.

Exit with a bounded brief that an unfamiliar implementer can follow and trace.
Route missing business rules back to synthesis, candidate direction to external
`idea-refine`, missing project vision to `define-project-vision`, missing
business-case or feasibility decisions to the responsible external product or
portfolio process, missing behavioral detail to use cases or contracts, and
missing architecture to the relevant design workflow. Never fill those gaps
merely to make the brief appear executable.

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

## Confidentiality and Responsible Capture

Stakeholder discovery can expose personal, contractual, operational, or
commercially sensitive information. Across the family:

- elicitation establishes consent and intended use before recording interviews
  or observations, collects the minimum identifying detail, prefers roles over
  personal names, and records retention, access, deletion, and publication
  expectations;
- synthesis and briefing carry those handling constraints forward, keep private
  raw evidence separate from sanitized requirements and implementation briefs,
  and review permitted use before publishing an issue, committing an artifact,
  or sending content to an external service; and
- the skills preserve a trace link to a protected source without copying
  sensitive content into broadly visible artifacts.

## Validation, Feedback, and Change

Approval is revision-specific. A later interview, changed policy, delivery
observation, or stakeholder test may corroborate, contradict, or supersede an
earlier requirement. Preserve that history instead of silently rewriting the
old record.

An implementation brief becomes stale when one of its approved sources or
decisions changes. Delivery evidence and stakeholder feedback should return to
`requirements-synthesis-validation`, which updates statuses and examples before
a revised slice is briefed. Technical verification can show that the software
matches the brief; it cannot by itself show that the brief still represents the
stakeholders' needs.

## Recommended References

### Overall Requirements Process

If choosing one comprehensive foundation, use **Mastering the Requirements
Process, 4th Edition** by James Robertson, Suzanne Robertson, and Adrian Reed.
It covers problem scoping, stakeholder discovery, prototypes, functional and
non-functional requirements, measurable fit criteria, stories, and iterative
requirements work. It is probably the strongest backbone for all three skills.

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

## Reference Stack

1. *Mastering the Requirements Process* for the overall model.
2. *Interviewing Users* for evidence acquisition.
3. *Specification by Example* for validation and executable handoff.
4. *User Story Mapping* when refining the delivery-slice skill.

The central design principle is:

> Coding agents receive validated decisions plus visible uncertainty—not a
> prompt that makes uncertainty disappear.
