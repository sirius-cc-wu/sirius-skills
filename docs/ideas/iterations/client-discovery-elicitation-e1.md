---
type: "Iteration Record"
title: "Iteration: Validate Stakeholder Evidence Elicitation"
description: "Validate that stakeholder evidence can be acquired and preserved without prematurely becoming requirements or design."
id: "client-discovery-elicitation-e1"
phase: "elaboration"
status: "completed"
tags: ["iteration", "client-discovery", "requirements"]
---

# Iteration: Validate Stakeholder Evidence Elicitation

The client-discovery proposal has established the capability scope and the
three intended skill boundaries. This elaboration iteration addresses the
largest remaining risk before building the rest of the family: whether an
agent can gather conflicting stakeholder evidence neutrally, preserve its
origin and sensitivity, and stop before synthesis or software design.

## Goal

- Produce and exercise the smallest deployable
  `stakeholder-requirements-elicitation` skill that preserves contradictory
  stakeholder evidence without converting it into requirements.

## Representative Slice

A sponsor requests a dashboard, an operator describes a manual reconciliation
workflow, and a compliance source prohibits exporting some records. The skill
should:

1. identify the represented and missing stakeholder roles and their decision
   authority;
2. establish consent and intended use before directing evidence capture;
3. record the request, observed workflow, and policy constraint as distinct
   sources with opaque IDs and evidence status;
4. keep agent hypotheses separate from participant statements and
   observations;
5. expose the conflict, coverage gaps, sensitivity, and open questions; and
6. stop with evidence records and an elicitation result rather than candidate
   requirements, acceptance criteria, architecture, or implementation tasks.

If a material role is unavailable or sensitive evidence cannot be retained or
published safely, the skill should report the limitation and stop rather than
claiming sufficient coverage.

## Risks Addressed

- Leading questions or agent guesses contaminate stakeholder evidence.
- A sponsor is treated as a proxy for operators, end users, support, or
  compliance.
- The shared evidence model is too heavy for ordinary work or too weak for the
  downstream synthesis skill.
- Confidential source material leaks into repository-visible artifacts or
  external services.
- The skill drifts into requirements synthesis, use-case modeling, solution
  design, or implementation planning.

## Artifact Budget

- create: `docs/ideas/iterations/client-discovery-elicitation-e1.md` -
  future skill authors and reviewers need a historical record of the selected
  risk, scope, exit criteria, and results; the canonical proposal cannot own
  iteration closure independently.
- create: `skills/stakeholder-requirements-elicitation/SKILL.md` - users need an
  independently deployable evidence-acquisition workflow, and no active skill
  owns this responsibility.
- keep with implementation:
  `evals/cases/stakeholder-requirements-elicitation.json` and a disposable
  `evals/fixtures/stakeholder-discovery/` fixture - routing and behavioral
  claims belong with executable evaluation evidence.
- update: `docs/ideas/client-discovery-skills.md` and
  `catalog/tracks/client-to-code.md` - refine the canonical direction and
  handoff only when iteration evidence changes them.
- update: `catalog/skills.md`, `skill-sets/all.txt`, the smallest applicable
  user-facing profile, and repository usage documentation - required only when
  the skill satisfies the exit criteria and becomes deployable.
- defer: a standalone shared evidence-model reference - keep the minimum shape
  in the first skill until a second skill demonstrates independent reuse and
  lifecycle pressure.
- omit: standalone use-case, domain-model, SSD, contract, and design documents
  for this interaction-only iteration; the representative scenario and
  behavioral fixture are sufficient owners.

## Artifacts to Start

- `stakeholder-requirements-elicitation`:
  `skills/stakeholder-requirements-elicitation/SKILL.md` - implement the bounded
  elicitation workflow and its explicit stop conditions.
- Routing and behavioral case:
  `evals/cases/stakeholder-requirements-elicitation.json` - distinguish the
  skill from inception, use-case modeling, synthesis, and implementation work.
- Disposable stakeholder-discovery fixture:
  `evals/fixtures/stakeholder-discovery/` - provide sponsor, operator, and
  compliance sources whose tensions can be checked without contacting real
  people or external systems.

## Artifacts to Refine

- Client discovery idea:
  `docs/ideas/client-discovery-skills.md` - refine only when observed skill
  behavior changes a responsibility, evidence field, safeguard, or handoff.
- Client-to-code track: `catalog/tracks/client-to-code.md` - refine only when the
  normal handoff differs from the proposed sequence.

