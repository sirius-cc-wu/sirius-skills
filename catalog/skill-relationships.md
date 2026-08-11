# Skill Relationships

Use this guide to choose a workflow track and understand its normal handoffs.
The skills remain independently deployable: follow only the path needed to
reduce the current risk or complete the current behavior slice.

## Bird's-eye view

This view groups all 31 deployable Sirius skills by responsibility and shows
two optional external intent-shaping skills at the boundary. It shows only the
main movement between groups so readers can locate a starting point before
using the detailed views below. Solid arrows are normal handoffs, not a
mandatory waterfall. Dashed arrows are optional routing, support, or feedback.

```plantuml
@startuml sirius-skills-birds-eye
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam defaultTextAlignment center
skinparam ArrowColor #52606D
skinparam nodesep 35
skinparam ranksep 45
skinparam rectangle {
  BackgroundColor #FFFFFF
  BorderColor #52606D
  RoundCorner 12
}
skinparam rectangle<<external>> {
  BackgroundColor #F2F2F2
  BorderColor #888888
}

package "Optional external intent shaping\naddyosmani/agent-skills" as addy #F2F2F2 {
  rectangle "interview-me" as addyInterview <<external>>
  rectangle "idea-refine" as addyIdea <<external>>
}

package "**Sirius: Intake and Direction**" as intake #FFF4CC {
  rectangle "assess-development-input" as assess
  rectangle "author-software-proposal" as proposal
}

rectangle "**Client Discovery**\nstakeholder-requirements-elicitation\nrequirements-synthesis-validation\nimplementation-slice-briefing" as discovery #E8F5E9

rectangle "**Reverse Engineering**\nreverse-engineer-software-system\nsurvey-existing-system\nrecover-system-behavior\nreconstruct-software-architecture\nreconcile-recovered-design" as reverse #EAF4FB

rectangle "**Iterative Analysis and Design**\nrun-development-iteration\niterative-up-analysis-design\ninception\nuse-case-modeling\nbehavior-driven-specification\ndomain-modeling\nsystem-sequence-diagrams\noperation-contracts\ngrasp-responsibility-design\nuse-case-realization\numl-class-diagram-design\ndesign-pattern-application" as design #EEF8EE

rectangle "**Implementation and Evolution**\ntest-driven-implementation\nbehavior-preserving-refactoring" as implementation #FFF5EA

rectangle "**Repository Workflow**\nsimplify\ncommit\ncreate-pr\ngovernance-update" as repository #F3EEFF

rectangle "**Cross-cutting Support**\nsoftware-design-language-adaptation\ndesign-rust-lifecycles\nrewrite-technical-artifacts" as support #FFFBEA

proposal -[hidden]right-> assess
assess -[hidden]right-> discovery
discovery -[hidden]right-> reverse
design -[hidden]right-> support

addyInterview --> addyIdea : confirmed intent
addyIdea --> proposal : refined idea
addyInterview ..> proposal : intent already concrete
proposal ..> assess : reviewed; route unclear
assess ..> discovery : stakeholder evidence needed
assess ..> reverse
assess ..> design
assess ..> implementation
discovery --> design
discovery --> implementation
reverse --> design
reverse ..> implementation
design --> implementation
implementation ..> design : durable feedback
implementation --> repository
@enduml
```

The gray nodes belong to Addy Osmani's external `agent-skills` collection, not
the Sirius catalog or installation profiles. They make one common composition
visible: `interview-me` confirms the requester's actual intent, `idea-refine`
turns that intent into a focused and user-confirmed idea one-pager, and
`author-software-proposal` turns that input into one decision-seeking artifact:
a proposed decision record for one focused choice or a software proposal for
broader exploration. If the intent is already concrete, `idea-refine` can be
skipped.

The resulting artifact still requires review by the responsible authority.
The dashed edge to `assess-development-input` applies only when the reviewed
artifact's next Sirius owner remains unclear.

The Sirius groups are navigation aids, not installation profiles or lifecycle
gates. The diagrams that follow show the internal choices and conditional
feedback that this overview deliberately collapses. Cross-cutting support is
left unconnected because it is selected for a specific language or readability
need, not as a required workflow stage.

