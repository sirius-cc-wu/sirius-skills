---
name: batch
description: Use this skill to decompose large repetitive work into independent subtasks, execute them in parallel batches, track progress, and merge verified results.
---

# Batch

Orchestrate large-scale changes by splitting work into independent units and running them in parallel with explicit tracking.

## When To Use

- "Apply this change across the whole repo."
- "Migrate old API usage everywhere."
- "Run this in parallel."
- "Split this big task and process each chunk."

## Workflow

1. Decompose the goal
- Convert the high-level request into independent units of work.
- Define boundaries so each unit can be executed without cross-unit conflicts.
- Record acceptance criteria for each unit.

2. Build and prioritize the queue
- Enumerate targets with `rg`/globs and assign each to a batch.
- Mark risky or ambiguous targets for manual handling.
- Track state per unit: `todo`, `in_progress`, `blocked`, `done`.

3. Execute in parallel
- Run multiple worker threads/sessions/worktrees on disjoint batches.
- Keep each worker on deterministic, scoped transformations.
- Reconcile overlaps immediately if discovered.

4. Verify each batch before merge
- Run focused validation for each completed unit.
- Reject and rework units that fail checks.

5. Merge and finalize
- Integrate verified units back into the main branch in controlled steps.
- Run repo-level validation after integration.
- Provide final status with completed units and remaining manual tasks.

## Guardrails

- Do not parallelize tasks with hidden shared state unless isolated first.
- Do not run blind global replacements without preview and sampling.
- Keep semantic rewrites separate from mechanical migrations when possible.
- If conflict rate is high, reduce batch size and rebalance units.

## Practical Patterns

- Use worktrees or equivalent isolated branches for workers.
- Prefer syntax-aware codemods over raw text replacement.
- Keep a live progress board (for example via `sb` or a simple checklist).
- Merge small verified batches frequently instead of one large final merge.

## Output Checklist

1. Goal decomposition and batch plan.
2. Parallel execution setup (workers/worktrees).
3. Status summary (`todo/in_progress/done/blocked`).
4. Validation results per batch and after merge.
5. Remaining manual follow-ups.
