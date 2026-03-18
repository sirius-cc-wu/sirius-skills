# Output Patterns

Use this guide when a skill needs to produce outputs in a consistent format or quality bar.

## When to specify output structure

Be explicit about output format when:

- the user expects a fixed structure
- the output will be copied into another system
- consistency matters more than creativity
- reviewers need predictable sections to scan

If multiple output formats are valid, describe how to choose among them instead of forcing one rigid template.

## Pattern 1: Exact section template

Use this when every result should follow the same outline.

```markdown
## Report structure

Use this template:

# [Title]
## Executive summary
## Key findings
## Risks
## Recommendations
```

This works well for reports, plans, summaries, and audits.

## Pattern 2: Example-driven formatting

Examples are often more effective than long prose descriptions.

```markdown
## Commit message format

Example:
Input: Add JWT authentication for the API
Output: feat(auth): add JWT authentication
```

Use examples when the skill needs to demonstrate tone, level of detail, or naming patterns.

## Pattern 3: Required fields with flexible wording

Use this when certain information must be present, but the exact prose can vary.

```markdown
## Response requirements

Always include:
- what changed
- why it changed
- risks or follow-up items
```

This is useful when some flexibility helps the model adapt to context.

## Pattern 4: Machine-readable plus human summary

For structured workflows, define both the human-facing summary and any machine-readable output.

Examples:

- a JSON object plus a short explanation
- a generated file plus a one-line success summary
- a checklist plus the final recommendation

When a script is involved, make the script output concise, readable success or failure messages rather than full tracebacks.

## Quality guardrails

When defining outputs, clarify:

- what must always be present
- what should be omitted
- how much detail is appropriate
- what counts as a successful result

Avoid vague guidance like "make it good" when you can define the actual success criteria.

## Choosing the right amount of rigidity

Use higher rigidity when:

- downstream tools expect exact structure
- the task is fragile or regulated
- consistency is more valuable than stylistic variation

Use lower rigidity when:

- the task is exploratory
- multiple valid structures exist
- the model needs room to adapt the answer to context

## Common mistakes

- Over-specifying trivial formatting while under-specifying the important content
- Giving examples that are too abstract to reuse
- Hiding crucial output requirements deep in a long paragraph
- Requiring a template when a checklist would be more flexible

## A practical recipe

When writing output guidance for a skill:

1. Decide what the user actually needs to receive.
2. List the non-negotiable parts of the output.
3. Show one concrete example.
4. Add only as much rigidity as the task requires.
5. Re-test on a real prompt to see whether the format is easy to follow.
