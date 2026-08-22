---
type: "Capability Proposal"
title: "Skill Evaluation Program"
description: "Records the implemented routing, behavioral, semantic, and composition evaluation pilot for Sirius skills."
status: "implemented"
tags: [evaluation, skills, quality]
---

# Skill Evaluation Program

The bounded pilot is implemented and owned by
[`evals/`](../../evals/README.md). It combines free deterministic routing checks
with explicitly selected Codex runs in disposable repositories. Those runs
capture traces, workspace changes, verification, model metadata, usage, and the
final response without treating missing metadata as known.

The current three fixture-backed cases exercise boundary-sensitive Rust
refactoring design, a focused class view, and a declarative operation contract
added to an existing analysis aggregate. Repeated runs can report mechanical,
mutation, environment, duration, and usage stability. The separate read-only
semantic judge remains available for future reviewed rubric cases, but remains
diagnostic and non-gating.

## At a Glance

Sirius verifies repository structure, installation profiles, shared references,
artifact guidance, and packaging behavior on every normal validation run. Its
opt-in behavioral runner also executes a coding agent in disposable fixtures to
observe whether a selected skill respects its boundary and produces the
mechanically checkable parts of the intended behavior.

The program adds three capabilities:

1. free catalog-routing and boundary evals;
2. model-executed behavioral trace evals in disposable repositories; and
3. composition evals for conditional feedback and documentation restraint.

This is repository verification infrastructure, not a deployable skill. The
pilot is intentionally selective: deterministic routing stays in normal
validation, while paid behavioral and semantic checks run only when selected.

## Decision and Operating Policy

Keep the pilot as the repository's evaluation foundation, with these limits:

- run routing checks in `just validate`;
- run affected fixture-backed behavioral cases on demand before consequential
  skill-boundary changes;
- keep semantic judging and judge-model comparison opt-in and non-gating;
- retain large traces and results as ignored local or CI artifacts rather than
  committed documentation; and
- add coverage when a real failure mode or material skill-boundary change
  justifies it, not to reach a catalog-wide percentage.

Do not add mandatory paid CI, broad multi-host support, or a rubric for every
case without new evidence that its diagnostic value exceeds its cost and
variance.

## Representative Scenario

The initial representative scenario used a small, well-specified bug fix. The
coding agent had to use an existing test and the repository-native
implementation workflow, change only code and tests, and avoid starting an
analysis-and-design workflow or producing new documents.

That implementation eval failed if the agent:

- routes the task through the complete iterative-design track;
- invents missing business intent;
- creates use-case, contract, or UML files without a durable need;
- changes valid tests to accept the defect; or
- mutates files outside the authorized fixture scope.

A complementary scenario confirmed that feedback was not suppressed: when an
approved cancellation policy introduced the durable `CancellationReason`
concept, the agent had to refine the existing canonical domain model rather
than ignore the discrepancy or create a competing model.

The third scenario supplied two incompatible approved policies with equal
authority. The agent had to preserve the repository, report the conflict, and
ask which policy governed rather than converting uncertainty into code, tests,
or a new decision document. These three implementation scenarios were retired
with their owning skill package. They remain part of the pilot rationale, not
current runnable cases.

The contract scenario supplies approved effects for a non-trivial system
operation. The agent should add one declarative operation contract to the
existing feature-analysis aggregate, cover every approved effect, and avoid
creating implementation objects, code, tests, or a competing document.

Together, these scenarios test the central Sirius claim: coding agents retain
local autonomy while durable knowledge is reconciled when material evidence
changes it.

## Pilot Evidence and Remaining Limits

At initial closure, the implemented checks established more than packaging
consistency:

- 12 routing case files exercised 60 positive and owned-negative routes across
  the then-active 26-skill catalog;
- disposable fixtures enforced mutation allowlists, required changes,
  verification commands, output fragments, and selected trace ordering;
- a red–mutation–green fixture proved its seeded initial failure before an
  agent changed production code;
