# Discovery techniques

Use these prompts selectively; they are ways to expose uncertainty, not a required interview script.

| Signal | Experiment | Evidence to retain |
|---|---|---|
| Experts describe screens or reports only | Ask what decision the output enables, and walk backward to its rule | The business decision and required information |
| Two terms appear synonymous | Substitute each in the same scenario, including an exception | Whether they are synonyms, distinct concepts, or context-specific meanings |
| A familiar noun hides different meanings | Compare identity, lifecycle, and rules in each usage | An explicit scope for each meaning |
| Rules live only in people's explanations | Ask for a valid and invalid example with identical-looking data | The previously implicit policy or constraint |
| A diagram seems convincing but code resists it | Implement or sketch the smallest meaningful interaction | The concrete mismatch; revise the abstraction if needed |
| The model grows without getting clearer | Remove a concept and rerun the important scenarios | Which concepts are necessary and which are incidental |

## Knowledge crunching

Do not treat the expert as a requirements oracle or the developer as a transcription service. Compare multiple explanations and let prototypes expose gaps in both business understanding and implementation. The useful result is accumulated understanding, even when an early feature or model is later discarded. Distinguish simplification for the application's purpose from denial of a real rule. (Chapter 1, pp. 15–23.)

Original example: a repair desk asks for a list of overdue tools. Determine whether lateness belongs to a tool, a particular loan, or a return commitment. Ask how extensions and replacement tools work. Those scenarios can show that a tool's identity and a loan's deadline are different concepts; collecting more fields on `Tool` would hide that distinction.

## Language as a model experiment

Use verbs and sentences, not only a glossary. Ask whether “the borrower extends the tool” says what the business means, or whether “the desk extends the loan's due date” exposes the real rule. Shared language evolves with insight and is consistent within an explicit context. Retain outside terminology where it supplies context; do not force every word into the software model. (Chapter 2, pp. 24–30.)

## Documents and diagrams

Use a diagram to expose a few important relationships and prose to explain their meaning. Do not try to encode every implementation detail in UML. Documents should explain intent and selected concepts, complementing executable behavior. A document that nobody uses or cannot keep aligned should be reduced or retired rather than treated as an authoritative parallel model. (Chapter 2, pp. 31–36.)

## One model with implementation feedback

An analysis model that cannot support the design loses knowledge during the handoff. Seek concepts that are meaningful in the domain and practical in the implementation. This does not mean turning a database schema into the business vocabulary. Where a model is visible to users, check that its distinctions support their tasks. Maintain direct feedback between model decisions and the code that realizes them. (Chapter 3, pp. 37–48.)
