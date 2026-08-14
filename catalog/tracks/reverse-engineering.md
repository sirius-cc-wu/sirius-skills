# Reverse Engineering

Use this track when an existing system must be understood before maintenance,
migration, modernization, audit, onboarding, resumed development, or
redocumentation.

When externally prepared requirements or proposals contain unevidenced claims
about the current system,
[`assess-development-input`](../../skills/assess-development-input/SKILL.md)
may route them here before those claims are used as intended behavior or
implementation inputs.

## Sequence

1. [`reverse-engineer-software-system`](../../skills/reverse-engineer-software-system/SKILL.md)
   states the decision, fixes the revision and scope, selects evidence
   perspectives, and coordinates a risk-sized recovery iteration.
2. [`survey-existing-system`](../../skills/survey-existing-system/SKILL.md)
   maps governance, manifests, entry points, interfaces, dependencies, state,
   verification surfaces, documentation, and priority recovery slices.
3. [`recover-system-behavior`](../../skills/recover-system-behavior/SKILL.md)
   recovers black-box scenarios, failures, effects, and externally visible
   constraints when the decision depends on current behavior.
4. [`reconstruct-software-architecture`](../../skills/reconstruct-software-architecture/SKILL.md)
   reconstructs only the module, component, runtime, state, deployment, data,
   or trust-boundary views required by the decision.
5. [`reconcile-recovered-design`](../../skills/reconcile-recovered-design/SKILL.md)
   compares the recovered account with executed tests, runtime observations,
   documentation, accepted decisions, and history when those perspectives may
   disagree.
6. Feed stakeholder-validated behavior and design knowledge into the
   [iterative analysis and design track](iterative-analysis-design.md), or use
   the [implementation and evolution track](implementation-evolution.md) when
   a safely bounded change is already justified.

## Recorded Decision Discovery

Use
[`record-architecture-decision`](../../skills/record-architecture-decision/SKILL.md)
in read-only mode when the investigation needs to identify which ADRs currently
govern a product, subsystem, or concern. Follow supersession links and preserve
proposed, accepted, and historical states. An ADR is evidence of a recorded
choice and rationale at its revision; it does not prove that current code still
conforms. Missing ADRs do not authorize inferring undocumented decisions from
implementation.

## Evidence Rule

Every material claim identifies its perspective, status, confidence, temporal
status, and locator using the shared
[Recovery Evidence and Confidence](../../skills/reverse-engineer-software-system/references/recovery-evidence.md)
vocabulary.

Recovered artifacts describe a fixed revision. They do not become intended
requirements merely because they match current code or tests.

Write recovered artifacts in STE-style from the owning recovery skill while
preserving evidence, confidence, temporal status, and residual uncertainty.

## Selection Rule

Do not execute every skill at full depth. A first-contact onboarding question
may stop after the survey. A behavior-preserving migration may require behavior
recovery and architecture reconstruction. Documentation drift requires
reconciliation. Use
[`select-technical-artifacts`](../../skills/select-technical-artifacts/SKILL.md)
when the recovered artifact set itself is a material question. Apply its
[Artifact Selection Budget](../../skills/select-technical-artifacts/references/artifact-selection-budget.md)
locally before splitting recovered evidence into another standalone document.
When a
justified recovered artifact has no obvious home, several paths compete, or a
migration must preserve links and history, use
[`design-repository-artifact-layout`](../../skills/design-repository-artifact-layout/SKILL.md)
for that placement decision. Close each iteration when the original decision
has enough evidence, and expose any residual uncertainty.
