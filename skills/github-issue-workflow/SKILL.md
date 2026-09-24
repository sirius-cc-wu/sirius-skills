---
name: github-issue-workflow
description: Triage and advance an existing GitHub issue through clarification, specification handoff, and evidence-based closure. Use when working, refining, linking, commenting on, updating, closing, or reopening a known issue; do not use to create a new issue.
---

# GitHub Issue Workflow

Treat an existing issue as a traceable work record. This Thinker skill prepares
specifications and Worker handoffs; it does not implement code or review PRs.

## Workflow

1. **Read the issue and governing context.** Confirm the repository and issue
   identity, then inspect current content, metadata, comments, related PRs, and
   likely duplicates. Read `AGENTS.md`, the target project's relevant canonical
   documentation, and issue templates. Stop and clarify ambiguous repository or
   issue identity.
2. **Classify the next outcome.** A problem needs observed and expected behavior
   with reproduction evidence. A capability needs rules and examples. A design
   decision needs an ADR. A delivery slice needs linked specs/ADRs plus a
   task-board or Worker-handoff link. A duplicate or superseded issue must link
   the authoritative record without silently merging scope.
3. **Route through the Spec–Validate loop.** Use `interview-me` for unclear
   intent; `use-case-slicing` and `example-mapping` for requirements;
   `system-behavior`, domain, design, and ADR skills as needed. Put authoritative
   artifacts in the target project's canonical documentation directories, and
   link them from the issue. Do not treat the issue body as the specification.

   For an EtherCAT hardware issue, require a reproduction strategy in the
   specification or Worker handoff. Try the affected slave first; otherwise name
   the closest available hardware and its fidelity gaps (identity/revision, ESI,
   PDO/CoE configuration, topology, master version, and AL state). If physical
   hardware is insufficient, the Worker may propose a temporary, reversible code
   emulation at a controlled seam. It must state the emulated fault or behavior,
   activation boundary, fidelity limits, and removal/restore evidence. Mark each
   result as physical, compatible-hardware, emulated, or inferred; unavailable
   exact hardware alone is never a reproduction verdict.
4. **Propose every mutation.** Present the exact body, comment, metadata, links,
   and state change before writing. Separate facts, assumptions, questions,
   scope/non-goals, acceptance evidence, and traceability. Re-read immediately
   before editing; preserve unrelated content, metadata, comments, and links.
5. **Apply only explicit, narrow authorization.** Editing, commenting, metadata
   changes, closing, and reopening are external writes. Do not invent labels,
   milestones, projects, assignees, priorities, or dates. Re-fetch and report
   the exact result. Stop if it differs from the approved proposal or concurrent
   changes make the edit unsafe.
6. **Close on evidence.** Close or reopen only with explicit authorization. For
   closure, link resolution evidence, verify current traceability and acceptance
   evidence, and resolve or explicitly waive open questions. A worker claim or
   merged PR alone is not closure evidence.

## Report

State the issue URL, classification, facts, assumptions/questions, duplicate
assessment, linked artifacts, and next action. After a mutation, also state the
exact fields changed and residual blockers.

## Boundaries

- Never create a new issue; use `github-issue-creation`.
- Never publish credentials, tokens, private keys, personal data, or unredacted
  security details.
- Never implement work, run build/test loops, or review a PR under this skill.
