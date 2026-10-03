---
name: vision
description: Defines, refines, or audits conformance against an evidence-backed project vision. Use to author or revise VISION.md with explicit identity, principles, non-goals, and accept-or-resist criteria, OR use to audit candidate features, design specifications, ADRs, or pull requests against an approved VISION.md to determine whether to accept, resist, or amend the project vision.
---

# Project Vision & Conformance Audit

## Overview

Project vision serves as the durable constitution of a repository or initiative: it states what the project exists to do, what it refuses to become, and how a reviewer judges a proposed change. A vision is an approval-controlled governance policy, not a business case, feature roadmap, or marketing summary.

This skill operates in two complementary modes:
* **Mode A: Define or Refine Project Vision**: Create or update the canonical `VISION.md` when an initiative lacks shared boundaries, principles, non-goals, or acceptance criteria.
* **Mode B: Conformance Audit Against Vision**: Audit an incoming feature request, requirement specification, architecture decision (ADR), or pull request directly against an approved `VISION.md` to evaluate strategic alignment and prevent off-mission drift.

---

## When to Use

### Mode A: Define or Refine Vision
- A repository or independently sponsored initiative lacks a shared project identity, principles, non-goals, or contribution-acceptance policy.
- An existing vision needs a revision after material approved direction, baseline architecture, or evidence has changed.
- Maintainers ask what the project should accept, resist, or deliberately not become.

### Mode B: Conformance Audit Against Vision
- **Stage 1 Intake**: A new feature request or capability idea arrives. Evaluate whether it falls within project scope or violates explicit non-goals before investing effort in detailed specification.
- **Gate 1 Design Review**: Audit draft specifications (`docs/requirements/<module-id>.md`) or architecture decisions (`docs/decisions/adr-*.md`) to verify that the proposed realization does not breach `VISION.md` principles or introduce mission creep.
- **Pull Request / Contribution Review**: Maintainers ask: *"Does this change conform to VISION.md, or should it be resisted?"*

### When NOT to Use
- Do not use when one requester's intent is unclear; use external `interview-me`.
- Do not use when a candidate direction needs alternatives, assumptions, or MVP scope; use external `idea-refine`.
- Do not use to approve a business case, feasibility commitment, funding, or investment decision; use the responsible external product or portfolio process.
- Do not use to infer intended architecture or product behavior from an undocumented codebase.

---

## Inputs and Evidence

### Mode A Inputs (Authoring / Revision)
- The responsible vision authority, project boundary, and the decision the vision must support;
- A confirmed candidate-direction one-pager from external `idea-refine` (when direction is not already sufficiently clear);
- Clarification from external `interview-me` (when requester intent is unclear);
- Approved requirements, decisions, repository guidance, and existing vision artifacts; and
- Relevant merged pull requests, commit messages, documentation, rejection history, and implementation evidence.

### Mode B Inputs (Conformance Audit)
- Approved, canonical `VISION.md` in the repository root or canonical governance location;
- The candidate artifact under review:
  - Feature proposal or issue intake;
  - Stage 1 Requirements specification (`docs/requirements/<module-id>.md`);
  - Stage 3 Architecture Decision Record (`docs/decisions/adr-*.md`); or
  - Git diff / Pull Request.

---

## Workflows

### Workflow A: Define or Refine Project Vision

1. **Set the vision boundary.** Identify the project or independent initiative, intended users, responsible vision authority, current decision, existing vision status, and non-goals. Do not make a release, component, or completed milestone a project vision unless it has independent authority and scope.
2. **Check for an existing vision.** Treat an approved `VISION.md` or canonical vision artifact as the baseline. Propose a bounded, evidence-backed delta; do not create a competing vision document.
3. **Clarify the direction.** Route a vague candidate direction to external `idea-refine`. Route unclear individual intent to external `interview-me`. Preserve their result as candidate input until the responsible authority accepts it.
4. **Mine proportionate evidence.** Inspect approved artifacts and a relevant range of repository history. Treat history as evidence, not approval. Record source revisions and recurring patterns: what the project builds, refuses, fixes at the root, or protects. Keep the evidence sheet conversational or otherwise ephemeral unless it has a justified independent lifecycle.
5. **Draft the acceptance policy.** State the project identity, intended users, durable principles, concrete non-goals, and accept-or-resist criteria. Make each claim traceable to approved intent, evidence, or authority-approved reasoning. Use short declarative sentences.
6. **Stress-test the draft.** Present a small set of concrete boundary cases: tempting off-mission features, principle conflicts, scope expansions, and ambiguous contributions. Explain both defensible outcomes. Replace trivial cases whose answer is already obvious.
7. **Obtain approval or preserve uncertainty.** Ask the responsible authority to approve, reject, or revise the draft. Record the authority and approved source revision. Return `needs prerequisite` rather than presenting an evidence-mined draft as approved.
8. **Route follow-up decisions.** Route business cases, feasibility commitments, and investment decisions to the responsible external product or portfolio process. Route actor goals to `use-case-modeling`, quality requirements to `specify-quality-constraints`, and architecture questions to `design-software-architecture`.