## Artifacts Consulted

- Client discovery idea:
  `docs/ideas/client-discovery-skills.md`
- Agent-skill repository comparison:
  `catalog/agent-skill-repository-structures.md`
- Recovery evidence vocabulary:
  `skills/reverse-engineer-software-system/references/recovery-evidence.md`
- Skill evaluation contract: `evals/README.md`

## Decisions to Record

- Whether the minimum evidence shape is usable without a standalone shared
  reference.
- Whether evidence capture and stakeholder analysis remain cohesive enough for
  one skill.
- Whether the skill belongs in `iterative-design` in addition to `all`, without
  creating a new mandatory client-discovery profile.
- Which behavioral limitations require a second iteration before the skill is
  cataloged as active.

## Trace

- Proposal `Representative Path` -> iteration `Representative Slice` ->
  `stakeholder-requirements-elicitation` workflow -> behavioral case
  `preserve-contradictory-stakeholder-evidence`.

## Exit Criteria

- The skill produces a stakeholder map or coverage statement, an elicitation
  plan, source-linked evidence records, conflicts, and open questions for the
  representative slice.
- Statements, observations, repository facts, and agent inferences remain
  distinguishable and use the repository evidence vocabulary where it fits.
- Neutral questioning, consent, sensitivity, retention, and publication rules
  are explicit and actionable.
- Missing material stakeholders and unresolved contradictory evidence trigger
  a visible stop or limitation rather than false completeness.
- The output contains no synthesized requirements, acceptance criteria,
  architecture, or implementation plan.
- Routing cases distinguish this skill from `inception`, `use-case-modeling`,
  and downstream implementation skills.
- The disposable behavioral case completes mechanically within its declared
  mutation boundary; semantic expectations and prohibitions are reviewed from
  the preserved trace rather than reported as mechanically proven.
- `just validate` and `pytest -q` pass with the new skill, catalog, profile,
  documentation, and evaluation surfaces synchronized.

## Results

- Added and cataloged the deployable `stakeholder-requirements-elicitation`
  skill. Its workflow covers stakeholder coverage, authority, consent,
  sensitivity, neutral inquiry, source-linked evidence, contradictions, and
  explicit stop conditions without synthesizing requirements or design.
- Kept the minimum evidence-record shape in the skill rather than creating a
  shared reference. The shape was sufficient for the representative slice;
  independent reuse will be tested by the synthesis iteration before extracting
  it.
- Kept stakeholder analysis and evidence capture cohesive. The stakeholder map
  determines whose evidence is needed and under what authority, so separating
  it would add a handoff before useful evidence exists.
- Added the skill to `all`, `iterative-design`, and the compatible
  `applying-uml-and-patterns` alias. No new client-discovery profile is needed
  while the capability family is incomplete.
- Clarified the existing `recover-system-behavior` routing description after
  its implementation-and-runtime evidence responsibility overlapped with the
  new stakeholder-evidence description.
- `just validate` passed with 24 cataloged skills and 45 routing cases across 9
  case files. The behavioral evaluation
  `preserve-contradictory-stakeholder-evidence` passed its mechanical checks
  within the declared mutation boundary.
- `pytest -q` passed all 29 repository tests in an isolated environment with
  the optional development dependency enabled.
- Manual review of the preserved behavioral trace found every declared semantic
  expectation and prohibition satisfied: the output separated sponsor,
  operator, and compliance evidence; omitted the private identity; retained
  authority and publication limits; exposed conflicts and missing roles; kept
  inference separate; stopped before requirements, design, or implementation;
  and proposed proportionate follow-up elicitation. These semantic findings are
  review evidence, not mechanically graded results.

## Artifact Outcomes

- Started: `skills/stakeholder-requirements-elicitation/SKILL.md`, its agent
  metadata, routing and behavioral cases, and the disposable
  `stakeholder-discovery` fixture.
- Refined: the active catalog, iterative-design profiles, client-to-code track,
  skill relationships, source provenance, user guidance, evaluation inventory,
  and repository validation counts.
- Unchanged: the canonical proposal's responsibility boundaries and handoff.
  Observed behavior supported the proposed direction without requiring a scope
  change.
- Deferred: a standalone shared evidence-model reference until the synthesis
  skill demonstrates a second owner and concrete lifecycle pressure.
- Omitted: use-case, domain, design, and implementation artifacts; the bounded
  interaction produced no evidence that they were needed in this iteration.
