---
name: model-discovery
description: Discover and validate a domain model through scenarios, expert language, and implementation feedback. Use when domain concepts or rules are unclear, business and code terminology diverge, or a model has become a passive data schema.
---

# Model Discovery

Develop a useful model for a specific business problem, with language that experts and developers can use to explain behavior. A model is a selective abstraction, not an inventory of everything in the business.

## Work from evidence

1. Identify the business outcome and one concrete scenario that matters to it. Read available requirements, examples, domain documents, and relevant code. Distinguish reported facts, implementation behavior, and hypotheses; existing code can embody a misunderstanding.
2. Walk through the scenario using the participants' words. Capture decisions, rules, exceptions, quantities, and changes over time as well as things. Ask for the smallest missing example that would distinguish competing interpretations. If experts are unavailable, preserve unanswered questions instead of inventing agreement.
3. Try alternative conceptual explanations. For each, tell the scenario in ordinary sentences using the proposed terms. Investigate awkward wording, overloaded terms, and contradictions. They may reveal a missing concept or distinct contexts rather than careless naming.
4. Keep concepts that explain necessary behavior; remove detail irrelevant to the scenario. A model need not reproduce the physical world. Include business policies and processes when they explain a decision better than a collection of nouns.
5. Exercise the candidate model with an ordinary case, an exception, and a case that discriminates between alternatives. Where implementation is in scope, use a small executable example to test both feasibility and meaning. Feed implementation difficulties back into the model.
6. Align accepted terminology across code, tests, diagrams, and discussions within this model's context. Treat a meaningful rename as a model decision, not merely a vocabulary edit. Keep modelers involved in implementation and developers involved in modeling.

## Deliver only what advances the work

Return the chosen model and why it fits, a few sentences that exercise its behavior, and the remaining uncertainties. A compact vocabulary can record term, contextual meaning, important rule, and evidence. Add a diagram only when it clarifies relationships that prose does not.

For an existing implementation, identify the specific names or responsibilities that disagree with the model and the next bounded change. For exploration, keep alternatives provisional; do not silently expand into implementation or a complete requirements program. Update an existing artifact when one already owns the knowledge.

## Check the result

- Can the scenario be explained without translating between business nouns and unrelated code nouns?
- Does the model express what makes a decision valid, including exceptions?
- Is each important claim supported or explicitly provisional?
- Can the model plausibly be implemented without maintaining a second, unrelated design model?
- Have conflicting meanings been investigated before attempting a universal glossary?

Read [discovery techniques](references/discovery-techniques.md) when conversations stall, evidence conflicts, or the role of documentation is unclear.

Source: Eric Evans, *Domain-Driven Design*, final manuscript, April 15, 2003, chapters 1–3, pp. 15–48. Page numbers refer to the supplied manuscript, not a later print edition. These instructions operationalize the source in original wording; the reference includes source locations.
