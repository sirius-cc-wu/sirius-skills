---
name: specify
description: Brainstorming and requirement specification expert.
---

# Specification Skill

Use this skill to transform vague ideas into concrete `spec.md` files.

## Specification Format
This skill uses a single, comprehensive specification format that includes:
- **User Scenarios**: Prioritized user journeys (P1, P2, etc.).
- **Acceptance Scenarios**: BDD-style Given/When/Then tests for each user story.
- **Functional Requirements**: A formal list of what the system must do.
- **Key Entities**: A description of data models involved.
- **Success Criteria**: Measurable outcomes to validate the feature's success.

## Specification Template
This skill uses a single markdown template (`spec-template.md`) to ensure a consistent, rigorous structure for all specifications.

## Protocol: Sequential Questioning

To maintain precision and reduce cognitive load, follow these rules:
1. **Identify**: Scan the feature request for all ambiguities in the template.
2. **Prioritize**: Group related ambiguities into logical clusters.
3. **The One-Question Rule**: Present only ONE group of questions to the user at a time.
4. **Iterate**: Integrate the user's answer into the draft before moving to the next ambiguity group.

## Workflow
1. Use the `spec-driver` skill to initialize the track.
2. **Copy the `spec-template.md`** from the `templates/` directory to the `specs/<ID>-<name>/spec.md` file.
3. Apply Sequential Questioning to fill in all sections of the template.
4. Output the final `spec.md` in the designated `specs/<ID>-<name>/` folder.