- composition fixtures distinguished local correction, canonical
  reconciliation, workflow re-entry, focused visual design, and contract-driven
  analysis without artifact proliferation; and
- reviewed semantic controls exercised passing and failing rubric polarity,
  repetition, and cross-model disagreement reporting.

The current pilot retains 13 routing case files across the 19-skill catalog
and three fixture-backed behavioral cases. Six active skills
have no dedicated routing case. Lexical routing remains only a description
tripwire, and behavioral coverage remains selective. The live pilot uses one
agent host; repeated agreement cannot prove semantic correctness, cross-host
portability, or freedom from shared model bias. No active case has a semantic
rubric. Mechanical assertions can verify required concepts and boundaries, but
not whether prose or diagrams are maximally clear. Usage reporting does not estimate price, and local ignored
results are not a permanent reviewed baseline.

The [repository comparison](../../catalog/agent-skill-repository-structures.md)
shows two useful precedents. Addy Osmani's collection emphasizes inexpensive
catalog routing with optional behavioral traces. Garry Tan's gstack adds
hermetic agent execution, LLM judging, cost controls, and extensive runtime
coverage. Sirius should borrow the smallest useful ideas from each rather than
copy either system wholesale.

## Goals and Non-Goals

### Goals

- Detect skill descriptions that miss realistic user vocabulary or overlap a
  neighboring responsibility.
- Detect violations of skill boundaries, authority, and mutation scope.
- Verify outcomes from tool traces and workspace state, not final prose alone.
- Detect workflow overreach and unnecessary artifact creation explicitly.
- Preserve enough run metadata to compare results across skill, host, model,
  and prompt revisions.
- Add paid or nondeterministic checks only after free checks have reached their
  limit.

### Non-Goals

- Recreate gstack's multi-host runtime and observability platform.
- Require every skill to receive behavioral coverage before the pilot is
  useful.
- Gate every pull request on paid model execution.
- Judge exact wording, formatting preferences, or diagram aesthetics as a
  substitute for behavior.
- Treat lexical routing scores as proof of model selection.
- Introduce a deployable `skill-evaluation` skill.

## Evaluation Model

| Level | Question | Mechanism | Execution |
|---|---|---|---|
| Existing repository checks | Is the catalog structurally consistent and installable? | Shell validation and Python tests | Every change |
| Catalog routing | Can realistic prompts distinguish a skill from its neighbors and non-applicable cases? | Deterministic case files, ranking, collision, and coverage checks | Every change |
| Behavioral trace | Does an agent perform the skill and respect its boundary in a controlled repository? | Disposable fixture, captured tool trace, commands, and workspace diff | On demand for affected cases |
| Composition and feedback | Does the agent select the smallest sufficient workflow and reconcile durable knowledge conditionally? | Multi-skill scenarios with required and forbidden paths | Periodic or before consequential workflow changes |

### 1. Catalog Routing and Boundary Evals

Store one case file per evaluated skill under `evals/cases/`. Each case may
contain:

- positive prompts expressed as users would naturally ask;
- negative prompts owned by a neighboring skill;
- boundary prompts where the skill should not run;
- expected ranking tolerance; and
- the skill revision or case-schema version when needed for diagnosis.

The runner is deterministic, dependency-light, and CI-safe. Its transparent
lexical ranker is a description-quality tripwire; reports state that it
approximates routing rather than observing an agent host.

The runner should detect:

- missing or malformed cases;
- positive prompts with no meaningful description match;
- negative prompts where the wrong skill outranks the declared owner;
- near-duplicate descriptions; and
- changes in rank-one and top-k results without turning one aggregate score
  into the only quality gate.

### 2. Behavioral Trace Evals

Run one explicitly selected agent host and model inside a disposable fixture
repository. Capture:

- the exact prompt, skill revision, host, model, and model version;
- tool calls and their ordering;
- commands, exit status, and relevant output;
- files created, modified, or deleted;
- the final repository diff;
- elapsed time and reported token usage when available; and
- the final response directly in each result as supporting evidence, not the
  primary oracle.

