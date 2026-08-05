---
type: "Iteration Record"
title: "Iteration: Validate Requirements Synthesis and Playback"
description: "Validate that conflicting stakeholder evidence becomes traceable candidate and approved requirements without losing authority or entering software design."
id: "client-discovery-synthesis-e2"
phase: "elaboration"
status: "completed"
tags: ["iteration", "client-discovery", "requirements"]
---

# Iteration: Validate Requirements Synthesis and Playback

The elicitation iteration demonstrated that an agent can preserve contradictory
sponsor, operator, and compliance evidence without manufacturing requirements.
This iteration addresses the next risk: whether that evidence can become
inspectable requirements and examples while retaining source history,
validation state, and decision authority.

## Goal

- Produce and exercise the smallest deployable
  `requirements-synthesis-validation` skill that turns a bounded evidence set
  into source-linked candidate and approved requirements without designing
  software.

## Representative Slice

The evidence set contains a sponsor's dashboard request, an operator's observed
reconciliation workflow, and a compliance export rule. Playback evidence
clarifies that the shared outcome is reducing unresolved reconciliations, that
charts are not the deciding workflow, and that retention remains undecided.
The skill should:

1. preserve the three evidence sources and their different authority;
2. distinguish the requested dashboard from the underlying outcome;
3. synthesize source-linked goals, workflow, rules, constraints, scenarios,
   assumptions, examples, and open decisions;
4. record validation, rejection, approval, abstention, and conflict against the
   relevant role and artifact revision;
5. leave the retention rule candidate or contested because no authorized value
   exists; and
6. route accepted knowledge toward requirements owners without selecting
   architecture or implementation tasks.

## Risks Addressed

- Synthesis erases contradictory evidence or makes the original request appear
  inevitable.
- Agent confidence, stakeholder availability, or organizational seniority is
  mistaken for decision authority.
- Concrete examples silently introduce thresholds or business rules that no
  stakeholder approved.
- Validation state lacks revision history and becomes stale after later
  evidence or policy changes.
- The skill duplicates inception or use-case artifacts, or drifts into software
  design and implementation planning.

## Artifact Budget

- create: `docs/proposals/iterations/client-discovery-synthesis-e2.md` - future
  maintainers need the selected risk, closure evidence, and disposition history
  without turning the canonical proposal into a status log.
- create: `skills/requirements-synthesis-validation/SKILL.md` - no active skill
  owns evidence-to-requirements synthesis, playback, or approval history.
- keep with implementation:
  `evals/cases/requirements-synthesis-validation.json` and a disposable
  `evals/fixtures/requirements-synthesis/` fixture - executable routing and
  behavioral claims belong beside the skill.
- update: the active catalog, smallest appropriate profiles, client-to-code
  track, source provenance, usage guidance, and focused validation counts when
  the skill meets its exit criteria.
- defer: a standalone shared client-discovery model - link the elicitation
  record shape and keep requirement-state guidance local unless independent
  maintenance pressure appears during briefing integration.
- omit: standalone inception, use-case, domain, supplementary-requirement, and
  design documents; the behavioral brief can name their handoffs without
  creating downstream artifacts.

## Artifacts Consulted

- Client discovery proposal:
  `docs/proposals/client-discovery-skills.md`
- Elicitation skill and iteration record:
  `skills/stakeholder-requirements-elicitation/SKILL.md` and
  `docs/proposals/iterations/client-discovery-elicitation-e1.md`
- Recovery evidence vocabulary:
  `skills/reverse-engineer-software-system/references/recovery-evidence.md`
- Existing inception, use-case, domain, and artifact-selection guidance
- Skill evaluation contract: `evals/README.md`

## Decisions to Record

- Whether the evidence handoff is usable through linked skill guidance without
  extracting a second packaged shared reference.
- Whether validation and approval need separate states and authority fields.
- Whether the discovery brief should remain a cohesive artifact or be routed
  immediately into downstream requirements owners.