## Choose a track

- Use **Assess Development Input** when requirements-shaped material already
  exists but its readiness or correct Sirius entry point is unclear.
- Use **Author Software Proposal** when technical input needs a consequential
  direction framed for responsible review.
- Start with **Client Discovery** when stakeholder evidence must be gathered,
  synthesized, and validated before a coding handoff can be prepared.
- Start with **Reverse Engineering** when an existing system must be understood.
- Start with **Iterative Analysis and Design** when an approved change needs a
  bounded behavior, analysis, design, language, or implementation iteration.
- Start with **Implementation and Evolution** when the behavior or structural
  change is already sufficiently bounded.
- Use **Repository Workflow** after a change is verified and authorized for
  cleanup, recording, or publication.

## External development inputs

`assess-development-input` is an optional content-based gateway. It accepts
intent statements, specifications, proposals, BDD scenarios, story maps,
brainstorm notes, and similar material without depending on the tool or method
that produced them. It selects the narrowest skill that owns the first material
gap, or reports an external prerequisite when no Sirius skill can responsibly
proceed. The assessment neither rewrites the source nor executes the selected
skill.

A common cross-repository path uses Addy Osmani's
[`interview-me`](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/skills/interview-me/SKILL.md)
and
[`idea-refine`](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/skills/idea-refine/SKILL.md)
before Sirius proposal authoring:

```text
interview-me
  → idea-refine
  → author-software-proposal
```

The handoffs depend on output meaning, not shared runtime state. A confirmed
intent feeds idea refinement; its confirmed problem, direction, assumptions,
MVP scope, and non-goals then provide source material for proposal authoring.
The Sirius proposal skill remains responsible for separating evidence from
proposed intent, documenting alternatives and risks, and stopping before
approval or implementation. Clarifying one requester's intent does not replace
client discovery when several stakeholder roles, evidence sources, conflicts,
or decision authorities matter; `assess-development-input` can route that gap
to the client-discovery skills.

## Software proposal authoring

`author-software-proposal` turns technical discussions, findings, incidents,
candidate changes, or an existing draft into one decision-seeking artifact. It
uses a proposed decision record for one focused consequential choice and a
software proposal when broader exploration or several decisions need review.
It separates current evidence from proposed intent, makes alternatives and
risks reviewable, and defines acceptance evidence without implying acceptance.
The responsible authority reviews the draft outside the skill. After that
review, `assess-development-input` can select a Sirius owner when the next
step remains unclear.

Decision-seeking authoring is not a substitute for inception, requirements
discovery, current-system recovery, or an accepted decision record. It may
expose a need for any of those owners and stop at that boundary. It should not
create both a proposal and a proposed decision record for the same focused
choice unless their audiences or lifecycles differ.

## Reverse engineering

`reverse-engineer-software-system` coordinates the recovery effort.
`survey-existing-system` establishes the first map; behavior recovery and
architecture reconstruction are selected only when the decision needs them.
Reconciliation is useful when recovered evidence may disagree with tests,
observations, documentation, decisions, or history. Stop as soon as the
original decision has enough evidence.

```plantuml
@startuml reverse-engineering-skill-relationships
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam rectangle {
  BackgroundColor #FFFFFF
  BorderColor #52606D
  RoundCorner 12
}
skinparam rectangle<<coordinator>> {
  BackgroundColor #DCEEFF
  BorderColor #2F6690
}

rectangle "reverse-engineer-\nsoftware-system" as reverse <<coordinator>>
rectangle "survey-existing-system" as survey
rectangle "recover-system-behavior" as behavior
rectangle "reconstruct-software-architecture" as architecture
rectangle "reconcile-recovered-design" as reconcile

reverse --> survey
survey ..> behavior : observable behavior needed
survey ..> architecture : internal structure needed
behavior ..> reconcile : perspectives may disagree
architecture ..> reconcile : perspectives may disagree
@enduml
```

See the [Reverse Engineering track](tracks/reverse-engineering.md) for evidence
rules, stopping conditions, and selection examples.