---

### Workflow B: Audit Conformance Against Project Vision

```text
Candidate Artifact (Request / Spec / ADR / PR) + Approved VISION.md
                             │
                             ▼
     [Step 1: Ingest Baseline & Candidate]
                             │
                             ▼
     [Step 2: Non-Goals & Boundary Audit] ────► Hits explicit Non-Goal? ──► RESIST
                             │
                             ▼
     [Step 3: Principles & Refusals Audit] ───► Violates principle? ──────► RESIST
                             │
                             ▼
     [Step 4: Acceptance Policy Evaluation] ──► Meets "Aligns when..."?
                             │                  Triggers "Resisted when..."?
                             ▼
     [Step 5: Conformance Verdict & Routing] ──► ALIGNED | RESIST | AMENDMENT NEEDED
```

1. **Ingest Baseline & Candidate**: Load the canonical `VISION.md` and extract its Scope, Non-Goals, Principles, and Acceptance Policy. Identify the exact problem, design choice, or diff in the candidate artifact.
2. **Non-Goals & Scope Audit**:
   - Does the proposal fall within the bounded responsibilities of the project?
   - Does it attempt any explicitly excluded direction listed under `## Non-Goals`? If yes, halt immediately with a `RESIST` recommendation.
3. **Principles & Commitments Audit**:
   - Does the design violate any durable commitments or stated refusals (e.g. introducing external cloud dependencies to a local-first system, bypassing safety loops, or creating synthetic mock scaffolding)?
4. **Acceptance Policy Evaluation**:
   - Evaluate positive criteria: Does the change satisfy the testable conditions under *"A change aligns when it..."*?
   - Evaluate negative criteria: Does the change trigger any condition under *"A change should be resisted when it..."*?
5. **Boundary Case Precedents**:
   - Check if `VISION.md` contains an established boundary case resolving this exact tension or pattern.
6. **Issue Conformance Verdict & Routing**:
   - **`ALIGNED`**: The proposal directly fulfills the mission, avoids non-goals, and satisfies the acceptance policy. Unblock progression to Golden Path specification or execution.
   - **`RESIST`**: The proposal triggers a non-goal or resistance criterion. Recommend rejection, de-scoping, or routing the capability to an external collaborator or adapter.
   - **`AMENDMENT NEEDED`**: The proposal represents a genuine, high-value strategic shift that contradicts the current `VISION.md`. Escalate to the responsible vision authority for a formal revision before proceeding.

---

## Output Templates

### Output A: Canonical `VISION.md` Template

```markdown
---
type: "Vision"
title: "Vision: [Project or Initiative]"
description: "[One sentence stating the project purpose and acceptance boundary]"
id: "[Stable ID when cross-referenced]"
status: "[draft | proposed | approved | superseded]"
tags: [vision, governance]
---

# Vision: [Project or Initiative]

[Project] exists so that [intended user and outcome].
It owns [bounded responsibility].

## Intended Users

- [Intended user or collaborating system]: [Role and how it relies on the project]

## Scope

[Project] owns:

- [Bounded capability, contract, or core responsibility];
- [Explicit artifact or subsystem boundary].

## Principles

- **[Principle]**: [Concrete commitment and refusal]

## Non-Goals

- [Explicit excluded direction]: [Reason]

## Integration Boundary

- **[Collaborator or subsystem boundary]**: [Explicit boundary contracts and responsibilities]

## Acceptance Policy

A change aligns when it:

- [testable positive criterion].

A change should be resisted when it:

- [testable negative criterion].

## Boundary Cases

- **[Concrete boundary case or tempting off-mission feature]**: [Defensible outcome and policy resolution]

## Authority and Evidence

- Authority and status: [role, decision, and revision]
- Source revision: [Git commit hash or baseline release]
- Evidence: [approved artifact, pull request, commit, or source revision]
- Open questions: [unresolved authority, architecture, or evidence questions]
```

