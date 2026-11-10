# Context transformations

Use only when changing a relationship is in scope. A target context map is a hypothesis about feasible model and team changes. Keep the current map accurate throughout the transition. (Chapter 14, pp. 268–278.)

## Compare the tradeoffs

Larger contexts can reduce translation and make integrated behavior easier to explain, but demand coordination and a genuinely unified model. Smaller contexts permit local variation and autonomy, but add contracts, translations, and consistency costs. Consider real team relationships and system constraints before choosing a direction. The most elegant model is irrelevant if nobody can sustain its integration process. (pp. 268–273.)

## Introduce a Shared Kernel

Confirm that each context is internally coherent first. Establish shared ownership, integration practices, and a joint test mechanism before sharing model code. Start with a small duplicated, relatively noncritical concept and reconcile its semantics explicitly. Refactor both contexts toward the shared model and test their behavior together. Expand based on evidence rather than moving a large common package at once. (pp. 274–275.)

## Merge contexts

A growing Shared Kernel does not itself prove that a full merger is appropriate. Prepare shared code ownership and compatible integration practices; develop understanding of both models and their core concepts. Unify incrementally, using temporary translation where necessary, and recognize that vocabulary and team coordination change with the code. Treat organizational changes as proposals until the relevant people have actually adopted them. (p. 276.)

## Phase out a legacy capability

Choose a behavior small enough to replace and verify. Determine the required ACL changes, how requests reach the new behavior, and what still depends on the old system. Compare old and new results where appropriate, with explicit handling for intentional differences. Remove old responsibility only after the replacement and its integrations have been demonstrated. Keep each iteration's remaining legacy boundary visible. (p. 277.)

Operational adaptation: for stateful migration, specify data ownership during transition, compatibility needs, failure detection, and rollback or another recovery strategy. These details depend on the actual stack; the manuscript's incremental transition is not a complete migration runbook.

## Move to a Published Language

Identify the interchange concepts and consumer expectations, define the shared vocabulary, and migrate translations without assuming all participants change simultaneously. Versioning and compatibility mechanisms depend on the existing contract. Keep specialized local concepts behind translations when they are not part of the exchange. (p. 278.)
