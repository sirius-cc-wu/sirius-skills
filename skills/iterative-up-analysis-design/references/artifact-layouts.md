# Artifact Durability and Repository Layouts

Use this reference when a repository needs a home for durable analysis and
design artifacts plus iteration history. Preserve an established documentation
structure unless it is causing a concrete navigation or ownership problem.

## Artifact Lifecycles

| Artifact kind | Examples | Lifecycle |
|---|---|---|
| Durable design artifact | Use case, domain model, SSD, operation contract, realization, design class diagram | Refine the canonical artifact in place across iterations; retain a stable ID when other artifacts or iterations reference it. |
| Iteration record | Objective, risks, selected scope, exit criteria, results | Create one record per iteration, close it when evidence is known, and retain it as history. |
| Decision record | Architectural choice, rejected alternatives, consequences | Keep the accepted decision durable; supersede it explicitly rather than silently rewriting its history. |
| Verification evidence | Acceptance test, experiment result, benchmark, threat-model check | Keep it near executable verification or link to it from the iteration result and affected design artifact. |

Durability does not mean immutability. Durable design artifacts remain the
current source of truth and are expected to change as later contracts,
realizations, implementation, and feedback reveal better information.

Iteration records are historically stable but usually become less important
after closure. They should point to canonical artifacts instead of containing
iteration-specific copies of those artifacts.

## Selection Workflow

1. Inspect repository governance, documentation indexes, and neighboring files.
2. Identify how readers primarily navigate: by feature, artifact type, product
   area, or chronology.
3. Estimate whether a feature needs one document or several independently
   changing artifacts.
4. Select the smallest layout that gives each durable artifact one obvious
   canonical location.
5. Record canonical paths in the iteration record and assign stable IDs to
   artifacts referenced across iterations or by other artifacts.
6. Revisit the layout only when growth, shared ownership, or navigation creates
   evidence that the current structure no longer works.

## Layout Options

### Flat Hybrid

```text
docs/
  features/
    view-markdown-with-plantuml.md
  iterations/
    e1-view-markdown-with-plantuml.md
  decisions/
  index.md
```

Use when:

- The repository is small or early in development.
- Most features fit in one durable document.
- Readers navigate primarily by feature.

Tradeoffs:

- It has low ceremony and short paths.
- Large feature files may eventually need decomposition.

### Feature Packages

```text
docs/
  features/
    view-markdown-with-plantuml/
      index.md
      use-case.md
      analysis.md
      design.md
  iterations/
    e1-view-markdown-with-plantuml.md
  decisions/
```

Use when:

- A feature has several durable artifacts that change independently.
- Feature cohesion matters more than browsing by artifact type.
- One feature document has become difficult to review or navigate.

Tradeoffs:

- It keeps related knowledge together.
- It can create empty or tiny files when introduced too early.

### Artifact-Oriented

```text
docs/
  use-cases/
  domain-models/
  system-sequences/
  contracts/
  realizations/
  design-models/
  iterations/
  decisions/
```

Use when:

- Models and contracts are shared across many features.
- Readers commonly search by artifact type.
- Stable identifiers and a strong cross-reference index already exist.

Tradeoffs:

- It gives each modeling discipline an obvious home.
- Reconstructing one user goal requires following links across directories.

### Product-Area Oriented

```text
docs/
  viewer/
    requirements/
    analysis/
    design/
  workspace/
    requirements/
    analysis/
    design/
  iterations/
  decisions/
```

Use when:

- The system has stable subsystems or bounded product areas.
- Ownership and navigation follow those areas.
- Features regularly span multiple artifacts inside one area.

Tradeoffs:

- It scales with stable organizational boundaries.
- Early use can preserve boundaries that later learning disproves.

### Iteration-First

```text
docs/
  current/
    index.md
    use-case.md
    design.md
  iterations/
    e1/
      plan.md
      snapshots/
        use-case.md
        design.md
    e2/
      plan.md
      snapshots/
        design.md
```

Use when:

- Auditability or chronological reconstruction is the primary goal.
- The repository explicitly accepts versioned artifact snapshots.

Tradeoffs:

- It preserves iteration context directly.
- It duplicates design knowledge and makes the current source of truth hard to
  locate.

Do not choose iteration-first by default when durable design knowledge is the
goal. Prefer a separate `iterations/` ledger linked to canonical design
artifacts. When controlled snapshots are required, keep canonical evolving
artifacts and their index under `current/`; iteration snapshots are historical
copies and never become the current-artifact locator.

## Selection Matrix

| Repository condition | Preferred starting layout |
|---|---|
| Small repository with one-page features | Flat hybrid |
| Large cohesive features with independently changing artifacts | Feature packages |
| Shared models spanning many features | Artifact-oriented |
| Stable subsystems with area ownership | Product-area oriented |
| Regulated chronological snapshots | Iteration-first, with canonical artifacts and an explicit index under `current/` |

These are starting points, not mandatory taxonomies. A repository may combine
them, such as feature packages for user-facing work, product-area architecture,
and a shared top-level iteration ledger.

## Linking Rules

- Give artifacts referenced across iterations or by other artifacts stable IDs
  such as `UC-01`, `SSD-01`, or `ADR-003`. Local supporting notes may use only
  a title and canonical path.
- Keep one canonical path for each current design artifact.
- Link iteration records to canonical artifacts and identify whether each was
  started, refined, or only consulted.
- Link design decisions back to use cases, system events, contracts, risks, or
  verification evidence.
- Update indexes and inbound links when moving a canonical artifact.
- Do not copy a complete design artifact into an iteration record merely to
  preserve history; version control already records revisions. Controlled
  iteration snapshots are the explicit audit-oriented exception and must link
  back to the canonical artifact under `current/`.

## Migration Guidance

- Move from flat hybrid to a feature package when a feature has multiple
  independently maintained sections, not merely because the file is long.
- Introduce artifact-oriented directories when models become genuinely shared
  across features.
- Introduce product areas only after their boundaries and ownership are stable.
- Keep old iteration records at their historical paths when reorganizing
  current design artifacts; update their links or provide a small migration
  index.
- Avoid organizing durable artifacts by UP phase. Use cases and design models
  commonly begin in one phase and mature in later phases.
