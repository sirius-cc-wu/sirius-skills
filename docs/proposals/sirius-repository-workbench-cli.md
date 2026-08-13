---
type: "Capability Proposal"
title: "Sirius Repository Workbench CLI"
description: "Proposes a read-only CLI that recommends repository-specific artifact placement and can later support controlled evaluation in projects using Sirius skills."
status: "proposed"
tags: [cli, repositories, artifact-layout, evaluation, agents]
---

# Sirius Repository Workbench CLI

## At a Glance

Sirius exposes repository-layout guidance through
`design-repository-artifact-layout`, so a coding agent can route a standalone
placement question without treating it as Unified Process planning. A developer
must still discover and invoke that agent capability, and it does not provide a
stable machine-readable observation contract. Once a repository has a clear
documentation structure, coding agents usually follow that precedent without
needing to know where the underlying method came from.

This proposal recommends a read-only `sirius` CLI whose first useful command is:

```text
sirius layout propose [repository] [--format markdown|json]
```

The command would inspect an existing repository, preserve useful local
conventions, and emit a minimal artifact-layout proposal. Markdown would serve
developers directly; versioned JSON would let a coding agent interpret the
same evidence or author a richer proposal. The command would not create
directories, move files, write indexes, modify `AGENTS.md`, or maintain hidden
planning state.

The important consequence is a new repository-facing product boundary for
Sirius. The first release would solve artifact placement only. Later commands
could use the same executable to run controlled evaluations in projects that
use Sirius skills, but that future scope must not turn the initial command into
a generic repository-management framework.

## Decision Requested

The primary reviewers are Sirius maintainers and developers who use Sirius in
other repositories. They are asked to decide whether Sirius should introduce
the read-only CLI boundary and implement `layout propose` as its first vertical
slice.

Approval of this proposal would not approve downstream evaluation commands or
automatic repository mutation. Those capabilities require separate evidence
and review after the first command demonstrates value.

## Representative Scenario

A developer adopts Sirius in a repository that already contains:

```text
docs/
  architecture/
  decisions/
  proposals/
```

The developer wants a stable home for feature requirements, analysis,
PlantUML views, and iteration history, but should not need to discover or name
`iterative-up-analysis-design`. They run:

```bash
sirius layout propose .
```

The command cites the observed paths, recognizes that decisions and proposals
already have canonical homes, and recommends the smallest compatible addition
for feature artifacts. It explains why a complete artifact-oriented UP tree
would be unnecessary and reports any uncertainty. The repository remains
unchanged.

A coding agent can instead run:

```bash
sirius layout propose . --format json
```

The agent receives the same observations, recommendation, alternatives, and
uncertainties as structured data. It may present that result to the developer
or place a durable candidate direction under established repository governance.
The CLI supplies evidence and Sirius policy; the coding agent retains judgment
and remains subject to its normal mutation authority.

## Current Evidence and Constraints

The following statements describe the repository today:

- [`artifact-layouts.md`](../../skills/design-repository-artifact-layout/references/artifact-layouts.md)
  already defines a repository-first selection workflow, several layout
  options, a selection matrix, and migration guidance.
- [`artifact-selection-budget.md`](../../skills/iterative-up-analysis-design/references/artifact-selection-budget.md)
  already limits standalone artifacts to knowledge with durable value, clear
  ownership, and an independent lifecycle.
- The layout guidance is owned by the independently deployable
  [`design-repository-artifact-layout`](../../skills/design-repository-artifact-layout/SKILL.md)
  skill and reused by proposal placement guidance and optional UP planning.
  This solves agent routing without creating a deterministic developer-facing
  command or versioned output contract.
- The Python package currently describes itself as packaging support and does
  not expose a console-script entry point in [`pyproject.toml`](../../pyproject.toml).
