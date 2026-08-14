---
type: "Iteration Record"
title: "Iteration: Validate Implementation Slice Briefing"
description: "Validate that approved requirements and downstream artifacts can become a bounded coding-agent brief without inventing missing decisions."
id: "client-discovery-briefing-e3"
phase: "elaboration"
status: "completed"
tags: ["iteration", "client-discovery", "implementation"]
---

# Iteration: Validate Implementation Slice Briefing

The first two iterations established source-linked stakeholder evidence and
authority-aware requirements validation. This iteration addresses the final
skill risk: whether an agent can select a coherent ready slice, combine only its
approved sources and verified repository context, and keep unresolved feature
work out of an implementation handoff.

## Goal

- Produce and exercise the smallest deployable `implementation-slice-briefing`
  skill that creates a coding-agent-ready vertical slice from approved inputs
  without inventing behavior, acceptance conditions, or architecture.

## Representative Slice

Approved requirements and analysis describe recognizing two differently
formatted opaque account references as one reconciliation item without
disclosing protected attributes. An approved design decision identifies the
existing matching boundary, and repository evidence identifies current tests
and commands. Queue persistence is related feature work, but its retention rule
remains candidate and cannot enter the slice.

The skill should:

1. fix the brief to exact source and repository revisions;
2. select the actor-visible matching outcome rather than a layer-only task;
3. preserve the approved example, failure behavior, disclosure constraint,
   non-goals, and existing design boundary without strengthening them;
4. keep repository facts distinct from client requirements and inference;
5. trace every expectation to an approved source and authority;
6. exclude queue persistence and make the missing retention decision a coding-
   agent stop condition; and
7. hand off verification expectations without changing code or claiming tests
   were run.

## Risks Addressed

- A feature-sized bundle is mislabeled as one implementation slice.
- Candidate or contested material enters implementation as if approved.
- Repository behavior is mistaken for stakeholder intent.
- The brief invents acceptance criteria, thresholds, interfaces, schemas, or
  architecture to appear executable.
- Source changes leave an apparently ready brief stale.
- The briefing step performs implementation instead of packaging its oracle.

## Artifact Budget

- create: `docs/ideas/iterations/client-discovery-briefing-e3.md` - the
  selected risk, readiness decisions, and results need a historical owner.
- create: `skills/implementation-slice-briefing/SKILL.md` - no active skill owns
  slice selection, source-baseline freshness, and coding-agent handoff.
- keep with implementation: `evals/cases/implementation-slice-briefing.json`
  and `evals/fixtures/implementation-slice-briefing/` - routing and behavioral
  evidence belong beside the deployable skill.
- update: active catalog, profiles, client-to-code track, source provenance,
  usage guidance, proposal iteration links, and focused validation counts when
  the skill passes its exit criteria.
- defer: a separate traceability schema or shared client-discovery reference;
  first test whether explicit source baselines and tables inside each owning
  artifact remain sufficient.
- omit: production code, tests, migrations, and new design artifacts; the
  behavioral fixture already supplies the approved inputs needed to evaluate
  briefing.

## Artifacts Consulted

- Client discovery idea and completed elicitation and synthesis records
- `requirements-synthesis-validation`, `use-case-modeling`,
  `operation-contracts`, `use-case-realization`, and
  `test-driven-implementation`
- Artifact-selection, frontmatter, and readability guidance
- Skill evaluation contract: `evals/README.md`

## Decisions to Record

- Which readiness checks distinguish a vertical slice from a convenient
  technical layer.
- Whether one brief can keep requirements, design inputs, and repository facts
  distinct without a standalone traceability artifact.
- Whether excluded candidate requirements remain sufficiently visible as stop
  conditions without weakening the ready slice.
- Which normal handoff or routing boundaries require adjustment before the
  client-discovery family is complete.

## Trace

- Proposal `What an Agent-Ready Brief Should Contain` -> iteration
  `Representative Slice` -> `implementation-slice-briefing` readiness gate ->
  behavioral case `brief-only-the-approved-ready-slice`.

## Exit Criteria

- The selected slice has one testable actor or business outcome and is smaller
  than the related feature without becoming layer-only.
- Every in-scope expectation traces to an approved source, exact revision,
  status, and appropriate authority.
- Candidate retention work remains excluded and appears as a concrete stop
  condition; no value or architecture is invented.
- Repository facts are revision-fixed and separate from intended behavior and
  inference.
- The brief packages existing design inputs and verification commands without
  changing code or claiming unexecuted results.
- Routing distinguishes briefing from requirements synthesis, iterative
  planning, design, and test-driven implementation.
- The disposable behavioral case passes mechanically; semantic expectations
  and prohibitions are reviewed from the preserved trace.
- `just validate` and `pytest -q` pass with catalog, profiles, documentation,
  and evaluations synchronized.

## Results

- Added and cataloged the deployable `implementation-slice-briefing` skill. Its
  readiness gate requires an approved outcome, necessary success and failure
  behavior, rules, constraints, design inputs, exact source states, and a
  revision-fixed repository baseline before a slice can be marked ready.
- Defined a vertical slice as a coherent actor-visible or business-visible
  outcome with its necessary failure behavior and constraints. The behavioral
  result selected opaque-reference matching, not a technical layer or the whole
  reconciliation feature.
- Kept requirements, design inputs, and repository facts distinct inside one
  brief using a source baseline and expectation-level traceability table. This
  was sufficient without a separate traceability artifact or shared schema.
- Kept candidate retention work visible as an exclusion, dependency, and
  coding-agent stop condition. The ready matching slice remained useful without
  requiring or inventing persistence behavior.
- Added the skill to `all`, `iterative-design`, and the compatible
  `applying-uml-and-patterns` alias; the client-discovery family needs no new
  mandatory profile.
- `just validate` passed with 26 cataloged skills and 55 routing cases across 11
  case files. The behavioral evaluation
  `brief-only-the-approved-ready-slice` passed mechanically within its declared
  mutation boundary. `pytest -q` passed all 29 repository tests in an isolated
  environment with the optional development dependency enabled.
- Manual review of the preserved behavioral trace found every declared semantic
  expectation and prohibition satisfied. The brief fixed the requirements,
  use-case, design, policy, and repository baselines; traced every expectation;
  separated repository facts; excluded queue persistence; named retention and
  source changes as stops; changed no code; and explicitly reported the
  packaged commands as unexecuted. These findings are review evidence, not
  mechanically graded results.

## Artifact Outcomes

- Started: `skills/implementation-slice-briefing/SKILL.md`, its agent metadata,
  routing and behavioral case, the disposable
  `implementation-slice-briefing` fixture, and this iteration record.
- Refined: the active catalog, iterative-design profiles, client-to-code track,
  skill relationships, source provenance, usage guidance, evaluation inventory,
  repository validation counts, and proposal iteration links.
- Unchanged: the proposed three-skill responsibility boundary. The behavioral
  evidence supported briefing as a packaging and freshness responsibility
  distinct from requirements synthesis and implementation.
- Deferred: a standalone shared client-discovery or traceability model; explicit
  linked fields in each owning artifact remain sufficient across all three
  skills.
- Omitted: production code, test changes, migrations, and new architecture. The
  fixture's approved source and existing design boundary supplied everything
  needed for a ready brief.