## Iterative analysis and design

`run-development-iteration` executes one approved, risk-sized objective and
stops after validation and one authorized commit. It routes to the smallest
specialists that answer the current question. `iterative-up-analysis-design`
remains an optional planner when a team explicitly wants UP phase framing and
use-case-driven artifact dependencies.

```plantuml
@startuml iterative-design-skill-relationships
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam rectangle {
  BackgroundColor #FFFFFF
  BorderColor #52606D
  RoundCorner 12
}
skinparam rectangle<<coordinator>> {
  BackgroundColor #DCEEFF
  BorderColor #2F6690
}

rectangle "run-development-\niteration" as iterative <<coordinator>>
rectangle "iterative-up-analysis-\ndesign" as up

package "Requirements and analysis" #EEF8EE {
  rectangle "inception" as inception
  rectangle "use-case-modeling" as usecases
  rectangle "behavior-driven-\nspecification" as behavior
  rectangle "domain-modeling" as domain
  rectangle "system-sequence-diagrams" as ssd
  rectangle "operation-contracts" as contracts
}

package "Optional object design" #F3EEFF {
  rectangle "grasp-responsibility-\ndesign" as grasp
  rectangle "use-case-realization" as realization
  rectangle "uml-class-diagram-\ndesign" as classdiagram
  rectangle "design-pattern-\napplication" as patterns
}

iterative ..> inception : scope or feasibility
iterative ..> usecases : actors or scenarios
iterative ..> behavior : observable examples
iterative ..> domain : vocabulary
iterative ..> ssd : system events
iterative ..> contracts : state effects
iterative ..> up : explicit UP planning
up --> usecases
inception --> usecases
usecases --> behavior
usecases --> domain
usecases --> ssd
behavior ..> contracts : clarify observable effects
domain ..> contracts : refine vocabulary
ssd --> contracts
domain --> grasp
contracts --> grasp
ssd --> realization
contracts --> realization
grasp --> realization
realization --> classdiagram
grasp ..> patterns : justified pressure
classdiagram ..> patterns : justified pressure
@enduml
```

See the
[Iterative Analysis and Design track](tracks/iterative-analysis-design.md) for
artifact boundaries and the iteration rule.

## Implementation and repository workflow

Implementation begins from an independent oracle: for example, an approved use
case, operation contract, realization, design class diagram, acceptance
example, invariant, defect report, reconciled change, or implementation brief.
The repository workflow begins only after the change is verified and the user
has authorized its next effect.

```plantuml
@startuml implementation-repository-skill-relationships
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam rectangle {
  BackgroundColor #FFFFFF
  BorderColor #52606D
  RoundCorner 12
}
skinparam rectangle<<input>> {
  BackgroundColor #F2F2F2
  BorderColor #888888
}
skinparam rectangle<<support>> {
  BackgroundColor #FFF4CC
  BorderColor #A66B00
}

rectangle "Approved behavior or design input" as oracle <<input>>

package "Implementation and Evolution" #FFF5EA {
  rectangle "test-driven-\nimplementation" as implementation
  rectangle "behavior-preserving-refactoring" as refactoring
}

package "Repository Workflow" #F3EEFF {
  rectangle "simplify" as simplify
  rectangle "commit" as commit
  rectangle "create-pr" as createpr
  rectangle "governance-update" as governance <<support>>
}

oracle --> implementation
implementation --> refactoring : green baseline
implementation ..> simplify : optional cleanup
refactoring ..> simplify : optional cleanup
simplify --> commit
commit --> createpr
simplify ..> governance : repeated drift
@enduml
```

See the
[Implementation and Evolution](tracks/implementation-evolution.md) and
[Repository Workflow](tracks/repository-workflow.md) tracks for their entry
conditions, safety rules, and authority boundaries.

## Feedback and re-entry

The forward diagrams stay small by collapsing feedback into a few dashed
arrows and prose. This view expands only the paths where later evidence can
refine earlier design knowledge, restart design work, or improve repository
governance. A feedback edge is conditional: follow it only when the named
trigger changes knowledge owned by the target skill.

