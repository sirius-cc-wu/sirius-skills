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

## Story Type Guidance

To provide flexibility in capturing requirements, the specification template supports several story formats. Choose the one that best fits the context of the requirement.

### 1. Standard User Story

This is the most common format, focused on a user's needs and goals.

- **Format**: `As a [user role], I want to [goal] so that [benefit].`
- **Use When**: You need to describe a feature from the perspective of an end-user who will interact directly with the system.

### 2. Job Story

This format focuses on the "job to be done" and the context that triggers it, rather than just the user role.

- **Format**: `When [situation], I want to [motivation] so I can [expected outcome].`
- **Use When**: The user's role is less important than the situation they are in. It helps to understand the underlying motivations and expected outcomes.

### 3. Team Story

This format is for requirements that address the needs of the development team itself.

- **Format**: `We want to [action] so that [reason].`
- **Use When**: The work is not directly for an end-user but is necessary for the team to improve its process, tooling, or infrastructure (e.g., "We want to refactor the database schema so that it is more maintainable").

### 4. Technical Story

This format is used for technical tasks or non-functional requirements that don't have a direct user-facing benefit.

- **Format**: `[Action] the [result] [by|for|of|to] a(n) [object].`
- **Use When**: You need to describe a purely technical task, such as a backend change, an API integration, or a performance improvement (e.g., "Estimate the closing price of a stock").

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
