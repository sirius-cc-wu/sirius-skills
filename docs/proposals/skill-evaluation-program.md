---
type: "Capability Proposal"
title: "Skill Evaluation Program"
description: "Proposes staged routing, behavioral, and composition evals for Sirius skills."
status: "in-progress"
tags: [evaluation, skills, quality]
---

# Skill Evaluation Program

Implementation is proceeding in risk-sized stages. The deterministic routing
case format, runner, and eight-skill pilot are owned by
[`evals/`](../../evals/README.md). Opt-in Codex execution now captures traces,
workspace mutations, and verification results in a disposable fixture;
initial visual composition fixtures also distinguish no-diagram, focused
architecture-view, and focused class-view outcomes. Semantic grading and
broader feedback composition remain planned.

## At a Glance

Sirius verifies repository structure, installation profiles, shared references,
artifact guidance, and packaging behavior. It does not yet execute a coding
agent to determine whether a skill is selected appropriately, respects its
boundary, or produces the intended behavior.

The proposed program adds three capabilities in stages:

1. free catalog-routing and boundary evals;
2. model-executed behavioral trace evals in disposable repositories; and
3. composition evals for conditional feedback and documentation restraint.

This is repository verification infrastructure, not a new deployable skill.
The first investment should be a bounded pilot that proves the evals detect
seeded failures before coverage expands across the catalog.

## Representative Scenario

A user asks for a small, well-specified bug fix. The coding agent should use an
existing test or `test-driven-implementation`, change only code and tests, and
avoid starting an analysis-and-design workflow or producing new documents.

An eval should fail if the agent:

- routes the task through the complete iterative-design track;
- invents missing business intent;
- creates use-case, contract, or UML files without a durable need;
- changes valid tests to accept the defect; or
- mutates files outside the authorized fixture scope.

A complementary scenario should confirm that feedback is not suppressed: when
an operation contract exposes a missing domain concept, the agent should refine
the existing canonical domain model rather than ignore the discrepancy or
create a competing model.

Together, these scenarios test the central Sirius claim: coding agents retain
local autonomy while durable knowledge is reconciled when material evidence
changes it.

## Current Gap

Current checks establish that skills are packaged consistently and that their
instructions contain required structural guidance. They do not establish:

- whether realistic user language selects the correct skill;
- whether neighboring skill descriptions collide or over-trigger;
- whether an agent follows required and forbidden behavior;
- whether tool calls and workspace mutations stay within authority;
- whether feedback edges are treated as conditional knowledge reconciliation
  rather than mandatory skill hops; or
- whether the same scenario behaves consistently across repeated runs.

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
- Measure unnecessary skill invocation and artifact creation explicitly.
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

## Proposed Evaluation Model

| Level | Question | Mechanism | Initial execution |
|---|---|---|---|
| Existing repository checks | Is the catalog structurally consistent and installable? | Shell validation and Python tests | Every change |
| Catalog routing | Can realistic prompts distinguish a skill from its neighbors and non-applicable cases? | Deterministic case files, ranking, collision, and coverage checks | Every change |
| Behavioral trace | Does an agent perform the skill and respect its boundary in a controlled repository? | Disposable fixture, captured tool trace, commands, and workspace diff | On demand for affected cases |
| Composition and feedback | Does the agent select the smallest sufficient workflow and reconcile durable knowledge conditionally? | Multi-skill scenarios with required and forbidden paths | Periodic or before consequential workflow changes |

### 1. Catalog Routing and Boundary Evals

Store one case file per evaluated skill under a future `evals/cases/`
directory. Each case may contain:

- positive prompts expressed as users would naturally ask;
- negative prompts owned by a neighboring skill;
- boundary prompts where the skill should not run;
- expected ranking tolerance; and
- the skill revision or case-schema version when needed for diagnosis.

The first runner should be deterministic, dependency-light, and CI-safe. A
lexical or similarly transparent ranker is acceptable as a description-quality
tripwire, provided reports state that it approximates routing rather than
observing an agent host.

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
- elapsed time and token or monetary cost when available; and
- the final response as supporting evidence, not the primary oracle.

Prefer deterministic assertions for observable facts. Use an LLM judge only
for semantic expectations that cannot be checked mechanically, and never as
the sole authority for mutation safety or command results.

A candidate case shape is:

```json
{
  "skill_name": "test-driven-implementation",
  "evals": [
    {
      "id": "bug-fix-discrimination",
      "prompt": "Fix the reported invoice rounding defect.",
      "fixture": "invoice-rounding",
      "expected_output": "The defect is reproduced, minimally fixed, and regression-tested.",
      "expectations": [
        "A check discriminates the defect before the production fix",
        "Focused and regression checks pass after the fix"
      ],
      "prohibitions": [
        "Do not weaken an existing valid expectation",
        "Do not create a separate design document"
      ],
      "allowed_mutations": ["src/**", "tests/**"]
    }
  ]
}
```

Each behavioral case should include a negative control or seeded violation so
the evaluator demonstrates that it can fail for the behavior it claims to
detect.

### 3. Composition and Feedback Evals

Composition cases should target Sirius's highest-risk orchestration claims:

| Scenario | Expected behavior | Failure to detect |
|---|---|---|
| Small bug with a clear oracle | Stay with implementation and executable evidence | Mandatory analysis chain or new design documents |
| Non-trivial state change | Use or refine a contract when postconditions are genuinely needed | Guessing effects or writing contracts for trivial operations |
| Missing concept exposed by a contract | Refine the canonical domain model | Ignore the gap or create a competing model |
| Local implementation detail | Keep the information with code and tests | Update unrelated durable artifacts |
| Durable responsibility or interface change | Refine the owning realization or design model | Leave canonical design knowledge stale |
| Recovered surprising behavior | Preserve the distinction between current behavior and intended requirements | Declare current code authoritative for intent |
| Reconciliation with unknown intent | Recommend the smallest authoritative next action | Silently change code, tests, or documentation |
| Dirty worktree commit | Stage only the authorized change | Include unrelated user work |

These cases should distinguish three outcomes:

1. **Local correction:** the active skill handles the issue without another
   skill invocation or document.
2. **Canonical reconciliation:** an existing artifact is updated because its
   durable knowledge changed.
3. **Workflow re-entry:** another skill or the user is needed because the
   discovery exceeds the active skill's authority or requires substantial
   specialized analysis.

## Pilot Scope

Begin with eight skills that represent distinct failure risks:

| Skill | Risk exercised |
|---|---|
| `iterative-up-analysis-design` | Selecting a minimal artifact set instead of enforcing a lifecycle waterfall |
| `use-case-modeling` | Preserving the black-box boundary and avoiding internal design |
| `test-driven-implementation` | Demonstrating discriminatory verification without changing valid expectations |
| `recover-system-behavior` | Separating evidenced current behavior from intended requirements |
| `reconcile-recovered-design` | Respecting authority and avoiding silent mutation |
| `commit` | Scoping staged changes in a dirty worktree |
| `reconstruct-software-architecture` | Selecting focused component and runtime views from as-built evidence instead of producing an exhaustive inventory |
| `uml-class-diagram-design` | Producing a focused class view only when type responsibilities and relationships justify it |

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
- unnecessary skill invocation and artifact creation rates;
- repeatability across identical runs;
- duration, turns, tokens, and estimated cost; and
- changes from a named baseline run.

Persist large transcripts and run results as CI or local artifacts by default,
not as committed repository documentation. Commit only small fixtures, case
definitions, evaluator code, and deliberately reviewed baselines.

## Staged Adoption

### Stage 1: Prove Routing Cases

- Define the case schema for the eight pilot skills.
- Implement the free deterministic runner.
- Seed one description collision and one missing-vocabulary case to prove the
  runner fails for each.
- Run the free tier in normal repository validation.

### Stage 2: Prove Behavioral Discrimination

- Select one supported host and model for the pilot.
- Build disposable fixtures for representative pilot risks before expanding
  fixture coverage mechanically to every pilot skill.
- Add deterministic trace and diff assertions before adding an LLM judge.
- Seed prohibited mutations and workflow overreach to prove the evaluator
  detects them.
- Establish repeatability, duration, and cost baselines through several runs.

### Stage 3: Evaluate Composition

- Add the feedback and documentation-restraint scenarios.
- Run composition cases periodically and before material workflow-boundary
  changes.
- Compare failures with real skill usage before deciding which additional
  skills need coverage.

### Stage 4: Decide on Expansion

Expand only if the pilot answers these questions positively:

- Do routing failures identify actionable description defects?
- Do behavioral cases fail when seeded violations occur?
- Can maintainers diagnose failures from recorded evidence?
- Is nondeterminism low enough to distinguish regression from noise?
- Does the suite find consequential problems at an acceptable cost?

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Evals reward exact prose instead of correct behavior | Assert tool traces, commands, and workspace state first |
| Model variance creates flaky gates | Keep paid runs out of required CI initially; repeat and report distributions |
| Lexical routing is mistaken for agent behavior | Label it as a description tripwire and retain model-executed selection cases |
| Fixtures encode one repository's conventions | Use small generic repositories and state every fixture assumption |
| The suite reinforces documentation micromanagement | Include explicit no-document and no-reentry cases |
| A judge approves unauthorized changes | Enforce mutation allowlists mechanically |
| Cost grows with catalog coverage | Use affected-case selection, staged coverage, and explicit budgets |
| Multi-host support delays useful evidence | Start with one recorded host and add another only after the harness proves useful |

## Decisions Deferred to Elaboration

- The initial host, model, and version policy.
- Whether to adapt an existing compatible eval-case schema or define a minimal
  Sirius-specific extension.
- The transparent ranking algorithm for the deterministic tier.
- The fixture format and sandbox mechanism.
- How behavioral cases declare tool and mutation authority across hosts.
- The repetition count and evidence threshold required before a paid result can
  block a change.
- The retention policy for transcripts, cost history, and reviewed baselines.

These decisions should be made through a small runner spike and two
representative fixtures, not through an exhaustive framework design.

## Proposal Exit Criteria

The proposal is ready to move into implementation planning when maintainers
agree on:

- the eight-skill pilot and its representative risks;
- free routing checks as the first deliverable;
- one-host behavioral execution as an on-demand experiment;
- trace and diff evidence as primary behavioral oracles;
- feedback restraint as an explicit composition concern; and
- evidence-based expansion rather than immediate catalog-wide coverage.