```plantuml
@startuml sirius-skill-feedback
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam defaultTextAlignment center
skinparam ArrowColor #A15C38
skinparam rectangle {
  BackgroundColor #FFFFFF
  BorderColor #52606D
  RoundCorner 12
}
skinparam rectangle<<coordinator>> {
  BackgroundColor #DCEEFF
  BorderColor #2F6690
}

package "Analysis and design knowledge" #EEF8EE {
  rectangle "run-development-\niteration" as iterative <<coordinator>>
  rectangle "domain-modeling" as domain
  rectangle "operation-contracts" as contracts
  rectangle "grasp-responsibility-\ndesign" as grasp
  rectangle "use-case-realization +\numl-class-diagram-design" as designviews
  rectangle "design-pattern-\napplication" as patterns
}

package "Execution and evidence" #FFF5EA {
  rectangle "test-driven-\nimplementation" as implementation
  rectangle "behavior-preserving-\nrefactoring" as refactoring
  rectangle "reconcile-recovered-\ndesign" as reconcile
}

package "Repository learning" #F3EEFF {
  rectangle "simplify" as simplify
  rectangle "governance-update" as governance
}

contracts ..> domain : missing concept or association
patterns ..> designviews : participants or dependencies change

implementation ..> contracts : postcondition changes
implementation ..> designviews : responsibility, collaboration, or interface changes

refactoring ..> grasp : responsibility or coupling pressure
refactoring ..> patterns : justified variation pressure
refactoring ..> designviews : durable structure changes

reconcile ..> iterative : stakeholder-validated knowledge
reconcile ..> implementation : authorized bounded correction

simplify ..> governance : repeated repository drift
@enduml
```

The combined `use-case-realization + uml-class-diagram-design` node keeps the
view readable; implementation and refactoring can refine either or both. In
particular:

- contract feedback changes the domain model only when a postcondition exposes
  missing domain vocabulary;
- implementation and refactoring update design artifacts only when durable
  postconditions, responsibilities, collaborations, interfaces, or dependency
  direction changed;
- reconciliation recommends the authoritative next action first—it does not
  automatically turn current code into intended design or authorize a change;
  and
- `rewrite-technical-artifacts` is not a design-feedback edge because it must
  preserve normative meaning.

## Cross-cutting skills

Cross-cutting skills are listed instead of connected to every consumer. This
keeps the diagrams readable without changing where they apply.

| Skill | Use with | Selection trigger |
|---|---|---|
| `software-design-language-adaptation` | `run-development-iteration`, approved behavior and contracts, optional object design, and `test-driven-implementation` | Language-specific data, interfaces, ownership, errors, concurrency, lifecycle, or runtime conventions affect the design |
| `design-rust-lifecycles` | `run-development-iteration`, approved scenarios and contracts, language adaptation, implementation briefing, and Rust implementation | Ownership, capability transfer, staged startup, readiness, rollback, cancellation, supervision, or fallible cleanup creates a material Rust design risk |
| `rewrite-technical-artifacts` | Recovered artifacts, iterative-design artifacts, behavior-slice evidence, and refactoring records | The knowledge is sound but its reading order or progressive disclosure needs improvement |

## Client discovery upstream path

All three client-discovery skills in this optional handoff are deployable:

```text
stakeholder-requirements-elicitation
  → requirements-synthesis-validation
  → inception, use-case modeling, behavior-driven-specification when examples
    are needed, and selected analysis/design
  → implementation-slice-briefing
  → test-driven-implementation
```

The `assess-development-input` skill provides a smaller, method-independent
entry point when requirements-shaped material already exists. It can assess
outputs from these skills or any other external discovery and specification
method, but it cannot gather stakeholder evidence, validate requirements, or
prepare an implementation brief on their behalf.

The [Client to Code track](tracks/client-to-code.md) is the active handoff
guide. The
[client-discovery proposal](../docs/proposals/client-discovery-skills.md)
records the skill-family rationale and implementation history.

The [workflow tracks](tracks/) remain the authoritative descriptions of when
to select each skill.
