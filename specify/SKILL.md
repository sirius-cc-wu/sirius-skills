---
name: specify
description: Brainstorming and requirement specification expert.
---

# Specification Skill

Use this skill to transform vague ideas into concrete `spec.md` files.

## Supported Specification Formats
This skill supports the creation of specifications in three primary formats:
- **User Story**: Describes a feature from an end-user perspective, focusing on "who," "what," and "why."
- **Use Case**: Details interactions between users and a system to achieve a specific goal.
- **Behavior-Driven Development (BDD)**: Defines features through examples using a Gherkin-like syntax (Given, When, Then).

## Specification Templates
This skill uses markdown templates to ensure a consistent structure for each specification format. The templates are located in the `templates/` directory:
- `user_story.md`
- `use_case.md`
- `bdd.md`

## Protocol: Sequential Questioning

To maintain precision and reduce cognitive load, follow these rules:
1. **Identify**: Scan the feature request for all ambiguities.
2. **Prioritize**: Group related ambiguities into logical clusters.
3. **The One-Question Rule**: Present only ONE group of questions to the user at a time.
4. **Iterate**: Integrate the user's answer into the draft before moving to the next ambiguity group.

## Workflow
1. Prompt the user to choose a specification format (User Story, Use Case, or BDD).
2. Use the `spec-driver` skill to initialize the track.
3. **Copy the corresponding template** from the `templates/` directory to the `specs/<ID>-<name>/spec.md` file.
4. Apply Sequential Questioning to fill in the template with the defined boundaries, inputs, and expected outcomes.
5. Output the final `spec.md` in the designated `specs/<ID>-<name>/` folder.
