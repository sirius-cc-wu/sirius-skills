# Templates

## Rule

```markdown
### <ID>. <Short name>

<Subject> must <required behavior>. <Subject> must not <prohibited behavior>.

- Example: <precondition>. <stimulus>. <observable result that fails when the rule is broken>.
```

Rules for writing rules:

- One required behavior for each rule.
- Name an observable result in each example: a response, a state change, a
  stored value, an error, or a message.
- Use the terms that the artifact defines.

## Decision

```markdown
D<n>. **<Name>.** <Subject> must <decision>.
Decided by <decision owner> on <date>. Reason: <one sentence>.
```

## Open Question

```markdown
- Q<n>. <Question>. Options: <A>, <B>. Consequence of each: <...>.
  Recommendation: <...>. Owner: <decision owner>.
```

## Conformance Record

```markdown
Baseline: <repository revision or change identifiers>
Specification: <links to the normative artifacts>

| Rule | Status | Evidence | Gap | Follow-up owner |
| :--- | :--- | :--- | :--- | :--- |
| <ID> | Conforms / Partial / Gap / Not verified | <locator> | <what is missing> | <owner or work item> |
```
