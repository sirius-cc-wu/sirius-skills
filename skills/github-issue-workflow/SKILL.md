---
name: github-issue-workflow
description: File, triage, and advance GitHub issues through duplicate checking, structured intake, specification handoff, and evidence-based closure. Use when creating non-duplicative issues, proposing updates, or verifying and closing known issues.
---

# GitHub Issue Workflow

Manage the full lifecycle of a GitHub issue as a durable, traceable work record.
This Thinker skill handles non-duplicative intake, triage, specification handoff,
and evidence-based closure; it does not implement code or review PRs.

## Workflow

### 1. Issue Intake & Creation (New Issues)

When filing a new issue:
1. **Confirm the target.** Identify the repository and desired outcome. Ask only
   questions that would change the title, scope, or acceptance evidence.
2. **Inspect before proposing.** Read `AGENTS.md`, applicable issue templates,
   existing labels, and search for duplicates. If a duplicate is likely, present it
   and ask whether to create a distinct issue, contribute context to the existing
   issue, or stop. Never create a duplicate merely to preserve a conversation.
3. **Propose the issue structure.** Present title, body, proposed existing labels,
   and related links before creating. Keep facts, assumptions, and questions
   distinct; do not invent implementation details, owners, priority, or dates:

   ```markdown
   ## Goal
   [Observable outcome and why it matters]

   ## Context
   [Problem evidence or request source]

   ## Scope / non-goals
   - Included: [...]
   - Excluded: [...]

   ## Acceptance evidence
   1. [Observable condition]

   ## Open questions / assumptions
   - [...]

   ## Related work
   - [...]
   ```

4. **Create only with explicit authority.** A direct request authorizes only its
   specified fields. Never put secrets, tokens, private keys, personal data, or
   unredacted security details in the issue. Re-fetch the created issue, report its
   URL, exact fields set, and the requester's unresolved questions.

### 2. Triage & Classification (Existing Issues)

When reviewing or working an existing issue:
1. **Read the issue and governing context.** Confirm the repository and issue
   identity, then inspect current content, metadata, comments, related PRs, and
   likely duplicates. Read `AGENTS.md`, the target project's relevant canonical
   documentation, and issue templates. Stop and clarify ambiguous repository or
   issue identity.
2. **Classify the next outcome.**
   - *Problem*: Needs observed and expected behavior with reproduction evidence.
   - *Capability*: Needs rules and concrete examples.
   - *Design decision*: Needs an Architecture Decision Record (ADR).
   - *Delivery slice*: Needs linked specs/ADRs plus a task-board or Worker-handoff link.
   - *Duplicate or superseded*: Link the authoritative record without silently merging scope.
3. **Route through the Spec–Validate loop.** Use `interview-me` for unclear intent;
   `use-case-slicing` and `example-mapping` for requirements; `system-behavior`, domain,
   design, and ADR skills as needed. Put authoritative artifacts in the target project's
   canonical documentation directories, and link them from the issue. Do not treat
   the issue body as the specification.

   For an EtherCAT hardware issue, require a reproduction strategy in the specification
   or Worker handoff. Try the affected slave first; otherwise name the closest available
   hardware and its fidelity gaps (identity/revision, ESI, PDO/CoE configuration,
   topology, master version, and AL state). If physical hardware is insufficient, the
   Worker may propose a temporary, reversible code emulation at a controlled seam. It
   must state the emulated fault or behavior, activation boundary, fidelity limits, and
   removal/restore evidence. Mark each result as physical, compatible-hardware,
   emulated, or inferred; unavailable exact hardware alone is never a reproduction verdict.

### 3. Propose Mutations with Narrow Authorization

1. **Propose every mutation.** Present the exact body, comment, metadata, links,
   and state change before writing. Separate facts, assumptions, questions,
   scope/non-goals, acceptance evidence, and traceability. Re-read immediately
   before editing; preserve unrelated content, metadata, comments, and links.
2. **Apply only explicit, narrow authorization.** Editing, commenting, metadata
   changes, closing, and reopening are external writes. Do not invent labels,
   milestones, projects, assignees, priorities, or dates. Re-fetch and report
   the exact result. Stop if it differs from the approved proposal or concurrent
   changes make the edit unsafe.

### 4. Evidence-Based Closure

1. **Close on evidence.** Close or reopen only with explicit authorization. For
   closure, link resolution evidence, verify current traceability and acceptance
   evidence, and resolve or explicitly waive open questions. A worker claim or
   merged PR alone is not closure evidence.

## Report

State the issue URL, action taken (created, triaged, updated, closed), classification,
facts, assumptions/questions, duplicate assessment, linked artifacts, and next action.
After a mutation, also state the exact fields changed and residual blockers.

## Boundaries

- Never publish credentials, tokens, private keys, personal data, or unredacted
  security details.
- Never create labels, milestones, projects, assignees, priorities, or due dates
  unless explicitly authorized.
- Do not claim that an issue is implementation-ready without Spec–Validate artifacts.
- Never implement work, run build/test loops, or review a PR under this skill.
