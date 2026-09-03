---
name: inception
description: Guides Unified Process inception for a project or independently sponsored initiative. Use when establishing high-level vision, business case, scope, feasibility, major risks, and an invest, pause, stop, or prerequisite decision before elaboration. Do not use to make a release, implementation phase, component, or completed milestone its own inception without an independent business case and decision authority.
---

# Inception

## Overview

Inception is a short decision phase for a project or independently sponsored
initiative. Establish a common vision, basic scope, and feasibility. Decide
whether to invest in elaboration, pause, stop, or obtain a material
prerequisite.

Do not use inception to define all requirements, make reliable plans or
estimates, or design the architecture. Do not make a release, implementation
phase, component, or completed milestone its own inception merely because it
has a name. Such work is evidence within the project or initiative boundary
unless it has its own business case and decision authority.

## Inception Boundary

Identify the project or independently sponsored initiative, its decision
authority, and the decision to make before creating artifacts. State the
product or system boundary, the intended outcome, and the investment question.

For an existing project that lacks inception, recover a project-level baseline
only when it informs a current investment decision. Treat releases, code, tests,
plans, and operational observations as evidence. Preserve their source and
revision, label reconstructed claims and missing authority, and do not present
inference as historical approval.

Route an approved release or implementation-phase objective through the
repository's planning or iterative-development process. Treat it as a separate
inception only when it has an independently approved business case, scope, and
go/no-go authority.

## When to Use

- Establishing or recovering the vision and business case for a project or
  independently sponsored initiative.
- Deciding whether the project or initiative merits investment beyond a
  discovery or proof-of-concept step.
- Estimating feasibility, including buy-versus-build, order-of-magnitude cost,
  and alignment with goals.
- Identifying primary actors, expected use cases, and risks that affect the
  investment decision.
- Setting up the development environment or adapting the UP Development Case
  for the project or initiative.
- Preparing the first elaboration iteration after an invest decision.
- Do not use for a release, implementation phase, component, or completed
  milestone without its own business case and decision authority.
- Do not use for detailed requirements, reliable plans or estimates, or
  architecture design; those belong in later work.

## Workflow

0. **Set the Inception Boundary.** Identify the project or independent
   initiative, decision authority, investment question, and relationship of any
   existing releases or proof points to that boundary. Stop for the responsible
   authority if the boundary or decision is unknown.
1. **Establish the Vision and Business Case.** Define high-level goals, key
   constraints, and business justification.
2. **Determine Feasibility.** Evaluate technical feasibility, buy-versus-build
   alternatives, and order-of-magnitude cost ranges. Record unknown evidence
   instead of inventing an assessment.
3. **Identify System Scope and Actors.** List primary actors and expected use
   cases. Detail approximately 10-20% of use cases when that sample validates
   scope; otherwise detail the smallest representative scenario set that does.
4. **Identify Critical Non-Functional Requirements.** Capture the quality,
   operational, regulatory, or other constraints with major architectural
   impact.
5. **Establish Glossary and Key Terminology.** Capture the terms that must have
   one shared meaning for the decision.
6. **Construct the Risk List.** Identify major technical, business, resource,
   and schedule risks, with mitigation or an explicit decision owner.
7. **Build Proof-of-Concepts.** Create low-fidelity prototypes or run focused
   experiments only for show-stopper technical questions.
8. **Obtain and Record the Investment Decision.** Record an
   authority-approved outcome and its evidence revision: invest in elaboration,
   pause, or stop. If the authority or evidence is unavailable, return `needs
   prerequisite` instead. For an approved invest decision, define the first
   elaboration iteration and a low-precision effort range. Do not manufacture a
   plan when the decision is not to invest.
9. **Define the Development Case After an Approved Invest Outcome.** Adapt the
   UP activities and selected artifacts to the project's scale and constraints.

## File Output

Before creating a new document, apply
[Artifact Selection Budget](../select-technical-artifacts/references/artifact-selection-budget.md).
Establish the required knowledge without treating the UP artifact names as a
mandatory document inventory. Prefer an existing owner or one aggregate
inception artifact when it has the same consumer and lifecycle. Create separate
artifacts only when their value, ownership, and lifecycle differ.

When persisting an inception artifact as a standalone Markdown file, follow
[Markdown Artifact Frontmatter](../iterative-risk-driven-development/references/markdown-artifact-frontmatter.md)
and use STE-style. Use an artifact-specific type (`Vision`, `Business Case`,
`Risk List`, `Development Case`, `Phase Plan`, and so on), not a generic
`Inception` type. Put identity, summary, and lifecycle metadata in frontmatter
and keep scope, assumptions, analysis, and evidence in the body. For one
aggregate inception file, describe the aggregate once in file-level frontmatter
and do not add nested frontmatter between sections.

For a recovered baseline, identify the evidence source and revision, the
approval state, material unknowns, and the responsible prerequisite. Do not
convert implemented behavior or retrospective inference into approved intent.

## Decision Outcome

Return the smallest useful decision record. State:

- the project or initiative boundary, authority, and investment question;
- established evidence, assumptions, and material unknowns;
- the minimal scope, actors, quality constraints, and risks that affect the
  decision;
- one outcome: `invest`, `pause`, `stop`, or `needs prerequisite`, with the
  approving authority and evidence revision for any decision; and
- the next owner or first elaboration iteration only when the outcome supports
  it.

## Red Flags

- Treating a release, implementation phase, component, or completed milestone
  as the project inception without an independent business case and authority.
- Recovering a past decision from code or tests and presenting it as approved.
- Inception lasting more than a few weeks.
- Attempting to define most requirements.
- Expecting project plans or estimates to be reliable.
- Defining the architecture, which should be done iteratively in Elaboration.
- Requiring a separate document for every UP artifact name.
- Writing all use cases in detail or writing no representative scenario.
- Believing that requirements, architecture, and implementation must occur in
  one fixed sequence.

## Verification

- [ ] The project or independent-initiative boundary, decision authority, and
      investment question are explicit.
- [ ] Releases, phases, components, and completed milestones are treated as
      evidence unless each has its own business case and go/no-go authority.
- [ ] The vision, business case, and basic feasibility are established or their
      material evidence gaps are explicit.
- [ ] Primary actors, expected use cases, and a representative detailed
      scenario set validate the proposed scope.
- [ ] Critical quality constraints and major technical, business, resource, and
      schedule risks are established with mitigation or a decision owner.
- [ ] Any proof-of-concept addresses a named show-stopper question.
- [ ] One outcome is explicit: invest, pause, stop, or needs prerequisite.
      Invest, pause, and stop cite the approving authority and evidence
      revision; missing approval or evidence returns needs prerequisite.
- [ ] An approved invest outcome has a first elaboration iteration,
      low-precision effort range, and development case proportionate to the
      project.
- [ ] Selected artifacts pass the artifact budget. No document exists only to
      satisfy a methodology checklist.
- [ ] Recovered material distinguishes source evidence, reconstruction,
      approval state, and unknown authority.
- [ ] Reader-facing artifacts explain the opportunity, decision, and important
      consequence before detailed scope or evidence.
- [ ] Every standalone Markdown artifact has frontmatter appropriate to its
      artifact type.
