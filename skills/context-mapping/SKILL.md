---
name: context-mapping
description: Identify bounded contexts and map actual relationships between domain models and teams. Use when terminology conflicts across systems, integration leaks foreign concepts, or context boundaries and integration strategies must be designed or reviewed; not to infer microservices from business nouns.
---

# Context Mapping

Make the scope of each model explicit and describe what happens at its boundaries. Start with the system and team relationships that exist, then separate any proposed transformation.

## Map the current situation

1. Gather evidence from behavior, terminology, repositories, schemas, interfaces, team ownership, and integration practices. Include legacy and external systems even when they lack an explicit object model.
2. Identify where a term, identity, or rule has a consistent meaning and where it changes. Name each bounded context and describe its scope in code, data, usage, and team responsibility. A repository, team, process, or database alone does not prove a context boundary.
3. Map each actual contact: model or data exchanged, semantic translation, shared artifacts, and the people who can change it. Label arrows so upstream/downstream influence cannot be confused with request or data-flow direction. Mark unknowns and inconsistent regions rather than inventing clean boundaries.
4. Describe how each context keeps its own model unified: frequent integration, automated checks, and active use of shared language. Passing builds alone do not prevent incompatible meanings of the same concept.
5. Decide which relationships need improvement. Consider whether integration is needed, how much influence the downstream has, whether independent models are valuable, and whether teams can sustain joint ownership. Use [relationship choices](references/relationship-choices.md) to choose or combine patterns supported by that evidence.

## Keep distinct boundaries distinct

- A bounded context defines where a model applies; a module organizes concepts, and an aggregate protects consistency. None automatically defines the other.
- Different contexts can live in one executable. Similar-looking models can require different contexts. Do not prescribe microservices or a universal enterprise model from a map alone.
- A context map records reality. Keep desired relationships separately labeled and do not imply that teams have agreed to proposed cooperation.
- An anticorruption layer translates meaning and actions, not just wire formats. Identify mismatched identities, statuses, units, and rules before naming an adapter an ACL.

## Deliver and validate

Return a context inventory and a map or relationship table, with evidence and unknowns. For each material connection, identify semantic contract, change ownership, translation/sharing, and the check that would expose breakage. Trace a representative exchange in both directions where applicable, including an incompatible or missing value.

If a transformation is requested, read [context transformations](references/context-transformations.md) and propose a bounded first step with transition behavior, checks, and a recovery path. A diagram change does not itself merge models, reorganize teams, or authorize a deployment.

Source: Eric Evans, *Domain-Driven Design*, final manuscript, April 15, 2003, chapter 14, pp. 235–278. These are original operational instructions; modern deployment distinctions prevent extending the manuscript's claims beyond their scope.
