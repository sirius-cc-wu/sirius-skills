---
name: example-mapping
description: Clarify a user story through Example Mapping before implementation. Use for BDD discovery, three-amigos preparation or facilitation, and reviewing acceptance criteria for uncertainty or oversized scope. Not a Gherkin-generation or implementation workflow.
---

# Example Mapping

## Discovery workflow

Seek shared understanding with product, development, and testing perspectives; include other relevant expertise. Focus on one story, usually for 25 minutes.

Capture a map as the conversation develops:

| Card | Meaning |
| --- | --- |
| Yellow | Story; separately capture deferred slices |
| Blue | Rule or acceptance constraint beneath its story |
| Green | Concrete example beneath its rule |
| Red | Unanswered question or assumption |

Rules generalize; examples illustrate particular situations and outcomes. Use brief descriptions, adding detail where ambiguity demands it. An unknown outcome is a question. Skip examples for rules already understood. Record unresolved debates and continue.

Many questions suggest missing knowledge; many rules suggest splitting the story; many examples under one rule suggest separating rules. Slice along rule boundaries.

Stop when scope is clear or time expires. Let participants assess readiness; minor questions need not block development. Otherwise identify research or smaller slices. Treat 25 minutes as guidance, not a deadline proving readiness.

Usually defer Gherkin formulation; joint formulation can help establish domain language early.

## Agent adaptation

These operating conventions adapt the workshop to an assistant:

- Start from the supplied story and evidence. If no story is identifiable, ask for it. Do not manufacture requirements to fill the map.
- Distinguish supplied decisions from proposed rules, illustrative examples, and unresolved assumptions. Never present simulated participant perspectives as stakeholder agreement.
- In an interactive session, ask the question most likely to change scope or an expected outcome, then update the map. For a document-only request, deliver a provisional map with explicit unknowns.
- Use nested Markdown or the user's existing board. Keep each example attached to its rule; link questions to affected items. Colors are optional labels.
- Close with the map, proposed deferred stories, unresolved questions and suggested sources of answers, and a readiness assessment with its basis. If stakeholders have not assessed readiness, label yours provisional.
- Use an existing artifact location when saving is requested; do not create a specification hierarchy or start implementation merely because mapping is complete.

## Source

Distilled from Matt Wynne, [Introducing Example Mapping](https://cucumber.io/blog/bdd/example-mapping-introduction/), December 8, 2015. The agent conventions above are adaptations, not claims from the article.