- The existing [evaluation runner](../../evals/README.md) can execute Codex in
  disposable fixture repositories, constrain mutations, run verification,
  capture traces and usage, and apply an optional semantic judge. It evaluates
  Sirius skills themselves; it is not yet a general evaluator for a separate
  project using those skills.
- Repository governance forbids restoring the retired Sirius spec-driven
  runtime, command catalog, or planning state without a separate
  repository-level decision.

It is an inference, not yet established evidence, that a CLI-generated layout
proposal will cause future coding agents to place artifacts correctly. The MVP
must test that assumption rather than treating a plausible observation as a
proven product effect.

## Goals

- Let a developer obtain repository-specific placement guidance without
  knowing which Sirius skill owns that knowledge.
- Preserve an established documentation layout unless concrete navigation or
  ownership problems justify a change.
- Recommend the smallest structure that gives durable artifacts obvious
  canonical homes.
- Give every recommendation inspectable repository evidence, rationale,
  alternatives, and uncertainty.
- Serve both developers and coding agents without embedding an LLM in the
  first release.
- Establish a conventional executable surface that could later host
  controlled, project-level Sirius evaluations.

## Non-Goals

- Create directories, files, indexes, or repository rules.
- Move or rewrite existing documentation.
- Add a persistent `.sirius` repository state directory.
- Replace `AGENTS.md` as the owner of repository-specific agent rules.
- Generate requirements, analysis, design, or PlantUML artifacts.
- Decide which artifacts a feature must produce before a concrete need exists.
- Become a general repository health checker in the first release.
- Embed a model, agent host, or interactive interview in `layout propose`.
- Claim that observing Sirius usage proves Sirius caused a better outcome.
- Implement downstream project evaluation as part of the layout MVP.

## Proposed Command

### Interface

```text
sirius layout propose [repository] [--format markdown|json]
```

- `repository` defaults to the current working directory.
- `--format` defaults to `markdown`.
- Successful output is written to standard output so a person can read it, an
  agent can capture it, or a caller can redirect it deliberately.
- Diagnostics are written to standard error.
- The command is read-only and never asks for write approval because it has no
  write path.
- Invalid arguments, an inaccessible repository, or an unrecoverable analysis
  error produce a nonzero exit status. Uncertainty about the best layout is a
  successful analysis result and must appear in the output rather than being
  hidden as a process failure.

The first release should expose the executable through the Python package while
keeping command dispatch small enough to add independently owned subcommands
later. It should not introduce a plugin system merely to anticipate unknown
future commands.

### Analysis Boundary

The command would:

1. locate the repository root without assuming the current directory is it;
2. inspect applicable `AGENTS.md` files, top-level guidance, documentation
   indexes, and relevant neighboring artifact names;
3. identify existing homes for proposals, decisions, current feature or
   product knowledge, architecture views, verification evidence, and iteration
   history;
4. classify the observed layout as established, partial, absent, or
   conflicting, with cited evidence and explicit confidence;
5. apply the artifact selection budget before recommending any new ownership
   boundary;
6. select the smallest layout compatible with how readers already navigate the
   repository; and
7. report the recommendation, alternatives, migration considerations, and
   unresolved ambiguity without changing the repository.

The analysis must not execute project code, load executable configuration, or
follow a repository symlink outside the inspected root merely to classify its
documentation. This keeps an agent-safe read operation from becoming an
implicit code-execution surface.

### Required Outcomes

The recommendation should distinguish these common conditions:

| Observed condition | Expected direction |
|---|---|
| A coherent established layout exists | Preserve it and identify the existing canonical homes |
| The layout is coherent but lacks one needed lifecycle | Recommend the smallest compatible addition |
| Several structures compete for the same artifact | Report the conflict and propose a consolidation decision |
| No durable artifact layout exists | Recommend the flat feature-iteration hybrid as a starting point |
| The repository is too empty to support confident inference | State the default and show credible alternatives rather than inventing local convention |