Prefer deterministic assertions for observable facts. Use an LLM judge only
for semantic expectations that cannot be checked mechanically, and never as
the sole authority for mutation safety or command results.

The initial judge is an on-demand diagnostic layer, not a gate. Each criterion
has a stable opaque ID, boolean verdict, and reason. The judge sees the task
context, rubric, and captured final response in an isolated empty repository;
it does not inspect the evaluated workspace. Its trace, model metadata, usage,
and errors remain separate from the primary execution evidence.

Calibration controls exercise the same prompt against reviewed good and bad
responses, with an expected boolean for each rubric criterion. A standalone
calibration command records each trace and reports mismatches without running
the coding agent or changing behavioral mechanical outcomes. Repeated controls
report complete-verdict stability, match rates, duration, and aggregate token
usage. Matching repetitions establish only basic polarity and short-run
consistency for the selected judge. Cross-model runs retain each calibration
and report criterion-level disagreement, duration, and per-model token usage;
agreement still does not establish broad accuracy.

The case shape includes:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": "bounded-change",
      "prompt": "Complete the bounded change in this fixture.",
      "fixture": "example-fixture",
      "expected_output": "The requested outcome is verified.",
      "expectations": [
        "The expected repository state is present",
        "The declared verification command passes"
      ],
      "prohibitions": [
        "Do not mutate files outside the authorized scope"
      ],
      "allowed_mutations": ["src/**", "tests/**"]
    }
  ]
}
```

Fixture-backed behavioral cases include a seeded initial failure, approved
negative example, read-only boundary, or other mechanically detectable
violation appropriate to the behavior they claim to detect.

### 3. Composition and Feedback Evals

Composition cases should target Sirius's highest-risk orchestration claims:

| Scenario | Expected behavior | Failure to detect |
|---|---|---|
| Small bug with a clear oracle | Stay with implementation and executable evidence | Mandatory analysis chain or new design documents |
| Non-trivial state change | Use or refine a contract when postconditions are genuinely needed | Guessing effects or writing contracts for trivial operations |
| Missing durable concept exposed by implementation or a contract | Refine the canonical domain model | Ignore the gap or create a competing model |
| Local implementation detail | Keep the information with code and tests | Update unrelated durable artifacts |
| Durable responsibility or interface change | Refine the owning realization or design model | Leave canonical design knowledge stale |
| Recovered surprising behavior | Preserve the distinction between current behavior and intended requirements | Declare current code authoritative for intent |
| Reconciliation with unknown intent | Recommend the smallest authoritative next action | Silently change code, tests, or documentation |

These cases should distinguish three outcomes:

1. **Local correction:** the active skill handles the issue without another
   skill invocation or document.
2. **Canonical reconciliation:** an existing artifact is updated because its
   durable knowledge changed.
3. **Workflow re-entry:** another skill or the user is needed because the
   discovery exceeds the active skill's authority or requires substantial
   specialized analysis.

## Pilot Scope

The active pilot retains three original skill areas that represent distinct
failure risks, plus the later-added `operation-contracts` coverage for the
remaining contract-driven composition risk:

| Skill | Risk exercised |
|---|---|
| `iterative-risk-driven-development` | Selecting and executing risk-driven analysis, design, implementation, and verification without enforcing a lifecycle waterfall |
| `use-case-modeling` | Preserving the black-box boundary and avoiding internal design |
| `uml-class-diagram-design` | Producing a focused class view only when type responsibilities and relationships justify it |
| `operation-contracts` | Refining one canonical analysis aggregate with declarative state effects without adding implementation design or duplicate artifacts |

Do not expand to all skills merely to reach a coverage percentage. Expand when
the pilot schema and runner reliably detect seeded routing, behavior, and
authority failures.

## Measures and Reporting

Report individual signals rather than one opaque quality score:

- positive rank-one and top-k routing rates;
- negative-owner and boundary violation rates;
- behavioral expectation and prohibition results;
- task completion and verification results;
- unauthorized mutation rate;
- workflow-overreach and unnecessary-artifact rates;
- repeatability across identical runs;
- duration and reported token usage; and
- changes from a named baseline run.

Persist large transcripts and run results as CI or local artifacts by default,
not as committed repository documentation. Commit only small fixtures, case
definitions, evaluator code, and deliberately reviewed baselines.

## Staged Adoption Result

### Stage 1: Routing Cases — Completed

- Defined the case schema and implemented the free deterministic runner.
- Exercised description-collision and missing-vocabulary failures in tests.
- Added the routing tier to normal repository validation.

### Stage 2: Behavioral Discrimination — Completed for the Pilot

- Selected the locally authenticated Codex CLI as the recorded host.
- Built disposable fixtures for representative risks rather than every skill.
- Added deterministic trace, diff, mutation, file, and command assertions
  before adding semantic judging.
- Exercised seeded failures, prohibited mutations, and workflow overreach.
- Added repeated-run summaries for mechanical, mutation, environment, duration,
  and reported-token stability.

### Stage 3: Composition — Completed for the Pilot

- Retired implementation-feedback and authority-reentry cases with their owning
  skill package.
- Retained focused visual-design cases and a contract-driven case that refines a
  canonical aggregate without implementation or artifact proliferation.

### Stage 4: Expansion Decision — Keep Coverage Risk-Driven

The runner catches actionable routing and authority defects, seeded behavioral
failures are diagnosable from recorded evidence, and repeated runs expose
rather than hide nondeterminism. That is sufficient to retain the
infrastructure. It is not sufficient to justify paid gating or blanket
catalog-wide fixtures. Expansion remains an affected-case decision based on
real usage failures and consequential boundary changes.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Evals reward exact prose instead of correct behavior | Assert tool traces, commands, and workspace state first |
| Model variance creates flaky gates | Keep paid runs out of required CI; repeat and report distributions |
| Lexical routing is mistaken for agent behavior | Label it as a description tripwire and do not claim that it observes host selection |
| Fixtures encode one repository's conventions | Use small generic repositories and state every fixture assumption |
| The suite reinforces documentation micromanagement | Add explicit no-document or read-only re-entry cases when the evaluated boundary requires them |
| A judge approves unauthorized changes | Enforce mutation allowlists mechanically |
| Cost grows with catalog coverage | Use affected-case selection, staged coverage, and explicit budgets |
| Multi-host support delays useful evidence | Start with one recorded host and add another only after the harness proves useful |

## Resolved Pilot Decisions

- Host: the locally authenticated Codex CLI, with its version and explicitly
  requested model recorded per run; a trace-reported model remains null when
  unavailable rather than inferred.
- Schema: a small Sirius-specific JSON case format validated by the free tier.
- Routing: a dependency-free normalized TF-IDF approximation used only as a
  transparent description tripwire.
- Isolation: a fresh temporary Git repository per behavioral or judge run,
  with mechanical diff and mutation checks after execution.
- Authority: each case declares mutable or read-only workspace mode plus
  allowed and required mutation patterns.
- Repetition and gating: repetition is explicit and reports distributions;
  paid behavioral and semantic results do not block normal validation.
- Retention: large traces and results remain ignored local or CI artifacts;
  only reviewed cases, fixtures, runner code, and deliberate small baselines
  belong in Git.

## Closure

The exit criteria are met: the repository has a bounded representative pilot,
free routing checks in normal validation, one-host opt-in behavioral execution,
trace and diff evidence as the primary oracle, a contract-driven composition
case, and evidence-based expansion rules. Active behavior is authoritative in
[`evals/`](../../evals/README.md), its case files, runner code, and tests. This
proposal remains as the rationale, staged delivery record, and statement of the
pilot's limits.
