# Skills Methodology

The managed collection contains four independent repository workflow skills.
Use only the skills that match the work at hand; they are not a mandatory
lifecycle or a spec-driven development process.

## Typical change flow

1. Implement and verify the requested change using the repository's own
   guidance and tooling.
2. Use `simplify` for a focused cleanup pass over the branch or pull-request
   diff. Preserve behavior and keep unrelated files out of scope.
3. Use `commit` when the change is ready to record. Review the diff, run
   relevant checks, stage only intended files, and follow configured message
   conventions.
4. Use `create-pr` when the committed branch is ready to share. Confirm the
   worktree is clean, review the base/head diff, avoid duplicate pull requests,
   and include concrete validation evidence.

`governance-update` is intentionally orthogonal to that flow. Use it only when
multiple examples reveal a durable policy gap. A one-off defect or stale file
should normally be fixed at its direct owner instead of becoming a repository
rule.

## Shared principles

- Follow the nearest `AGENTS.md` and repository-local instructions.
- Keep staging, formatting, and validation scoped to the intended change set.
- Prefer project configuration over company- or tracker-specific hardcoding.
- Treat identifiers as opaque values and validate them only when the repository
  config defines a format.
- Report the checks run, their results, and any intentional exception.

## Configuration

When `.skills/conventions.json` exists, `commit` and `create-pr` may use:

- `commit_format` for commit summaries
- `pr_title_format` for pull-request titles
- `branch_extract_pattern` to obtain an identifier from a branch
- `id_pattern` to validate identifiers

Without repository-specific configuration, both skills use their documented
generic defaults.