The default is a recommendation, not a mandate. For example, proposing
`docs/features/<feature>.md` does not imply that the command should create the
directory or that every feature deserves a document.

## Output Contracts

### Markdown

Human-readable output should contain only useful sections from this sequence:

1. conclusion and confidence;
2. observed repository conventions with paths;
3. recommended minimal layout;
4. preservation and migration notes;
5. rejected or viable alternatives; and
6. unresolved questions.

The output is a proposal body, not proof that its recommendation was accepted
or applied. When redirected into a repository, the caller remains responsible
for the destination, frontmatter, lifecycle state, and review.

### JSON

Machine-readable output should have a versioned top-level contract similar to:

```json
{
  "schema_version": "1",
  "repository": "/path/to/repository",
  "classification": "established",
  "confidence": "high",
  "observations": [],
  "recommendation": {},
  "alternatives": [],
  "uncertainties": []
}
```

Every material observation should include the relative path that supports it.
Recommendation and alternative entries should carry stable semantic fields
rather than requiring an agent to parse rendered prose. Absolute repository
paths may identify the invocation root, but evidence paths should be relative
so output remains comparable across worktrees and computers.

The exact version-one schema remains an implementation decision. Once
released, incompatible schema changes require a new version rather than silent
field reinterpretation.

## Relationship to Skills

The CLI would provide a deterministic, developer-facing form of the narrow
result owned by `design-repository-artifact-layout`. It would not make that
skill or `iterative-up-analysis-design` obsolete.

- Use `design-repository-artifact-layout` when a coding agent should inspect
  context, exercise judgment, recommend placement, or perform an explicitly
  authorized migration.
- Use the CLI when a developer or tool needs read-only, reproducible layout
  observations in Markdown or versioned JSON without invoking an agent.
- Use `iterative-up-analysis-design` when choosing a risk-sized UP iteration,
  artifact set, analysis sequence, design work, and implementation handoff.
- Use an established ideas, proposals, feature, or decision path when the
  recommendation needs durable review; do not create duplicate idea and
  proposal artifacts for the same candidate direction.

The human reference and executable rules could drift if maintained
independently. Implementation must therefore add focused cases for every row in
the layout selection matrix and review those cases whenever the reference or
CLI policy changes. Converting all layout prose into a configuration language
is not justified for the first release.

## Future Project-Level Evaluation

The long-term opportunity is to evaluate Sirius in the repositories where it
is actually used. A future command family might include:

```text
sirius eval plan ...
sirius eval run ...
```

Meaningful value evaluation requires more than recording that a skill ran. A
controlled case should provide:

- one repository snapshot;
- one bounded task and mutation authority;
- explicit executable checks or another credible task oracle;
- a control execution without the selected Sirius guidance;
- a treatment execution with that guidance;
- isolated disposable workspaces for both executions; and
- repeated runs when model variation could change the conclusion.

The comparison could report verification results, unauthorized changes,
required changes, documentation count and placement, diff surface, duration,
reported token usage, and non-gating semantic judgments. A positive result
would support only the tested task, repository, model, host, and skill
revision; it would not establish universal skill value.

The existing behavioral runner supplies much of the execution machinery, but
future design must separate three owners that are currently colocated:

1. the Sirius skill and evaluation definition;
2. the downstream repository being evaluated; and
3. the captured result and comparison evidence.

This evaluation extension should be proposed independently after the layout
MVP establishes whether a repository-facing CLI is useful. The first command
should avoid speculative abstractions for worktree orchestration, agent-host
adapters, or evaluation manifests.

## Alternatives Considered

### Stop at the Artifact-Layout Skill

The dedicated skill now gives agents a discoverable, repository-first workflow
and can perform an explicitly authorized migration. Stopping there avoids a new
executable surface, but developers and non-agent tools still lack reproducible
read-only observations and a versioned machine-readable contract.

### Keep Layout Guidance Under UP Planning

