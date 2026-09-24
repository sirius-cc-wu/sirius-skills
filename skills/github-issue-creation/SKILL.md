---
name: github-issue-creation
description: Create a clear, non-duplicative GitHub issue from a request. Use when the user asks to open, file, or create a GitHub issue; do not use to refine, hand off, or close an existing issue.
---

# GitHub Issue Creation

Create a durable intake record, not a specification or implementation plan. For
an existing issue, use `github-issue-workflow` instead.

## Workflow

1. **Confirm the target.** Identify the repository and the requester's desired
   outcome. Ask only questions that would change the issue's title, scope, or
   acceptance evidence.
2. **Inspect before proposing.** Read `AGENTS.md`, applicable issue templates,
   existing labels, and likely duplicates. If a duplicate is likely, present it
   and ask whether to create a distinct issue, contribute context to the
   existing issue, or stop. Never create a duplicate merely to preserve a
   conversation.
3. **Propose the issue.** Present title, body, proposed existing labels, and
   related links before writing. Keep facts, assumptions, and questions
   separate; do not invent implementation details, owners, priority, or dates.

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
4. **Create only with authority.** A direct request authorizes only its specified
   fields. Never put secrets, tokens, private keys, personal data, or unredacted
   security details in the issue. Re-fetch the created issue, report its URL,
   exact fields set, and the requester's unresolved questions.

## Boundaries

- Do not edit, comment on, close, reopen, or otherwise work an existing issue.
- Do not create labels, milestones, projects, assignees, priorities, or due
  dates unless those changes are separately and explicitly authorized.
- Do not claim that the issue is implementation-ready. That conclusion belongs
  to `github-issue-workflow` after the Spec–Validate artifacts exist.
