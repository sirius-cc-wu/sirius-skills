# Playbook 4: Fleet Batch Orchestration (Parallel Builders)

**Trigger:** Queue of independent issues, bugs, or parallel feature slices.
**Alpha Progression:** *Work* → *Prepared* & *Concluded (Batch)*.

## Steps

1. **Decompose & Frame Queue**
   - Ingest the list of tickets, independent tasks, or parallel slices.
   - Generate compact 1-paragraph briefs for each item (`Goal`, `Scope`, `Worktree`, `Verify`, `Acceptance`).

2. **Parallel Worktree Provisioning**
   - Verify clean root worktree (`git status --porcelain`).
   - Allocate concurrent worktrees: `bun scripts/worktree.ts create <branch-i> [base]`.

3. **Concurrent Builder Subagent Launch**
   - Spawn parallel background builder subagents into their respective isolated worktrees.

4. **Drain & Babysit**
   - Collect Builder Delivery Reports as builders complete.
   - If CI or tests fail on any slice, dispatch a targeted Builder Mode B run in that worktree to fix.

5. **Present Fleet Delivery Board**
   - Summarize task, branch, PR URL/commit, CI status, and test evidence in a clean markdown table.
