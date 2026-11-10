---
name: system-behavior
description: Derive black-box system sequence diagrams and selective operation contracts from use-case scenarios. Use to clarify external system events and domain state changes before object design; not to specify internal service collaborations.
---

# Specify the system boundary and observable effects

Start with a selected use-case path, a defined system boundary, and the relevant domain vocabulary. If inputs are incomplete, work with a clearly labeled partial scenario rather than inventing a complete requirement set.

## Derive system events

1. Identify the external actors that directly interact with the system on this path.
2. Read the scenario in order. Extract events crossing the system boundary and relevant returned information. Distinguish an actor's intent from a particular device gesture.
3. Name input events as operations at the intent level, with meaningful parameters: `borrowItem(itemId)` rather than `scanBarcode()` unless scanning itself is the domain operation.
4. Draw the system as one black-box participant in a system sequence diagram (SSD). Include supporting external systems when their interaction matters. Do not open the box into controllers, services, or databases.
5. Show repetition, significant conditions, and results needed to understand the chosen path. Model important alternate paths separately or with readable fragments.
6. Define ambiguous parameter types, formats, units, and returned values in the glossary.

The SSD identifies a system interface. Its `System` lifeline does not require a software class named `System` or a single implementation object responsible for all operations.

## Add contracts selectively

Write an operation contract when the scenario leaves subtle state changes unclear. Skip contracts whose effects are already obvious to the implementer from the requirements.

Use:

- **Operation:** signature and parameter meanings.
- **Cross-references:** use case and selected scenario.
- **Preconditions:** noteworthy facts assumed to hold before invocation.
- **Postconditions:** domain-state changes true after successful completion.

Describe postconditions declaratively, preferably as completed changes: instances created or deleted, attributes changed, and links formed or broken. State the identities involved. A new instance usually needs associations as well as attribute values.

Do not write an algorithm, name implementation methods, prescribe SQL, or specify memory allocation. Do not claim that a successful contract defines failure behavior; describe failures and preserved guarantees separately when the scenario requires them. Do not hide required validation by declaring the checked condition a precondition.

If a contract discovers a missing concept or relationship, revise the domain model. If legal event order is complex, add a focused state machine; do not force ordering rules into unrelated contracts.

## Deliver and review

Provide the SSD, necessary contracts, and any newly exposed requirement questions. Trace each event back to the scenario and each postcondition to a domain concept. Walk a concrete before/after state through the contract and confirm that identities, links, and relevant invariants agree.

Read [worked contract](references/worked-contract.md) for an example and common omissions.

## Source

Distilled and paraphrased from Larman, *Applying UML and Patterns*, third edition, chapters 10, 11, and 31; supplied PDF pp. 272–307 and 683–689. Positions are 1-based PDF pages. Explicit failure-guarantee checks are practical additions to the book's primarily successful-operation examples.
