# Skill Inventory

| Skill | Source Concepts Preserved | Primary Artifact | Boundary |
|---|---|---|---|
| `iterative-up-analysis-design` | Unified Process phases, inception/elaboration/construction/transition, risk-driven iterations, durable design artifacts, historical iteration records, repository layout selection | Iteration plan, artifact map, and lifecycle-aware placement | Coordinates the sequence and artifact durability; does not replace detailed artifact skills or impose one repository taxonomy |
| `use-case-modeling` | Actors, goals, elementary business processes, black-box use cases, main success and extensions, use-case diagrams as summaries | Use-case model | Captures requirements, not internal object design |
| `domain-modeling` | Conceptual classes, associations, attributes, category lists, domain model vs design model | Domain model | Models real-world concepts, not software classes or database tables |
| `system-sequence-diagrams` | System boundary, actors, system events, system operations, scenarios from use cases | SSDs | Shows actor-system interaction, not object collaboration |
| `operation-contracts` | Preconditions, postconditions, state changes, created/deleted instances, associations, attributes | Operation contracts | Used for complex system operations; not a restatement of use-case text |
| `grasp-responsibility-design` | Information Expert, Creator, Controller, Low Coupling, High Cohesion, Polymorphism, Pure Fabrication, Indirection, Protected Variations | Responsibility assignment decisions | Chooses object responsibilities; does not mandate specific GoF patterns |
| `use-case-realization` | Interaction diagrams, object messages, controller entry points, design classes discovered while realizing use cases | Sequence/communication diagrams | Shows software object collaboration for one scenario |
| `uml-class-diagram-design` | Design model classes, attributes, operations, associations, navigability, visibility, packages, domain vs design model | Design class diagram | Summarizes discovered software classes after responsibility design |
| `design-pattern-application` | Adapter, Factory, Strategy, Composite, Observer, Abstract Factory and pattern-to-GRASP connections | Pattern decision record and implementation sketch | Applies patterns when forces justify them; avoids pattern catalog dumping |
| `software-design-language-adaptation` | Language-native mappings for responsibilities, variation, lifecycle, errors, concurrency, and UML notation | Implementation-facing design adaptation | Adapts design intent to Rust, Python, TypeScript, C#, or C++; does not alter language-neutral requirements or domain models |

## Distillation Rules

- Convert source material into agent behavior, not a chapter summary.
- Prefer checklists, decision points, and artifact templates over explanation.
- Keep each skill small enough to load independently.
- Avoid copying long source passages; preserve concepts as practical procedures.
