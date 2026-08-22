# Repository Workflow

Use this track to understand a pull request, commit, branch, or local change,
or to record and publish an already implemented change. The skills
remain independently selectable; each sequence is a common handoff, not
authority to perform later review or publication steps without the user's
request.

When the `all` installation is available, optionally use Addy Osmani's external
[`code-review-and-quality`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/code-review-and-quality/SKILL.md)
before commit or pull-request publication. Use external
[`code-simplification`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/code-simplification/SKILL.md)
after checks pass when recently changed code needs a behavior-preserving
clarity pass. Both remain external skills, not Sirius catalog entries or
lifecycle gates.

## Interactive code-change tour

1. Use [`walkthrough-me`](../../skills/walkthrough-me/SKILL.md) when a reader
   needs a paced explanation of a pull request, commit, range, branch diff, or
   staged, unstaged, or selected untracked worktree changes.
2. Fix committed sources to their revisions. Capture local changes as a mutable
   snapshot, keep staged, unstaged, and untracked sources distinct, and recheck
   the snapshot before advancing.
3. Inspect the selected change claim, hunks, nearby context, and tests without
   changing repository, index, PR, or remote state.
4. Group the change into a few dependency-ordered sections. Show the map and
   first section, then wait for explicit confirmation before advancing.
5. End with the end-to-end flow, verification evidence, and open questions.
   Treat this as comprehension, not approval, commit authority, or a formal
   code-review verdict.
6. Invoke `code-review-and-quality` separately when the user requests a
   correctness, architecture, security, performance, or merge review.

## Typical change flow

1. Implement and verify the requested outcome using the repository's own
   guidance. For behavior changes, the
   [implementation and evolution track](implementation-evolution.md) can supply
   a test-first implementation or behavior-preserving refactoring workflow.
2. With the `all` installation, optionally use `code-simplification` on the
   recently changed scope. Preserve exact behavior and rerun affected checks.
3. Use [`commit`](../../skills/commit/SKILL.md) when a prepared change still
   needs to be recorded. Review repository state, run proportional
   verification, and stage only the intended files.
4. Use [`create-pr`](../../skills/create-pr/SKILL.md) when committed work is
   ready to publish for review. Confirm base, head, push state, duplicate pull
   requests, title conventions, and validation evidence.

Each step requires the authority appropriate to its effects. `simplify` is
retired. Use
[`behavior-preserving-refactoring`](../../skills/behavior-preserving-refactoring/SKILL.md)
for an intentional, verified local structural improvement before returning to
this track.

## Governance feedback

When multiple examples expose a durable policy gap, directly update the
nearest applicable `AGENTS.md` with the narrowest enforceable rule. A one-off
defect or stale artifact should normally be fixed at its direct owner instead
of becoming repository policy. Repository-specific naming and tracker
conventions belong in `AGENTS.md`; the shared workflow skills retain useful
generic defaults.