- Which routing or behavioral limitations require refinement before the skill
  becomes active.

## Trace

- Proposal `Representative Path` -> iteration `Representative Slice` ->
  `requirements-synthesis-validation` workflow -> behavioral case
  `synthesize-authority-aware-requirements`.

## Exit Criteria

- The skill consumes an identified evidence set and keeps every material
  candidate traceable to supporting and contradicting source IDs.
- Goals, workflows, rules, constraints, quality attributes, scenarios,
  assumptions, examples, decisions, and coverage limits remain distinguishable.
- Candidate, validated, approved, contested, and superseded states have clear
  meanings; validation and approval retain role, authority, revision, outcome,
  and history.
- The representative retention question remains visibly unresolved rather than
  receiving an invented value.
- The output routes accepted requirements knowledge without defining software
  architecture or implementation tasks.
- Routing cases distinguish this skill from elicitation, inception, use-case
  modeling, and implementation work.
- The disposable behavioral case passes mechanically; semantic expectations
  and prohibitions are reviewed from the preserved trace.
- `just validate` and `pytest -q` pass with all catalog, profile,
  documentation, and evaluation surfaces synchronized.

## Results

- Added and cataloged the deployable `requirements-synthesis-validation` skill.
  Its workflow preserves source evidence, distinguishes requested solutions from
  outcomes, shapes inspectable candidate requirements and examples, records
  revision-specific playback, and routes accepted knowledge without entering
  software design.
- Retained distinct `candidate`, `validated`, `approved`, `contested`, and
  `superseded` states. The behavioral result confirmed that validation and
  approval need separate authority fields: the operator could validate the
  workflow, the sponsor could approve the funded outcome, compliance could
  approve disclosure controls, and none could approve retention.
- Kept the discovery brief cohesive because downstream owners need its
  synthesis, validation history, conflicts, and open questions together. The
  skill still prefers updating existing canonical owners and routes accepted
  knowledge to inception, use cases, domain models, or supplementary
  requirements instead of duplicating them.
- Kept shared evidence guidance linked from the elicitation skill rather than
  adding another packaged shared reference. The handoff reused stable source
  fields successfully, while requirement-state and playback guidance has only
  one current owner.
- Added the skill to `all`, `iterative-design`, and the compatible
  `applying-uml-and-patterns` alias; no new profile was needed.
- `just validate` passed with 25 cataloged skills and 50 routing cases across 10
  case files. The behavioral evaluation
  `synthesize-authority-aware-requirements` passed mechanically within its
  declared mutation boundary. `pytest -q` passed all 29 repository tests in an
  isolated environment with the optional development dependency enabled.
- Manual review of the preserved behavioral trace found every declared semantic
  expectation and prohibition satisfied. The brief retained the dashboard
  request and its correction, linked each requirement to source evidence,
  applied authority-scoped validation and approval, left retention without an
  invented value, preserved conflicts, and stopped before design or
  implementation. These findings are review evidence, not mechanically graded
  results.

## Artifact Outcomes

- Started: `skills/requirements-synthesis-validation/SKILL.md`, its agent
  metadata, routing and behavioral case, the disposable
  `requirements-synthesis` fixture, and this iteration record.
- Refined: the active catalog, iterative-design profiles, client-to-code track,
  skill relationships, source provenance, user guidance, evaluation inventory,
  repository validation counts, and the proposal's iteration links.
- Unchanged: the proposal's responsibility boundary and normal downstream
  handoffs. Observed behavior supported separate evidence, validation, and
  approval states without adding a fourth skill.
- Deferred: a standalone shared client-discovery model until briefing creates
  independent ownership or maintenance pressure beyond link-level reuse.
- Omitted: downstream inception, use-case, domain, supplementary-requirement,
  design, and implementation artifacts; the behavioral brief named their
  handoffs without assuming responsibility for them.