### Output B: Vision Conformance Assessment Template

```markdown
# Vision Conformance Assessment: [Feature / Design / PR]

## 1. Context & Baseline
- **Governing Vision**: `VISION.md` (Revision: `[commit SHA | status]`)
- **Evaluated Artifact**: `[spec path | ADR path | PR # | issue]`
- **Evaluator**: `[Thinker / Reviewer]`
- **Verdict**: **[ALIGNED | RESIST | AMENDMENT NEEDED]**

## 2. Policy Conformance Audit

| Evaluation Axis | Vision Policy Reference | Findings & Evidence | Conformance Status |
| :--- | :--- | :--- | :--- |
| **Scope & Boundaries** | `## Scope` | [Analysis of capability ownership] | [PASS | BREACH] |
| **Explicit Non-Goals** | `## Non-Goals` | [Check against listed exclusions] | [PASS | TRIGGERED] |
| **Durable Principles** | `## Principles` | [Check against commitments & refusals] | [PASS | CONFLICT] |
| **Positive Criteria** | `## Acceptance Policy (Aligns)` | [Analysis of positive criteria] | [SATISFIED | UNSATISFIED] |
| **Negative Criteria** | `## Acceptance Policy (Resist)` | [Analysis of resistance criteria] | [CLEAR | TRIGGERED] |

## 3. Boundary Cases & Precedents
- [Discussion of relevant precedent in VISION.md or novel trade-off]

## 4. Verdict & Recommendation
- **Verdict**: **[ALIGNED | RESIST | AMENDMENT NEEDED]**
- **Actionable Disposition**:
  - *If ALIGNED*: Approved from vision perspective. Proceed with Stage 1-4 Golden Path or implementation.
  - *If RESIST*: Recommend declining this change or removing off-mission capability [detail].
  - *If AMENDMENT NEEDED*: Halt execution. Escalate proposal to [Vision Authority] to formally amend `VISION.md`.
```

---

## Boundaries

- External `idea-refine` owns candidate-direction exploration. External `interview-me` owns clarification of one requester's intent. This skill turns sufficiently grounded input into a project-level acceptance policy or audits against an existing one.
- The responsible external product or portfolio process owns business-case, feasibility, funding, and investment approval. A vision does not authorize those decisions.
- `use-case-modeling` owns actor goals and black-box behavior. `specify-quality-constraints` owns measurable quality requirements and binding constraints. `architecture` / `design-software-architecture` owns intended major structure.
- `doubt-driven-development` executes the adversarial Gate 1 design review; `vision` provides the authoritative baseline for strategic and non-goal alignment during that review.
- Repository history may reveal evidence but does not recover missing approval or make an inferred policy authoritative.

---

## Red Flags

- A vision repeats generic virtues without source evidence or a concrete acceptance consequence.
- A draft presents commit history, code, or a candidate idea as approved organizational intent.
- A business case, delivery plan, roadmap, or architecture design appears in the vision.
- A design is approved without checking against `VISION.md` non-goals.
- A change that matches a "should be resisted when" criterion is accepted without formal vision amendment.
- A review transcript or answers ledger becomes a second source of truth.

---

## Verification

### Mode A Verification (Authoring / Revision)
- [ ] The project or independent-initiative boundary and vision authority are explicit.
- [ ] Existing approved vision material is refined in place or its delta is explicit.
- [ ] Candidate direction, repository evidence, approved intent, and authority reasoning remain distinguishable.
- [ ] Each principle and non-goal has an evidence reference or authority-approved rationale.
- [ ] The acceptance policy gives concrete positive and negative tests for a proposed change.
- [ ] Boundary cases exposed non-trivial scope or principle decisions.
- [ ] Approval status, authority, and source revision are explicit; missing approval returns `needs prerequisite`.
- [ ] Any standalone vision passes the artifact budget in `skills/select-technical-artifacts/references/artifact-selection-budget.md` and has one `Vision` frontmatter block matching `skills/design-repository-artifact-layout/references/markdown-artifact-frontmatter.md`.

### Mode B Verification (Conformance Audit)
- [ ] The audit cites the exact baseline revision of the canonical `VISION.md`.
- [ ] The candidate artifact is checked explicitly against `## Non-Goals` and `## Principles`.
- [ ] Every positive and negative criterion in the acceptance policy is evaluated with evidence.
- [ ] The verdict is unambiguously `ALIGNED`, `RESIST`, or `AMENDMENT NEEDED`.
- [ ] The disposition provides clear next steps for the engineering pipeline.
