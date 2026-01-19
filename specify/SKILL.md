---
name: specify
description: Brainstorming and requirement specification expert.
---

# Specification Skill

Use this skill to transform vague ideas into concrete `spec.md` files.

## Protocol: Sequential Questioning

To maintain precision and reduce cognitive load, follow these rules:
1. **Identify**: Scan the feature request for all ambiguities.
2. **Prioritize**: Group related ambiguities into logical clusters.
3. **The One-Question Rule**: Present only ONE group of questions to the user at a time.
4. **Iterate**: Integrate the user's answer into the draft before moving to the next ambiguity group.

## Workflow
1. Use `.github/skills/conductor/scripts/manage_specs.py` to initialize the track.
2. Apply Sequential Questioning to define boundaries, inputs, and expected outcomes.
3. Output the final `spec.md` in the designated `specs/<ID>-<name>/` folder.
