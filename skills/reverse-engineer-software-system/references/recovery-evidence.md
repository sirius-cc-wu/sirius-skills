# Recovery Evidence and Confidence

Use this vocabulary in every reverse-engineering artifact. Evidence strength
depends on the question; there is no universal ordering that makes code,
tests, documents, or history authoritative for every claim.

## Evidence Perspectives

| Perspective | What it can establish | Common sources |
|---|---|---|
| As-built | Current implementation structure and configured wiring | Source, manifests, generated configuration, dependency graphs |
| As-tested | Behavior that a check asserts and, when executed, currently verifies | Unit, integration, contract, system, and static checks |
| As-observed | Behavior seen under recorded runtime conditions | Safe commands, traces, logs, responses, files, metrics |
| As-documented | What a document claims at its stated lifecycle point | READMEs, diagrams, API docs, runbooks, specifications |
| Intended | What an authorized source says should be true | Accepted requirements, decisions, standards, stakeholder confirmation |
| Historical | What existed or changed at an earlier revision | Version history, retired documents, release notes, prior builds |

## Claim Status

- `observed`: supported directly by one named source or repeatable observation.
- `corroborated`: independently supported by at least two relevant
  perspectives.
- `inferred`: reasoned from evidence but not directly demonstrated.
- `contradicted`: relevant sources disagree.
- `unknown`: available evidence cannot answer the question.

Do not upgrade a claim merely because several files repeat the same underlying
assumption.

## Confidence

- `high`: direct relevant evidence, fixed revision or conditions, and no known
  conflict.
- `medium`: credible but incomplete evidence, a limited observation, or a
  reasonable inference with alternatives.
- `low`: indirect, stale, ambiguous, or unrepeatable evidence.

Confidence does not replace claim status. An inference can be well reasoned and
still remain an inference.

## Temporal Status

Use `current`, `retired`, `superseded`, or `uncertain`. Record the commit, tag,
build, or snapshot whenever the repository can change.

## Evidence Locators

Prefer stable, reviewable locators:

- repository revision plus path and symbol;
- test name plus execution result;
- command plus relevant environment and output;
- route, schema, configuration key, log event, or external observation;
- artifact ID plus lifecycle status;
- commit or change range for historical claims.

Line numbers may supplement a symbol or artifact ID but should not be the only
locator when later edits can move the evidence.

## Claim Record

```markdown
### [Concise claim]

- Perspective: [as-built | as-tested | as-observed | as-documented | intended | historical]
- Status: [observed | corroborated | inferred | contradicted | unknown]
- Confidence: [high | medium | low]
- Temporal status: [current | retired | superseded | uncertain]
- Evidence:
  - [revision, path and symbol, test and result, command, artifact, or commit]
- Limits:
  - [conditions, missing evidence, or competing interpretation]
```

## Authority by Question

- For current structure, start with the current build and source graph.
- For current observable behavior, prefer repeatable observations and executed
  checks, then explain relevant implementation support.
- For intended behavior, prefer accepted requirements, decisions, standards,
  and stakeholder confirmation.
- For evolution and rationale, use version history and lifecycle-aware
  decisions without assuming a commit message tells the whole story.
- For security or failure guarantees, seek negative evidence and boundary
  checks, not only successful examples.

Never perform destructive, production-affecting, privacy-sensitive, or
externally visible probes without explicit authorization.
