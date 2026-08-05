# Skill Catalog

This catalog describes each deployable skill's responsibility and boundary.
See [Source Catalog](sources.md) for intellectual provenance and
[Workflow Tracks](tracks/) for ways to compose the skills.

| Skill | Source Concepts Preserved | Primary Artifact | Boundary |
|---|---|---|---|
| `simplify` | Diff-scoped cleanup, behavior preservation, configuration ownership, and proportional verification | Verified simplified change set | Improves an existing change without intentionally expanding its behavior or scope |
| `commit` | Intentional staging, repository checks, configurable message conventions, and concise change records | Git commit | Records an already prepared change; does not broaden scope, discard unrelated work, or publish it |
| `create-pr` | Base and head verification, duplicate detection, convention-aware titles, validation evidence, and draft-first publication | GitHub pull request | Publishes committed work for review; does not implement, silently commit, or resolve divergent history |
| `governance-update` | Repeated-drift evidence, narrow rule ownership, generic defaults, and enforceable repository guidance | Updated governance surface | Changes durable policy only when recurring evidence justifies it; does not turn one-off defects into rules |
| `reverse-engineer-software-system` | Question-driven recovery, evidence perspectives, confidence calibration, risk-sized investigation, as-of-revision artifact lifecycles | Reverse-engineering record and recovered-artifact map | Coordinates recovery skills and handoffs; does not model an entire repository or convert inference into intended requirements |
| `survey-existing-system` | First contact, repository reconnaissance, entry points, external interfaces, packaging, verification surfaces, documentation and risk mapping | System survey | Orients and prioritizes deeper recovery; does not claim detailed behavior or architecture |
| `recover-system-behavior` | Black-box behavior recovery, executable and observational evidence, main and alternate scenarios, failures, externally visible qualities | Recovered behavior model | Describes evidenced current behavior; does not assign internal responsibilities or approve product intent |
| `reconstruct-software-architecture` | Architecture extraction and abstraction, view selection, module and component relations, runtime collaborations, state ownership, deployment and trust boundaries | Recovered architecture | Describes as-built structure at a decision-relevant level; does not invent design rationale or intended architecture |
| `reconcile-recovered-design` | As-built versus as-tested, as-observed, as-documented, intended, and historical comparison; lifecycle-aware drift classification | Design reconciliation | Classifies agreement, drift, gaps, and unknown intent; does not silently edit code, tests, or canonical documents |
| `rewrite-technical-artifacts` | Cognitive simplification, progressive disclosure, reader orientation, representative scenarios, canonical-rule linking, semantic inventories, and diff-focused review | Revised canonical technical artifact or changed-artifact review | Reduces reader effort without changing normative meaning, evidence, identifiers, lifecycle, or traceability |
| `assess-development-input` | Content-based readiness assessment, source and approval preservation, explicit uncertainty, and next-owner selection | Development input assessment | Routes requirements-shaped input to one Sirius skill without conducting discovery, rewriting the source, inventing decisions, or executing the handoff |
| `iterative-up-analysis-design` | Unified Process phases (elaboration/construction/transition coordination), risk-driven iterations, durable design artifacts, historical iteration records, repository layout selection | Iteration plan, artifact map, and lifecycle-aware placement | Coordinates the sequence and artifact durability; does not replace detailed artifact skills or impose one repository taxonomy |
| `inception` | Envision product scope, vision, business case, feasibility, sample inception artifacts (Vision, Use-Case Model name list, Supplementary Specification, Glossary, Risk List, Development Case), inception red flags | Vision and Business Case, Risk List, Development Case | Defines the boundaries, objectives, and minimal artifact set for the project kickoff phase; transitions to Elaboration |
| `use-case-modeling` | Actors, goals, elementary business processes, black-box use cases, main success and extensions, use-case diagrams as summaries | Use-case model | Captures requirements, not internal object design |
| `domain-modeling` | Conceptual classes, associations, attributes, category lists, domain model vs design model | Domain model | Models real-world concepts, not software classes or database tables |
| `system-sequence-diagrams` | System boundary, actors, system events, system operations, scenarios from use cases | SSDs | Shows actor-system interaction, not object collaboration |
| `operation-contracts` | Preconditions, postconditions, state changes, created/deleted instances, associations, attributes | Operation contracts | Used for complex system operations; not a restatement of use-case text |
| `grasp-responsibility-design` | Information Expert, Creator, Controller, Low Coupling, High Cohesion, Polymorphism, Pure Fabrication, Indirection, Protected Variations | Responsibility assignment decisions | Chooses object responsibilities; does not mandate specific GoF patterns |
| `use-case-realization` | Interaction diagrams, object messages, controller entry points, design classes discovered while realizing use cases | Sequence/communication diagrams | Shows software object collaboration for one scenario |
| `uml-class-diagram-design` | Design model classes, attributes, operations, associations, navigability, visibility, packages, domain vs design model | Design class diagram | Summarizes discovered software classes after responsibility design |
| `design-pattern-application` | Adapter, Factory, Strategy, Composite, Observer, Abstract Factory and pattern-to-GRASP connections | Pattern decision record and implementation sketch | Applies patterns when forces justify them; avoids pattern catalog dumping |
| `software-design-language-adaptation` | Language-native mappings for responsibilities, variation, lifecycle, errors, concurrency, and UML notation | Implementation-facing design adaptation | Adapts design intent to Rust, Python, TypeScript, C#, or C++; does not alter language-neutral requirements or domain models |
| `test-driven-implementation` | Risk-calibrated behavior slices, implementation-independent oracles, discriminating tests and mechanical checks, executable interface clarification, focused regression verification | Tested production increment and behavior-slice evidence | Implements scoped behavior from requirements or design inputs; avoids both per-test red-green ritual and whole-module test-first batching by default |
| `behavior-preserving-refactoring` | Small behavior-preserving transformations, bounded mechanical batches, verification after each reviewable step, code smells, common refactorings, structural design feedback | Verified structural improvement and refactoring record | Improves structure behind passing checks; separates behavior changes and delegates pattern selection to explicit design forces |

## Distillation Rules

- Convert source material into agent behavior, not a chapter summary.
- Prefer checklists, decision points, and artifact templates over explanation.
- Keep each skill small enough to load independently.
- Avoid copying long source passages; preserve concepts as practical procedures.
- Put discovery and lifecycle metadata for standalone Markdown artifacts in one
  OKF-aligned YAML frontmatter block; keep narrative analysis, design,
  rationale, and evidence in the body.
