---
name: select-technical-artifacts
description: "Selects the smallest durable disposition for candidate requirements, analysis, design, decision, planning, recovery, or verification knowledge: create a standalone artifact, update an existing owner, embed it, keep it with implementation, defer it, or omit it. Use when asked which technical artifacts should exist, whether a document should be created or split out, how to reduce a proposed documentation set, or to review an artifact budget; use design-repository-artifact-layout after a justified artifact needs a canonical home and the artifact's specialist to author its content."
---

# Select Technical Artifacts

## Overview

Select the smallest durable owner for technical knowledge.

Use this skill when a proposed artifact set needs a disposition. Assign one
disposition to each candidate:

- `create`
- `update`
- `embed`
- `keep with implementation`
- `defer`
- `omit`

Prefer executable evidence and existing canonical owners. Create a standalone
artifact only when its value, ownership, and lifecycle justify the additional
maintenance boundary.

Return a read-only recommendation by default. Do not author specialist
content, choose canonical paths, implement changes, commit changes, or publish
results.

Use the [Artifact Selection Budget](references/artifact-selection-budget.md) as
the decision rule.

## When to Use

Use this skill when:

- A proposed change lists several documents and needs the smallest sufficient
  set.
- It is unclear whether knowledge belongs in code, tests, schemas,
  configuration, an existing artifact, an aggregate section, or a new file.
- A document or section may need an independent lifecycle.
- Several proposed artifacts may duplicate one owner.
- A branch, plan, or workflow needs an artifact-budget review.
- The user explicitly authorizes an update to an existing artifact budget or
  plan.

Do not use this skill when:

- The artifact disposition is already clear and only its content needs to be
  written. Use the owning specialist.
- A justified artifact needs a canonical path, index, lifecycle-aware layout,
  or migration. Use
  [Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md).
- The request requires requirements discovery, design, implementation,
  verification, iteration coordination, commit, or publication.
- No material artifact-selection question exists. An owning skill may apply the
  budget locally.

## Workflow

1. **Read local governance.**
   Inspect the nearest `AGENTS.md`, documentation rules, established artifact
   types, canonical owners, indexes, templates, validators, and relevant
   history. Preserve explicit repository policy.

2. **Define the selection boundary.**
   List the candidate knowledge, requested scope, intended decisions or
   consumers, material risks, and authority for the request. Keep content
   design and repository placement out of scope unless they provide ownership
   evidence.

3. **Inventory existing owners.**
   Search code, tests, schemas, configuration, generated evidence, and canonical
   artifacts. Distinguish an established owner from a nearby file that only
   repeats the information.

4. **Apply the creation gate.**
   Test each candidate for:

   - **Value:** The knowledge records a durable decision, serves a named future
     consumer, or reduces a material risk.
   - **Ownership:** No executable source or canonical artifact owns the
     knowledge clearly enough.
   - **Lifecycle:** The knowledge will be reviewed, reused, or maintained
     independently.

   A standalone artifact requires all three conditions. Record missing
   evidence. Do not convert possible future usefulness into value.

5. **Assign the first sufficient disposition.**
   Prefer these owners in order:

   1. Code, tests, schemas, or configuration.
   2. An existing canonical artifact.
   3. An embedded section in the current feature or aggregate artifact.
   4. A new standalone artifact that passes the creation gate.
   5. No artifact for temporary reasoning without durable value.

   Use `defer` when potential value is plausible but current evidence is
   insufficient.

6. **Minimize the selected set.**
   Combine candidates that share an owner, consumer, and lifecycle. Split
   knowledge only when the resulting parts have independent maintenance or
   reuse. Do not create a boundary because a methodology, artifact type,
   template, or document length suggests one.

7. **Check lifecycle conflicts.**
   Keep current knowledge, candidate ideas, accepted decisions, fixed recovery
   baselines, verification evidence, and historical records separate when
   their authority or maintenance differs. Do not duplicate the same governing
   fact or candidate direction across equivalent homes.

8. **Route the result.**
   Send selected content to its owning specialist. Send placement and migration
   questions to
   [Design Repository Artifact Layout](../design-repository-artifact-layout/SKILL.md).
   Keep executable dispositions with the relevant implementation or test
   owner. Give deferred candidates an evidence-based promotion trigger.

9. **Apply only within authority.**
   Return the disposition, evidence, consumer or risk, ownership, lifecycle
   rationale, confidence, and next owner. If the user authorizes updating an existing artifact budget or plan, change only
   its dispositions and rationale. Preserve unrelated content and validate the
   result.

   Do not create selected artifacts or execute their handoffs without separate
   authorization.

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

Omit empty sections. Keep the recommendation conversational or embed it in the
owning planning workflow. Do not create a standalone artifact-budget document
merely to record that fewer artifacts should exist.

## Boundaries

- **Selection versus placement:** This skill decides whether knowledge needs a
  new, existing, embedded, executable, deferred, or omitted owner.
  `design-repository-artifact-layout` decides canonical paths and migrations
  after selection.
- **Selection versus content:** Requirements, design, ADR, recovery, planning,
  and verification specialists author the meaning of selected artifacts.
- **Selection versus coordination:**
  `iterative-risk-driven-development` coordinates risk-driven analysis, design,
  implementation, and verification. This skill reviews a material artifact-set
  question without running an iteration.
- **Selection versus delivery:** This skill does not implement, verify, commit,
  or publish repository changes.

## Red Flags

- Treating a methodology checklist as a required document inventory.
- Using “for documentation,” “best practice,” or “might be useful later” as the
  only value claim.
- Selecting a new file without searching executable and canonical owners.
- Creating multiple artifacts for one audience, owner, and lifecycle.
- Splitting a long file without independent ownership or maintenance pressure.
- Merging current knowledge, ideas, accepted decisions, recovery evidence, and
  historical records with different authority or lifecycle.
- Inventing a directory, filename, identifier, or template before a material
  placement decision exists.
- Continuing into authoring, placement, migration, implementation, commit, or
  publication without authority.

## Verification

- [ ] Local governance and existing executable and canonical owners were
      inspected.
- [ ] Every candidate has exactly one disposition.
- [ ] Every `create` recommendation passes the value, ownership, and lifecycle
      tests with concrete evidence.
- [ ] Every `update` or `embed` recommendation identifies its canonical owner.
- [ ] Every `keep with implementation` recommendation identifies its executable
      owner.
- [ ] Every `defer` recommendation names a promotion trigger.
- [ ] Equivalent candidates were consolidated without merging distinct
      authority or lifecycles.
- [ ] Content authoring, placement, migration, and iteration coordination remain
      with their owning skills.
- [ ] Any budget or plan mutation was explicitly authorized, scoped to
      dispositions and rationale, and validated.
- [ ] No selected artifact, implementation, commit, or publication was
      produced without separate authorization.
