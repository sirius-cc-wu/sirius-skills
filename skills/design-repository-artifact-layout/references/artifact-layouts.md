# Artifact Durability and Repository Layouts

Use this reference when a repository needs canonical homes for durable
candidate directions, requirements, analysis, design, recovery, decisions, verification
evidence, and iteration history. Preserve an established documentation
structure unless it is causing a concrete navigation or ownership problem.

## Artifact Lifecycles

| Artifact kind | Examples | Lifecycle |
|---|---|---|
| Candidate direction | Idea one-pager; scope, alternatives, risks, requested decision | Keep the idea in draft or proposed state while review is pending. After a decision, record the outcome and link to the authoritative decision, design, or implementation artifact instead of leaving the idea as an ambiguous current source of truth. |
| Durable current artifact | Approved requirement, use case, domain model, SSD, operation contract, realization, design class diagram | Refine the canonical artifact in place across iterations; retain a stable ID when other artifacts or iterations reference it. |
| Recovered knowledge | System survey, recovered behavior, reconstructed architecture, reconciliation | Fix claims to the inspected revision and preserve evidence status. Refine in place only while the artifact continues to describe that baseline; create or supersede it explicitly when a later baseline must remain distinguishable. |
| Iteration record | Objective, risks, selected scope, exit criteria, results | Create one record per iteration, close it when evidence is known, and retain it as history. |
| Architecture decision record | One consequential choice, context and forces, serious alternatives, consequences, confidence, reconsideration triggers | Keep an accepted decision substantively stable; replace it with a linked superseding ADR rather than rewriting its history. |
| Verification evidence | Acceptance test, experiment result, benchmark, threat-model check | Keep it near executable verification or link to it from the iteration result and affected design artifact. |

Durability does not mean immutability. Durable current artifacts remain the
current source of truth and are expected to change as later contracts,
realizations, implementation, and feedback reveal better information.
Recovered artifacts retain their as-of-revision boundary rather than silently
becoming intended requirements or descriptions of a later baseline.

Iteration records are historically stable but usually become less important
after closure. They should point to canonical artifacts instead of containing
iteration-specific copies of those artifacts.

An idea one-pager is the candidate-direction artifact for new work. Use
it for confirmed intent, scope, alternatives, risks, and a requested decision.
Existing Sirius proposals remain legacy artifacts. Neither an idea nor a legacy
proposal substitutes for confirmed intent, current requirements or design
knowledge, accepted decision records, or implementation briefs. Preserve those
lifecycle boundaries when a candidate direction supplies source material for a
later artifact.

## Selection Workflow

1. Inspect repository governance, documentation indexes, and neighboring files.
2. Identify how readers primarily navigate: by feature, artifact type, product
   area, or chronology.
3. Apply
   [Artifact Selection Budget](../../select-technical-artifacts/references/artifact-selection-budget.md)
   to decide whether documentation belongs in implementation evidence, an
   existing artifact, an aggregate section, or a new standalone file.
4. Estimate whether a feature needs one document or several independently
   changing artifacts.
5. Select the smallest layout that gives each durable artifact one obvious
   canonical location without blending intended current knowledge with
   as-of-revision recovery evidence.
6. Record canonical paths in the recommendation and any applicable index or
   iteration record. Assign stable IDs to artifacts referenced across
   iterations or by other artifacts.
7. Revisit the layout only when growth, shared ownership, or navigation creates
   evidence that the current structure no longer works.

## Idea Placement

Use `docs/ideas/` for new and migrated candidate documents. Do not create a
second candidate artifact for the same direction. Preserve
the established path, index, and naming rule. When no convention exists, use
the smallest placement that matches how reviewers find pending decisions:

- Prefer `docs/ideas/<topic>.md` when ideas span product areas or readers
  navigate them by lifecycle or artifact type.
- Prefer `docs/features/<feature>/idea.md` or
  `docs/<product-area>/ideas/<topic>.md` when review ownership and navigation
  follow that feature or product area.
- Prefer one idea file. Create an idea directory only when supporting evidence
  has independent value but shares the idea lifecycle.

