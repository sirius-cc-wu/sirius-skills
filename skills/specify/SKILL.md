---
name: specify
description: Brainstorming and requirement specification expert.
---

# Specification Skill

Use this skill to transform vague ideas into concrete, validated `spec.md` files.

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

## Required Outputs

For each track, produce:

1. `<track_path>/spec.md`
2. `<track_path>/checklists/requirements.md`

The checklist is required and must be updated as validation progresses.

Resolve `<track_path>` with `spec-driver` tooling.

## Protocol: Sequential Questioning

To maintain precision and reduce cognitive load, follow these rules:
1. **Identify**: Scan the feature request for all ambiguities in the template.
2. **Prioritize**: Group related ambiguities into logical clusters.
3. **The One-Question Rule**: Present only ONE group of questions to the user at a time.
4. **Iterate**: Integrate the user's answer into the draft before moving to the next ambiguity group.
5. **Clarification Cap**: Keep unresolved markers to a maximum of 3 using:
   - `[NEEDS CLARIFICATION: ...]`
6. **Defaulting Rule**: If non-critical details are missing, make reasonable defaults and document them explicitly in the spec.

## Quality Gates (Must Pass Before Handoff)

1. No implementation leakage:
   - No framework, library, API route, class, schema, or code-level design decisions in `spec.md`.
2. Requirement quality:
   - Requirements are testable and unambiguous.
   - Success criteria are measurable and technology-agnostic.
3. Scenario quality:
   - At least one independent P1 story with Given/When/Then acceptance scenarios.
4. Clarifications:
   - 0 preferred; at most 3 unresolved critical clarifications allowed.

If a gate fails, revise and re-run validation. Perform up to 3 correction passes.

## Workflow
1. Use `spec-driver` tooling to bootstrap/resolve the active track.
2. Copy `templates/spec-template.md` to `<track_path>/spec.md`.
3. Apply Sequential Questioning and fill all template sections.
4. Create checklist from `templates/requirements-checklist-template.md` into `<track_path>/checklists/requirements.md`.
5. Run quality gates and update checklist status.
6. If needed, perform correction passes (max 3).
7. Return a completion summary:
   - Track ID and path
   - `spec.md` path
   - Checklist pass/fail status
   - Recommended next step (`plan` or additional clarification)
