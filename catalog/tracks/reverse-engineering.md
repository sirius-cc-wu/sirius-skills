# Reverse Engineering

`reverse-engineer-software-system`, `survey-existing-system`,
`recover-system-behavior`, `reconstruct-software-architecture`, and
`reconcile-recovered-design` are retired. Existing surveys, recovered behavior
models, reconstructed architecture, reconciliation records, and fixed-revision
evidence remain valid at their recorded revisions.

The `reverse-engineering` installation name remains as a compatibility profile.
It installs `select-technical-artifacts`,
`design-repository-artifact-layout`, and `record-architecture-decision`. These
skills can manage justified artifacts and recorded decisions, but they do not
recover current-system facts.

## New Current-System Evidence

Use a responsible external recovery process when maintenance, migration,
modernization, audit, onboarding, or resumed development needs new evidence
about current commands, behavior, architecture, deployment, state, or
constraints.

The external process must:

- fix the repository revision, runtime build, or other baseline under study;
- state the decision, bounded scope, exclusions, and authority for probes;
- distinguish as-built, as-tested, as-observed, as-documented, intended, and
  historical claims;
- attach locators and calibrated confidence to material claims;
- preserve contradictions, lifecycle state, and residual uncertainty; and
- avoid converting current implementation or tests into approved intent.

Use
[`assess-development-input`](../../skills/assess-development-input/SKILL.md)
when requirements-shaped material depends on current-system claims and its
Sirius readiness or next owner is unclear. The assessment must return an
external prerequisite when those claims still lack sufficient evidence.

## Active Support

Use
[`record-architecture-decision`](../../skills/record-architecture-decision/SKILL.md)
in read-only mode to identify which ADRs govern a concern. An ADR records a
choice and rationale at its revision. It does not prove that current code still
conforms, and missing ADRs do not authorize inferred rationale.

Use
[`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md)
when externally recovered knowledge needs a disposition such as updating an
existing owner, staying with executable evidence, becoming a justified
standalone artifact, being deferred, or being omitted.

Use
[`design-repository-artifact-layout`](../../skills/design-repository-artifact-layout/SKILL.md)
when a justified recovered artifact lacks a canonical home or when migration
must preserve links, identifiers, indexes, and history. Placement authority does
not authorize new recovery claims or content changes.

## Handoff Rule

Feed only externally validated current-system knowledge into the
[iterative analysis and design track](iterative-analysis-design.md) or the
[implementation and evolution track](implementation-evolution.md). Preserve the
source baseline, evidence status, confidence, authority, uncertainty, and
lifecycle. Stop when missing evidence would require invention.
