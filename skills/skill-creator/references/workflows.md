# Workflow Patterns

Use this guide when a skill needs to teach a repeatable multi-step process rather than a loose set of tips.

## When to use workflow structure

Choose a workflow-oriented skill when:

- the slice naturally happens in stages
- later steps depend on earlier decisions
- there are common failure points or branches
- the user benefits from consistent sequencing

Good examples include data-cleaning pipelines, deployment flows, investigation playbooks, and review processes.

## Core workflow shapes

### 1. Straight sequence

Use this when the same major steps happen every time.

```markdown
## Workflow

1. Inspect the input
2. Choose the approach
3. Execute the transformation
4. Validate the result
5. Summarize what changed
```

This is the simplest pattern and works well for predictable slices.

### 2. Decision tree

Use this when the first decision changes the rest of the workflow.

```markdown
## Workflow Decision Tree

- If the input is already normalized, skip to validation
- If columns differ, run schema normalization first
- If files are too large for memory, use the streaming path
```

After the decision tree, provide sections for each branch.

### 3. Capability plus workflow

Use this when the skill supports several operations, but each operation still has a repeatable sequence.

```markdown
## Quick Start

- Merge PDFs
- Split PDFs
- Extract text

## Merge PDFs workflow
...

## Split PDFs workflow
...
```

This keeps discovery easy without losing process detail.

## Turning examples into reusable skill content

For each realistic user request:

1. Write down how you would solve it from scratch.
2. Notice what repeats across requests.
3. Extract repeated work into one of these:
   - `scripts/` for deterministic operations
   - `references/` for detailed knowledge the model may need to read
   - `assets/` for templates, boilerplate, or files reused in outputs

If the same helper script gets rewritten across multiple examples, it belongs in `scripts/`.

## Documenting a workflow clearly

Strong workflow sections usually include:

- the purpose of the step
- the decision that determines whether the step applies
- the main action to take
- the expected output or checkpoint
- what to do when the step fails

Prefer imperative wording, but explain why the step matters when the reason is not obvious.

## Avoiding brittle workflows

Avoid overconstraining the skill when several valid routes exist.

Instead of:

```markdown
ALWAYS do steps A, B, C exactly in this order.
```

Prefer:

```markdown
Start with A because it reduces downstream mistakes. If A already looks correct, continue to B.
```

This preserves the workflow while still giving the model room to adapt.

## Iteration workflow for improving a skill

When refining a skill over time:

1. Collect a few real prompts that represent the work.
2. Run the skill on them.
3. Notice where it wastes effort, misses edge cases, or repeats manual work.
4. Update the skill to address the general pattern, not just one example.
5. Re-test the same prompts before adding new edge cases.

If the skill has objectively testable behavior, keep those prompts in a local root-level `evals/` directory while iterating.
