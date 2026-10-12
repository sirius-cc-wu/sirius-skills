# Behavior Classification

Classify each observed behavior before it can enter a normative artifact.

| Class | Evidence that supports the class | Result in the specification | Result in the conformance record |
| :--- | :--- | :--- | :--- |
| Intended | A requirement, ticket, decision record, standard, interface contract, test name that states the behavior as wanted, or a decision of the decision owner | A rule with an acceptance example | Conforms |
| Accidental | No intent evidence and no dependent caller | Omit | Omit |
| Defect | The behavior breaks stated intent, a standard, an invariant, or a reasonable safety expectation: a crash, a hang, silent data loss, a misrouted or lost response, or an unbounded resource use | A rule for the remedy only when cited intent, a standard, or an invariant determines it. Otherwise an open question that lists the remedy options (for example reject, retry, recover, or stop) | Gap, with a follow-up owner |
| Undecided | The evidence supports more than one reasonable behavior, the choice is a product or policy choice, or only a dependent caller supports the behavior | An open question until the decision owner decides | Not verified until a rule exists |

## Evidence Weight

- A dependent caller shows the compatibility impact of a change. It is not
  intent evidence: a caller and a callee can grow around an accident together.
  Present the dependency to the decision owner as a consequence of each
  option.
- A test proves that a behavior exists. It is intent evidence only when its
  name or its assertion states the behavior as wanted.
- A commit message, a review comment, or an issue can be intent evidence. Cite
  it with a locator.
- An old document is intent evidence only for its own revision. It does not
  prove that the current code conforms.

## Common Mistakes

- Writing the current behavior as a rule because no one complained.
- Writing a defect as behavior because the code does it.
- Deciding an undecided item silently, in either direction.
- Treating a dependent caller as approval of the behavior that it uses.
- Choosing a defect remedy that the evidence does not determine.
- Treating an implementation detail (a task, a queue, a build switch) as a
  requirement.
