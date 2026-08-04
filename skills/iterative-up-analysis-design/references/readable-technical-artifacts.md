# Readable Technical Artifacts

Use these rules when creating or revising reader-facing analysis, design,
decision, planning, or verification artifacts. Preserve repository conventions
and the artifact structure required by its owning skill.

## Writing Flow

1. Identify the primary reader and the question the artifact must answer.
2. Open with a plain-language explanation of the problem, intended behavior or
   decision, and its important consequence. Do not rely on frontmatter or links
   to supply this orientation.
3. For unfamiliar, stateful, or concurrent behavior, show one representative
   scenario before exhaustive terminology, contracts, edge cases, or
   traceability.
4. Introduce canonical terms in the context of the explanation. Prefer a plain
   description followed by the canonical term in parentheses on first use.
5. Put exact rules, contracts, state transitions, diagrams, identifiers, and
   traceability after the reader understands the situation.
6. Define a rule at one canonical location. Elsewhere, state only the context
   needed by that reader and link to the canonical rule.

The headings `At a glance`, `Representative scenario`, `Exact rules`, and
`Technical reference` are available when they fit; they are not a mandatory
template. A use case's main success scenario may already serve as its
representative scenario. An operation contract may link to the scenario that
discovered it instead of repeating that scenario.

## Preserve Meaning

Before reorganizing an existing artifact, inventory its requirements,
guarantees, prohibitions, identifiers, states, operations, and traceability
links. Afterward, verify that:

- no normative fact or uncertainty was lost or strengthened;
- the explanation and representative scenario agree with the exact rules;
- exact code and protocol identifiers remain available where readers need them;
- moving detail did not create a second source of truth; and
- the artifact did not become materially longer by retaining avoidable
  repetition underneath a new summary.

Report contradictions or uncertain meaning instead of silently resolving them
as a writing change.

## Keep the Structure Proportionate

Keep low-risk and local artifacts lightweight. Indexes, registries,
traceability ledgers, narrow checklists, and similarly structural files do not
need an explanation layer when it would add ceremony without helping their
readers.

Do not try to make one artifact serve every audience. Prefer one canonical
technical artifact with a layered opening. Create a separate operator guide or
companion explanation only when a genuinely different task or audience cannot
be served safely by the canonical artifact.

## Final Editorial Pass

The owning skill should produce a readable artifact directly. After producing
or materially revising a substantial artifact, use
[Rewrite Technical Artifacts](../../rewrite-technical-artifacts/SKILL.md) as a
focused final pass when the reading path, proportion, canonical ownership, or
cross-artifact consistency remains difficult. The same pass can review the
reader-facing artifacts in a branch or pull-request diff before commit or
review.

This handoff is risk-calibrated, not mandatory. Skip it for a narrow structural
artifact that is already proportionate, and accept a review that finds no
high-confidence improvement.
