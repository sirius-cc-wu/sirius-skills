# Skill Relationships

Use this guide to choose a workflow track and understand its normal handoffs.
The skills remain independently deployable: follow only the path needed to
reduce the current risk or complete the current behavior slice.

## Choose a track

- Start with **Reverse Engineering** when an existing system must be understood.
- Start with **Iterative Analysis and Design** when intended behavior, scope, or
  object design is not yet clear.
- Start with **Implementation and Evolution** when the behavior or structural
  change is already sufficiently bounded.
- Use **Repository Workflow** after a change is verified and authorized for
  cleanup, recording, or publication.

Solid arrows show a normal handoff, not a mandatory waterfall. Dashed arrows
show an optional alternative or feedback path.

```plantuml
@startuml skill-track-overview
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam defaultTextAlignment center
skinparam ArrowColor #52606D
skinparam rectangle {
  BackgroundColor #FFFFFF
  BorderColor #52606D
  RoundCorner 12
}

rectangle "Reverse Engineering\nunderstand an existing system" as reverse #EAF4FB
rectangle "Iterative Analysis and Design\nclarify behavior and design" as design #EEF8EE
rectangle "Implementation and Evolution\nchange verified behavior or structure" as implementation #FFF5EA
rectangle "Repository Workflow\nrefine, record, and publish" as repository #F3EEFF

reverse --> design : stakeholder-validated knowledge
reverse --> implementation : safely bounded change
design --> implementation : selected behavior and design inputs
implementation ..> design : discoveries or durable design pressure
implementation --> repository : verified change
@enduml
```

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

`iterative-up-analysis-design` coordinates risk-driven iterations. The diagram
shows artifact dependencies, not a requirement to create every artifact.
Choose only the analysis and design work needed for the selected risk and
behavior slice.

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

rectangle "iterative-up-analysis-\ndesign" as iterative <<coordinator>>

package "Requirements and analysis" #EEF8EE {
  rectangle "inception" as inception
  rectangle "use-case-modeling" as usecases
  rectangle "domain-modeling" as domain
  rectangle "system-sequence-diagrams" as ssd
  rectangle "operation-contracts" as contracts
}

package "Object design" #F3EEFF {
  rectangle "grasp-responsibility-\ndesign" as grasp
  rectangle "use-case-realization" as realization
  rectangle "uml-class-diagram-\ndesign" as classdiagram
  rectangle "design-pattern-\napplication" as patterns
}

iterative --> inception
inception --> usecases
usecases --> domain
usecases --> ssd
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
conditions, safety rules, and authority boundaries. When refactoring exposes a
durable design pressure, return to `grasp-responsibility-design` or
`design-pattern-application`.

## Cross-cutting skills

Cross-cutting skills are listed instead of connected to every consumer. This
keeps the diagrams readable without changing where they apply.

| Skill | Use with | Selection trigger |
|---|---|---|
| `software-design-language-adaptation` | `grasp-responsibility-design`, `use-case-realization`, `uml-class-diagram-design`, `design-pattern-application`, and `test-driven-implementation` | Language-specific ownership, errors, concurrency, lifecycle, or interface conventions affect the design |
| `rewrite-technical-artifacts` | Recovered artifacts, iterative-design artifacts, behavior-slice evidence, and refactoring records | The knowledge is sound but its reading order or progressive disclosure needs improvement |

## Proposed upstream path

Three client-discovery skills are proposed but not deployable from this
repository. Their intended handoff remains:

```text
stakeholder-requirements-elicitation
  → requirements-synthesis-validation
  → inception, use-case modeling, and selected analysis/design
  → implementation-slice-briefing
  → test-driven-implementation
```

The [Client to Code track](tracks/client-to-code.md) and
[client-discovery proposal](../docs/proposals/client-discovery-skills.md) are
the authoritative sources for this future path.

The [workflow tracks](tracks/) remain the authoritative descriptions of when
to select each skill.
