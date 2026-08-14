# Repository Workflow

Use this track to refine, record, and publish an already implemented change.
The skills remain independently selectable; the sequence is a common handoff,
not authority to perform later publication steps without the user's request.

When the `all` installation is available, optionally use Addy Osmani's external
[`code-review-and-quality`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/code-review-and-quality/SKILL.md)
before commit or pull-request publication. It remains an external review
skill, not a Sirius catalog entry or lifecycle gate.

## Typical change flow

1. Implement and verify the requested outcome using the repository's own
   guidance. For behavior changes, the
   [implementation and evolution track](implementation-evolution.md) can supply
   a test-first implementation or behavior-preserving refactoring workflow.
2. Use [`simplify`](../../skills/simplify/SKILL.md) for a focused cleanup pass
   over the branch or pull-request diff while preserving intended behavior.
3. Use [`commit`](../../skills/commit/SKILL.md) when the change is ready to
   record. Review repository state, run proportional verification, and stage
   only the intended files.
4. Use [`create-pr`](../../skills/create-pr/SKILL.md) when committed work is
   ready to publish for review. Confirm base, head, push state, duplicate pull
   requests, title conventions, and validation evidence.

Each step requires the authority appropriate to its effects. Selecting
`simplify` does not implicitly authorize a commit, push, or pull request.

## Governance feedback

When multiple examples expose a durable policy gap, directly update the
nearest applicable `AGENTS.md` with the narrowest enforceable rule. A one-off
defect or stale artifact should normally be fixed at its direct owner instead
of becoming repository policy. Repository-specific naming and tracker
conventions belong in `AGENTS.md`; the shared workflow skills retain useful
generic defaults.
