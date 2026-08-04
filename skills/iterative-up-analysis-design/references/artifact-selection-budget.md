# Artifact Selection Budget

Use this gate before creating a requirements, analysis, design, decision,
planning, recovery, or verification document. The budget is a decision rule,
not a fixed document count: spend documentation effort only where a durable
artifact has a clear owner and future value.

## Creation Gate

A new standalone artifact is justified only when all three tests pass:

1. **Value:** it captures a durable decision, will be reused by a named person
   or skill, or materially reduces implementation, operational, review, or
   change risk.
2. **Ownership:** existing code, tests, configuration, or a canonical artifact
   cannot own the information clearly enough.
3. **Lifecycle:** the information will be maintained, reviewed, or reused
   independently rather than changing as one part of an existing artifact.

Name the expected consumer or risk concretely. "For documentation" and
"might be useful later" do not establish value. When evidence is incomplete,
start with the least expensive disposition and promote it only when actual
reuse, ownership, or maintenance pressure appears.

## Disposition Order

Choose the first sufficient owner in this order:

1. Keep executable facts in code, tests, schemas, or configuration.
2. Update the existing canonical artifact that already owns the knowledge.
3. Embed a small section in the current feature or aggregate artifact.
4. Create a standalone artifact only when the creation gate passes.
5. Omit temporary reasoning that has no durable consumer or risk-reduction
   value.

Use these labels when recording the decision:

| Disposition | Use when |
|---|---|
| `create` | The value, ownership, and lifecycle tests all pass. |
| `update` | The knowledge is durable, but an existing canonical artifact owns it. |
| `embed` | The knowledge helps the current feature but does not change independently. |
| `keep with implementation` | Code, tests, schemas, configuration, or executable evidence are the clearest owner. |
| `omit` | The reasoning is temporary or does not affect a durable decision, consumer, or material risk. |
| `defer` | The potential value is plausible but not yet supported by evidence. |

## Practical Defaults

- Start a behavior slice with one evolving feature artifact when a document is
  needed at all.
- Split use cases, models, contracts, diagrams, or decisions only when they
  are independently reused or maintained.
- Create a decision record for a consequential, cross-cutting, or
  expensive-to-reverse choice, not for every implementation choice.
- Keep verification evidence with executable checks unless an audit,
  external review, or durable unresolved risk needs a separate record.
- Link iteration records to canonical artifacts instead of copying their
  contents.

These defaults do not prohibit additional artifacts. They require an explicit
reason for each additional ownership and lifecycle boundary.

## Iteration Use

Before work begins, record the planned disposition of material documentation:

```markdown
Artifact Budget:
- create: `[path]` - [consumer or risk] - [why no existing owner is sufficient and why it changes independently]
- update: `[path]` - [consumer, decision, or risk]
- embed: `[path#section]` - [local purpose]
- keep with implementation: `[code, test, schema, or configuration path]` - [evidence owned there]
- omit: [artifact kind] - [why it is unnecessary for this iteration]
```

Do not add empty categories merely to complete the template. If an unplanned
standalone artifact becomes necessary, add it with its justification. At
iteration close, record the actual disposition and any changed ownership.

## Review

Review can verify that the gate was applied, but usefulness remains a judgment
call. Check that:

- every new standalone artifact names its consumer, decision, or material risk;
- no existing canonical artifact or executable source already owns the same
  information;
- the new artifact has an independently meaningful lifecycle;
- planned and actual dispositions agree or the difference is explained; and
- removing the artifact would cause a concrete loss of ownership,
  traceability, reuse, or risk control.
