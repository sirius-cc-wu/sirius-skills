---
name: select-technical-artifacts
description: Selects the smallest durable disposition for candidate requirements, analysis, design, decision, planning, recovery, or verification knowledge: create a standalone artifact, update an existing owner, embed it, keep it with implementation, defer it, or omit it. Use when asked which technical artifacts should exist, whether a document should be created or split out, how to reduce a proposed documentation set, or to review an artifact budget; use design-repository-artifact-layout after a justified artifact needs a canonical home and the artifact's specialist to author its content.
---

# Select Technical Artifacts

## Overview

Decide whether technical knowledge deserves an independently maintained
artifact before deciding its path or writing its body. Prefer the smallest
owner that preserves durable value, traceability, reuse, or material risk
control. The normal output is a read-only disposition recommendation. When the
user separately authorizes updating an existing artifact budget or plan, apply
only the selected dispositions there; do not author specialist content, invent
paths, implement, commit, or publish.

Use the detailed [Artifact Selection Budget](references/artifact-selection-budget.md)
as the decision rule. Selection is a judgment supported by repository evidence,
not a fixed document count or a checklist of expected artifact types.

## When to Use

- A proposed change lists several documents and needs the smallest sufficient
  artifact set.
- It is unclear whether knowledge belongs in code, tests, configuration, an
  existing canonical artifact, an aggregate section, or a standalone file.
- A document or section may need an independent lifecycle, or several proposed
  artifacts may duplicate one owner.
- A branch, plan, or workflow needs an artifact-budget review or an authorized
  update to its recorded dispositions.
- Use the artifact's specialist directly when its disposition is already clear
  and only its content must be produced.
- Use `design-repository-artifact-layout` when justified artifacts need
  canonical paths, indexes, lifecycle-aware organization, or migration.
- Do not invoke this skill mechanically before every artifact. Owning skills
  may apply the budget locally when there is no material selection question.

## Workflow

1. **Read local governance.** Inspect the nearest `AGENTS.md`, documentation
   rules, established artifact types, canonical owners, indexes, templates,
   validators, and relevant history. Preserve explicit repository policy.
2. **Bound the selection question.** List the candidate knowledge or artifacts,
   requested scope, intended decisions or consumers, material risks, and
   whether the request is advisory only. Keep content design and placement out
   of scope unless needed as evidence about ownership.
3. **Inventory sufficient owners.** Search current code, tests, schemas,
   configuration, generated evidence, and canonical artifacts. Distinguish an
   established owner from a nearby file that merely repeats the information.
4. **Apply the creation gate.** For each candidate, test:
   - **Value:** a durable decision, named future consumer, or material risk
     reduction exists.
   - **Ownership:** no executable or canonical source owns the knowledge
     clearly enough.
   - **Lifecycle:** the knowledge is reviewed, reused, or maintained
     independently.
   A standalone artifact requires all three. Record missing evidence instead of
   converting possible future usefulness into value.
5. **Choose the first sufficient disposition.** Prefer, in order, executable
   ownership; an existing canonical artifact; an embedded section; then a new
   standalone artifact. Use exactly one of `create`, `update`, `embed`,
   `keep with implementation`, `omit`, or `defer` for each candidate.
6. **Minimize the selected set.** Combine candidates that share an owner,
   consumer, and lifecycle. Split knowledge only when the resulting parts are
   independently maintained or reused. Length, methodology phase, artifact
   type, or template availability alone does not justify a boundary.
7. **Check lifecycle conflicts.** Keep evolving current knowledge, ideas,
   legacy proposals, accepted decisions, fixed recovery baselines, verification
   evidence, and historical records distinct when their authority or
   maintenance differs.
   Do not duplicate the same candidate direction or governing fact across
   equivalent homes.
8. **Route the result.** Send selected content to its narrow owning skill. Send
   material path or migration questions to
   [Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md).
   Keep executable dispositions with the relevant implementation or test owner.
   Give deferred candidates an evidence-based promotion trigger.
9. **Report or apply within authority.** Return the disposition, evidence,
   consumer or risk, ownership and lifecycle rationale, confidence, and next
   owner. If the user explicitly authorized updating an existing budget or
   plan, change only its dispositions and rationale, preserve unrelated
   content, and run relevant checks. Do not create the selected artifacts or
   execute their handoffs without separate authorization.

## Output

Use the smallest useful form of this table:

```markdown
Scope:
- [candidate set, repository area, and decision boundary]

| Candidate knowledge or artifact | Disposition | Consumer, decision, or risk | Existing or proposed owner | Independent lifecycle evidence | Confidence and gap | Next owner |
|---|---|---|---|---|---|---|
| [candidate] | [create | update | embed | keep with implementation | omit | defer] | [concrete value] | [path, executable source, or owner] | [why it does or does not change independently] | [confidence and missing evidence] | [skill or role] |

Minimal selected set:
- [remaining canonical or executable owners after consolidation]

Promotion triggers:
- [deferred candidate and evidence that would justify reconsideration]
```

Omit empty sections. The recommendation itself normally remains conversational
or is embedded by an owning planning workflow. Do not create a standalone
artifact-budget document merely to record that fewer artifacts should exist.

## Boundaries

- **Selection versus placement:** this skill decides the disposition;
  `design-repository-artifact-layout` decides canonical homes and migrations
  after selection.
- **Selection versus content:** requirements, design, ADR, recovery, planning,
  and verification specialists own artifact meaning and authoring in STE-style.
- **Selection versus coordination:** `iterative-risk-driven-analysis-design`
  coordinates risk-driven analysis and design, while
  `run-development-iteration` owns execution. This skill reviews a material
  artifact-set question without planning or running an iteration.

## Red Flags

- A methodology checklist is treated as a required document inventory.
- “For documentation,” “best practice,” or “might be useful later” is the only
  stated value.
- A new file is selected without searching executable and canonical owners.
- Two artifacts restate the same knowledge for the same audience and lifecycle.
- A long file is split without independent ownership or maintenance pressure.
- Current knowledge, an idea or legacy proposal, an accepted decision, and
  historical evidence are merged despite different authority or lifecycle.
- The recommendation invents a directory, filename, identifier, or template
  before a material placement decision is made.
- Selection silently proceeds into authoring, moving, implementation, commit,
  or publication, or edits a plan that was requested only for review.

## Verification

- [ ] Repository governance and existing executable and canonical owners were
      inspected.
- [ ] Every candidate has exactly one disposition.
- [ ] Every `create` disposition passes value, ownership, and lifecycle tests
      with concrete evidence.
- [ ] Every `update` or `embed` disposition identifies the canonical owner.
- [ ] Every `keep with implementation` disposition identifies the executable
      owner.
- [ ] Every `defer` disposition names the evidence that could trigger
      promotion.
- [ ] Equivalent candidates were consolidated without merging distinct
      authority or lifecycles.
- [ ] Content authoring, placement, rewriting, and iteration coordination
      remain with their narrow owners.
- [ ] Any budget or plan mutation was explicitly authorized, scoped to
      dispositions, and validated.
- [ ] No selected artifact, implementation, commit, or publication was produced
      without separate authorization.