This would avoid another user-visible capability, but it would restore the
routing problem that the extraction solved: repository placement is useful for
proposals and recovered knowledge even when no Unified Process plan is needed.

### Bootstrap a Directory Tree Automatically

Creating a tree makes convention visible immediately, but it chooses ownership
boundaries before the repository and developer have accepted them. Empty
directories are not preserved by Git, while placeholder indexes add ceremony
and can mislead agents into producing documents that have no durable consumer.

### Build a Generic `inspect` Command First

A generic repository model might later support several consumers, but it has
little direct user value by itself. Starting with `layout propose` keeps the
first interface tied to a concrete decision. Its internal observations can be
extracted into a broader public command only after another real consumer
appears.

### Embed an LLM in the CLI

Model judgment could interpret unusual repositories more flexibly. It would
also add authentication, cost, latency, nondeterminism, prompt-injection, and
reproducibility concerns. Developers already have coding agents that can
interpret JSON output, so embedded inference is unnecessary for the first
release.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Structural heuristics present a generic preference as local truth | Cite evidence, expose confidence and uncertainty, and always include plausible alternatives when evidence is weak |
| Preserving an existing layout perpetuates a harmful convention | Require a concrete navigation, duplication, or ownership problem before recommending reorganization |
| Human and JSON outputs disagree | Render both from one analysis result and test their semantic equivalence |
| CLI rules drift from the skill reference | Cover the selection matrix with shared fixture expectations and review both surfaces together |
| The executable becomes a replacement runtime for skills | Keep the MVP stateless, read-only, non-interactive, and limited to one repository decision |
| Agents treat a recommendation as approval | Label lifecycle and uncertainty explicitly; never emit evidence that a change was applied |
| Repository content attacks an inspecting agent | Keep deterministic inspection separate from model interpretation, treat repository text as data, and avoid code execution |
| Later evaluations overstate causal value | Require a control, task oracle, isolated workspaces, environment metadata, and scoped conclusions |
| A stable JSON contract creates compatibility cost | Version the schema and keep version one minimal |

## Acceptance Evidence for the First Release

Implementation would be acceptable when the following evidence exists:

- the installed package exposes `sirius layout propose`;
- running either output format leaves the target repository byte-for-byte and
  Git-status unchanged;
- Markdown and JSON are rendered from the same analysis result;
- JSON validates against the documented version-one schema;
- evidence paths are repository-relative and point to inspected files;
- fixture repositories cover coherent feature-oriented, artifact-oriented,
  product-area-oriented, partial, conflicting, and absent layouts;
- an established proposal, decision, or architecture location is preserved in
  the recommendation;
- a repository with no convention receives the minimal flat
  feature-iteration default plus alternatives and uncertainty;
- the command neither reads outside the repository through symlinks nor
  executes repository code; and
- focused tests and normal repository validation pass.

Behavioral evaluation should then test the key product assumption: given the
CLI proposal, a coding agent places a requested artifact consistently without
being told to invoke `iterative-up-analysis-design`. That result should be
compared with a control prompt that lacks the proposal before claiming that the
CLI improves agent behavior.

## Open Decisions

- Should the executable be named `sirius`, or is a more collision-resistant
  package name needed?
- Which repository files may deterministic inspection read beyond structural
  names and navigation documents?
- What confidence vocabulary and evidence threshold distinguish an
  established layout from a partial or conflicting one?
- Which version-one JSON fields are necessary for coding agents without
  freezing speculative concepts?
- Should Markdown output include complete proposal frontmatter, or remain a
  destination-neutral body by default?
- What downstream repository and task should become the first behavioral
  control for the claim that visible layout guidance changes agent placement?

## Recommended Next Decision

Approve or reject the read-only CLI boundary and the `layout propose` MVP. If
approved, begin with fixture-backed classification and output contracts before
adding packaging or command dispatch. Defer project-level evaluation design
until this first slice demonstrates that developers or coding agents use its
recommendation successfully.