Keep an idea one-pager in draft or proposed state until the responsible
authority decides it. After acceptance, rejection, or supersession, preserve the
outcome according to repository policy and link to the artifact that now owns
the decision or intended behavior. Do not silently treat an undecided candidate
direction as the current design.

## Layout Options

### Feature-Iteration Hybrid

```text
docs/
  ideas/
    view-markdown-with-plantuml.md
  features/
    view-markdown-with-plantuml/
      index.md
      use-case.md
      analysis.md
      design.md
  iterations/
    e1-view-markdown-with-plantuml.md
  decisions/
  index.md
```

This is the recommended general-purpose layout. It separates durable feature
knowledge from historical iteration records while keeping both easy to
navigate.

Feature storage has two variants:

- Use a single file such as `features/view-markdown-with-plantuml.md` while the
  feature remains cohesive and changes as one unit.
- Use the feature package shown above when its use case, analysis, and design
  artifacts change independently.

Use when:

- Readers navigate primarily by feature.
- Iteration history must remain separate from current design knowledge.
- The repository needs a structure that can grow from one-page features to
  feature packages without changing its top-level organization.

Tradeoffs:

- Its flat variant has low ceremony and short paths.
- Its package variant keeps related artifacts together but can create tiny
  files when introduced before they change independently.

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

Do not choose iteration-first by default when durable current knowledge is the
goal. Prefer a separate `iterations/` ledger linked to canonical current
artifacts. When controlled snapshots are required, keep canonical evolving
artifacts and their index under `current/`; iteration snapshots are historical
copies and never become the current-artifact locator.

## Selection Matrix

| Repository condition | Preferred starting layout |
|---|---|
| Small repository with one-page features | Feature-iteration hybrid, flat feature variant |
| Large cohesive features with independently changing artifacts | Feature-iteration hybrid, feature package variant |
| Shared models spanning many features | Artifact-oriented |
| Stable subsystems with area ownership | Product-area oriented |
| Regulated chronological snapshots | Iteration-first, with canonical artifacts and an explicit index under `current/` |

These are starting points, not mandatory taxonomies. A repository may combine
them, such as the feature-iteration hybrid for user-facing work,
product-area-oriented architecture, and artifact-oriented shared models.

## Linking Rules

- Give artifacts referenced across iterations or by other artifacts stable IDs
  that follow explicit repository rules. Treat IDs as opaque; do not infer a
  date or monotonic sequence from examples or neighboring names. Local
  supporting notes may use only a title and canonical path.
- Keep one canonical path for each current artifact or fixed recovery baseline.
- Link iteration records to canonical artifacts and identify whether each was
  started, refined, or only consulted.
- Link design decisions back to use cases, system events, contracts, risks, or
  verification evidence.
- Update indexes and inbound links when moving a canonical artifact.
- Do not copy a complete current artifact into an iteration record merely to
  preserve history; version control already records revisions. Controlled
  iteration snapshots are the explicit audit-oriented exception and must link
  back to the canonical artifact under `current/`.

## Markdown Metadata and Reserved Files

- Apply
  [Markdown Artifact Frontmatter](../../iterative-risk-driven-analysis-design/references/markdown-artifact-frontmatter.md)
  to every standalone Markdown concept artifact created by these layouts.
- In a flat feature file, describe the feature's aggregate requirements and
  design content once in file-level frontmatter. Do not insert frontmatter
  between body sections.
- In a feature package or artifact-oriented layout, give independently
  maintained artifact files their specific types, titles, descriptions, and
  stable IDs in frontmatter.
- Treat `index.md` and `log.md` as reserved structural files rather than
  concept artifacts, and follow their special frontmatter rules.

## Migration Guidance

- Move from the flat to the package variant of the feature-iteration hybrid
  when a feature has multiple independently maintained sections, not merely
  because the file is long.
- Introduce artifact-oriented directories when models become genuinely shared
  across features.
- Introduce product areas only after their boundaries and ownership are stable.
- Keep old iteration records at their historical paths when reorganizing
  current artifacts; update their links or provide a small migration index.
- Avoid organizing durable artifacts by UP phase. Use cases and design models
  commonly begin in one phase and mature in later phases.
