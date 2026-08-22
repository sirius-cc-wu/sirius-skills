# Repository Workflow

Use this track to understand a pull request, commit, branch, or local change,
or to record and publish an already implemented change. The skills remain
independently selectable; each sequence is a common handoff, not authority to
perform later review or publication steps without the user's request.

When the `all` installation is available, optionally use Addy Osmani's external
[`code-review-and-quality`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/code-review-and-quality/SKILL.md)
before commit or pull-request publication. Route readability and
local-complexity findings to external
[`code-simplification`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/code-simplification/SKILL.md).
Route findings about established structural ownership to
[`behavior-preserving-refactoring`](../../skills/behavior-preserving-refactoring/SKILL.md).
Use external
[`git-workflow-and-versioning`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/git-workflow-and-versioning/SKILL.md)
for standalone commit, branch, worktree, release, or semantic-version guidance.
Use external
[`documentation-and-adrs`](https://github.com/addyosmani/agent-skills/blob/5a1b82d6445d1e2f0abeea1072851419a50c0e5c/skills/documentation-and-adrs/SKILL.md)
when a significant technical decision or durable engineering context needs a
record. These four Addy skills remain external, not Sirius catalog entries or
lifecycle gates. `behavior-preserving-refactoring` remains a Sirius skill.

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
   [implementation and evolution track](implementation-evolution.md) describes
   external or repository-native implementation.
2. With the `all` installation, use `code-review-and-quality` for formal review.
   Otherwise, follow repository-native review guidance.
3. Route readability and local-complexity findings to `code-simplification`.
   Route established responsibility, dependency, variation, or configuration
   ownership findings to
   [`behavior-preserving-refactoring`](../../skills/behavior-preserving-refactoring/SKILL.md).
   Route material boundary findings to `iterative-risk-driven-development`.
   A direct, independently bounded structural request may enter its owner
   without first passing through review.
4. Return substantive changes to review, preserve exact behavior, and rerun
   affected checks.
5. With the `all` installation, use `documentation-and-adrs` when the change
   makes a significant technical decision or adds durable engineering context.
   Preserve local documentation, identifier, authority, status, and history
   rules.
6. With the `all` installation, use `git-workflow-and-versioning` when a
   prepared change needs a standalone commit or broader branch, worktree, or
   version guidance. Otherwise, follow repository guidance directly. Review
   repository state and diffs, run proportional verification, stage only the
   intended paths, and follow local message conventions.
7. Use [`create-pr`](../../skills/create-pr/SKILL.md) when committed work is
   ready to publish for review. Confirm base, head, push state, duplicate pull
   requests, title conventions, and validation evidence.

Each step requires the authority appropriate to its effects. `simplify` is
retired. Review findings select between `code-simplification`,
`behavior-preserving-refactoring`, and coordinated redesign; these are not
mandatory lifecycle gates.

## Governance feedback

When multiple examples expose a durable policy gap, directly update the
nearest applicable `AGENTS.md` with the narrowest enforceable rule. A one-off
defect or stale artifact should normally be fixed at its direct owner instead
of becoming repository policy. Repository-specific naming and tracker
conventions belong in `AGENTS.md`; the shared workflow skills retain useful
generic defaults.
